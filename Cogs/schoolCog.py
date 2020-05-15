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

    RECEIVE_CATTEGORY_ID = "696433108899201155"

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

         # Subject colletion elements
        self.subCol = self.mDB[self.dbStruct['db_collections']['subject']]
        self.schoolSubject = []
        for sub in self.subCol.find({}, {self.dbStruct['db_collections']['subject_fields']["id"]: 0, self.dbStruct['db_collections']['subject_fields']["subjectName"]: 1}):
            self.schoolSubject.append(sub[self.dbStruct['db_collections']['subject_fields']["subjectName"]])
        # self.schoolSubject = ['mathématiques', 'spe-math','physique-chimie', 'si-mecanique', 'si-electronique', 'isn', 'svt', 'philo', 'anglais', 'espagnol', 'allemand', 'section-euro', ]

        # Channel collection elements
        chanDB = self.mDB[self.dbStruct['db_collections']['channel']]
        self.authorizedChan = []
        for chan in chanDB.find({self.dbStruct['db_collections']['channel_fields']['categoryID']: SchoolBot.RECEIVE_CATTEGORY_ID}):
            self.authorizedChan.append(chan[self.dbStruct['db_collections']['channel_fields']['channelID']])


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
    
    def userChanCheck(self, chanID):
        return str(chanID) in self.authorizedChan


    @commands.Cog.listener('on_message')
    async def messageListener(self, message):
        if message.author == self.schoolBot.user:
            return
        
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
                    newMsg = f"{message.author.mention}\n"
                    (msgBack, emojiList) = self.hmwManager.setHmwDoc(message.author.id, message.attachments)
                    newMsg += msgBack

                    if message.author in self.hmwChecker:
                        await self.hmwChecker[message.author]['botMsg'].delete()
                        message.delete()
                        # self.hmwChecker[message.author]['userMsgList'].append(message)

                    newBotMsg = await message.channel.send(newMsg)

                    if message.author in self.hmwChecker:
                        self.hmwChecker[message.author]['botMsg'] = newBotMsg

                    for emoji in emojiList:
                        await newBotMsg.add_reaction(emoji)
            else:
                await message.channel.send("Homework too old --> Has been deleted")
                pass
        else:
            # Casual talker, not configuring any homework at the moment
            pass
    
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
                    ######## Informing that a doc will be added to an homework
                    (msgBack, emojis) = self.hmwManager.setDocStatus(user.id)
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
                    (msgBack, emojis, chanID, hmwDocList) = self.hmwManager.insertNewDict(user.id, self.userRoleCheck(user.roles))
                    newMsg += msgBack

                    ######## Selecting the right text channel to send the homework documents
                    channel = reaction.message.channel.guild.get_channel(int(chanID))
                    for doc in hmwDocList:
                        docFile = await doc.to_file()
                        await channel.send(file = docFile)

                    hmwComplete = True

                elif str(reaction) in self.numberEmojis:
                    (msgBack, emojis) = self.hmwManager.correctSubVal(user.id, self.numberEmojis.index(str(reaction)))
                    newMsg += msgBack

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
        """Commande permettant de lister et manipuler les devoirs"""
        chanAuthorized = self.userChanCheck(ctx.message.channel.id)

        if chanAuthorized:
            userAuthorized = self.userRoleCheck(ctx.author.roles)
            (formatedHmwList, emojis) = self.hmwManager.listHmw(userAuthorized)
            
            # Sending the msg
            hmwListMsg  = await ctx.send(formatedHmwList)
            
            if userAuthorized:
                if chanAuthorized:
                    # Add managing reactions to it
                    for hmwEmoji in emojis:
                        await hmwListMsg.add_reaction(hmwEmoji)

                    self.hmwChecker[ctx.author] = {
                        'botMsg': hmwListMsg,
                        'userMsgList': [ctx.message]
                    }
            else:
                print(f"SCHOOLBOT - User not authorized")
        else:
            print(f"SCHOOLBOT - Channel not authorized")

    # @commands.command()
    # async def createSubject(self, ctx):
    #     print('\n')
    #     # subjectCol = self.mDB['matiere']
    #     chanCol = self.mDB['salon']
    #     # doc_cat_id = "696433109163573254"
    #     rec_cat_id = "696433108899201155"

    #     allCat = ctx.message.channel.guild.by_category()
    #     for cat in allCat:
    #         # if cat[0].id == int(doc_cat_id):
    #         if cat[0].id == int(rec_cat_id):
    #             for chan in cat[1]:
    #                 print(f"Treating channel {chan.name}")
    #                 if 'reception' in chan.name:
    #                     print(f"\t Treating... {chan.name[10:-2]}")
    #                     subjectRes = get_close_matches(chan.name[10:-1], self.schoolSubject, 1, 0.45)
    #                     if len(subjectRes) > 0:
    #                         subjectName = str(subjectRes[0])
    #                         print('\t' + subjectName)
    #                         # subDict = {
    #                         #     'subjectName': subjectName
    #                         # }
    #                         chanDict = {
    #                             'channelID': str(chan.id),
    #                             'channelName': str(chan.name),
    #                             'categoryID': rec_cat_id,
    #                             'categoryName': cat[0].name,
    #                             'subject': subjectName
    #                         }

    #                         # existingDBSub = subjectCol.find_one({'subjectName': subjectName}, {'_id': 0, 'subjectName': 1})['subjectName']
    #                         existingDBChan = chanCol.find_one({'channelID': str(chan.id)})
    #                         # if not existingDBSub:
    #                         #     subjectCol.insert_one(subDict)
    #                         #     await ctx.send(f"Creating subject '{subjectName}' automatically in DB")
    #                         if not existingDBChan:
    #                             print(f"Creating channel {chan.name}")
    #                             # chanCol.insert_one(chanDict)
    #                             # await ctx.send(f"Creating channel '{chan.name}' automatically in DB")
    #                             sleep(0.01)
    #                         else:
    #                             print(f"Channel {chan.name} already existing:\n{existingDBChan}")
    #                     else:
    #                         print(f"No subject for channel {chan.name}")
    #                         # await ctx.send(f"Subject not found for channel {chan.name}")
    #             break
            

def setup(schoolBot):
    schoolBot.add_cog(SchoolBot(schoolBot))
