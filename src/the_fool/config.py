import dotenv
import os

dotenv.load_dotenv()


if not os.environ["DISCORD_BOT_TOKEN"]:
    print("DISCORD_BOT_TOKEN is not present.")
    exit(1)

if not os.environ["DISCORD_CHANNEL_ID"]:
    print("DISCORD_CHANNEL_ID is not present.")
    exit(1)

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])
