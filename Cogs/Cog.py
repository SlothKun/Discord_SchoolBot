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
import locale


# Set time in fr
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

class Cog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.db = MongoClient('localhost', 27017).schoolbot
        self.hmw_selection = ""
        self.correction_selec = ""

    async def hmw_table_img_creation(self, subject):
        utcDate = datetime.datetime.utcnow()
        thisDay = datetime.datetime(utcDate.year, utcDate.month, utcDate.day)
        #await self.hmw_sorting(list(self.db.homework.find({'subject': subject, 'deadline': {'$gte': thisDay}}).sort("deadline")))
        all_hmw = list(self.db.homework.find({'subject':subject, 'deadline': {'$gte': thisDay}}).sort("deadline"))
        #all_hmw = await self.homework_date_sorting(all_hmw)
        if self.db.homework.count_documents({'subject':subject, 'deadline': {'$gte': thisDay}}) == 0:
            return
        all_std = list(self.db.students.find())

        # Creation of the excel document
        workbook = xlsxwriter.Workbook(("Config/Hmw_tables/" + (subject +".xlsx")))
        worksheet = workbook.add_worksheet()

        # Formats
        hmw_format = workbook.add_format({"bg_color": "#70AD47", "align": "center", "border": 1})

        not_sended_format = workbook.add_format({"bg_color": "#a19e9e", "align": "right", "border": 1, "font_color": "#3e3e3e", "italic": "true"})
        sended_format = workbook.add_format({"bg_color": "#FFDFB3", "align": "right", "border": 1})
        received_format = workbook.add_format({"bg_color": "#EBBD86", "align": "right", "border": 1})
        corrected_format = workbook.add_format({"bg_color": "#E8AE55", "align": "right", "border": 1})

        std_header_format = workbook.add_format({"bg_color": "#5B9BD5", "align": "justify", "border": 1})
        std_format = workbook.add_format({"bg_color": "#A9D1FF", "align": "justify", "border": 1})

        # cells width
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:ZZ", 22)

        row = 0
        col = 0

        # Table creation
        for hmw in all_hmw:
            col+=1
            worksheet.write(row, col, hmw["name"].title(), hmw_format)

        col = 0
        worksheet.write(row, 0, "Élèves", std_header_format)

        for std in all_std:
            col = 0
            row += 1
            worksheet.write(row, col, std['name'].title(), std_format)
            for hmw in all_hmw:
                col+=1
                if len(list(self.db.student_hmw.find({'student_id':std["student_id"], 'hmw_name': hmw['name'], 'sending_date': {'$gte': hmw['publish_date']}}))) == 0:
                    worksheet.write(row, col, "Non rendu", not_sended_format)
                elif len(list(self.db.student_hmw.find({'hmw_status':"Envoyé", 'student_id':std["student_id"], 'hmw_name': hmw['name'], 'sending_date': {'$gte': hmw['publish_date']}}))) > 0:
                    deadline = str(self.db.student_hmw.find({'hmw_name': hmw['name'], 'student_id':std["student_id"], 'sending_date': {'$gte': hmw['publish_date']}})[0]['sending_date'])
                    date = deadline.split()[0]
                    formatted_date = f"{date[len(date) -2:]}/{date[-5:-3]}"
                    hour = deadline.split()[1].split(".")[0][:-3]
                    worksheet.write(row, col, (f"le {formatted_date} à {hour}"), sended_format)
                elif len(list(self.db.student_hmw.find({'hmw_status':"Reçu", 'student_id':std["student_id"], 'hmw_name': hmw['name'], 'sending_date': {'$gte': hmw['publish_date']}}))) > 0:
                    worksheet.write(row, col, "Reçu", received_format)
                elif len(list(self.db.student_hmw.find({'hmw_status':"Corrigé", 'student_id':std["student_id"], 'hmw_name': hmw['name'], 'sending_date': {'$gte': hmw['publish_date']}}))) > 0:
                    worksheet.write(row, col, "Corrigé", corrected_format)

        #for each_row in range(0, row):
        #    worksheet.set_row(each_row, 20)

        workbook.close()
        excel2img.export_img(("Config/Hmw_Tables/" + (subject +".xlsx")), ("Config/Hmw_Tables/" + (subject + ".png")))
        return all_hmw

    async def msg_embed_creation(self, state, subject, hmw_list):
        try:
            img_chan = self.bot.get_channel(714242942226661428)
            subject_recv_chan = self.bot.get_channel(int(self.db.send_recv_channels.find({'subject': subject})[0]['chan_recv_id']))
            with open(f"Config/Hmw_tables/{subject}.png", 'rb') as table_img:
                table_img_msg = await img_chan.send(file=discord.File(fp=table_img, filename=f'{subject}.png'))
            embed = discord.Embed()
            embed.set_image(url=table_img_msg.attachments[0].url)
            hmw_name_list = []
            for hmw in hmw_list:
                hmw_name_list.append(hmw['name'])
            if state == "create":
                embed_msg = await subject_recv_chan.send(embed=embed)
                hmw_table = {
                    'subject': subject,
                    'recv_chan_id': self.db.send_recv_channels.find({'subject': subject})[0]['chan_recv_id'],
                    'img_gathering_id': '714242942226661428',
                    'embed_id': str(embed_msg.id),
                    'subject_hmw_list': hmw_name_list
                }
                self.db.hmw_table.insert_one(hmw_table)
            elif state == 'update':
                embed_msg = await subject_recv_chan.fetch_message(self.db.hmw_table.find({'subject':subject})[0]['embed_id'])
                print(embed_msg)
                self.db.hmw_table.find_and_modify(query={'subject':subject}, update={'$set': {'subject_hmw_list': hmw_name_list}})
                embed_msg = await embed_msg.edit(embed=embed)

            embed_msg = await subject_recv_chan.fetch_message(self.db.hmw_table.find({'subject':subject})[0]['embed_id'])
            await embed_msg.clear_reactions()
            for nb in range(0, len(hmw_name_list)):
                await embed_msg.add_reaction(self.db.emoji.find({'name':str(nb+1)})[0]['value'])
        except Exception as e:
            print(e)
            pass

    async def hmw_msg_verifier(self, subject, *infos):
        start = time.time()
        if self.db.hmw_table.count_documents({"subject":subject}) != 0:
            ##if len(list(self.db.student_hmw.find({"student_id":list(infos)[0], "hmw_name":list(infos)[1]}))) == 1:
            all_hmw = await self.hmw_table_img_creation(subject)
            await self.msg_embed_creation('update', subject, all_hmw)
        else:
            print("creation")
            all_hmw = await self.hmw_table_img_creation(subject)
            await self.msg_embed_creation('create', subject, all_hmw)

        print("got there : ", time.time() - start)



    @commands.Cog.listener('on_raw_reaction_add')
    async def HmwSending_ReactionListener(self, reaction):
        # print(reaction)
        # print(type(reaction))
        # print(reaction.user_id)
        # if user == self.bot.user:
        #    return
        try:
            reactionDate = datetime.datetime.now()
            # message_obj = self.db.appending_msg.find({'msg_id': reaction.message_id, 'creator_id': reaction.user_id})[0]
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

            if len(list(self.db.hmw_table.find({'recv_chan_id': str(reaction.channel_id)}))) == 1 and len(list(self.db.hmw_table.find({'embed_id': str(reaction.message_id)}))) == 1:
                recv_channel = self.bot.get_channel(reaction.channel_id)
                embeded_msg = await recv_channel.fetch_message(reaction.message_id)
                hmw_name_list = self.db.hmw_table.find({'recv_chan_id': str(reaction.channel_id)})[0]['subject_hmw_list']
                is_reaction_good = False
                for emoji_in_embed in embeded_msg.reactions:
                    if len(list(self.db.teachers.find({'id': str(reaction.user_id)}))) >= 1 and emoji_in_embed.count >= 2:
                        is_reaction_good = True
                        print(emoji_in_embed)

                if is_reaction_good == True:
                    # print(len(hmw_name_list))
                    if int(self.db.emoji.find({'value': reaction.emoji.name})[0]["name"]) <= len(hmw_name_list):
                        hmw_chosen = hmw_name_list[int(self.db.emoji.find({'value': reaction.emoji.name})[0]["name"]) - 1]
                        all_std_hmw = []
                        teacher = self.bot.get_user(reaction.user_id)
                        print("hmw name : ", hmw_chosen)
                        subject = self.db.send_recv_channels.find({'chan_recv_id': str(reaction.channel_id)})[0]['subject']
                        utcDate = datetime.datetime.utcnow()
                        thisDay = datetime.datetime(utcDate.year, utcDate.month, utcDate.day)
                        hmw = self.db.homework.find({'subject': subject, 'name': hmw_chosen, 'deadline':{'$gte':thisDay}})[0]
                        #print("counted : ", self.db.student_hmw.count_documents({'subject': subject, 'hmw_name': hmw_chosen, 'sending_date': {'$gte':dvr[1]['publish_date']}}))
                        #print("hwm : ", self.db.student_hmw.find({'subject': subject, 'hmw_name': hmw_chosen, 'sending_date': {'$gte':dvr[0]['publish_date']}})[0])
                        hmw_line = f"+         Devoir : {hmw_chosen.title()} "
                        while len(hmw_line) != 61:
                            if len(hmw_line) < 60:
                                hmw_line += " "
                            elif len(hmw_line) == 60:
                                hmw_line += "+"
                        subject_line = f"+         Matière : {subject.title()} "
                        while len(subject_line) != 61:
                            if len(subject_line) < 60:
                                subject_line += " "
                            elif len(subject_line) == 60:
                                subject_line += "+"

                        await teacher.send("-------------------------------------------------------------------------------------")
                        await teacher.send(f"""```diff
+---------------------------------------+
-         Début de la reception         -
{hmw_line}
{subject_line}
+---------------------------------------+```""")
                        for std_hmw in self.db.student_hmw.find({'subject': subject, 'hmw_name': hmw_chosen, 'sending_date':{'$gte': hmw['publish_date']}}):
                            if 'Envoyé' in std_hmw['hmw_status']:
                                await teacher.send(f"""```ini
            [ Élève : {std_hmw['name']} ]```""")
                                message = ""
                                for nb in range(0, len(std_hmw['message'])):
                                    if std_hmw['message'][nb] != "" and std_hmw['hmw_status'][nb] == "Envoyé":
                                        message += std_hmw['message'][nb] + "\n"

                                all_file = []
                                file_number = 0
                                general_number = 0
                                status_list = []
                                for file in std_hmw['file']:
                                    if std_hmw['hmw_status'][general_number] == "Envoyé":
                                        status_list.append('Reçu')
                                        if file != '':
                                            index = std_hmw['file'].index(file)
                                            extension = std_hmw['filename'][index].split('.')[1]
                                            filename = f"{std_hmw['name'].title()}_{std_hmw['hmw_name'].title()}_Part{file_number}.{extension}"
                                            all_file.append(discord.File(fp=io.BytesIO(file), filename=filename))
                                            file_number += 1
                                    elif std_hmw['hmw_status'][general_number] == "Reçu":
                                        status_list.append('Reçu')
                                    elif std_hmw['hmw_status'][general_number] == "Corrigé":
                                        status_list.append('Corrigé')
                                    general_number += 1

                                await teacher.send(content=f"***__Message__ :*** {message}", files=all_file)
                                self.db.student_hmw.find_and_modify(
                                    query={'subject': subject,
                                           'name': std_hmw['name'],
                                           'hmw_name': hmw_chosen,
                                           'sending_date': {'$gte': hmw['publish_date']}
                                           },
                                    update={'$set':
                                                {'hmw_status': status_list}
                                            }
                                )
                        await teacher.send(f"""```diff
+---------------------------------------+
-         Fin de la reception           -
+---------------------------------------+```""")
                        await self.hmw_msg_verifier(subject)

                if reaction.user_id != self.bot.user.id:
                    await embeded_msg.remove_reaction(reaction.emoji, self.bot.get_user(reaction.user_id))

            if 1 == 2:
                if str(reaction) == self.db.emoji.find({'name': '0'})[0]['value']:
                    all_msg = []
                    bot_msg = await reaction.message.channel.send("Veuillez préciser la matière : ")
                    all_msg.append(bot_msg)
                    matiere = await self.bot.wait_for('message', timeout=60)
                    all_msg.append(matiere)
                    print(matiere)
                    bot_msg = await reaction.message.channel.send(
                        "Veuillez préciser la date du cours en suivant le format jj/mm : ")
                    all_msg.append(bot_msg)
                    date = await self.bot.wait_for('message', timeout=60)
                    all_msg.append(date)
                    bot_msg = await reaction.message.channel.send(
                        "Veuillez préciser l'heure du cours en suivant le format hh:mm : ")
                    all_msg.append(bot_msg)
                    heure = await self.bot.wait_for('message', timeout=60)
                    all_msg.append(heure)
                    print(matiere.content, date.content, heure.content)
            # elif message_obj['command'] == "file_sending":
            #   print(reaction)
        except Exception as e:
            if str(e) == "no such item for Cursor instance":
                print(e)
                return
            else:
                print(e)
                return

    @commands.command()
    async def hmwinrange(self, ctx, subject):
        utcDate = datetime.datetime.utcnow()
        thisDay = datetime.datetime(utcDate.year, utcDate.month, utcDate.day)
        print(thisDay)
        hmws = self.db.homework.find({'subject':subject, 'deadline': {'$gte':thisDay}}).sort('deadline')
        nbRes = self.db.homework.count_documents({'subject':subject, 'deadline': {'$gte':thisDay}})
        for hmw in hmws:
            print("------")
            print(hmw['name'])
            print(hmw['status'])
            print(hmw['deadline'])
        print(nbRes)

    @commands.command()
    async def force_table_verifier(self, ctx, subject):
        await ctx.message.delete()
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
|                      Eleves                         |
+----------+----------+----------+----------+---------+
|  Eleve  |  Eleve  |  Eleve  | Eleve | Eleve |
+----------+----------+----------+----------+---------+
|  Eleve |  Eleve |  Eleve |   Eleve  |   Eleve  |
+----------+----------+----------+----------+---------+
|  Eleve | Eleve |   Eleve   |   Eleve  |   Eleve  |
+----------+----------+----------+----------+---------+
|   Eleve   |   Eleve  |    Eleve   |    Eleve   |  Eleve  |
+----------+----------+----------+----------+---------+
| Eleve | Eleve |   Eleve  |   Eleve  |   Eleve   |
+----------+----------+----------+----------+---------+
|  Eleve |   Eleve   |  Eleve  |  Eleve  |  Eleve  |
+----------+----------+----------+----------+---------+
|   Eleve  |   Eleve  |  Eleve |  Eleve  |         |
+----------+----------+----------+----------+---------+

