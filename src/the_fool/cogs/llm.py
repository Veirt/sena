import g4f
import aiohttp
import logging
from discord.ext import commands
from ..bard import bard_instance
from ..config import DISCORD_BARD_CHANNEL_ID
from ..utils import MAX_MESSAGE_LEN, split_message_to_chunks


async def setup(bot):
    await bot.add_cog(LLM(bot))


async def get_image(image_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            return await resp.read()


class LLM(commands.Cog):
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
            links = links[:3]
            link_chunks = split_message_to_chunks("\n".join(links))
            for link_chunk in link_chunks:
                await ctx.send(link_chunk)

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
        await self._get_bard_answer(ctx, " ".join(args))

    @commands.command()
    async def gpt3(self, ctx, *args):
        providers = [
            provider.__name__
            for provider in g4f.Provider.__providers__
            if provider.working
        ]

        # Execute with a specific provider
        async with ctx.typing():
            answer = await g4f.ChatCompletion.create_async(
                model=g4f.models.gpt_35_turbo,
                messages=[{"role": "user", "content": " ".join(args)}],
                providers=providers,
            )  # type: ignore

        if len(answer) > MAX_MESSAGE_LEN:
            msg_chunks = split_message_to_chunks(answer)
            for msg in msg_chunks:
                await ctx.reply(msg)

            return

        await ctx.reply(answer)

    @commands.command()
    async def gpt4(self, ctx, *args):
        providers = [
            provider.__name__
            for provider in g4f.Provider.__providers__
            if provider.working
        ]

        # Execute with a specific provider
        async with ctx.typing():
            answer = await g4f.ChatCompletion.create_async(
                model=g4f.models.gpt_4,
                messages=[{"role": "user", "content": " ".join(args)}],
                providers=providers,
            )  # type: ignore

        if len(answer) > MAX_MESSAGE_LEN:
            msg_chunks = split_message_to_chunks(answer)
            for msg in msg_chunks:
                await ctx.reply(msg)

            return

        await ctx.reply(answer)
