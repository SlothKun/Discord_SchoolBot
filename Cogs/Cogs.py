from discord.ext import commands
import discord
from pymongo import MongoClient
import datetime
import json

class Test(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Tu devrais regarder mon status")
        await self.bot.change_presence(status=discord.Status.dnd)

def setup(bot):
    bot.add_cog(Test(bot))