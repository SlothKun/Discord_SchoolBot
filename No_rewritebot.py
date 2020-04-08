#!/usr/bin/python
import os
import discord
import asyncio

TOKEN = "Njg5MTg0MTU5MDcxMzM4NTAy.Xm_K3g.-NejIbWzgY9SNV5lUf5LQAMPc4s"

client = discord.Client()
devoirs_envoyés = {}
number_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
liste_eleves = {
    "alexis": 186873599565496321,
    "amelie": 689104501105492071,
    "amélie": 689104501105492071,
    "axelle": 386439191040622593,
    "baptiste": 343338598139035659,
    "bastian": 306773911008444426,
    "camille": 689125354971201622,
    "charlie": 689083785932701699,
    "emeline": 653688496871047168,
    "emile": 493352801963868171,
    "émile": 493352801963868171,
    "enzo": 404357629171859466,
    "florian": 579959262273339394,
    "gregoire": 655569750457319464,
    "grégoire": 655569750457319464,
    "hugo": 300732781124911114,
    "jean": 399918118803210252,
    "louis": 248125458221105153,
    "lea": 689077188707876864,
    "léa": 689077188707876864,
    "leo": 339000242437488641,
    "léo": 339000242437488641,
    "manon": 689051766490136578,
    "margauxl": 689179100379742242,
    "margauxq": 689100355178332401,
    "marie": 689055094838132736,
    "mateo": 503881403386298369,
    "matéo": 503881403386298369,
    "max": 305305968693215235,
    "maxence": 242949235404832769,
    "mael": 494781231200731157,
    "maël": 494781231200731157,
    "pierre": 405104557862027275,
    "romain": 381359044062871555,
    "sarah": 170267883182489600,
    "theog": 689083790014152714,
    "théog": 689083790014152714,
    "theob": 122372446761254912,
    "théob": 122372446761254912,
    "thibaut": 689170490753024045,
    "juan": 510731707553415168,
    "jason": 419239963062829057,
    "vivien": 689984197019959316,
    "ambre": 690478499974348813,
    "margauxo": 689835629478936576,
    "mona": 690304465089462342
}

liste_profs = {
    "guyot": 689957656609292402,
    "cresson": 689817117926621204,
    "delandre": 689862626125152365,
    "nowicki": 689873074614698056,
    "ioos": 689121305454313632
}
user_sended = {
    689957656609292402: True, # Guyot
    689817117926621204: True, # Cresson
    689862626125152365: True, # Delandre
    689873074614698056: True, # Nowicki
    689121305454313632: True, # Ioos
    122372446761254912: True, # Boully
    170267883182489600: True, # Sarah
    493352801963868171: True, # Emile
    306773911008444426: True # Bastian
}

async def sondage(message, user_sended):
    try:
        await message.delete()
        all_msg = []
        channel_validator = False
        channel_sondages = client.get_channel(696433108559331347)
        nb_proposition = int(message.content.split(" ")[1][:1])
        if nb_proposition > 9 or nb_proposition < 1:
            await message.channel.send("Veuillez entrer un nombre entre 1 et 9 !")
            return
        bot_answer = await message.channel.send("Veuillez écrire la description de votre sondage :")
        all_msg.append(bot_answer)
        while channel_validator == False:
            description = await client.wait_for('message', timeout=60.0)
            if description.channel == message.channel:
                print(description.channel)
                all_msg.append(description)
                channel_validator = True
        complete_string = f"<@&689285153562165374> Sondage proposé par {message.author.nick} :\n" + description.content + "\n"
        for i in range(0, nb_proposition):
            proposition_validator = False
            if message.author.id in user_sended and user_sended[message.author.id] == True:
                user_sended[message.author.id] = False
                bot_answer = await message.channel.send(f"Veuillez écrire la proposition n°{i + 1} :")
                while proposition_validator == False:
                    proposition = await client.wait_for('message', timeout=60.0)
                    if proposition.channel == message.channel:
                        proposition_validator = True
                        user_sended[message.author.id] = True
                        all_msg.append(proposition)
                        all_msg.append(bot_answer)
                complete_string += (number_list[i] + " : " + proposition.content + "\n")
                print(complete_string)
        bot_msg = await channel_sondages.send(content=complete_string)
        for i in range(0, nb_proposition):
            await bot_msg.add_reaction(number_list[i])
        bot_answer = await message.channel.send(f"<@{message.author.id}>, le message a bien été envoyé")
        for i in range(0, len(all_msg)):
            await all_msg[i].delete()
        await asyncio.sleep(30)
        await bot_answer.delete()



    except Exception as e:
        if str(e) == "list index out of range":
            await message.channel.send("Veuillez préciser le nombre de proposition.")
        else:
            await message.channel.send("Le bot a eu un problème, veuillez reessayer.")
            sloth = client.get_user(122372446761254912)
            await sloth.send(content="Il y a eu un problème dans sondage, mate tes logs !")
            print(e)

