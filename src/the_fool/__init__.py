import discord
from discord.ext import commands
from .help import HelpCommand


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)
bot.help_command = HelpCommand()