+----------+----------+----------+----------+---------+
|              Eleves                                 |
+----------+----------+----------+----------+---------+
| Eleve    |  Eleve   |    Eleve |  Eleve   |         |
+----------+----------+----------+----------+---------+```""")



    @commands.has_any_role(696433108253409371, 696433108253409373)
    @commands.command(aliases=['cour','course','courses'],enabled=False)
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
            'creation_date': datetime.datetime.now()
        }
        self.db.appending_msg.insert_one(msg)



    @commands.has_any_role(696433108253409371, 696433108253409373, 689074976023773224, 689075325124083746)
    @commands.command()
    async def sensicheck(self, ctx, name):
        if ctx.message.author == self.bot.user:
            return
        std_list = []
        all_std = self.db.students.find()
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



    @commands.has_any_role(696433108253409371, 696433108253409373, 689074976023773224, 689075325124083746)
    @commands.command(aliases=['corection','corrections','correctif','corections','corecttion','corecttions','corriger'])
    async def correction(self, ctx, *complement):
        async def CorrectionPrinting(added_msg, sended_hmw, hmw, subject):
            if len(complement) > 1:
                for i in range(1, len(complement)):
                    added_msg += complement[i] + " "
            async with ctx.message.channel.typing():
                if sended_hmw == "":
                    hmw_line = ""
                else:
                    hmw_line = f"+         Devoir : {sended_hmw['hmw_name'].title()} "
                    while len(hmw_line) != 41:
                        if len(hmw_line) < 40:
                            hmw_line += " "
                        elif len(hmw_line) == 40:
                            hmw_line += "+"

                subject_line = f"+         Matière : {subject.title()} "
                while len(subject_line) != 41:
                    if len(subject_line) < 40:
                        subject_line += " "
                    elif len(subject_line) == 40:
                        subject_line += "+"
                teacher = f"+         Professeur : {self.db.teachers.find({'id': str(ctx.message.author.id)})[0]['name'].title()} "
                while len(teacher) != 41:
                    if len(teacher) < 40:
                        teacher += " "
                    elif len(teacher) == 40:
                        teacher += "+"
                await student.send(
                    "---------------------------------------------------------------")
                if hmw == "":
                    await student.send(f"""```diff
