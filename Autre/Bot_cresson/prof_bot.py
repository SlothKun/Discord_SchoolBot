import discord
import os
import asyncio
from discord.ext import commands

client = commands.Bot(command_prefix="§")


#events
@client.event
async def on_message(message):
    if message.author == client.user: # On évite que le bot se réponde à lui même
        return
    
    if message.content.startswith("§") == False: # on évite que les commandes du bot soient prises en compte, autrement ça créé des conflits
        if message.channel.id == 694580781565083671: #si on est dans le canal envoi-de-fichiers
            auteur = message.author #la personne qui a ecrit le message et souhaite le transfert
            moi=client.get_user(689817117926621204) #juste moi
            pas_de_fichier=False#booleen pour différentier les cas
            
            try:#general
                try:#pour le cas ou on n'a pas de fichier
                    message_file = message.attachments[0] # on récupère la partie fichier du message
                except:
                    pas_de_fichier=True
                    les_roles=auteur.roles# les roles de l'utilisateur
                    matiere=les_roles[1].name#recuperation du nom de la matière (le second role car le premier est eleve)
                    if pas_de_fichier:# si le message ne contient pas de fichier
                        print(f"{matiere} par {auteur.display_name} mais pas de fichier") # on affiche dans les logs le nom du fichier
                        await message.delete() # on supprime le message de l'élève pour pas qu'il soit visible du reste des élèves
                        await moi.send(content=f"en {matiere}, {auteur.display_name} a envoyé le message: {message.content} mais pas de fichier") # on m'envoie le message (sans fichier)
                        bot_msg = await message.channel.send(content=f"<@{auteur.id}>, le message a bien été envoyé mais il ne contient pas de fichier") # on confirme l'envoi à l'élève
                    else:#sinon
                        print(f"{message_file.filename} en {matiere} par {auteur.display_name}") # on affiche dans les logs le nom du fichier la matiere et l'expediteur
                        file = await message.attachments[0].to_file() # on transforme le fichier récupéré sous une forme que l'on peut envoyer
                        await message.delete() # on supprime le message de l'élève pour pas qu'il soit visible du reste des élèves
                        await moi.send(content=f"{matiere} : {auteur.display_name} : {message.content}", file=file) # on m'envoie le message et le fichier
                        bot_msg = await message.channel.send(content=f"<@{auteur.id}>, le message a bien été envoyé avec le fichier {message_file.filename}") # on confirme l'envoi à l'élève
                    await asyncio.sleep(30) # on attend 30sec
                try:
                    await bot_msg.delete() # on supprime la confirmation pour éviter le flood
                except:
                    pass # si le message à déjà été supprimé ou autre, on laisse tomber
            except Exception as e:
                print(str(e))
                await moi.send(content=str(e)) # on m'envoi l'erreur
                bot_msg = await message.channel.send(content=f"une erreur s'est produite, contacter M.CRESSON") # on prévient de l'erreur
                await asyncio.sleep(30) # on attend 30sec
                try:
                    await bot_msg.delete() # on supprime le message d'erreur
                except:
                    pass # si le message à déjà été supprimé ou autre, on laisse tomber
    await client.process_commands(message)
    
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('\"Je travaille pour vous\"'))
    print("monbot est en ligne")
    
@client.event
async def on_member_join(member):#si un membre rejoint le serveur        
    embeded = discord.Embed(colour = discord.Colour.blue())
    embeded.set_author(name=f"{member} a rejoint le serveur.")
    embeded.add_field(name="contenu", value=message, inline=False)
    print(f'{member} a rejoint le serveur.')
       
    await ctx.send(embed=embeded)#envoi dans 
        
@client.event
async def on_member_remove(member):#si un membre quitte le serveur
    print(f'{member} a quitté le serveur')
        

#commandes

@client.command()
@commands.has_permissions(administrator=True)
async def ping(ctx):
    await ctx.send(f"Pong! en {round(client.latency*1000)}ms")#affiche le temps de latence

@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):#chargement d'une extension
    client.load_extension(f"cogs.{extension}")
    
@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):#suppression d'une extension
    client.unload_extension(f"cogs.{extension}")

@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):#rechargement d'une extension
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")

for filename in os.listdir('./cogs'):#boucle sur la liste des extensions dans le repertoire cogs
    if filename.endswith('.py'):#si l'extension est du type python
        client.load_extension(f"cogs.{filename[:-3]}")#charge l'extension
#récupération du token  
with open("donnees.txt") as donnees:#ouvre le fichier contenant le token
    token=donnees.readline();#recupération du token
    
client.run(token) #lancement
