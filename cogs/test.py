import discord
from discord.ext import commands
from pymongo import MongoClient
import datetime
import json

class Example(commands.Cog):
    def __init__(self, schoolBot):
        super().__init__()
        self.schoolBot = schoolBot

        # Data about the mongo database used
        # Needs to have a predefined mongo database
        with open("source_sloth/config/dbStruct.json", "r") as dbConfig:
            self.dbStruct = json.load(dbConfig)

        # Connect and access to mongo database "schoolBot"
        self.mongoCli = MongoClient(self.dbStruct['db_address'], self.dbStruct['db_port'])
        self.mDB = self.mongoCli[self.dbStruct['db_name']]

        # # Access example to the collection 'homework' in database 'db'
        # devoirDB = db[dbStruct['db_collections']['homework']]
        # # Fake data were registered for test purpose
        # dateTest = datetime.datetime(2020, 4, 9)
        # devoirs = devoirDB.find({dbStruct['db_collections']['homework_fields']['deadline']:{'$gt':dateTest}}).sort([(dbStruct['db_collections']['homework_fields']['target'], 1)])
        # for dev in devoirs:
        #     print(dev)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.__class__.__name__} is online")

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong")

    homeworkDesc = """Fonction pour manipuler les devoirs
    --> listage, ajout, modification, suppression"""
    @commands.command(pass_context=True, description=homeworkDesc)
    async def devoir(self, ctx):
        dMsg = ctx.message

        # Connection to the homework database
        hmwDB = self.mDB[self.dbStruct['db_collections']['homework']]
        # Get all homework with a deadline greater than the current time
        homeworks = hmwDB.find({self.dbStruct['db_collections']['homework_fields']['deadline']: {'$gte':datetime.datetime.now()}})

        # Formatting the listing homework message before sending it
        formatedHmwList = "```"
        for homework in homeworks:
            formatedHmwList += f"{homework[self.dbStruct['db_collections']['homework_fields']['deadline']]}\n\t- {homework[self.dbStruct['db_collections']['homework_fields']['subject']]} : devoir\n"
        formatedHmwList += "```"

        # Sending the msg
        hmwListMsg  = await ctx.send(formatedHmwList)

        # TODO: Add Reactions to the message : add, edit, delete

def setup(schoolBot):
    schoolBot.add_cog(Example(schoolBot))