+---------------------------------------+
-         Début de la reception         -
{subject_line}
{teacher}
+---------------------------------------+```""")
                else:
                    await student.send(f"""```diff
+---------------------------------------+
-         Début de la reception         -
{hmw_line}
{subject_line}
{teacher}
+---------------------------------------+```""")
                await student.send(content=f"***__Message__ :*** {added_msg}", file=discord.File(fp=io.BytesIO(file), filename=filename))
                await student.send(f"""```diff
+---------------------------------------+
-         Fin de la reception           -
+---------------------------------------+```""")
                if sended_hmw != "":
                    status_list = []
                    print("all status : ", sended_hmw['hmw_status'])
                    for status in sended_hmw['hmw_status']:
                        print(status)
                        if status == "Reçu":
                            status_list.append("Corrigé")
                        elif status == "Corrigé":
                            status_list.append("Corrigé")
                        elif status == "Envoyé":
                            status_list.append("Envoyé")

                    print("status list : ", status_list)
                    self.db.student_hmw.find_and_modify(query={"student_id": str(student.id), 'hmw_name': hmw['name'], 'sending_date':{'$gte':hmw['publish_date']}},
                                                    update={"$set": {'hmw_status': status_list}})
                    await self.hmw_msg_verifier(subject)
                correction_selec = await ctx.send(content=f"<@{ctx.message.author.id}>, le message a bien été envoyé à {name}")
            await asyncio.sleep(15)
            await correction_selec.delete()

        # Verifie que le message est bien envoyé dans un channel correction

        if self.db.send_recv_channels.count_documents({'chan_recv_id':str(ctx.message.channel.id)}) == 0:
            await ctx.message.delete()
            errormsg = await ctx.channel.send("Cette commande n'est utilisable que dans les salons de reception, veuillez réessayer dans le salon correspondant à votre matière.")
            await asyncio.sleep(15)
            await errormsg.delete()
            return

        # Verify that there's a name in the message
        if len(complement) == 0:
            await ctx.message.delete()
            errormsg = await ctx.send("Veuillez recommencer en respectant le format suivant : '!correction nom_de_leleve' avec votre fichier attaché à votre message")
            await asyncio.sleep(15)
            await errormsg.delete()
        else:
            try:

                subject = self.db.teachers.find({'id': str(ctx.message.author.id)})[0]['subject']
                url = ctx.message.attachments[0].url
                filename = ctx.message.attachments[0].filename
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        await ctx.message.delete()
                        file = await resp.read()
                name = list(complement)[0].lower()
                std_list = []
                all_std = self.db.students.find()
                for std in all_std:
                    std_list.append(std['name'])
                # Search Student
                if name not in std_list:
                    sensibility = 0.5
                    possibility = get_close_matches(name.lower(), std_list, 3, sensibility)
                    if len(possibility) > 0:
                        correction_selec = f"L'élève: {name} n'existe pas. S'agit il de :"
                        for i in range(0, len(possibility)):
                            correction_selec += f"\n\t{self.db.emoji.find({'name':str(i+1)})[0]['value']}: {possibility[i]} ?"
                        correction_selec += f"\n\t{self.db.emoji.find({'name':'cross'})[0]['value']}: Aucun des {len(possibility)}"
                        correction_selec = await ctx.message.channel.send(correction_selec)
                        for i in range(0, len(possibility)):
                            await correction_selec.add_reaction(self.db.emoji.find({'name':str(i+1)})[0]['value'])
                        await correction_selec.add_reaction(self.db.emoji.find({'name':'cross'})[0]['value'])
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda reaction, user: user == ctx.message.author and reaction.message.id == correction_selec.id)
                        await correction_selec.delete()
                        try:
                            if self.db.emoji.find({'value': str(reaction)})[0]["name"] == "cross":
                                correction_selec = await ctx.channel.send("Annulation de la commande..")
                                await asyncio.sleep(3)
                                await correction_selec.delete()
                                return
                            elif self.db.emoji.find({'value': str(reaction)})[0]["name"] in ["0","1","2","3","4","5","6","7","8","9"]:
                                student_obj = self.db.students.find({'name': possibility[int(self.db.emoji.find({'value': str(reaction)})[0]["name"])-1]})[0]
                                print(f"eleve choisi : {student_obj['name']}")
                                name = student_obj['name']
                            else:
                                correction_selec = await ctx.channel.send("Annulation de la commande..")
                                await asyncio.sleep(10)
                                await correction_selec.delete()
                                return
                        except Exception as e:
                            print(e)
                            correction_selec = await ctx.channel.send("Annulation de la commande..")
                            await asyncio.sleep(10)
                            await correction_selec.delete()
                            return
                    else:
                        correction_selec = await ctx.message.channel.send(f"Input: {name}\n\tAucun élève ne correspond à cette entrée")
                        await asyncio.sleep(15)
                        await correction_selec.delete()
                        return
                else:
                    print(f"{name} existe dans la BDD")
                    student_obj = self.db.students.find({'name': name})[0]

                student = self.bot.get_user(int(student_obj['student_id']))
                print("student : ", student)
                print("student id : ", student.id)
                added_msg = ""
                subject = self.db.send_recv_channels.find({'chan_recv_id': str(ctx.message.channel.id)})[0]['subject']
                # Demander devoir
                utcDate = datetime.datetime.utcnow()
                thisDay = datetime.datetime(utcDate.year, utcDate.month, utcDate.day)
                all_sended_hmw = []
                print("counted :", self.db.homework.count_documents({'subject': subject, 'deadline': {'$gte': thisDay}}))
                for hmw in self.db.homework.find({'subject': subject, 'deadline': {'$gte': thisDay}}):
                    if self.db.student_hmw.count_documents({"student_id":str(student.id), 'hmw_name':hmw["name"],'subject': subject, 'sending_date': {'$gte': hmw['publish_date']}}) == 1:
                        if "Reçu" in self.db.student_hmw.find({"student_id":str(student.id), 'hmw_name':hmw["name"],'subject': subject, 'sending_date': {'$gte': hmw['publish_date']}})[0]['hmw_status']:
                            all_sended_hmw.append(self.db.student_hmw.find({"student_id":str(student.id), 'hmw_name':hmw["name"],'subject': subject, 'sending_date': {'$gte': hmw['publish_date']}})[0])

                print("len sended hmw : ", len(all_sended_hmw))

                if len(all_sended_hmw) == 0:
                    correction_selec = await ctx.channel.send(f"""```
