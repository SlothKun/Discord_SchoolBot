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
import os
from pathlib import Path
import xlsxwriter
from difflib import get_close_matches
import excel2img


class Test(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.db = MongoClient('localhost', 27017).schoolbot
        self.hmw_selection = ""
        self.correction_selec = ""

    async def hmw_table_img_creation(self, subject):
        all_hmw = list(self.db.devoir.find({'subject':subject, 'deadline': {'$gte': datetime.datetime.now()}}))
        if len(all_hmw) == 0:
            return
        all_std = list(self.db.eleve.find())

        # Creation of the excel document
        workbook = xlsxwriter.Workbook(("Hmw_tables/" + (subject +" .xlsx")))
        worksheet = workbook.add_worksheet()

        # Formats
        hmw_format = workbook.add_format({"bg_color": "#70AD47", "align": "center", "border": 1})
        corrected_format = workbook.add_format({"bg_color": "#FF6347", "align": "right", "border": 1})
        sended_format = workbook.add_format({"bg_color": "#A9D08E", "align": "right", "border": 1})
        not_sended_format = workbook.add_format({"bg_color": "#a19e9e", "align": "right", "border": 1, "font_color": "#3e3e3e", "italic": "true"})
        std_header_format = workbook.add_format({"bg_color": "#5B9BD5", "align": "justify", "border": 1})
        std_format = workbook.add_format({"bg_color": "#9BC2E6", "align": "justify", "border": 1})

        # cells width
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:ZZ", 22)

        row = 0
        col = 0

        # Table creation
        for hmw in all_hmw:
            col+=1
            worksheet.write(row, col, hmw["name"], hmw_format)

        col = 0
        worksheet.write(row, 0, "Élèves", std_header_format)

        for std in all_std:
            col = 0
            row += 1
            worksheet.write(row, col, std['name'].title(), std_format)
            for hmw in all_hmw:
                col+=1
                if len(list(self.db.student_hmw.find({'student_id':std["student_id"], 'hmw_name': hmw['name']}))) == 0:
                    worksheet.write(row, col, "Non rendu", not_sended_format)
                elif len(list(self.db.student_hmw.find({'hmw_status':"Corrigé", 'student_id':std["student_id"], 'hmw_name': hmw['name']}))) > 0:
                    worksheet.write(row, col, "Corrigé", corrected_format)
                else:
                    # GERER LA DATE
                    worksheet.write(row, col, ("le 05/16 à 11h53"), sended_format)

        #for each_row in range(0, row):
        #    worksheet.set_row(each_row, 20)

        workbook.close()
        excel2img.export_img(("Config/Hmw_Tables/" + (subject +" .xlsx")), ("Config/Hmw_Tables/" + (subject + ".png")))

    async def msg_embed_creation(self, state, subject):
        try:
            img_chan = self.bot.get_channel(708658324614283365)
            subject_recv_chan = self.bot.get_channel(self.db.send_recv_channels.find({'subject': subject})[0]['chan_recv_id'])
            with open(f"Hmw_tables/{subject}.png", 'rb') as table_img:
                table_img_msg = await img_chan.send(file=discord.File(fp=table_img, filename=f'{subject}.png'))
            embed = discord.Embed()
            embed.set_image(url=table_img_msg.attachments[0].url)

            if state == "create":
                embed_msg = await subject_recv_chan.send(embed=embed)
                hmw_table = {
                    'subject': subject,
                    'recv_chan_id': self.db.send_recv_channels.find({'subject': subject})[0]['chan_recv_id'],
                    'img_gathering_id': 708658324614283365,
                    'embed_id': embed_msg.id
                }
                self.db.hmw_table.insert_one(hmw_table)
            elif state == 'update':
                embed_msg = await subject_recv_chan.fetch_message(self.db.hmw_table.find({'subject':subject})[0]['embed_id'])
                embed_msg = await embed_msg.edit(embed=embed)
        except Exception as e:
            print(e)
            pass

    async def hmw_msg_verifier(self, subject, *infos):
        start = time.time()
        if len(list(self.db.hmw_table.find({"subject":subject}))) != 0:
            ##if len(list(self.db.student_hmw.find({"student_id":list(infos)[0], "hmw_name":list(infos)[1]}))) == 1:
            await self.hmw_table_img_creation(subject)
            await self.msg_embed_creation('update', subject)
        else:
            await self.hmw_table_img_creation(subject)
            await self.msg_embed_creation('create', subject)

        print("got there : ", time.time() - start)

    @commands.command()
    async def force_table_verifier(self, ctx, subject):
        await self.hmw_msg_verifier(subject)

    @commands.command()
    async def ping(self, ctx):
        pong = await ctx.message.channel.send("Pong !")
        await asyncio.sleep(15)
        await pong.delete()

    @commands.command(aliases=['eleve','élève','élèves','éleve','éleves','elève','elèves'])
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

    @commands.has_any_role(696433108253409371, 696433108253409373)
    @commands.command(aliases=['cour','course','courses'])
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





    @commands.has_any_role(696433108253409371, 696433108253409373)
    @commands.command()
    async def sensicheck(self, ctx, name):
        if ctx.message.author == self.bot.user:
            return
        std_list = []
        all_std = self.db.eleve.find()
        print(all_std)
        for std in all_std:
            std_list.append(std['name'])
        print(std_list)
        if name.lower() not in std_list:
            for sensibility in range(40, 60, 5):
                sensibility = sensibility / 100
                possibility = get_close_matches(name.lower(), std_list, 3, sensibility)
                if len(possibility) > 0:
                    res = f"Sensibilité {sensibility} - Input: {name} - {len(possibility)} possibilités"
                    for poss in possibility:
                        res += f"\n\tVoulez-vous dire: {poss} ?"
                else:
                    res = f"Sensibilité {sensibility} - Input: {name}\n\tAucune matière ne correspond à cette entrée"
                await ctx.message.channel.send(res)
        else:
            await ctx.message.channel.send(f"Matière `{name}` existe en BDD")



    ## BLOQUER AUX CHANNELS RECEPTIONS
    @commands.has_any_role(696433108253409371, 696433108253409373)
    @commands.command(aliases=['corection','corrections','corections','corecttion','corecttions','corriger'])
    async def correction(self, ctx, *complement):
        def check_reaction(reaction, user):
            if user == ctx.message.author and reaction.message.id == self.correction_selec.id:
                print(user)
                print(reaction)
                print("-----------------")
                return reaction, user

        if len(complement) == 0:
            errormsg = await ctx.send("Veuillez recommencer en respectant le format suivant : '!correction nom_de_leleve' avec votre fichier attaché à votre message")
            await asyncio.sleep(15)
            await errormsg.delete()
        else:
            subject = self.db.professeur.find({'id': ctx.message.author.id})[0]['subject']
            url = ctx.message.attachments[0].url
            filename = ctx.message.attachments[0].filename
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    await ctx.message.delete()
                    file = await resp.read()
            try:
                name = list(complement)[0].lower()
                std_list = []
                all_std = self.db.eleve.find()
                for std in all_std:
                    std_list.append(std['name'])
                if name not in std_list:
                    sensibility = 0.5
                    possibility = get_close_matches(name.lower(), std_list, 3, sensibility)
                    if len(possibility) > 0:
                        self.correction_selec = f"L'élève: {name} n'existe pas. S'agit il de :"
                        for i in range(0, len(possibility)):
                        #for poss in possibility:
                            self.correction_selec += f"\n\t{self.db.emoji.find({'name':str(i+1)})[0]['value']}: {possibility[i]} ?"
                        self.correction_selec += f"\n\t{self.db.emoji.find({'name':'cross'})[0]['value']}: Aucun des {len(possibility)}"
                        self.correction_selec = await ctx.message.channel.send(self.correction_selec)
                        for i in range(0, len(possibility)):
                            await self.correction_selec.add_reaction(self.db.emoji.find({'name':str(i+1)})[0]['value'])
                        await self.correction_selec.add_reaction(self.db.emoji.find({'name':'cross'})[0]['value'])
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
                        await self.correction_selec.delete()
                        try:
                            if self.db.emoji.find({'value': str(reaction)})[0]["name"] == "cross":
                                self.correction_selec = await ctx.channel.send("Annulation de la commande..")
                                await asyncio.sleep(3)
                                await self.correction_selec.delete()
                                return
                            elif self.db.emoji.find({'value': str(reaction)})[0]["name"] in ["0","1","2","3","4","5","6","7","8","9"]:
                                student_obj = self.db.eleve.find({'name': possibility[int(self.db.emoji.find({'value': str(reaction)})[0]["name"])-1]})[0]
                                print(f"eleve choisi : {student_obj['name']}")
                            else:
                                self.correction_selec = await ctx.channel.send("La commande a été annulée")
                                await asyncio.sleep(10)
                                await self.correction_selec.delete()
                                return
                        except Exception as e:
                            print(e)
                            self.correction_selec = await ctx.channel.send("La commande a été annulée")
                            await asyncio.sleep(10)
                            await self.correction_selec.delete()
                            return
                    else:
                        self.correction_selec = await ctx.message.channel.send(f"Input: {name}\n\tAucun élève ne correspond à cette entrée")
                        await asyncio.sleep(15)
                        await self.correction_selec.delete()
                        return

                else:
                    print(f"{name} existe dans la BDD")
                    student_obj = self.db.eleve.find({'name': name})[0]

                student = self.bot.get_user(int(student_obj['student_id']))
                added_msg = ""
                # Demander devoir
                student_sended_hmw = self.db.student_hmw.find({"student_id":student.id, 'subject': self.db.send_recv_channels.find({'chan_recv_id': ctx.message.channel.id})[0]['subject'], 'hmw_status':'Rendu'})
                all_sended_hmw = []

                for hmw_sended in student_sended_hmw:
                    all_sended_hmw.append(hmw_sended)

                if len(all_sended_hmw) == 0:
                    self.correction_selec = await ctx.channel.send(f"""```
Vous n'avez plus aucun devoir à corriger pour cet élève, dois-je tout de même envoyer votre fichier ?
        - {self.db.emoji.find({'name': str(1)})[0]['value']} : Oui
        - {self.db.emoji.find({'name': str(2)})[0]['value']} : Non             
                    ```""")
                    await self.correction_selec.add_reaction(self.db.emoji.find({'name':str(1)})[0]['value'])
                    await self.correction_selec.add_reaction(self.db.emoji.find({'name':str(2)})[0]['value'])
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
                    await self.correction_selec.delete()
                    if self.db.emoji.find({'value': str(reaction)})[0]["name"] == "1":
                        async with ctx.message.channel.typing():
                            await student.send(content=f"{subject} : {ctx.message.author.nick} vous a envoyé cette correction : \n {added_msg}", file=discord.File(fp=io.BytesIO(file), filename=filename))
                            self.correction_selec = await ctx.send(content=f"<@{ctx.message.author.id}>, le message a bien été envoyé à {name}")
                            await asyncio.sleep(15)
                            await self.correction_selec.delete()
                    else:
                        self.correction_selec = await ctx.channel.send("La commande a été annulée")
                        await asyncio.sleep(10)
                        await self.correction_selec.delete()
                        return
                else:
                    which_hmw = "```A quel devoir appartient cette correction ?\n"
                    printed = []
                    newhmwlist = []
                    print(all_sended_hmw)
                    print(type(all_sended_hmw))
                    for nb in range(0, len(all_sended_hmw)):
                        if all_sended_hmw[nb]['hmw_name'] not in printed:
                            which_hmw += f"{self.db.emoji.find({'name': str(nb+1)})[0]['value']} : {all_sended_hmw[nb]['hmw_name']}\n"
                            printed.append(all_sended_hmw[nb]['hmw_name'])
                            newhmwlist.append(all_sended_hmw[nb])
                    self.correction_selec = await ctx.message.channel.send(which_hmw+'```')
                    print("printed : ", printed)
                    for nb in range(0, len(printed)):
                        await self.correction_selec.add_reaction(self.db.emoji.find({'name':str(nb+1)})[0]['value'])
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
                    await self.correction_selec.delete()
                    hmw = newhmwlist[int(self.db.emoji.find({'value':str(reaction)})[0]['name'])-1]

                    print(hmw['hmw_name'])
                    if len(complement) > 1:
                        for i in range(1, len(complement)):
                            added_msg += complement[i] + " "
                    async with ctx.message.channel.typing():
                        await student.send(content=f"{subject} : {ctx.message.author.nick} vous a envoyé la correction de {hmw['hmw_name']} : \n {added_msg}", file=discord.File(fp=io.BytesIO(file), filename=filename))
                        #self.db.student_hmw.find({'hmw_status'})
                        self.db.student_hmw.find_and_modify(query={"student_id":student.id, 'hmw_name': hmw['hmw_name']}, update={"$set": {'hmw_status': "Corrigé"}})
                        await self.hmw_msg_verifier(subject)
                        self.correction_selec = await ctx.send(content=f"<@{ctx.message.author.id}>, le message a bien été envoyé à {name}")
                    await asyncio.sleep(15)
                    await self.correction_selec.delete()
            except Exception as e:
                if str(e) == "list index out of range":
                    await ctx.channel.send("Veuillez recommencer en attachant un fichier à votre message.")
                elif str(e) == "no such item for Cursor instance":
                    errormsg = await ctx.channel.send("L'élève n'a pas été trouvé, assurez vous que vous avez bien respecté le nom de l'élève donné dans la liste des élèves accessible grâce à la commande !eleves")
                    await asyncio.sleep(15)
                    await errormsg.delete()
                    #await ctx.channel.send("deux eleves seulement : sloth, skido ;)")
                else:
                    print(e)

    @commands.has_any_role(696433108253409371, 696433108253409373)
    @commands.command(aliases=['sondages','sonddage','sonddages'])
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
                    errormsg = await ctx.send("Veuillez s'il vous plait entrer un nombre entre 2 et 10.")
                    await asyncio.sleep(15)
                    await errormsg.delete()



### RECEPTION

    @commands.Cog.listener('on_message')
    async def file_sending(self, message):
        if message.author == self.bot.user:
            return

        url_list = []
        filename_list = []
        file_list = []

        def check_reaction(reaction, user):
            if user == message.author and reaction.message.id == self.hmw_selection.id:
                return reaction, user

        async def homework_date_sorting(hmw_list):
            current_date = datetime.datetime.utcnow()
            hmw_dict = {}
            decrement = 1
            for hmw in hmw_list:
                if hmw['deadline'] - current_date in hmw_dict:
                    hmw_dict[hmw['deadline'] - current_date - datetime.timedelta(milliseconds=decrement)] = hmw
                    decrement += 1
                else:
                    hmw_dict[hmw['deadline'] - current_date] = hmw
            hmw_list = []
            hmw_dict = sorted(hmw_dict.items())
            for item, value in hmw_dict:
                hmw_list.append(value)
            return hmw_list

        async def homework_printing(page_nb, start, stop, all_hmw):
            async with message.channel.typing():
                self.hmw_selection = f"<@{message.author.id}>\n```Veuillez selectionner le devoir correspondant :\n\n"
                hmw_list = []
                printed_elements = 0
                index = 1
                for hmw in all_hmw[start:stop]:
                    hmw_list.append([hmw['subject'], hmw['name']])
                    self.hmw_selection += f"{self.db.emoji.find({'name': str(index)})[0]['value']} -> {hmw['subject']} : {hmw['name']}\n"
                    printed_elements += 1
                    index +=1
                if page_nb > 1:
                    self.hmw_selection += f"\n{self.db.emoji.find({'name': 'back'})[0]['value']} : Revenir à la page précédente"
                if printed_elements < len(all_hmw):
                    self.hmw_selection += f"\n{self.db.emoji.find({'name': 'forward'})[0]['value']} : Aller à la page suivante"
                self.hmw_selection = await message.channel.send(self.hmw_selection + "```")

                if page_nb > 1:
                    await self.hmw_selection.add_reaction(self.db.emoji.find({'name': 'back'})[0]['value'])
                for nb in range(1, printed_elements+1):
                    await self.hmw_selection.add_reaction(self.db.emoji.find({'name': str(nb)})[0]['value'])
                if printed_elements < len(all_hmw):
                    await self.hmw_selection.add_reaction(self.db.emoji.find({'name': 'forward'})[0]['value'])

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
                except asyncio.TimeoutError:
                    await self.hmw_selection.delete()
                    return

                reaction = self.db.emoji.find({'value': str(reaction)})[0]['name']
                await self.hmw_selection.delete()
                if reaction == self.db.emoji.find({'name': 'forward'})[0]['name']:
                    hmw_list, reaction = await homework_printing(page_nb+1, stop, stop+5, all_hmw)
                elif reaction == self.db.emoji.find({'name': 'back'})[0]['name']:
                    hmw_list, reaction = await homework_printing(page_nb-1, start-5, start, all_hmw)
                return hmw_list, int(reaction)


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
                all_hmw = await homework_date_sorting(self.db['devoir'].find({'subject': channel_obj['subject']}))
                if len(all_hmw) == 0:
                    return

                hmw_list, reaction_nb = await homework_printing(1, 0, 5, all_hmw)
            except Exception as e:
                if str(e) == "no such item for Cursor instance":
                    print(e)
                    errormsg = await message.channel.send("```Aucun devoir pour cette matière```")
                    await asyncio.sleep(15)
                    await errormsg.delete()
                    return
                else:
                    if str(e) == "cannot unpack non-iterable NoneType object":
                        bot_msg = await message.channel.send(f"<@{message.author.id}> Pas de réponse, annulation de l'envoi...")
                        await asyncio.sleep(15)
                        await bot_msg.delete()
                        return
                    print("Error homework finding/sorting : ", str(e))
                    return

            async with message.channel.typing():
                student_hmw = {
                    'name': str(message.author.nick),
                    'student_id': message.author.id,
                    'subject': hmw_list[int(reaction_nb)-1][0],
                    'hmw_name': hmw_list[int(reaction_nb)-1][1],
                    'hmw_status': "Rendu",
                    'sending_date': datetime.datetime.utcnow(),
                    'message': message.content,
                    'filename': filename_list,
                    'file': file_list
                }
                self.db.student_hmw.insert_one(student_hmw)
                ### IMPORTANT : sur la ligne commentée suivante, on voit comment il faut envoyer le fichier !
                ### METTRE EN PLACE ENVOI DE FICHIER
                # await prof.send(content=f"{channel_obj['subject']} : {message.author.nick} : {message.content}", file=discord.File(fp=io.BytesIO(buffer), filename=filename))
                confirmation = await recv_chan.send(content=f"{message.author.nick} : a envoyé un fichier")
                await self.hmw_msg_verifier(hmw_list[int(reaction_nb)-1][0], message.author.id, hmw_list[int(reaction_nb)-1][1])
                await confirmation.delete()
                bot_msg = await send_chan.send(content=f"<@{message.author.id}>, le message a bien été reçu")
            await asyncio.sleep(30)
            await bot_msg.delete()

        except Exception as e:
            if str(e) == "no such item for Cursor instance":
                return
            else:
                print(e)

    @commands.has_any_role(696433108253409371, 696433108253409373)
    @commands.Cog.listener('on_message')
    async def calme_toi(self, message):
        if message.author == self.bot.user:
            return
        if message.content == "Parle moi autrement":
            await message.channel.send("Pardon humain")
        elif message.content == "C'est bien p'tit bot":
            await message.channel.send("Merci humain <3")

def setup(bot):
    bot.add_cog(Test(bot))