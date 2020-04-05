import discord
from discord.ext import commands

class Gestion_des_messages(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    #events
        
    #commandes        
    @commands.command(aliases=["efface","supprime"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount+1) #efface aussi le message contenant la commande
        
    
def setup(client):
    client.add_cog(Gestion_des_messages(client))

