import os
import sys
from . import bot
from .config import DISCORD_BOT_TOKEN
import logging
import logging.handlers


DEV = os.getenv("DEV", False)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG if DEV else logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("discord").setLevel(logging.INFO)


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
        logging.info(f"Cog {cog[:-3]} loaded successfully")


bot.run(DISCORD_BOT_TOKEN, log_handler=None)