async def send_file_to_rec(channel_out, channel_in, prof, matiere, message):
    try:
        if message.content.startswith("!") == False:
            list = message.attachments
            print(list[0].filename)
            for attachment in list:
                file = await attachment.to_file()
                await message.delete()
                await prof.send(content=f"{matiere} : {message.author.nick} : {message.content}", file=file)
                await channel_out.send(content=f"{message.author.nick} : a envoyé un fichier")
                devoirs_envoyés.setdefault(message.author.nick, [])
                devoirs_envoyés[message.author.nick].append(attachment.filename)
                bot_msg = await channel_in.send(content=f"<@{message.author.id}>, le message a bien été envoyé")
                await asyncio.sleep(30)
                try:
                    await bot_msg.delete()
                except:
                    pass
    except Exception as e:
        if str(e) == "list index out of range":
            await message.delete()
            await prof.send(content=f"{matiere} : {message.author.nick} : {message.content}")
            await channel_out.send(content=f"{message.author.nick} : a envoyé un message")
            bot_msg = await channel_in.send(content=f"<@{message.author.id}>, le message a bien été envoyé")
            await asyncio.sleep(60)
            try:
                await bot_msg.delete()
            except:
                pass
        print(e)

@client.event
async def on_ready():
    print('logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    channel_in = client.get_channel(message.channel.id)
    if message.channel.id == 696433108253409379: # envoi/reception tests
        channel_out = client.get_channel(696433108253409378)
        prof = client.get_user(139407866267303937)
        matiere = "test"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)
    elif message.channel.id == 692717266516574218: # envoi/reception anglais
        channel_out = client.get_channel(692717352227307552)
        prof = client.get_user(689957656609292402)
        matiere = "anglais"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)
    elif message.channel.id == 689148224782598174: # envoi/reception maths
        channel_out = client.get_channel(689149590540517438)
        prof = client.get_user(689817117926621204)
        matiere = "Maths"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)
    elif message.channel.id == 689145093164498981: # envoi/reception physique
        channel_out = client.get_channel(689149391738765332)
        prof = client.get_user(689121305454313632)
        matiere = "Physique"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)
    elif message.channel.id == 689878834409242824: # envoi/reception SI electronique
        channel_out = client.get_channel(689876788775616526)
        prof = client.get_user(689873074614698056)
        matiere = "SI"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)
    elif message.channel.id == 690162402125283358: # envoi/reception philo
        channel_out = client.get_channel(690162448954949709)
        prof = client.get_user(689862626125152365)
        matiere = "Philo"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)
    elif message.channel.id == 690221894712164440:  # envoi/reception isn
        channel_out = client.get_channel(690221950982815778)
        prof = client.get_user(689873074614698056)
        matiere = "Isn"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)
    elif client.private_channels != True:
        if message.content == "!devoirs" and message.author.id in user_sended:
            for eleve in devoirs_envoyés:
                await message.channel.send(f"{eleve} : {devoirs_envoyés[eleve]}")
        elif message.content.lower().startswith("!sondage") and message.author.id in user_sended:
            await sondage(message, user_sended)
        elif message.content.lower().startswith("!eleves") and message.author.id in user_sended:
            await message.channel.send("""```
Alexis    |  Amelie    |  Axelle   |  Baptiste   |  Bastian\n
Camille   |  Charlie   |  Emeline  |  Emile      |  Enzo\n
Florian   |  Gregoire  |  Hugo     |  Jason      |  Jean\n
Juan      |  Louis     |  Lea      |  Leo        |  Manon\n
MargauxL  |  MargauxQ  |  Marie    |  Mateo      |  Max\n
Maxence   |  Mael      |  Pierre   |  Romain     |  Sarah\n
TheoG     |  TheoB     |  Thibaut  |  Vivien     |

Hors TS1 : Spe ISN 
Ambre     |  MargauxO  |  Mona
            ```""")
        elif message.content.lower().startswith("!correction") and message.author.id in user_sended:
            if len(message.content.split(" ")) < 2:
                await message.channel.send("Veuillez recommencer en respectant le format suivant : '!correction nom_de_leleve' avec votre fichier attaché à votre message")
            else:
                message_split = message.content.split(" ")
                eleve = message_split[1]
                if eleve.lower() in liste_eleves:
                    try:
                        message_supp = ""
                        file = await message.attachments[0].to_file()
                        user_cible = client.get_user(liste_eleves[eleve.lower()])
                        if len(message_split) > 2:
                            for i in range(2, (len(message_split))):
                                message_supp += message_split[i] + " "
                        await user_cible.send(content=f"{message.author.nick} vous as envoyé cette correction : \n {message_supp}", file=file)
                        await message.delete()
                        bot_msg = await channel_in.send(content=f"<@{message.author.id}>, le message a bien été envoyé à {eleve}")
                    except Exception as e:
                        print(e)
                        if str(e) == "list index out of range":
                            await message.channel.send("Veuillez recommencer en attachant un fichier à votre message.")
                        else:
                            await message.channel.send("Je ne peux satisfaire votre demande pour le moment, veuillez patienter et réessayer")
                else:
                    await message.channel.send("L'élève n'a pas été trouvé, assurez vous que vous avez bien respecté le nom de l'élève donné dans la liste des élèves accessible grâce à la commande !eleves")


client.run(TOKEN)
