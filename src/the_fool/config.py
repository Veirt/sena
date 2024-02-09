import dotenv
import os

dotenv.load_dotenv()


if not os.environ["DISCORD_BOT_TOKEN"]:
    print("DISCORD_BOT_TOKEN is not present.")
    exit(1)

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_GEMINI_CHANNEL_ID = int(os.getenv("DISCORD_GEMINI_CHANNEL_ID", ""))

QBITTORRENT_HOST = os.getenv("QBITTORRENT_HOST")
QBITTORRENT_PORT = os.getenv("QBITTORRENT_PORT")
QBITTORRENT_USERNAME = os.getenv("QBITTORRENT_USERNAME")
QBITTORRENT_PASSWORD = os.getenv("QBITTORRENT_PASSWORD")

ARIA2_HOST = os.getenv("ARIA2_HOST")
ARIA2_PORT = os.getenv("ARIA2_PORT")
ARIA2_SECRET = os.getenv("ARIA2_SECRET")
