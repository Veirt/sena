import g4f
import aiohttp
import logging
from discord.ext import commands
from ..config import DISCORD_GEMINI_CHANNEL_ID
from ..utils.split_message import MAX_MESSAGE_LEN, split_message_to_chunks

import the_fool.utils.cookies


async def setup(bot):
    await bot.add_cog(LLM(bot))


async def get_image(image_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            return await resp.read()


messages = []


class LLM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _send_to_discord(self, ctx, answer):
        if len(answer) > MAX_MESSAGE_LEN:
            msg_chunks = split_message_to_chunks(answer)
            for msg in msg_chunks:
                await ctx.reply(msg)

            return

        await ctx.reply(answer)

    async def _get_gemini_answer_bardapi(self, ctx, question):
        try:
            from ..utils.gemini import bard_instance
        except Exception as e:
            logging.error(e)
            await ctx.reply("Gemini over Bard-API is not available.")
            return

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

        await self._send_to_discord(ctx, answer)
        if len(links) > 0:
            links = links[:3]
            await self._send_to_discord(ctx, "\n".join(links))

    async def _get_gemini_answer_g4f(self, ctx, question):
        global messages
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

        image = None
        image_name = None
        if len(attachments) > 0:
            image = await get_image(attachments[0].url)
            image_name = attachments[0].filename

        async with ctx.typing():
            messages.append({"role": "user", "content": question})
            answer = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,  # Using the default model
                provider=g4f.Provider.Gemini,  # Specifying the provider as Gemini
                messages=messages,
                image=image,
                image_name=image_name,
                stream=False,
            )  # type: ignore

            messages.append({"role": "assistant", "content": answer})

        if len(answer) > MAX_MESSAGE_LEN:
            msg_chunks = split_message_to_chunks(answer)
            for msg in msg_chunks:
                await ctx.reply(msg)

            return

        await ctx.reply(answer)

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.author.bot  # if author is a bot
            or message.content.startswith(
                self.bot.command_prefix
            )  # if it starts with the prefix
            or message.channel.id != DISCORD_GEMINI_CHANNEL_ID  # if it's not
        ):
            return

        ctx = await self.bot.get_context(message)
        try:
            await self._get_gemini_answer_bardapi(ctx, message.content)
        except Exception as e:
            logging.error(e)
            await self._get_gemini_answer_g4f(ctx, message.content)

    @commands.command(
        help="Ask Gemini a question. Supports asking questions about images.",
        brief="Ask Gemini a question.",
    )
    async def gemini(self, ctx, *args):
        question = " ".join(args)
        try:
            await self._get_gemini_answer_bardapi(ctx, question)
        except Exception:
            await self._get_gemini_answer_g4f(ctx, question)

    @commands.command(help="Ask GPT-3 a question.", brief="Ask GPT-3 a question.")
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

        await self._send_to_discord(ctx, answer)

    @commands.command(
        help="Ask GPT-4 a question. May not work all the time.",
        brief="Ask GPT-4 a question.",
    )
    async def gpt4(self, ctx, *args):
        providers = ["GptChatly", "Raycast", "Liaobots"]
        logging.debug(providers)

        # Execute with a specific provider
        async with ctx.typing():
            answer = await g4f.ChatCompletion.create_async(
                model=g4f.models.gpt_4,
                messages=[{"role": "user", "content": " ".join(args)}],
                providers=providers,
            )  # type: ignore

            await self._send_to_discord(ctx, answer)

    @commands.command()
    async def llama2(self, ctx, *args):
        async with ctx.typing():
            answer = await g4f.ChatCompletion.create_async(
                model=g4f.models.llama2_7b,
                messages=[{"role": "user", "content": " ".join(args)}],
            )  # type: ignore

            await self._send_to_discord(ctx, answer)

    @commands.command(help="Reset the conversation.", brief="Reset the conversation.")
    async def reset(self, ctx):
        global messages
        messages = []
        await ctx.reply("Conversation has been reset.")
