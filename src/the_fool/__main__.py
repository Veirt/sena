import os
from . import bot
from .config import DISCORD_BOT_TOKEN


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")

    cogs = list(
        filter(
            lambda file: not file.startswith("__") and file.endswith(".py"),
            os.listdir("src/the_fool/cogs"),
        )
    )

    for cog in cogs:
        await bot.load_extension(f"the_fool.cogs.{cog[:-3]}")


bot.run(DISCORD_BOT_TOKEN)
