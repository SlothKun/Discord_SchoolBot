import discord
from asyncio import sleep
from discord.ext import commands

class Gestion_des_membres(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    #commandes
    @commands.command(aliases=["membres"])
    @commands.has_permissions(administrator=True)
    async def members(self, ctx):
        texte="```   "
        i=0
        for member in ctx.guild.members:
            if not member.bot:
                if i%3!=0:
                    texte+="|   "
                else:
                    texte+="\n   "
                if member.nick!=None:
                    texte+=member.nick[:17].ljust(17)
                else:
                    texte+=member.name[:17].ljust(17)
                i+=1
        texte+="```"
        await ctx.send(texte)
    
    @commands.command(aliases=["membres_online","membres_enligne","membres_en_ligne"])
    @commands.has_permissions(administrator=True)
    async def members_online(self, ctx):
        texte="```   "
        i=0
        for member in ctx.guild.members:
            if str(member.status)=="online" and not member.bot:
                if i%3!=0:
                    texte+="|   "
                else:
                    texte+="\n   "
                texte+=member.display_name[:17].ljust(17)
                i+=1
        texte+="```"
        await ctx.send(texte)
        
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member : discord.Member):
        try:
            guild = ctx.guild
            
            for role in guild.roles:
                if role.name=="Muted":
                    await member.add_roles(role)
                    await ctx.send(f'{member.mention} is muted')
                    return
        except Exception as e:
            print(str(e))
            bot_msg = await ctx.send(content=f"une erreur s'est produite: {str(e)}") # on prévient de l'erreur
            await sleep(20) # on attend 20sec
            try:
                await bot_msg.delete() # on supprime le message d'erreur
            except:
                pass # si le message à déjà été supprimé ou autre, on laisse tomber
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member : discord.Member):
        try:
            guild = ctx.guild
            
            for role in guild.roles:
                if role.name=="Muted":
                    await member.remove_roles(role)
                    await ctx.send(f'{member.mention} is unmuted')
                    return
        except Exception as e:
            print(str(e))
            bot_msg = await ctx.send(content=f"une erreur s'est produite: {str(e)}") # on prévient de l'erreur
            await sleep(20) # on attend 20sec
            try:
                await bot_msg.delete() # on supprime le message d'erreur
            except:
                pass # si le message à déjà été supprimé ou autre, on laisse tomber
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        try:
            await member.kick(reason=reason)
        except Exception as e:
            print(str(e))
            bot_msg = await ctx.send(content=f"une erreur s'est produite: {str(e)}") # on prévient de l'erreur
            await sleep(20) # on attend 20sec
            try:
                await bot_msg.delete() # on supprime le message d'erreur
            except:
                pass # si le message à déjà été supprimé ou autre, on laisse tomber

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f'{member.mention} a été banni')
        except Exception as e:
            print(str(e))
            bot_msg = await ctx.send(content=f"une erreur s'est produite: {str(e)}") # on prévient de l'erreur
            await sleep(20) # on attend 20sec
            try:
                await bot_msg.delete() # on supprime le message d'erreur
            except:
                pass # si le message à déjà été supprimé ou autre, on laisse tomber
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, *, member):
        try:
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split("#")
            
            for ban_entry in banned_users:
                user = ban_entry.user
                
                if (user.name,user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    await ctx.send(f"{user.mention} a été débanni")
                    return
        except Exception as e:
            print(str(e),str(e)=="not enough values to unpack (expected 2, got 1)")
            if str(e)=="not enough values to unpack (expected 2, got 1)":
                bot_msg = await ctx.send(content="entrer le membre sous la forme NOM#ID") # on prévient s'il manque l'ID 
            else:
                bot_msg = await ctx.send(content=f"une erreur s'est produite: {str(e)}") # on prévient de l'erreur
            await sleep(20) # on attend 20sec
            try:
                await bot_msg.delete() # on supprime le message d'erreur
            except:
                pass # si le message à déjà été supprimé ou autre, on laisse tomber

def setup(client):
    client.add_cog(Gestion_des_membres(client))
