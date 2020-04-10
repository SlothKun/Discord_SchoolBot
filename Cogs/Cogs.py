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

    def check(self, ctx, user):
        return user == ctx.message.author

    @commands.Cog.listener('on_message')
    async def Give_proposition(self, message):
        return message

    @commands.command()
    async def sondage(self, ctx, *kwargs):
        print(kwargs)
        print(type(kwargs))
        print(len(kwargs))
        if len(kwargs) == 0:
            await ctx.send("Veuillez s'il vous plait préciser le nombre de proposition.")
        else:
            await ctx.message.delete()
            try:
                nb_proposition = int(list(*kwargs)[0])
            except Exception as e:
                print(e)
                if str(e).startswith("invalid literal for int() with base 10:"):
                    await ctx.send("Veuillez s'il vous plait entrer un nombre entre 2 et 9.")
                    return
            #print(nb_proposition)
            all_msg = []
            user_sended = ctx.message.author
            bot_msg = await ctx.message.channel.send("Veuillez écrire la description de votre sondage :")
            all_msg.append(bot_msg)
            channel_validator = False
            number_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
            while channel_validator == False:
                description = await Give_proposition()
                if description.channel == ctx.message.channel:
                    print(description.channel)
                    all_msg.append(description)
                    channel_validator = True
            complete_string = f"<@&689285153562165374> Sondage proposé par {ctx.message.author.nick} :\n" + description.content + "\n"
            for i in range(0, nb_proposition):
                proposition_validator = False
                if ctx.message.author == user_sended:
                    bot_answer = await ctx.message.channel.send(f"Veuillez écrire la proposition n°{i + 1} :")
                    while proposition_validator == False:
                        proposition = await Give_proposition()
                        if proposition.channel == ctx.message.channel:
                            proposition_validator = True
                            all_msg.append(proposition)
                            all_msg.append(bot_answer)
                    complete_string += (number_list[i] + " : " + proposition.content + "\n")
                    print(complete_string)
            bot_msg = await ctx.message.channel.send(content=complete_string)
            for i in range(0, nb_proposition):
                await bot_msg.add_reaction(number_list[i])
            bot_answer = await ctx.message.channel.send(f"<@{ctx.message.author.id}>, le message a bien été envoyé")
            for i in range(0, len(all_msg)):
                await all_msg[i].delete()
            await asyncio.sleep(30)
            await bot_answer.delete()



    @commands.Cog.listener('on_message')
    async def calme_toi(self, message):
        if message.author == self.bot.user:
            return
        if message.content == "Parle moi autrement":
            await message.channel.send("Pardon maitre")
def setup(bot):
    bot.add_cog(Test(bot))