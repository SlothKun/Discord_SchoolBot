from discord.ext import commands
import discord
from pymongo import MongoClient
import datetime
import asyncio
import json

class Test(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.db = MongoClient('localhost', 27017).SchoolBot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Un ping inutile into vexation et mise en 'ne pas deranger'")
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

    @commands.Cog.listener('on_reaction_add')
    async def reactionListener(self, reaction, user):
        if user == self.bot.user:
            return
        try:
            reactionDate = datetime.datetime.utcnow()
            message_obj = self.db.appending_msg.find({'msg_id': reaction.message.id, 'creator_id': user.id})[0]
            ## TO-DO : supprimer message après reaction
            '''
            TO-DO : 
                - Verification des formats (jj/mm, hh:mm)
                - temps limite de reaction
                - ajouter cours dans la bdd
                - afficher le prochain cours dans un channel
                - faire l'edition / suppression / affichage cours
            '''
            if str(reaction) == self.db.emoji.find({'name':'0'})[0]['value']:
                all_msg = []
                bot_msg = await reaction.message.channel.send("Veuillez préciser la matière : ")
                all_msg.append(bot_msg)
                matiere = await self.bot.wait_for('message', timeout=60)
                all_msg.append(matiere)
                print(matiere)
                bot_msg = await reaction.message.channel.send("Veuillez préciser la date du cours en suivant le format jj/mm : ")
                all_msg.append(bot_msg)
                date = await self.bot.wait_for('message', timeout=60)
                all_msg.append(date)
                bot_msg = await reaction.message.channel.send("Veuillez préciser l'heure du cours en suivant le format hh:mm : ")
                all_msg.append(bot_msg)
                heure = await self.bot.wait_for('message', timeout=60)
                all_msg.append(heure)
                print(matiere.content, date.content, heure.content)

        except Exception as e:
            print(e)
            return


    @commands.command()
    async def cours(self, ctx):
        await ctx.message.delete()
        ### TO-DO : améliorer aspect graphique
        bot_msg = await ctx.send(f"""```
                                                Liste des commandes disponibles :
            
    {self.db.emoji.find({'name': "0"})[0]['value']} : Ajouter un cours
    {self.db.emoji.find({'name': "1"})[0]['value']} : Editer un cours
    {self.db.emoji.find({'name': "2"})[0]['value']} : Supprimer un cours
    {self.db.emoji.find({'name': "3"})[0]['value']} : Voir la liste des cours
        ```""")
        for i in range(0, 4):
            await bot_msg.add_reaction(self.db.emoji.find({'name': str(i)})[0]['value'])

        msg = {
            'command':'cours',
            'msg_id': bot_msg.id,
            'creator_id': ctx.message.author.id,
            'channel_id': ctx.message.channel.id,
            'creation_date': datetime.datetime.utcnow()
        }
        self.db.appending_msg.insert_one(msg)


    @commands.command()
    async def correction(self, ctx, *complement):
        if len(complement) == 0:
            await ctx.send("Veuillez recommencer en respectant le format suivant : '!correction nom_de_leleve' avec votre fichier attaché à votre message")
        else:
            try:
                name = list(complement)[0].lower()
                student_obj = self.db.eleve.find({'name': name})[0]
                file = await ctx.message.attachments[0].to_file()
                await ctx.message.delete()
                ### TO-DO : retirer le int et met le nombre directement dans la bdd au lieu d'une str
                ### TO-DO : ajouter le writing mode
                student = self.bot.get_user(int(student_obj['student_id']))
                added_msg = ""
                if len(complement) > 1:
                    for i in range(1, len(complement)):
                        added_msg += complement[i] + " "
                await student.send(content=f"{ctx.message.author.nick} vous a envoyé cette correction : \n {added_msg}", file=file)
                bot_msg = await ctx.send(content=f"<@{ctx.message.author.id}>, le message a bien été envoyé à {name}")
                await asyncio.sleep(30)
                await bot_msg.delete()
            except Exception as e:
                if str(e) == "list index out of range":
                    await ctx.channel.send("Veuillez recommencer en attachant un fichier à votre message.")
                elif str(e) == "no such item for Cursor instance":
                    await ctx.channel.send("L'élève n'a pas été trouvé, assurez vous que vous avez bien respecté le nom de l'élève donné dans la liste des élèves accessible grâce à la commande !eleves")
                    await ctx.channel.send("deux eleves seulement : sloth, skido ;)")
                else:
                    print(e)


    @commands.command()
    async def sondage(self, ctx, *kwargs):
        msglist = []
        poll_info = {}
        all_propositions = []
        if len(kwargs) == 0:
            await ctx.send("Veuillez s'il vous plait préciser le nombre de proposition.")
        else:
            try:
                nb_proposition = int(list(kwargs)[0])
                if nb_proposition > 10 or nb_proposition < 2:
                    raise ValueError("invalid literal for int() with base 10:")
                else:
                    msglist.append(ctx.message)
                    bot_msg = await ctx.message.channel.send("Veuillez écrire la description de votre sondage : ")
                    msglist.append(bot_msg)
                    user_msg = await self.bot.wait_for('message', timeout=60)
                    while str(user_msg.author) != str(ctx.author) or str(user_msg.channel) != str(ctx.channel):
                        user_msg = await self.bot.wait_for('message', timeout=60)
                    complete_string = f"<@&696433108244889722> - Sondage proposé par {ctx.author.nick} :```\n{user_msg.content} \n"
                    poll_info['description'] = user_msg.content
                    msglist.append(user_msg)
                    for i in range(0, nb_proposition):
                        bot_msg = await ctx.message.channel.send(f"Veuillez écrire la proposition n°{i+1} : ")
                        user_msg = await self.bot.wait_for('message', timeout=60)
                        while str(user_msg.author) != str(ctx.author) or str(user_msg.channel) != str(ctx.channel):
                            user_msg = await self.bot.wait_for('message', timeout=60)
                        all_propositions.append(user_msg.content)
                        msglist.append(user_msg)
                        msglist.append(bot_msg)
                        complete_string += (f"\t{self.db.emoji.find({'name':str(i)})[0]['value']} :  {user_msg.content} \n")
                    bot_msg = await ctx.channel.send(complete_string+"```")
                    poll_info['nb_propositions'] = len(all_propositions)
                    poll_info['propositions'] = all_propositions
                    poll_info['published_time'] = datetime.datetime.utcnow()
                    poll_info['deadline'] = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                    self.db.sondage.insert_one(poll_info)
                    for i in range(0, nb_proposition):
                        await bot_msg.add_reaction(self.db.emoji.find({'name':str(i)})[0]['value'])
                    for i in range(0, len(msglist)):
                        await msglist[i].delete()
            except Exception as e:
                print(e)
                print(type(e))
                if str(e).startswith("invalid literal for int() with base 10:"):
                    await ctx.send("Veuillez s'il vous plait entrer un nombre entre 2 et 10.")
                    return

    @commands.Cog.listener('on_message')
    async def file_sending(self, message):
        if message.author == self.bot.user:
            return
        try:
            channel_obj = self.db.send_recv_channels.find({'chan_send_id': str(message.channel.id)})[0]
            ### TO-DO : retirer le int et met le nombre directement dans la bdd au lieu d'une str
            ### TO-DO : ajouter le writing mode
            prof = self.bot.get_user(int(channel_obj['teacher_id']))
            recv_chan = self.bot.get_channel(int(channel_obj['chan_recv_id']))
            send_chan = self.bot.get_channel(int(channel_obj['chan_send_id']))
            file = await message.attachments[0].to_file()
            await message.delete()
            print("message :", message.content)
            await prof.send(content=f"{channel_obj['subject']} : {message.author.nick} : {message.content}", file=file)
            await recv_chan.send(content=f"{message.author.nick} : a envoyé un fichier")
            bot_msg = await send_chan.send(content=f"<@{message.author.id}>, le message a bien été envoyé")
            await asyncio.sleep(30)
            await bot_msg.delete()
        except Exception as e:
            if str(e) == "no such item for Cursor instance":
                return
            elif str(e) == "list index out of range":
                await message.delete()
                await prof.send(content=f"{channel_obj['subject']} : {message.author.nick} : {message.content}")
                await recv_chan.send(content=f"{message.author.nick} : a envoyé un message")
                bot_msg = await send_chan.send(content=f"<@{message.author.id}>, le message a bien été envoyé")
                await asyncio.sleep(30)
                await bot_msg.delete()
            else:
                print(e)

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