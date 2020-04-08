#!/usr/bin/python
import os # pour autre chose ça
import discord
import asyncio

TOKEN = "Njg5MTg0MTU5MDcxMzM4NTAy.Xm_K3g.-NejIbWzgY9SNV5lUf5LQAMPc4s" # ici le token

client = discord.Client() # l'objet de la lib
number_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"] 
liste_eleves = { # liste de tous les élèves avec leur id (clic droit sur l'élève -> copier l'id) | améliorable
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
    "vivien": 689984197019959316
}
liste_profs = { # liste de tous les professeurs avec leur ID
    "guyot": 689957656609292402,
    "cresson": 689817117926621204,
    "delandre": 689862626125152365,
    "nowicki": 689873074614698056,
    "ioos": 689121305454313632,
    "boully": 122372446761254912
}
granted_user = { # liste des users qui ont le droit d'entrer les commandes (on peut aussi gerer par role)
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

@client.event # Vérification de la connexion du bot
async def on_ready():
    print('logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

''' 
Sondage version test : trouver meilleur moyen de bloquer la réception de message trop hatifs
'''

async def sondage(message, granted_user):
    try:
        await message.delete()
        all_msg = [] # on vide la liste des messages envoyés
        channel_validator = False # on prépare l'entrée dans la boucle
        channel_sondages = client.get_channel(691092710085492758) # on récupère le channel dans lequel le sondage sera affiché
        nb_proposition = int(message.content.split(" ")[1][:1]) # on récupère le nombre entré en paramètre de message
        if nb_proposition > 9 or nb_proposition < 1: # on limite le nombre de proposition à rentrer 
            await message.channel.send("Veuillez entrer un nombre entre 1 et 9 !")
            return # on prévient et on annule la commande
        bot_answer = await message.channel.send("Veuillez écrire la description de votre sondage :")
        all_msg.append(bot_answer) # on ajoute le message envoyé dans la liste des messages
        while channel_validator == False: # petit fix foireux mais fonctionnel pour éviter les conflits ou le bot envoi tous les messages d'un coup
            description = await client.wait_for('message', timeout=60.0) # on met un timer pour pas rester coincé éternellement
            if description.channel == message.channel: # on fait attention à ce que les messages des autres channels ne rentrent pas en conflit
                print(description.channel)
                all_msg.append(description) # on ajoute l'objet message dans la liste
                channel_validator = True # on valide pour sortir de la boucle
        complete_string = f"<@&689285153562165374> Sondage proposé par {message.author.nick} :\n" + description.content + "\n" # on prépare la str complète
        for i in range(0, nb_proposition):
            proposition_validator = False # on prépare l'entrée dans la boucle
            if message.author.id in granted_user and granted_user[message.author.id] == True:
                granted_user[message.author.id] = False # on bloque la reception de message pour éviter les conflits
                bot_answer = await message.channel.send(f"Veuillez écrire la proposition n°{i + 1} :")
                while proposition_validator == False:
                    proposition = await client.wait_for('message', timeout=60.0) # attente
                    if proposition.channel == message.channel: # message bien dans le meme channel que celui d'envoi
                        proposition_validator = True # on valide la sortie de la boucle
                        granted_user[message.author.id] = True # on reactive la reception de message
                        all_msg.append(proposition) # on ajoute l'objet message dans la liste
                        all_msg.append(bot_answer) # on ajoute l'objet message dans la liste
                complete_string += (number_list[i] + " : " + proposition.content + "\n") # on complète la str
                print(complete_string)
        bot_msg = await channel_sondages.send(content=complete_string) # on envoi la str dans le channel prévu plutot
        for i in range(0, nb_proposition):
            await bot_msg.add_reaction(number_list[i]) # on ajoute les reactions au sondage correspondant au nombre de propositions
        bot_answer = await message.channel.send(f"<@{message.author.id}>, le message a bien été envoyé") # on confirme à l'utilisateur
        for i in range(0, len(all_msg)): # pour chaque message dans tous les messages envoyés
            await all_msg[i].delete() # on supprime tous les messages envoyés lié à la commande
        await asyncio.sleep(30) 
        await bot_answer.delete() # on attend 30sec et on supprime la confirmation 
    except Exception as e:
        if str(e) == "list index out of range":
            await message.channel.send("Veuillez préciser le nombre de proposition.") # dans le cas ou aucun argument n'est ajouté
        else:
            await message.channel.send("Le bot a eu un problème, veuillez reessayer.") # on averti du problème et on l'affiche dans les logs
            print(e) # on envoi l'erreur dans les logs pour trouver le problème


async def send_file_to_rec(channel_out, channel_in, prof, matiere, message):
    try:
        if message.content.startswith("!") == False: # on évite que les commandes du bot soient prises en compte, autrement ça créé des conflits
            message_file = message.attachments # on récupère la partie fichier du message
            print(message_file[0].filename) # on affiche dans les logs le nom du fichier
            message_file = await message_file.to_file() # on transforme les bit en fichier
            await message.delete() # on supprime le message de l'élève pour pas qu'il soit visible du reste des élèves
            await prof.send(content=f"{matiere} : {message.author.nick} : {message.content}", file=message_file) # on envoi au prof concerné
            await channel_out.send(content=f"{message.author.nick} : a envoyé un fichier") # on envoi une notification dans le channel de sortie (permet de verifier l'envoi du fichier pour le confirmer aux élèves de mon côté)
            bot_msg = await channel_in.send(content=f"<@{message.author.id}>, le message a bien été envoyé") # on confirme l'envoi à l'élève
            await asyncio.sleep(30) # on attend 30sec
            try:
                await bot_msg.delete() # on supprime la confirmation pour éviter le flood
            except:
                pass # si le message à déjà été supprimé ou autre, on laisse tomber
    except Exception as e:
        if str(e) == "list index out of range": # on gère le cas où il n'y a pas de fichier envoyé (similaire à ce qu'il y a au dessus)
            await message.delete()
            await prof.send(content=f"{matiere} : {message.author.nick} : {message.content}")
            await channel_out.send(content=f"{message.author.nick} : a envoyé un message")
            bot_msg = await channel_in.send(content=f"<@{message.author.id}>, le message a bien été envoyé")
            await asyncio.sleep(30)
            try:
                await bot_msg.delete()
            except:
                pass
        print(e) # on envoi l'erreur dans les logs au cas où



@client.event
async def on_message(message):
    if message.author == client.user: # On évite que le bot se réponde à lui même
        return

    channel_in = client.get_channel(message.channel.id) # on récupère l'id du channel d'envoi 
    if message.channel.id == 690154420050067473: # envoi/reception tests
        channel_out = client.get_channel(690154447187214357)
        prof = client.get_user(liste_profs["boully"])
        matiere = "test" 
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)

    elif message.channel.id == 692717266516574218: # envoi/reception anglais
        channel_out = client.get_channel(692717352227307552) # on récupère le channel de sortie
        prof = client.get_user(liste_profs["guyot"]) # on récupère le prof
        matiere = "anglais" # ainsi que la matière 
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message) # on appelle la fonction en précisant les paramètres channel de sortie (reception), d'entrée (envoi), le prof, la matière et l'objet message

    elif message.channel.id == 689148224782598174: # envoi/reception maths
        channel_out = client.get_channel(689149590540517438)
        prof = client.get_user(liste_profs["cresson"]) # on récupère le prof
        matiere = "Maths"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)

    elif message.channel.id == 689145093164498981: # envoi/reception physique
        channel_out = client.get_channel(689149391738765332)
        prof = client.get_user(liste_profs["ioos"]) # on récupère le prof
        matiere = "Physique"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)

    elif message.channel.id == 689878834409242824: # envoi/reception SI electronique
        channel_out = client.get_channel(689876788775616526)
        prof = client.get_user(liste_profs["nowicki"]) # on récupère le prof
        matiere = "SI"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)

    elif message.channel.id == 690162402125283358: # envoi/reception philo
        channel_out = client.get_channel(690162448954949709)
        prof = client.get_user(liste_profs["delandre"]) # on récupère le prof
        matiere = "Philo"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message) 

    elif message.channel.id == 690221894712164440:  # envoi/reception isn
        channel_out = client.get_channel(690221950982815778)
        prof = client.get_user(liste_profs["nowicki"]) # on récupère le prof
        matiere = "Isn"
        await send_file_to_rec(channel_out, channel_in, prof, matiere, message)

    elif message.content.lower().startswith("!sondage") and message.author.id in granted_user: # on verifie la validé de la commade et on verifie que l'utilisateur est autorisé à utiliser la commande
        await sondage(message, granted_user)

    elif message.content.lower().startswith("!eleves") and message.author.id in granted_user: # on verifie la validé de la commade et on verifie que l'utilisateur est autorisé à utiliser la commande
        await message.channel.send("""```
Alexis    |  Amelie    |  Axelle   |  Baptiste   |  Bastian\n
Camille   |  Charlie   |  Emeline  |  Emile      |  Enzo\n
Florian   |  Gregoire  |  Hugo     |  Jason      |  Jean\n
Juan      |  Louis     |  Lea      |  Leo        |  Manon\n
MargauxL  |  MargauxQ  |  Marie    |  Mateo      |  Max\n
Maxence   |  Mael      |  Pierre   |  Romain     |  Sarah\n
TheoG     |  TheoB     |  Thibaut  |  Vivien     |
            ```""") # formatage assez sensible qui pourrait surement être amélioré
    elif message.content.lower().startswith("!correction") and message.author.id in granted_user: # on verifie la validée de la commade et on verifie que l'utilisateur est autorisé à utiliser la commande
        if len(message.content.split(" ")) < 2: # on vérifie que le nombre de paramètre est respecté
            await message.channel.send("Veuillez recommencer en respectant le format suivant : '!correction nom_de_leleve' avec votre fichier attaché à votre message")
        else:
            message_split = message.content.split(" ")
            eleve = message_split[1] # on récupère le nom de l'élève
            if eleve.lower() in liste_eleves: # on verifie qu'il est dans la liste
                try:
                    added_message = "" # on init la variable message ajouté (necessaire pour la suite)
                    file = await message.attachments[0].to_file() # on transforme le fichier récupéré sous forme de bit en veritable fichier
                    user_cible = client.get_user(liste_eleves[eleve.lower()]) # on récupère le compte de l'élève
                    if len(message_split) > 2: # on gère le cas des espaces
                        for i in range(2, (len(message_split))):
                            added_message += message_split[i] + " "
                    await user_cible.send(content=f"{message.author.nick} vous as envoyé cette correction : \n {added_message}", file=file) # on envoi le fichier à l'élève cible précisant le nom du professeur qui envoi
                    await message.delete() # on supprime le message de la commande
                    bot_msg = await channel_in.send(content=f"<@{message.author.id}>, le message a bien été envoyé à {eleve}") # on envoi la confirmation dans le channel ou a eu lieu la commande
                except Exception as e:
                    print(e) # on envoi l'exception dans les logs au cas ou
                    if str(e) == "list index out of range": # on gère le cas ou aucun fichier n'a été envoyé
                        await message.channel.send("Veuillez recommencer en attachant un fichier à votre message.")
                    else: # on gère les cas divers qui peuvent arriver notamment niveau connexion
                        await message.channel.send("Je ne peux satisfaire votre demande pour le moment, veuillez patienter et réessayer")
            else: # on gère le cas du mauvais nom d'élève
                await message.channel.send("L'élève n'a pas été trouvé, assurez vous que vous avez bien respecté le nom de l'élève donné dans la liste des élèves accessible grâce à la commande !eleves")


client.run(TOKEN)