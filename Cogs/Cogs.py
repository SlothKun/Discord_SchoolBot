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

    @commands.command()
    async def eleves(self, ctx):
        await ctx.send("""```
+-----------------------------------------------------+
|                      Eleves TS1                     |
+----------+----------+----------+----------+---------+
|  Alexis  |  Amelie  |  Axelle  | Baptiste | Bastian |
+----------+----------+----------+----------+---------+
|  Camille |  Charlie |  Emeline |   Emile  |   Enzo  |
+----------+----------+----------+----------+---------+
|  Florian | Gregoire |   Hugo   |   Jason  |   Jean  |
+----------+----------+----------+----------+---------+
|   Juan   |   Louis  |    Lea   |    Leo   |  Manon  |
+----------+----------+----------+----------+---------+
| MargauxL | MargauxQ |   Marie  |   Mateo  |   Max   |
+----------+----------+----------+----------+---------+
|  Maxence |   Mael   |  Pierre  |  Romain  |  Sarah  |
+----------+----------+----------+----------+---------+
|   TheoG  |   TheoB  |  Thibaut |  Vivien  |         |
+----------+----------+----------+----------+---------+

+----------+----------+----------+----------+---------+
|              Eleves hors TS1 (Spe ISN)              |
+----------+----------+----------+----------+---------+
|          |   Ambre  | MargauxO |   Mona   |         |
+----------+----------+----------+----------+---------+
            ```""")

    @commands.Cog.listener('on_message')
    async def Give_proposition(self, message):
        return message

    @commands.command()
    async def sondage(self, ctx, *kwargs):
        msglist = []
        number_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        if len(kwargs) == 0:
            await ctx.send("Veuillez s'il vous plait préciser le nombre de proposition.")
        else:
            try:
                nb_proposition = int(list(kwargs)[0])
                if nb_proposition > 9 or nb_proposition < 2:
                    raise ValueError("invalid literal for int() with base 10:")
                else:
                    msglist.append(ctx.message)
                    bot_msg = await ctx.message.channel.send("Veuillez écrire la description de votre sondage : ")
                    msglist.append(bot_msg)
                    user_msg = await self.bot.wait_for('message', timeout=60)
                    while str(user_msg.author) != str(ctx.author) or str(user_msg.channel) != str(ctx.channel):
                        user_msg = await self.bot.wait_for('message', timeout=60)
                    complete_string = f"<@&696433108244889722> - Sondage proposé par {ctx.author.nick} :```\n{user_msg.content} \n"
                    msglist.append(user_msg)
                    for i in range(0, nb_proposition):
                        bot_msg = await ctx.message.channel.send(f"Veuillez écrire la proposition n°{i+1} : ")
                        user_msg = await self.bot.wait_for('message', timeout=60)
                        while str(user_msg.author) != str(ctx.author) or str(user_msg.channel) != str(ctx.channel):
                            user_msg = await self.bot.wait_for('message', timeout=60)
                        msglist.append(user_msg)
                        msglist.append(bot_msg)
                        complete_string += (f"\t{number_list[i]} :  {user_msg.content} \n")
                    bot_msg = await ctx.channel.send(complete_string+"```")
                    for i in range(0, nb_proposition):
                        await bot_msg.add_reaction(number_list[i])
                    for i in range(0, len(msglist)):
                        await msglist[i].delete()

            except Exception as e:
                print(e)
                print(type(e))
                if str(e).startswith("invalid literal for int() with base 10:"):
                    await ctx.send("Veuillez s'il vous plait entrer un nombre entre 2 et 9.")
                    return

    @commands.Cog.listener('on_message')
    async def calme_toi(self, message):
        if message.author == self.bot.user:
            return
        if message.content == "Parle moi autrement":
            await message.channel.send("Pardon humain")
        elif message.content == "C'est bien bot":
            await message.channel.send("Merci humain <3")
def setup(bot):
    bot.add_cog(Test(bot))