from . import bot
from .bard import bard_instance
from .config import DISCORD_CHANNEL_ID, DISCORD_BOT_TOKEN
import re

MAX_MESSAGE_LEN = 2000


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == DISCORD_CHANNEL_ID:
        ctx = await bot.get_context(message)
        async with ctx.typing():
            try:
                answer = bard_instance.get_answer(message.content)["content"]
            except Exception as e:
                await message.channel.send(f"An error happened. Error: {e}")
                return

        paragraphs = re.split(r"(?:\n\s*\n)|(?:\r\n\s*\r\n)", answer)

        for paragraph in paragraphs:
            if not paragraph.strip():
                continue

            # Truncate paragraph if exceeds max length
            if len(paragraph) > MAX_MESSAGE_LEN:
                paragraph = paragraph[:MAX_MESSAGE_LEN] + "..."

            await message.channel.send(paragraph)


bot.run(DISCORD_BOT_TOKEN)
