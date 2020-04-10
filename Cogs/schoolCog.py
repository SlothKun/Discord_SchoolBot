import discord
from discord.ext import commands
from pymongo import MongoClient
from asyncio import sleep
import datetime
import locale
import json

class hmwManager():
    def __init__(self, creator, botMsg):
        self.user = creator
        self.botMsg = botMsg
        self.userAction = None
        self.creationDate = datetime.datetime.now()

    def updateBotMsg(self, newBotMsg):
        self.botMsg = newBotMsg

    def updateUserAction(self, action):
        self.userAction = action


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
        with open("source_sloth/config/dbStruct.json", "r") as dbConfig:
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

    # Listen to all reactions added on msg on the server
    @commands.Cog.listener('on_reaction_add')
    async def manageReactions(self, reaction, user):
        for hManKey in self.hmwManagers:
            # Try to find if the creator of the new reaction corresponds to a message linked to a `!devoir` command
            if user == self.hmwManagers[hManKey].user and reaction.message.id == self.hmwManagers[hManKey].botMsg:
                await reaction.message.channel.send(f"User {user.mention} reacted with {reaction}")

    homeworkDesc = """Fonction pour manipuler les devoirs
    --> listage, ajout, modification, suppression"""
    @commands.command(pass_context=True, description=homeworkDesc)
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
        self.hmwManagers[ctx.author] = hmwManager(ctx.author, hmwListMsg.id) 

def setup(schoolBot):
    schoolBot.add_cog(SchoolBot(schoolBot))