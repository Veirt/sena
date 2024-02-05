import os
import sys
from . import bot
from .config import DISCORD_BOT_TOKEN
import logging
import logging.handlers


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@bot.event
async def on_ready():
    logging.info(f"Logged on as {bot.user}!")

    cogs = list(
        filter(
            lambda file: not file.startswith("__") and file.endswith(".py"),
            os.listdir("src/the_fool/cogs"),
        )
    )

    for cog in cogs:
        await bot.load_extension(f"the_fool.cogs.{cog[:-3]}")


bot.run(DISCORD_BOT_TOKEN, log_handler=None)
