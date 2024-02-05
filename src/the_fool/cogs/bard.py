import aiohttp
import logging
from discord.ext import commands
from ..bard import bard_instance
from ..config import DISCORD_BARD_CHANNEL_ID
from ..utils import MAX_MESSAGE_LEN, split_message_to_chunks


async def setup(bot):
    await bot.add_cog(Bard(bot))


async def get_image(image_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            return await resp.read()


class Bard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _get_bard_answer(self, ctx, question):
        if len(ctx.message.attachments) > 1:
            ctx.reply(
                "Cannot read more than one image at a time. If you send multiple images, only the first one will be read."
            )
        attachments = list(
            filter(
                lambda attachment: attachment.filename.endswith(".png")
                or attachment.filename.endswith(".jpg"),
                ctx.message.attachments,
            )
        )

        async with ctx.typing():
            try:
                if len(attachments) > 0:
                    image = await get_image(attachments[0].url)
                    response = bard_instance.ask_about_image(question, image)
                else:
                    logging.debug("Bard: Regular question")
                    response = bard_instance.get_answer(question)

                links = response["links"]
                answer = response["content"]
            except Exception as e:
                await ctx.reply(f"An error happened. Error: {e}")
                return

        if len(answer) > MAX_MESSAGE_LEN:
            msg_chunks = split_message_to_chunks(answer)
            for msg in msg_chunks:
                await ctx.reply(msg)

            return

        await ctx.reply(answer)
        if len(links) > 0:
            await ctx.send("\n".join(links))

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.author.bot  # if author is a bot
            or message.content.startswith(
                self.bot.command_prefix
            )  # if it starts with the prefix
            or message.channel.id != DISCORD_BARD_CHANNEL_ID  # if it's not
        ):
            return

        ctx = await self.bot.get_context(message)
        await self._get_bard_answer(ctx, message.content)

    @commands.command()
    async def bard(self, ctx, *args):
        await self._get_bard_answer(ctx, "".join(args))
