import logging
import aria2p
import qbittorrentapi
from discord.ext import commands
from enum import Enum
from ..config import (
    ARIA2_HOST,
    ARIA2_PORT,
    ARIA2_SECRET,
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
    logging.error(e)

try:
    if not ARIA2_HOST or not ARIA2_PORT or not ARIA2_SECRET:
        raise ValueError("Aria2 connection info is not set")

    aria2 = aria2p.API(
        aria2p.Client(host=ARIA2_HOST, port=int(ARIA2_PORT), secret=ARIA2_SECRET)
    )
    aria2.get_downloads()
except Exception as e:
    aria2 = None
    logging.warning("Failed to connect to aria2. HTTP download is not available.")
    logging.error(e)


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
        assert aria2
        aria2.add(self.uri)

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

    @commands.command(
        help="Download a torrent or a file from a URL. Usage: download <URI> [category]",
        brief="Download a torrent or a file from a URL. Owner only.",
    )
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

        downloader.download()
        await ctx.reply("Download has started")
