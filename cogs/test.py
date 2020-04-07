import discord
from discord.ext import commands

class Example(commands.Cog):
    def __init__(self, client):
        super().__init__()
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.__class__.__name__} is online")

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong")

def setup(client):
    client.add_cog(Example(client))