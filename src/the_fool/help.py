import discord
from discord.ext import commands


class HelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=discord.Color.blurple(), description="")
        for page in self.paginator.pages:
            assert type(e.description) == str
            e.description += page
        await destination.send(embed=e)
