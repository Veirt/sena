from . import bot
from .bard import bard_instance
from .config import DISCORD_CHANNEL_ID, DISCORD_BOT_TOKEN
from .utils import MAX_MESSAGE_LEN, split_message_to_chunks


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

        if len(answer) > MAX_MESSAGE_LEN:
            msg_chunks = split_message_to_chunks(answer)
            for msg in msg_chunks:
                await message.channel.send(msg)

            return

        await message.channel.send(answer)


bot.run(DISCORD_BOT_TOKEN)
