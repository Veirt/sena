from discord.ext import commands
from ..bard import bard_instance
from ..config import DISCORD_BARD_CHANNEL_ID
from ..utils import MAX_MESSAGE_LEN, split_message_to_chunks


async def setup(bot):
    await bot.add_cog(Bard(bot))


class Bard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return

        if message.channel.id == DISCORD_BARD_CHANNEL_ID:
            ctx = await self.bot.get_context(message)
            async with ctx.typing():
                try:
                    response = bard_instance.get_answer(message.content)
                    links = response["links"]
                    answer = response["content"]
                except Exception as e:
                    await message.channel.send(f"An error happened. Error: {e}")
                    return

            if len(answer) > MAX_MESSAGE_LEN:
                msg_chunks = split_message_to_chunks(answer)
                for msg in msg_chunks:
                    await message.channel.send(msg)

                return

            await message.channel.send(answer)
            if len(links) > 0:
                await message.channel.send("\n".join(links))

    @commands.command()
    async def bard(self, ctx, *args):
        async with ctx.typing():
            try:
                answer = bard_instance.get_answer("".join(args))["content"]
            except Exception as e:
                await ctx.send(f"An error happened. Error: {e}")
                return

        if len(answer) > MAX_MESSAGE_LEN:
            msg_chunks = split_message_to_chunks(answer)
            for msg in msg_chunks:
                await ctx.send(msg)

            return

        await ctx.send(answer)
