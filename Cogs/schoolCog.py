import discord
from discord.ext import commands

from pymongo import MongoClient
from asyncio import sleep
import datetime
import locale
import json

from .cog_src.HomeworkManager import HomeworkManager
from .cog_src.Homework import Homework

class SchoolBot(commands.Cog):
    def __init__(self, schoolBot):
        super().__init__()
        self.schoolBot = schoolBot

        # Set time elements in french
        locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

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

        # Homework manager
        # Will keep track of all homeworks currently attended
        self.hmwManager = HomeworkManager(self.dbStruct, self.mDB)
        # Dict to keep track of people accessing the hmw
        self.hmwChecker = {}


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.__class__.__name__} is online")

    @commands.Cog.listener('on_message')
    async def messageListener(self, message):
        if message.author == self.schoolBot.user:
            return
        
        if self.hmwManager.checkHmw(message.author.id, message.channel.id):
            # User have previously created an Homework object and is writing in the same channel
            if self.hmwManager.checkHmwValidity(message.author.id):
                # User's created Homework object is still valid
                if len(message.attachments) == 0:
                    [resMsg, emojiList] = self.hmwManager.updateHmw(message.author.id, message.content)
                    if resMsg is not None:
                        newMsg = f"{message.author.mention}\n"
                        newMsg += resMsg

                        newBotMsg = await message.channel.send(newMsg)

                        if message.author in self.hmwChecker:
                            self.hmwChecker[message.author] = newBotMsg

                        for emoji in emojiList:
                            await newBotMsg.add_reaction(emoji)
                    else:
                        print("SCHOOLBOT - HOMEWORK_MAN updateHmw() returned None")
                else:
                    # Message contains a file
                    await message.channel.send("Message contains a file")
                    if self.hmwManager.checkHmwFileStatus(message.author.id):
                        # File awaited --> must be added
                        pass
                    else:
                        await message.channel.send("Homework doesn't wait for a file")
            else:
                await message.channel.send("Homework too old --> Has been deleted")
                pass
        else:
            # Casual talker, not configuring any homework at the moment
            pass
    #     if message.author in self.hmwManagers and len(message.attachments) > 0:
    #         # Detect if a file has been uploaded and if the uploader is currently trying to manage some homeworks
    #         # TODO: Take care to only add file for people who ask of it !
    #         if self.hmwManagers[message.author].fileAwaited:
    #             # Check if the uploader notified that a file will be linked to his homework
    #             hmwFiles = message.attachments
    #             for hmwFile in hmwFiles:
    #                 newFile = hmwFile.to_file()
    #                 self.hmwManagers[message.author].homework.addFiles(newFile)
    #                 await message.channel.send(f"Le fichier {hmwFile.filename} a été associé au devoir {self.hmwManagers[message.author].homework.name}")
    #             self.hmwManagers[message.author].fileAwaited = False
    #         else:
    #             await message.channel.send(f"{message.author.mention}: Vous n'avez pas notifié l'ajout d'un fichier pour le devoir {self.hmwManagers[message.author].homework.name}.\nLe fichier joint n'a été associé à aucun devoir.")

    # Listen to all reactions added on msg on the server
    @commands.Cog.listener('on_reaction_add')
    async def reactionListener(self, reaction, user):
        ## IGNORE BOT REACTIONS
        if user == self.schoolBot.user:
            return

        ## HOMEWORK REACTION MANAGEMENT
        if user in self.hmwChecker and reaction.message.id == self.hmwChecker[user].id:
            reactionDate = datetime.datetime.utcnow()
            reacTime = (reactionDate - reaction.message.created_at).total_seconds()
            if  reacTime < 15:
                # User reacted within 15 seconds
                print(f"Reaction: {str(reaction)}")
                # Emojis element from DB
                reactDB = self.mDB[self.dbStruct['db_collections']['emoji']]

                utilityField = self.dbStruct['db_collections']['emoji_fields']['utility']
                idField = self.dbStruct['db_collections']['emoji_fields']['id']
                nameField = self.dbStruct['db_collections']['emoji_fields']['name']
                valueField = self.dbStruct['db_collections']['emoji_fields']['value']

                newHmwEmoji = reactDB.find({nameField: 'add'}, {idField: 0, valueField: 1})[0][valueField]
                editHmwEmoji = reactDB.find({nameField: 'edit'}, {idField: 0, valueField: 1})
                delHmwEmoji = reactDB.find({nameField: 'delete'}, {idField: 0, valueField: 1})

                checkEmoji = reactDB.find({nameField: 'check'}, {idField: 0, valueField: 1})[0][valueField]
                crossEmoji = reactDB.find({nameField: 'cross'}, {idField: 0, valueField: 1})[0][valueField]
                backEmoji = reactDB.find({nameField: 'back'}, {idField: 0, valueField: 1})[0][valueField]
                validHmwEmoji = reactDB.find({nameField: 'confModif'}, {idField: 0, valueField: 1})[0][valueField]

                newMsg = f"{user.mention}\n"
                emojis = []
                userAction = None

                if str(reaction) == newHmwEmoji:
                    ######## Adding a new homework
                    userAction = "Ajout"
                    newMsg += self.hmwManager.newHmw(user.id, 0, reaction.message.channel.id, reaction.message.id)
                    emojis.append(crossEmoji)

                elif str(reaction) == editHmwEmoji:
                    ######## Editing an existing homework
                    userAction = "Édition"
                    #TODO: À COMPLÉTER
                    await reaction.message.channel.send("Edition mode is not implemented yet")

                elif str(reaction) == delHmwEmoji:
                    ######## Deleting an existing homework
                    userAction = "Suppression"
                    #TODO: À COMPLÉTER
                    await reaction.message.channel.send("Deletion mode is not implemented yet")

                elif str(reaction) == checkEmoji:
                    ######## Adding a doc to an homework
                    (msgBack, emojis) = self.hmwManager.setDoc(user.id)
                    newMsg += msgBack

                elif str(reaction) == crossEmoji:
                    ######## Cancel homework creation
                    if self.hmwManager.deleteHmw(user.id, reaction.message.channel.id):
                        newMsg += "Devoir en cours de création a été supprimé"
                        del self.hmwChecker[user]

                elif str(reaction) == backEmoji:
                    ######## Cancel last modification
                    (msgBack, emojis) = self.hmwManager.updateHmw(user.id, None, True)
                    newMsg += msgBack

                elif str(reaction) == validHmwEmoji:
                    ######## Validate new homework and send it to the database
                    hmwDB = self.mDB[self.dbStruct['db_collections']['homework']]

                    hmwDateField = self.dbStruct['db_collections']['homework_fields']['deadline']
                    hmwSubjectField = self.dbStruct['db_collections']['homework_fields']['subject']
                    hmwNameField = self.dbStruct['db_collections']['homework_fields']['name']

                    homeworks = hmwDB.find({hmwDateField: {'$gte':datetime.datetime.now()}})

                    (hmwDict, msgBack, emojis) = self.hmwManager.getHmwDict(user.id)
                    insertRes = hmwDB.insert_one(hmwDict)
                    newMsg += msgBack

                    if self.hmwManager.deleteHmw(user.id, reaction.message.channel.id):
                        del self.hmwChecker[user]

                if newMsg is not None:
                    botMsg = await reaction.message.channel.send(newMsg)

                    if user in self.hmwChecker:
                        self.hmwChecker[user] = botMsg

                    for emoji in emojis:
                        await botMsg.add_reaction(emoji)
            else:
                # Over 15 seconds
                if reacTime > 120:
                    # Over 2 minutes
                    print("Deleting hmw")
                    self.hmwManager.deleteHmw(user.id, reaction.message.channel.id)
                    del self.hmwChecker[user]
                    return
        else:
            # User who reacted to the message didn't create any homework
            print(f"No homework corresponding to user {user}")
            pass

    homeworkDesc = """Commande permettant de manipuler les devoirs
    --> listage, ajout, modification, suppression"""
    @commands.command(description=homeworkDesc, name='homework', aliases=['devoir', 'hmw', 'devoirs'])
    async def hmwList(self, ctx):
        (formatedHmwList, emojis) = self.hmwManager.listHmw()
        
        # Sending the msg
        hmwListMsg  = await ctx.send(formatedHmwList)
        
        # Add managing reactions to it
        for hmwEmoji in emojis:
            await hmwListMsg.add_reaction(hmwEmoji)

        self.hmwChecker[ctx.author] = hmwListMsg

def setup(schoolBot):
    schoolBot.add_cog(SchoolBot(schoolBot))
