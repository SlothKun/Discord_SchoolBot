from discord.ext import commands
import discord
from pymongo import MongoClient
import datetime
import asyncio
import json
import aiohttp
import io
import urllib
import time
import aiofiles

class Test(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.db = MongoClient('localhost', 27017).SchoolBot

    def homework_date_sorting(self, hmw_list):
        current_date = datetime.datetime.utcnow()
        hmw_dict = {}
        for hmw in hmw_list:
            hmw_dict[hmw['deadline']-current_date] = hmw
        hmw_list = []
        hmw_dict = sorted(hmw_dict.items())
        for item, value in hmw_dict:
            hmw_list.append(value)
        return hmw_list


    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Un ping inutile into vexation into mise en 'ne pas deranger'")
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
                - add verif no bot answer
            '''
            if message_obj['command'] == "cours":
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
            #elif message_obj['command'] == "file_sending":
             #   print(reaction)
        except Exception as e:
            if str(e) == "no such item for Cursor instance":
                return
            else:
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



### RECEPTION

    @commands.Cog.listener('on_message')
    async def file_sending(self, message):
        if message.author == self.bot.user:
            return
        hmw_selection = ""
        hmw_list = []
        url_list = []
        filename_list = []
        file_list = []
        def check_reaction(reaction, user):
            if user == message.author and reaction.message.id == hmw_selection.id:
                return reaction, user
        try:
            start = time.time()
            channel_obj = self.db.send_recv_channels.find({'chan_send_id': message.channel.id})[0]
            async with message.channel.typing():
                prof = self.bot.get_user(int(channel_obj['teacher_id']))
                recv_chan = self.bot.get_channel(int(channel_obj['chan_recv_id']))
                send_chan = self.bot.get_channel(int(channel_obj['chan_send_id']))
                for i in range(0, len(message.attachments)):
                    url_list.append(message.attachments[i].url)
                    filename_list.append(message.attachments[i].filename)

                for i in range(0, len(message.attachments)):
                    #file_list.append(await message.attachments[i].read())
                    print("msg attach : ", message.attachments)
                    print("msg attach len : ", len(message.attachments))
                    async with aiohttp.ClientSession() as session:
                        if len(message.attachments) == 1:
                            async with session.get(url_list[0]) as resp:
                                await message.delete()
                                end = time.time()
                                print("first session : ", end - start)
                                file_list.append(await resp.read())
                                #f = await aiofiles.open(filename_list[0], mode='wb')
                                #await f.write(await resp.read())
                                #await f.close()
                        else:
                            async with session.get(url_list[i]) as resp:
                                print("iterator : ", i)
                                file_list.append(await resp.read())
                                #f = await aiofiles.open(filename_list[i], mode='wb')
                                #await f.close()
                try:
                    await message.delete()
                    end = time.time()
                    print(end - start)
                except Exception as e:
                    if str(e) == "404 Not Found (error code: 10008): Unknown Message":
                        pass
                try:
                    all_hmw = self.homework_date_sorting(self.db['devoir'].find({'subject': channel_obj['subject']}))
                except Exception as e:
                    if str(e) == "no such item for Cursor instance":
                        await message.channel.send("```Aucun devoir pour cette matière```")
                    return
                hmw_selection = f"<@{message.author.id}>\n```Veuillez selectionner le devoir correspondant :\n"
                iterator = 0
                for hmw in all_hmw:
                    hmw_list.append([hmw['subject'], hmw['name']])
                    hmw_selection += f"{self.db.emoji.find({'name': str(iterator)})[0]['value']} -> {hmw['subject']} : {hmw['name']}\n"
                    iterator += 1
                hmw_selection = await message.channel.send(hmw_selection + "```")
                for nb in range(0, iterator):
                    await hmw_selection.add_reaction(self.db.emoji.find({'name': str(nb)})[0]['value'])
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
            await hmw_selection.delete()
            reaction_nb = int(self.db.emoji.find({'value': str(reaction)})[0]['name'])
            async with message.channel.typing():
                student_hmw = {
                    'student_id': message.author.id,
                    'subject': hmw_list[reaction_nb][0],
                    'hmw_name': hmw_list[reaction_nb][1],
                    'sending_date': datetime.datetime.utcnow(),
                    'message': message.content,
                    'filename': filename_list,
                    'file': file_list
                }
                self.db.student_hmw.insert_one(student_hmw)
                f = await aiofiles.open("bbb.jpg", mode='wb')
                await f.write(file_list[0])
                await f.close()

                ### IMPORTANT : sur la ligne commentée suivante, on voit comment il faut envoyer le fichier !
                # await prof.send(content=f"{channel_obj['subject']} : {message.author.nick} : {message.content}", file=discord.File(fp=io.BytesIO(buffer), filename=filename))
                await recv_chan.send(content=f"{message.author.nick} : a envoyé un fichier")
                bot_msg = await send_chan.send(content=f"<@{message.author.id}>, le message a bien été reçu")
            await asyncio.sleep(30)
            await bot_msg.delete()
        except Exception as e:
            if str(e) == "no such item for Cursor instance":
                print(e)
                return
            elif str(e) == "asyncio.exceptions.TimeoutError":
                bot_msg = await message.channel.send(f"<@{message.author.id}> Pas de réponse, annulation de l'envoi...")
                await asyncio.sleep(15)
                await bot_msg.delete()

            else:
                print(e)
            """
            elif str(e) == "list index out of range":
                try:
                    async with message.channel.typing():
                        await message.delete()
                        try:
                            all_hmw = self.homework_date_sorting(self.db['devoir'].find({'subject': channel_obj['subject']}))
                        except Exception as e:
                            if str(e) == "no such item for Cursor instance":
                                await message.channel.send("```Aucun devoir pour cette matière```")
                            return
                        hmw_selection = "```Veuillez selectionner le devoir correspondant :\n"
                        iterator = 0
                        for hmw in all_hmw:
                            hmw_list.append([hmw['subject'], hmw['name']])
                            hmw_selection += f"{self.db.emoji.find({'name': str(iterator)})[0]['value']} -> {hmw['subject']} : {hmw['name']}\n"
                            iterator += 1
                        hmw_selection = await message.channel.send(hmw_selection + "```")
                        for nb in range(0, iterator):
                            await hmw_selection.add_reaction(self.db.emoji.find({'name': str(nb)})[0]['value'])
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
                    reaction_nb = int(self.db.emoji.find({'value': str(reaction)})[0]['name'])
                    async with message.channel.typing():
                        student_hmw = {
                            'student_id': message.author.id,
                            'subject': hmw_list[reaction_nb][0],
                            'hmw_name': hmw_list[reaction_nb][1],
                            'sending_date': datetime.datetime.utcnow(),
                            'message': message.content
                        }
                        self.db.student_hmw.insert_one(student_hmw)
                        await recv_chan.send(content=f"{message.author.nick} : a envoyé un message")
                        bot_msg = await send_chan.send(content=f"<@{message.author.id}>, le message a bien été reçu")
                    await asyncio.sleep(30)
                    await bot_msg.delete()
                except asyncio.TimeoutError:
                    bot_msg = await message.channel.send(f"<@{message.author.id}> Pas de réponse, annulation de l'envoi...")
                    await asyncio.sleep(15)
                    await bot_msg.delete()
                except Exception as e:
                    if str(e) == "no such item for Cursor instance":
                        print(e)
                        return
                    else:
                        print(e)
            """


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