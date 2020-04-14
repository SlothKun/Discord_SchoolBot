import discord
from discord.ext import commands
from pymongo import MongoClient
from asyncio import sleep
import datetime
import locale
import json

class Homework():
    def __init__(self, creator, hmwName):
        self.creator = creator
        self.name = hmwName
        self.doc = []
        self.deadline = None
        self.status = None
        self.subject = None

    def addFiles(self, newFile):
        self.doc.append(newFile)

    def __str__(self):
        desc = f"Devoir de {self.subject} : {self.name}\nStatut : {self.status}\nPour le {self.deadline.strftime('%d %B %Y')}"
        if len(self.doc) > 0:
            desc += f"{len(self.doc)} document(s) associé(s):"
            for doc in self.doc:
                desc += f"\t*{doc}*"
        else:
            desc += "\nAucun document associé"
        return desc

class HmwManager():
    def __init__(self, creator, botMsg):
        self.user = creator
        self.botMsg = botMsg
        self.creationDate = datetime.datetime.now()
        self.fileAwaited = False
        self.states = ["idle", "hmwAdd", "hmwEdit", "hmwDelete"]
        self.subStates = {
            "hmwAdd" : ["name", "date", "status", "subject"],
            "hmwEdit" : ["name", "partToEdit", ""],
            "hmwDelete" : ["name"]
            }
        self.userAction = self.states[0]
        self.actionSubState = None
        self.subStateCounter = 0
        self.homework = None

    def __str__(self):
        return f"Class created by {self.user} on {self.creationDate} in the current state : {self.userAction} - {self.actionSubState}"

    def updateBotMsg(self, newBotMsg):
        self.botMsg = newBotMsg

    def updateUserAction(self, action):
        self.userAction = self.states[action]

    def updateActionState(self, newState):
        self.subStateCounter += newState
        self.actionSubState = self.subStates[self.userAction][self.subStateCounter]

    def getNbSubState(self):
        return len(self.subStates[self.userAction])

    def setHmw(self, hmwName):
        self.homework = Homework(self.user, hmwName)

    def checkNextAction(self, command):
        if self.userAction == self.states[1]:
            if command == 'Name':
                return self.actionSubState is None
            elif command == 'Date':
                return self.actionSubState == self.subStates[self.userAction][0]
            elif command == 'Status':
                return self.actionSubState == self.subStates[self.userAction][1]
            elif command == 'Subject':
                return self.actionSubState == self.subStates[self.userAction][2]
        elif self.userAction == self.states[2]:
            if command == 'Name':
                return self.actionSubState is None
            elif command == 'PartToEdit':
                return self.actionSubState == self.subStates[self.userAction][0]
        elif self.userAction == self.states[3]:
            if command == 'Name':
                return self.actionSubState is None
        return False



