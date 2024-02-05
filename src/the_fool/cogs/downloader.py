import logging
from discord.ext import commands
from enum import Enum
import qbittorrentapi
from ..config import (
    QBITTORRENT_HOST,
    QBITTORRENT_PORT,
    QBITTORRENT_USERNAME,
    QBITTORRENT_PASSWORD,
)


conn_info = dict(
    host=QBITTORRENT_HOST,
    port=QBITTORRENT_PORT,
    username=QBITTORRENT_USERNAME,
    password=QBITTORRENT_PASSWORD,
    VERIFY_WEBUI_CERTIFICATE=False,
)

logging.debug(f"Torrent connection info: {conn_info}")
try:
    qb = qbittorrentapi.Client(**conn_info)  # type: ignore
except Exception as e:
    qb = None
    logging.warning(
        "Failed to connect to qBittorrent. Torrent download is not available."
    )


class SupportedDownloadType(Enum):
    HTTP = 1
    TORRENT = 2


class DownloadHandler:
    def __init__(self, uri: str, category=""):
        self.uri = uri
        self.category = category

        if uri.endswith(".torrent") or uri.startswith("magnet"):
            self.type = SupportedDownloadType.TORRENT
            if not qb:
                raise ValueError("Torrent download is not available")
        elif uri.startswith("http"):
            self.type = SupportedDownloadType.HTTP
        else:
            logging.error(f"Unsupported download type with URI: {self.uri}")
            raise ValueError("Unsupported download type")

    def _download_http(self):
        pass

    def _download_torrent(self):
        assert qb
        qb.torrents_add(urls=self.uri, category=self.category)

    def download(self):
        if self.type == SupportedDownloadType.HTTP:
            self._download_http()
        elif self.type == SupportedDownloadType.TORRENT:
            self._download_torrent()


async def setup(bot):
    await bot.add_cog(Downloader(bot))


class Downloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def download(self, ctx, *args):
        if len(args) < 1:
            await ctx.reply("Too few arguments")
            return

        if len(args) > 2:
            await ctx.reply("Too many arguments")
            return

        uri = args[0]
        category = args[1] if len(args) == 2 else ""

        try:
            downloader = DownloadHandler(uri, category)
        except Exception as e:
            await ctx.reply(f"Cannot download. Error: {e}")
            return

        assert qb

        if downloader.type == SupportedDownloadType.TORRENT:
            available_categories = qb.torrents_categories().keys()
            if downloader.category not in available_categories:
                await ctx.reply(
                    f"Category doesn't exist.\nAvailable: {', '.join(available_categories)}"
                )
                return

        if downloader.type == SupportedDownloadType.HTTP:
            await ctx.reply("TODO. implement later.")
            return

        downloader.download()
        await ctx.reply("Download has started")