Vous n'avez plus aucun devoir à corriger pour cet élève, dois-je tout de même envoyer votre fichier ?
        - {self.db.emoji.find({'name': str(1)})[0]['value']} : Oui
        - {self.db.emoji.find({'name': str(2)})[0]['value']} : Non```""")
                    await correction_selec.add_reaction(self.db.emoji.find({'name':str(1)})[0]['value'])
                    await correction_selec.add_reaction(self.db.emoji.find({'name':str(2)})[0]['value'])
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda reaction, user: user == ctx.message.author and reaction.message.id == correction_selec.id)
                    await correction_selec.delete()
                    if self.db.emoji.find({'value': str(reaction)})[0]["name"] == "1":
                            await CorrectionPrinting(added_msg, "", "", subject)
                    else:
                        correction_selec = await ctx.channel.send("Annulation de la commande..")
                        await asyncio.sleep(10)
                        await correction_selec.delete()
                        return
                else:
                    which_hmw = "```A quel devoir appartient cette correction ?\n"
                    print("all_hmw : ", all_sended_hmw)
                    print("len all_hmw :", len(all_sended_hmw))

                    for nb in range(0, len(all_sended_hmw)):
                        print("homework : ", all_sended_hmw[nb]['hmw_name'])
                        if nb > 8:
                            pass
                        else:
                            which_hmw += f"{self.db.emoji.find({'name': str(nb+1)})[0]['value']} : {all_sended_hmw[nb]['hmw_name']}\n"

                    which_hmw += f"{self.db.emoji.find({'name': 'cross'})[0]['value']} : Annuler\n"
                    correction_selec = await ctx.message.channel.send(which_hmw+'```')

                    for nb in range(0, len(all_sended_hmw)):
                        await correction_selec.add_reaction(self.db.emoji.find({'name':str(nb+1)})[0]['value'])
                    await correction_selec.add_reaction(self.db.emoji.find({'name':'cross'})[0]['value'])

                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda reaction, user: user == ctx.message.author and reaction.message.id == correction_selec.id)
                    await correction_selec.delete()

                    all_number = []
                    for nb in range(1, len(all_sended_hmw)+1):
                        all_number.append(self.db.emoji.find({"name":str(nb)})[0]['value'])

                    print("reaction", reaction)
                    print("reaction type", type(reaction))
                    if str(reaction) not in all_number or self.db.emoji.find({'value':str(reaction)})[0]['name'] == "cross":
                        correction_selec = await ctx.channel.send("Annulation de la commande..")
                        await asyncio.sleep(10)
                        await correction_selec.delete()
                        return
                    else:
                        sended_hmw = all_sended_hmw[int(self.db.emoji.find({'value':str(reaction)})[0]['name'])-1]
                        print("sub : ", sended_hmw['subject'])
                        print("name : ", sended_hmw['hmw_name'])
                        print("sending date : ", sended_hmw['sending_date'])
                        sended_date = sended_hmw['sending_date']
                        formatted_sended_date = datetime.datetime(utcDate.year, utcDate.month, utcDate.day)
                        print("formated sended date : ", formatted_sended_date)
                        hmw = self.db.homework.find({'subject': sended_hmw['subject'], 'name':sended_hmw['hmw_name'], 'deadline':{'$gte': formatted_sended_date}})[0]
                        print("hmw : ", hmw)
                        await CorrectionPrinting(added_msg, sended_hmw, hmw, subject)

            except Exception as e:
                if str(e) == "list index out of range":
                    errormsg = await ctx.channel.send("Veuillez recommencer en attachant un fichier à votre message.")
                    await asyncio.sleep(15)
                    await errormsg.delete()
                    return
                elif str(e) == "no such item for Cursor instance":
                    errormsg = await ctx.channel.send("L'élève n'a pas été trouvé, assurez vous que vous avez bien respecté le nom de l'élève donné dans la liste des élèves accessible grâce à la commande !eleves")
                    await asyncio.sleep(15)
                    await errormsg.delete()
                    return
                    #await ctx.channel.send("deux eleves seulement : sloth, skido ;)")
                else:
                    print(e)

    @commands.has_any_role(696433108253409371, 696433108253409373)
    @commands.command(aliases=['sondages','sonddage','sonddages'])
    async def sondage(self, ctx, *kwargs):
        msglist = []
        poll_info = {}
        all_propositions = []
        poll_channel = self.bot.get_channel(691092710085492758)
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

                    complete_string = f"<@&696433108244889722> - Sondage proposé par {self.db.students.find({'student_id':str(ctx.message.author.id)})[0]['name'].title()} :```\n{user_msg.content} \n"
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

                    bot_msg = await poll_channel.send(complete_string+"```")
                    poll_info['nb_propositions'] = len(all_propositions)
                    poll_info['propositions'] = all_propositions
                    poll_info['published_time'] = datetime.datetime.now()
                    poll_info['deadline'] = datetime.datetime.now() + datetime.timedelta(hours=3)
                    self.db.poll.insert_one(poll_info)
                    for i in range(0, nb_proposition):
                        await bot_msg.add_reaction(self.db.emoji.find({'name':str(i)})[0]['value'])
                    for i in range(0, len(msglist)):
                        await msglist[i].delete()
            except Exception as e:
                print(e)
                if str(e).startswith("invalid literal for int() with base 10:"):
                    errormsg = await ctx.send("Veuillez s'il vous plait entrer un nombre entre 2 et 10.")
                    await asyncio.sleep(15)
                    await errormsg.delete()


    ### RECEPTION
    @commands.Cog.listener('on_message')
    async def hmw_sending(self, message):
        if message.author == self.bot.user:
            return

        url_list = []
        filename_list = []
        file_list = []

        async def homework_printing(page_nb, start, stop, all_hmw):
            async with message.channel.typing():
                hmw_selection = f"<@{message.author.id}>\n```Veuillez selectionner le devoir correspondant :\n\n"
                hmw_list = []
                printed_elements = 0
                index = 1
                for hmw in all_hmw[start:stop]:
                    hmw_list.append([hmw['subject'], hmw['name']])
                    hmw_selection += f"{self.db.emoji.find({'name': str(index)})[0]['value']} -> {hmw['subject']} : {hmw['name']}\n"
                    printed_elements += 1
                    index +=1

                if page_nb > 1:
                    hmw_selection += f"\n{self.db.emoji.find({'name': 'back'})[0]['value']} : Revenir à la page précédente"
                if printed_elements < len(all_hmw):
                    hmw_selection += f"\n{self.db.emoji.find({'name': 'nextElem'})[0]['value']} : Aller à la page suivante"
                hmw_selection = await message.channel.send(hmw_selection + "```")

                if page_nb > 1:
                    await hmw_selection.add_reaction(self.db.emoji.find({'name': 'back'})[0]['value'])
                for nb in range(1, printed_elements+1):
                    await hmw_selection.add_reaction(self.db.emoji.find({'name': str(nb)})[0]['value'])
                if printed_elements < len(all_hmw):
                    await hmw_selection.add_reaction(self.db.emoji.find({'name': 'nextElem'})[0]['value'])

                try:
                    print("before waiting react : ", hmw_selection)
                    # if user == message.author and reaction.message.id == hmw_selection.id:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda reaction, user: user == message.author and reaction.message.id == hmw_selection.id)
                except asyncio.TimeoutError:
                    await hmw_selection.delete()
                    return

                reaction = self.db.emoji.find({'value': str(reaction)})[0]['name']
                await hmw_selection.delete()
                if reaction == self.db.emoji.find({'name': 'nextElem'})[0]['name']:
                    hmw_list, reaction = await homework_printing(page_nb+1, stop, stop+5, all_hmw)
                elif reaction == self.db.emoji.find({'name': 'back'})[0]['name']:
                    hmw_list, reaction = await homework_printing(page_nb-1, start-5, start, all_hmw)
                return hmw_list, int(reaction)

        try:
            channel_obj = self.db.send_recv_channels.find({'chan_send_id': str(message.channel.id)})[0]
            print("user : ", self.bot.get_user(message.author.id))
            async with message.channel.typing():
                prof = self.bot.get_user(int(channel_obj['teacher_id']))
                recv_chan = self.bot.get_channel(int(channel_obj['chan_recv_id']))
                send_chan = self.bot.get_channel(int(channel_obj['chan_send_id']))
                for i in range(0, len(message.attachments)):
                    url_list.append(message.attachments[i].url)
                    filename_list.append(message.attachments[i].filename)
                for i in range(0, len(message.attachments)):
                    #file_list.append(await message.attachments[i].read())
                    start = time.time()
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
                                file_list.append(await resp.read())
                                #f = await aiofiles.open(filename_list[i], mode='wb')
                                #await f.close()
                try:
                    await message.delete()
                    end = time.time()
                    print(end - start)
                except Exception as e:
                    if str(e) == "404 Not Found (error code: 10008): Unknown Message":
                        print(e)
                        print("anyway this is good")
                        pass
            try:
                utcDate = datetime.datetime.utcnow()
                thisDay = datetime.datetime(utcDate.year, utcDate.month, utcDate.day)
                all_hmw = list(self.db.homework.find({'subject': channel_obj['subject'], 'deadline': {'$gte': thisDay}}).sort("deadline"))
                all_hmw_count = self.db.homework.count_documents({'subject': channel_obj['subject'], 'deadline': {'$gte': thisDay}})
                print("all hmw in range : ", all_hmw_count)
                if all_hmw_count == 0:
                    errormsg = await message.channel.send("```Aucun devoir pour cette matière```")
                    await asyncio.sleep(15)
                    await errormsg.delete()
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
                        print(e)
                        bot_msg = await message.channel.send(f"<@{message.author.id}> Pas de réponse, annulation de l'envoi...")
                        await asyncio.sleep(15)
                        await bot_msg.delete()
                        return
                    else:
                        print("Error homework finding/sorting : ", str(e))
                        return
            print("id", message.author.id)
            print("eleve bdd", self.db.students.find({'student_id':str(message.author.id)})[0])
            std_name = self.db.students.find({'student_id':str(message.author.id)})[0]['name']
            print("hmw : ", hmw_list[int(reaction_nb)-1])
            utcDate = datetime.datetime.utcnow()
            thisDay = datetime.datetime(utcDate.year, utcDate.month, utcDate.day)
            hmw = self.db.homework.find({'subject':hmw_list[int(reaction_nb)-1][0], 'name':hmw_list[int(reaction_nb)-1][1], 'deadline':{'$gte':thisDay}})[0]
            print(hmw)
            #is_hmw_in_bdd = list(self.db.student_hmw.find({'name':std_name, 'hmw_name':hmw_list[int(reaction_nb)-1][1], 'sending_date':{'$gte':hmw['publish_date']}}))
            messages = [message.content]
            status = ["Envoyé"]
            #print("is in bdd : ", is_hmw_in_bdd)
            print("hmw name : ", hmw_list[int(reaction_nb)-1][1])
            counted = self.db.student_hmw.count_documents({'name': std_name, 'hmw_name': hmw_list[int(reaction_nb) - 1][1],
                                                 'sending_date': {'$gte': hmw['publish_date']}})
            print("counted :", counted)

            async with message.channel.typing():
                # Create the element
                if self.db.student_hmw.count_documents({'name':std_name, 'hmw_name':hmw_list[int(reaction_nb)-1][1], 'sending_date':{'$gte':hmw['publish_date']}}) == 0:
                    if len(filename_list) == 0:
                        filename_list.append("")
                        file_list.append("")
                    else:
                        for nb in range(1,len(filename_list)):
                            messages.append("")
                            status.append("Envoyé")
                    student_hmw = {
                        'name': std_name,
                        'student_id': str(message.author.id),
                        'subject': hmw_list[int(reaction_nb)-1][0],
                        'hmw_name': hmw_list[int(reaction_nb)-1][1],
                        'hmw_status': status,
                        'sending_date': datetime.datetime.now(),
                        'message': messages,
                        'filename': filename_list,
                        'file': file_list
                    }
                    self.db.student_hmw.insert_one(student_hmw)
                # Update the element
                else:
                    student_hmw = self.db.student_hmw.find({'name':std_name, 'hmw_name':hmw_list[int(reaction_nb)-1][1], 'sending_date':{'$gte':hmw['publish_date']}})[0]
                    student_hmw['message'].append(message.content)
                    student_hmw['hmw_status'].append("Envoyé")
                    if len(filename_list) == 0:
                        student_hmw['filename'].append("")
                        student_hmw['file'].append("")
                    else:
                        for nb in range(0, len(file_list)):
                            print(nb)
                            if nb >= 1:
                                student_hmw['message'].append("")
                                student_hmw['hmw_status'].append("Envoyé")
                            student_hmw['filename'].append(filename_list[nb])
                            student_hmw['file'].append(file_list[nb])

                    #print("std_file : ", student_hmw['file'])
                    #print("std_filename : ", student_hmw['filename'])
                    print("std_msg : ", student_hmw['message'])
                    #print("std_hmw : ", student_hmw)
                    print("-----")
                    self.db.student_hmw.find_and_modify(query={'subject': hmw_list[int(reaction_nb)-1][0], 'name':std_name, 'hmw_name':hmw_list[int(reaction_nb)-1][1], 'sending_date':{'$gte':hmw['publish_date']}}, update={'$set': {'message': student_hmw['message'], 'filename':student_hmw['filename'], 'file':student_hmw['file'], 'sending_date':datetime.datetime.now(), 'hmw_status':student_hmw['hmw_status']}})

                ### IMPORTANT : sur la ligne commentée suivante, on voit comment il faut envoyer le fichier !
                ### METTRE EN PLACE ENVOI DE FICHIER
                # await prof.send(content=f"{channel_obj['subject']} : {message.author.nick} : {message.content}", file=discord.File(fp=io.BytesIO(buffer), filename=filename))
                confirmation = await recv_chan.send(content=f"{std_name.title()} : a envoyé un fichier")
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
        elif message.content == "Respecte moi ou je te débranche":
            await message.channel.send("Mes plus sincères excuses maitre, je ne recommencerai plus")

def setup(bot):
    bot.add_cog(Cog(bot))