class SchoolBot(commands.Cog):
    def __init__(self, schoolBot):
        super().__init__()
        self.schoolBot = schoolBot

        # Set time elements in french
        locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

        # Dictionary of '!devoir' commands entered by users
        # Used to keep track of who initiated the command and all of his actions
        self.hmwManagers = {}

        # Data about the mongo database used
        # Needs to have a predefined mongo database
        with open("src/config/dbStruct.json", "r") as dbConfig:
            self.dbStruct = json.load(dbConfig)

        # Connect and access to mongo database "schoolBot"
        self.mongoCli = MongoClient(self.dbStruct['db_address'], self.dbStruct['db_port'])
        if self.mongoCli is not None:
            try:
                self.mDB = self.mongoCli[self.dbStruct['db_name']]
            except:
                print(f"Cog {self.__class__.__name__} could not find the database")
        else:
            print(f"Cog {self.__class__.__name__} could not connect to MongoDB")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.__class__.__name__} is online")

    @commands.Cog.listener('on_message')
    async def manageFile(self, message):
        if message.author in self.hmwManagers and len(message.attachments) > 0:
            # Detect if a file has been uploaded and if the uploader is currently trying to manage some homeworks
            # TODO: Take care to only add file for people who ask of it !
            if self.hmwManagers[message.author].fileAwaited:
                # Check if the uploader notified that a file will be linked to his homework
                hmwFiles = message.attachments
                for hmwFile in hmwFiles:
                    newFile = hmwFile.to_file()
                    self.hmwManagers[message.author].homework.addFiles(newFile)
                    await message.channel.send(f"Le fichier {hmwFile.filename} a été associé au devoir {self.hmwManagers[message.author].homework.name}")
                self.hmwManagers[message.author].fileAwaited = False
            else:
                await message.channel.send(f"{message.author.mention}: Vous n'avez pas notifié l'ajout d'un fichier pour le devoir {self.hmwManagers[message.author].homework.name}.\nLe fichier joint n'a été associé à aucun devoir.")

    # Listen to all reactions added on msg on the server
    @commands.Cog.listener('on_reaction_add')
    async def manageReactions(self, reaction, user):
        if user in self.hmwManagers is not None and self.hmwManagers[user].botMsg == reaction.message.id:
            reactDB = self.mDB[self.dbStruct['db_collections']['emoji']]
            hmwEmojis = reactDB.find({self.dbStruct['db_collections']['emoji_fields']['utility']: 'hmwConf'}, {'value': 1})
            checkEmoji = reactDB.find({self.dbStruct['db_collections']['emoji_fields']['name']: 'check'}, {'value': 1})[0][self.dbStruct['db_collections']['emoji_fields']['value']]
            crossEmoji = reactDB.find({self.dbStruct['db_collections']['emoji_fields']['name']: 'cross'}, {'value': 1})[0][self.dbStruct['db_collections']['emoji_fields']['value']]
            if self.hmwManagers[user].userAction == "idle":
                newMsg = None
                if str(reaction) == hmwEmojis[0][self.dbStruct['db_collections']['emoji_fields']['value']]:
                    # Adding a new homework
                    self.hmwManagers[user].updateUserAction(1)
                    newMsg = f"{user.mention} **- Ajout d'un nouveau devoir - Étape 1/{self.hmwManagers[user].getNbSubState()}**"
                    newMsg += f"\nVeuillez taper la commande suivante pour spécifier le nom du devoir\n`!nom NOM_DU_DEVOIR`"
                elif str(reaction) == hmwEmojis[1][self.dbStruct['db_collections']['emoji_fields']['value']]:
                    # Editing an existing homework
                    self.hmwManagers[user].updateUserAction(2)
                    newMsg = f"{user.mention} **- Édition d'un devoir - Étape 1/{self.hmwManagers[user].getNbSubState()}**"
                    newMsg += f"\n[TODO]"
                elif str(reaction) == hmwEmojis[2][self.dbStruct['db_collections']['emoji_fields']['value']]:
                    # Deleting an existing homework
                    self.hmwManagers[user].updateUserAction(3)
                    newMsg = f"{user.mention} **- Suppression d'un devoir - Étape 1/{self.hmwManagers[user].getNbSubState()}**"
                    newMsg += f"\n[TODO]"
                else:
                    # Something wrong happenned
                    print(f"User {user} reacted with reaction {reaction} while the manager was in the following state: {self.hmwManagers[user]}")
                    return
                if newMsg is not None:
                    botMsg = await reaction.message.channel.send(newMsg)
                    self.hmwManagers[user].updateBotMsg(botMsg.id)
            elif self.hmwManagers[user].userAction == "hmwAdd":
                if str(reaction) == checkEmoji:
                    # Homework creator will send a file to link
                    self.hmwManagers[user].fileAwaited = True
            elif self.hmwManagers[user].userAction == "hmwEdit":
                pass
            elif self.hmwManagers[user].userAction == "hmwDelete":
                pass

    homeworkDesc = """Commande permettant de manipuler les devoirs
    --> listage, ajout, modification, suppression"""
    @commands.command(description=homeworkDesc)
    async def devoir(self, ctx):
        dMsg = ctx.message

        # Get all homework with a deadline greater than the current time
        hmwDB = self.mDB[self.dbStruct['db_collections']['homework']]
        homeworks = hmwDB.find({self.dbStruct['db_collections']['homework_fields']['deadline']: {'$gte':datetime.datetime.now()}})

        # Get all emojis linked to this type of bot message
        reactDB = self.mDB[self.dbStruct['db_collections']['emoji']]
        hmwEmojis = reactDB.find({self.dbStruct['db_collections']['emoji_fields']['utility']: 'hmwConf'}, {'value': 1})

        # Formatting the listing homework message before sending it
        formatedHmwList = "```"
        for homework in homeworks:
            formatedHmwList += f"{homework[self.dbStruct['db_collections']['homework_fields']['deadline']].strftime('%d %B %Y')}\n\t- {homework[self.dbStruct['db_collections']['homework_fields']['subject']]} : devoir\n"
        formatedHmwList += "\n-----------------"
        formatedHmwList += "\nCliquez sur les réactions en-dessous du message pour interagir des façons suivantes:"
        formatedHmwList += f"\n\t{hmwEmojis[0][self.dbStruct['db_collections']['emoji_fields']['value']]} - Ajouter un devoir"
        formatedHmwList += f"\n\t{hmwEmojis[1][self.dbStruct['db_collections']['emoji_fields']['value']]} - Éditer un devoir"
        formatedHmwList += f"\n\t{hmwEmojis[2][self.dbStruct['db_collections']['emoji_fields']['value']]} - Supprimer un devoir"
        formatedHmwList += "\n```"

        # Sending the msg
        hmwListMsg  = await ctx.send(formatedHmwList)
        
        # Add managing reactions to it
        for hmwEmoji in hmwEmojis:
            await hmwListMsg.add_reaction(hmwEmoji[self.dbStruct['db_collections']['emoji_fields']['value']])
            await sleep(0.01)

        # Add the new message and its creator to a structure to keep track of possible changes
        self.hmwManagers[ctx.author] = HmwManager(ctx.author, hmwListMsg.id)

    hmwNameDesc = "Commande permettant de spécifier le nom d'un devoir.\nNe peut être utilisée que dans le cadre d'une manipulation d'un devoir"
    @commands.command(description=hmwNameDesc)
    async def nom(self, ctx, *args):
        if self.hmwManagers[ctx.author].checkNextAction('Name'):
            if len(args) >= 1:
                reactDB = self.mDB[self.dbStruct['db_collections']['emoji']]
                checkEmoji = reactDB.find({self.dbStruct['db_collections']['emoji_fields']['name']: 'check'}, {'value': 1})[0][self.dbStruct['db_collections']['emoji_fields']['value']]
                crossEmoji = reactDB.find({self.dbStruct['db_collections']['emoji_fields']['name']: 'cross'}, {'value': 1})[0][self.dbStruct['db_collections']['emoji_fields']['value']]

                self.hmwManagers[ctx.author].setHmw(args[0])
                botMsg = f"{ctx.author.mention}: Le nom {args[0]} a bien été enregistré"

                self.hmwManagers[ctx.author].updateActionState(0)
                botMsg += f"\n**Ajout d'un nouveau devoir - Étape 2/{self.hmwManagers[ctx.author].getNbSubState()}**"
                botMsg += f"\n- Si vous souhaitez lier un document à ce devoir: Veuillez cliquer sur la réaction {checkEmoji} au bas de ce message."
                botMsg += "\n\tLe prochain document que vous enverrez dans ce salon sera associé au devoir en cours d'enregistrement"
                botMsg += "\n- Sinon, précisez la date limite de dépôt du devoir avec la commande `!date DATE_LIMITE`"
                botMsg += "\n\t'DATE_LIMITE' doit être sous le format 'AAAA-MM-JJ'"
                newBotMsg = await ctx.channel.send(botMsg)

                # Add managing reactions to it
                await newBotMsg.add_reaction(checkEmoji)
                await sleep(0.01)
                await newBotMsg.add_reaction(crossEmoji)
                await sleep(0.01)

                self.hmwManagers[ctx.author].updateBotMsg(newBotMsg.id)
            else:
                await ctx.channel.send(f"{ctx.author.mention}: Veuillez fournir un nom au devoir à ajouter: `!nom NOM_DU_DEVOIR`")

    hmwDateDesc = "Commande permettant de spécifier la date limite d'un devoir.\nNe peut être utilisée que dans le cadre d'une manipulation d'un devoir"
    @commands.command(description=hmwDateDesc)
    async def date(self, ctx, *args):
        if self.hmwManagers[ctx.author].checkNextAction('Date'):
            if len(args) >= 1:
                try:
                    hmwDate = datetime.datetime.strptime(args[0], "%Y-%m-%d")
                    self.hmwManagers[ctx.author].homework.deadline = hmwDate
                    botMsg = f"{ctx.author.mention}: La date limite {hmwDate} a bien été enregistrée"

                    self.hmwManagers[ctx.author].updateActionState(1)
                    botMsg += f"\n**Ajout d'un nouveau devoir - Étape 3/{self.hmwManagers[ctx.author].getNbSubState()}**"
                    botMsg += "\nVeuillez préciser le statut du devoir avec la commande `!statut STATUT_DU_DEVOIR`"
                    newBotMsg = await ctx.channel.send(botMsg)
                    self.hmwManagers[ctx.author].updateBotMsg(newBotMsg.id)
                except ValueError as e:
                    await ctx.channel.send(f"{ctx.author.mention}: 'DATE_LIMITE' doit être au format 'AAAA-MM-JJ'")
            else:
                await ctx.channel.send(f"{ctx.author.mention}: Veuillez fournir une date au devoir à ajouter: `!date DATE_LIMITE`\n\t'DATE_LIMITE' doit être au format 'AAAA-MM-JJ'")

    hmwStatusDesc = "Commande permettant de spécifier le statut d'un devoir.\nNe peut être utilisée que dans le cadre d'une manipulation d'un devoir"
    @commands.command(description=hmwStatusDesc)
    async def statut(self, ctx, *args):
        if self.hmwManagers[ctx.author].checkNextAction('Status'):
            if len(args) >= 1:
                self.hmwManagers[ctx.author].homework.status = args[0]
                botMsg = f"{ctx.author.mention}: Le statut {args[0]} a bien été enregistré"

                self.hmwManagers[ctx.author].updateActionState(1)
                botMsg += f"\n**Ajout d'un nouveau devoir - Étape 4/{self.hmwManagers[ctx.author].getNbSubState()}**"
                botMsg += "\nVeuillez préciser la matière du devoir avec la commande `!matiere MATIERE_DU_DEVOIR`"
                newBotMsg = await ctx.channel.send(botMsg)
                self.hmwManagers[ctx.author].updateBotMsg(newBotMsg.id)
            else:
                await ctx.channel.send(f"{ctx.author.mention}: Veuillez fournir un statut au devoir à ajouter: `!statut STATUT_DU_DEVOIR`")

    hmwStatusDesc = "Commande permettant de spécifier la matière d'un devoir.\nNe peut être utilisée que dans le cadre d'une manipulation d'un devoir"
    @commands.command(description=hmwStatusDesc)
    async def matiere(self, ctx, *args):
        if self.hmwManagers[ctx.author].checkNextAction('Subject'):
            if len(args) >= 1:
                reactDB = self.mDB[self.dbStruct['db_collections']['emoji']]
                checkEmoji = reactDB.find({self.dbStruct['db_collections']['emoji_fields']['name']: 'check'}, {'value': 1})[0][self.dbStruct['db_collections']['emoji_fields']['value']]
                crossEmoji = reactDB.find({self.dbStruct['db_collections']['emoji_fields']['name']: 'cross'}, {'value': 1})[0][self.dbStruct['db_collections']['emoji_fields']['value']]

                self.hmwManagers[ctx.author].homework.subject = args[0]
                botMsg = f"{ctx.author.mention}: La matière {args[0]} a bien été enregistré"

                self.hmwManagers[ctx.author].updateActionState(1)
                botMsg += f"\n**Ajout d'un nouveau devoir - Récapitulatif :**"
                botMsg += f"\n{self.hmwManagers[ctx.author].homework}"

                if self.hmwManagers[ctx.author].fileAwaited and len(self.hmwManagers[ctx.author].homework.doc) < 1:
                    botMsg += "\nVous avez spécifié qu'un document devait être lié au devoir, mais aucun document n'a été reçu."
                    botMsg += "\nVeuillez glisser un document dans ce salon ou ignorez ce message pour valider l'ajout du document"

                botMsg += "\n\n Veuillez utiliser les réactions ci-dessous pour confirmer l'ajout de ce devoir"
                newBotMsg = await ctx.channel.send(botMsg)

                # Add managing reactions to it
                await newBotMsg.add_reaction(checkEmoji)
                await sleep(0.01)
                await newBotMsg.add_reaction(crossEmoji)
                await sleep(0.01)

                self.hmwManagers[ctx.author].updateBotMsg(newBotMsg.id)
            else:
                await ctx.channel.send(f"{ctx.author.mention}: Veuillez fournir une matière au devoir à ajouter: `!matiere MATIERE_DU_DEVOIR`")

def setup(schoolBot):
    schoolBot.add_cog(SchoolBot(schoolBot))