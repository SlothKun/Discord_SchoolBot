import discord
from discord.ext import commands

from pymongo import MongoClient
from asyncio import sleep
from difflib import get_close_matches

import datetime
import locale
import json

from .cog_src.HomeworkManager import HomeworkManager
from .cog_src.Homework import Homework

class SchoolBot(commands.Cog):
    MAX_REACTION_TIME = 60 #60 seconds

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

        # Emojis element from DB
        reactDB = self.mDB[self.dbStruct['db_collections']['emoji']]

        utilityField = self.dbStruct['db_collections']['emoji_fields']['utility']
        idField = self.dbStruct['db_collections']['emoji_fields']['id']
        nameField = self.dbStruct['db_collections']['emoji_fields']['name']
        valueField = self.dbStruct['db_collections']['emoji_fields']['value']

        self.hmwManagementEmojis = {}
        self.hmwConfEmojis = {}
        self.numberEmojis = []

        self.hmwManagementEmojis["newHmwEmoji"] = reactDB.find_one({nameField: 'add'}, {idField: 0, valueField: 1})[valueField]
        self.hmwManagementEmojis["editHmwEmoji"] = reactDB.find_one({nameField: 'edit'}, {idField: 0, valueField: 1})[valueField]
        self.hmwManagementEmojis["delHmwEmoji"] = reactDB.find_one({nameField: 'delete'}, {idField: 0, valueField: 1})[valueField]

        self.hmwConfEmojis["checkEmoji"] = reactDB.find_one({nameField: 'check'}, {idField: 0, valueField: 1})[valueField]
        self.hmwConfEmojis["crossEmoji"] = reactDB.find_one({nameField: 'cross'}, {idField: 0, valueField: 1})[valueField]
        self.hmwConfEmojis["backEmoji"] = reactDB.find_one({nameField: 'back'}, {idField: 0, valueField: 1})[valueField]
        self.hmwConfEmojis["validHmwEmoji"] = reactDB.find_one({nameField: 'confModif'}, {idField: 0, valueField: 1})[valueField]

        for numberEmoji in reactDB.find({utilityField: 'number'}, {idField: 0, nameField:1, valueField:1}):
            self.numberEmojis.append(numberEmoji[valueField])

        # self.schoolSubject = ['mathématiques', 'spe-math','physique-chimie', 'si-mecanique', 'si-electronique', 'isn', 'svt', 'philo', 'anglais', 'espagnol', 'allemand', 'section-euro', ]


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.__class__.__name__} is online")

    def userRoleCheck(self, userRoles):
        roleCol = self.mDB[self.dbStruct['db_collections']['role']]
        
        idField = self.dbStruct['db_collections']['role_fields']['id']
        discordIDField = self.dbStruct['db_collections']['role_fields']['discordID']
        botAuthField = self.dbStruct['db_collections']['role_fields']['authorized']

        botAuthorizedRoles = roleCol.find({botAuthField: True}, {idField: 0, discordIDField: 1})

        for authRole in botAuthorizedRoles:
            for userRole in userRoles:
                if userRole.id == int(authRole[discordIDField]):
                    return True
        return False


    @commands.Cog.listener('on_message')
    async def messageListener(self, message):
        if message.author == self.schoolBot.user:
            return

        # docMatChannelID = int(self.mDB['salon'].find_one({'subject': 'mathématiques'}, {'_id': 0, 'channelID': 1})['channelID'])
        # docMatChannel = message.channel.guild.get_channel(docMatChannelID)

        

        if len(message.attachments) > 0:
            # for att in message.attachments:
            #     attFile = await att.to_file()
            #     await message.delete()
            #     await docMatChannel.send(file=attFile)
            pass
        
        if self.userRoleCheck(message.author.roles) and self.hmwManager.checkHmw(message.author.id, message.channel.id):
            # User have previously created an Homework object and is writing in the same channel
            if self.hmwManager.checkHmwValidity(message.author.id):
                # User's created Homework object is still valid
                if len(message.attachments) == 0:
                    [resMsg, emojiList] = self.hmwManager.updateHmw(message.author.id, message.content)
                    if resMsg is not None:
                        newMsg = f"{message.author.mention}\n"
                        newMsg += resMsg

                        if message.author in self.hmwChecker:
                            await self.hmwChecker[message.author]['botMsg'].delete()
                            self.hmwChecker[message.author]['userMsgList'].append(message)

                        newBotMsg = await message.channel.send(newMsg)

                        if message.author in self.hmwChecker:
                            self.hmwChecker[message.author]['botMsg'] = newBotMsg

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
        if self.userRoleCheck(user.roles) and user in self.hmwChecker and reaction.message.id == self.hmwChecker[user]['botMsg'].id:
            reactionDate = datetime.datetime.utcnow()
            reacTime = (reactionDate - reaction.message.created_at).total_seconds()
            if  reacTime < SchoolBot.MAX_REACTION_TIME:
                # User reacted within MAX_REACTION_TIME seconds

                newMsg = f"{user.mention}\n"
                emojis = []
                userAction = None
                hmwComplete = False

                if str(reaction) == self.hmwManagementEmojis["newHmwEmoji"]:
                    ######## Adding a new homework
                    userAction = "Ajout"
                    newMsg += self.hmwManager.newHmw(user.id, 0, reaction.message.channel.id, reaction.message.id)
                    emojis.append(self.hmwConfEmojis["crossEmoji"])

                elif str(reaction) == self.hmwManagementEmojis["editHmwEmoji"]:
                    ######## Editing an existing homework
                    userAction = "Édition"
                    #TODO: À COMPLÉTER
                    await reaction.message.channel.send("Edition mode is not implemented yet")

                elif str(reaction) == self.hmwManagementEmojis["delHmwEmoji"]:
                    ######## Deleting an existing homework
                    userAction = "Suppression"
                    #TODO: À COMPLÉTER
                    await reaction.message.channel.send("Deletion mode is not implemented yet")

                elif str(reaction) == self.hmwConfEmojis["checkEmoji"]:
                    ######## Adding a doc to an homework
                    (msgBack, emojis) = self.hmwManager.setDoc(user.id)
                    newMsg += msgBack

                elif str(reaction) == self.hmwConfEmojis["crossEmoji"]:
                    ######## Cancel homework creation
                    if self.hmwManager.deleteHmw(user.id, reaction.message.channel.id):
                        newMsg += "Devoir en cours de création a été supprimé"
                        del self.hmwChecker[user]

                elif str(reaction) == self.hmwConfEmojis["backEmoji"]:
                    ######## Cancel last modification
                    (msgBack, emojis) = self.hmwManager.updateHmw(user.id, None, True)
                    newMsg += msgBack

                elif str(reaction) == self.hmwConfEmojis["validHmwEmoji"]:
                    ######## Validate new homework and send it to the database
                    hmwDB = self.mDB[self.dbStruct['db_collections']['homework']]

                    hmwDateField = self.dbStruct['db_collections']['homework_fields']['deadline']
                    hmwSubjectField = self.dbStruct['db_collections']['homework_fields']['subject']
                    hmwNameField = self.dbStruct['db_collections']['homework_fields']['name']

                    homeworks = hmwDB.find({hmwDateField: {'$gte':datetime.datetime.now()}})

                    (msgBack, emojis) = self.hmwManager.insertNewDict(user.id, self.userRoleCheck(user.roles))
                    newMsg += msgBack

                    hmwComplete = True

                elif str(reaction) in self.numberEmojis:
                    (msgBack, emojis) = self.hmwManager.userVote(user.id, self.numberEmojis.index(str(reaction)))
                    newMsg += msgBack
                    #TODO: GÉRER LES EMOJIS À CHIFFRE POUR LA SELECTION DE CHOIX MATIERE POSSIBLE
                    #TODO: GERER L'AJOUT DE FICHER ET LES ASSOCIER AUX DEVOIRS + LES POUSSER VERS LE SALON APPROPRIÉ

                if newMsg is not None:
                    ######## Sending the new message to the channel + deleting old message
                    if user in self.hmwChecker:
                        await self.hmwChecker[user]['botMsg'].delete()
                        if hmwComplete and self.hmwManager.deleteHmw(user.id, reaction.message.channel.id):
                            for userMsg in self.hmwChecker[user]['userMsgList']:
                                await userMsg.delete()
                            del self.hmwChecker[user]

                    botMsg = await reaction.message.channel.send(newMsg)

                    if user in self.hmwChecker:
                        self.hmwChecker[user]['botMsg'] = botMsg

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
        userAuthorized = self.userRoleCheck(ctx.author.roles)
        (formatedHmwList, emojis) = self.hmwManager.listHmw(userAuthorized)
        
        # Sending the msg
        hmwListMsg  = await ctx.send(formatedHmwList)
        
        if userAuthorized:
            # Add managing reactions to it
            for hmwEmoji in emojis:
                await hmwListMsg.add_reaction(hmwEmoji)

            self.hmwChecker[ctx.author] = {
                'botMsg': hmwListMsg,
                'userMsgList': [ctx.message]
            }

    # @commands.command()
    # async def createSubject(self, ctx):
    #     # print('\n')
    #     subjectCol = self.mDB['matiere']
    #     chanCol = self.mDB['salon']
    #     doc_cat_id = "696433109163573254"

    #     allCat = ctx.message.channel.guild.by_category()
    #     for cat in allCat:
    #         if cat[0].id == int(doc_cat_id):
    #             for chan in cat[1]:
    #                 # print(f"Treating channel {chan.name}")
    #                 subjectRes = get_close_matches(chan.name[4:-1], self.schoolSubject, 1, 0.45)
    #                 if len(subjectRes) > 0:
    #                     subjectName = str(subjectRes[0])
    #                     # print('\t' + subjectName)
    #                     subDict = {
    #                         'subjectName': subjectName
    #                     }
    #                     chanDict = {
    #                         'channelID': str(chan.id),
    #                         'channelName': str(chan.name),
    #                         'categoryID': doc_cat_id,
    #                         'categoryName': cat[0].name,
    #                         'subject': subjectName
    #                     }

    #                     existingDBSub = subjectCol.find_one({'subjectName': subjectName}, {'_id': 0, 'subjectName': 1})['subjectName']
    #                     existingDBChan = chanCol.find_one({'channelID': str(chan.id)}, {'_id': 0, 'channelID': 1})['channelID']
    #                     if not existingDBSub:
    #                         subjectCol.insert_one(subDict)
    #                         await ctx.send(f"Creating subject '{subjectName}' automatically in DB")
    #                     if not existingDBChan:
    #                         chanCol.insert_one(chanDict)
    #                         await ctx.send(f"Creating channel '{chan.name}' automatically in DB")
    #                 else:
    #                     await ctx.send(f"Subject not found for channel {chan.name}")
    #             break
            

def setup(schoolBot):
    schoolBot.add_cog(SchoolBot(schoolBot))
