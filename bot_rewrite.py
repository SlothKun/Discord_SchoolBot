import discord
from discord.ext import commands
import os
from pymongo import MongoClient
import datetime
import json

TOKEN = "Njg5MTg0MTU5MDcxMzM4NTAy.Xm_K3g.-NejIbWzgY9SNV5lUf5LQAMPc4s"

schoolBot = commands.Bot(command_prefix='!')

# Data about the mongo database used
# Needs to have a predefined mongo database
with open("source_sloth/config/dbStruct.json", "r") as dbConfig:
    dbStruct = json.load(dbConfig)

# Connect and access to mongo database "schoolBot"
mongoCli = MongoClient(dbStruct['db_address'], dbStruct['db_port'])
db = mongoCli[dbStruct['db_name']]

# Access example to the collection called "devoir" in database "schoolBot"
devoirDB = db[dbStruct['db_collections']['homework']]
# Getting back all "devoir" corresponding to the "subject" = "math"
# Fake data were registered for test purpose
dateTest = datetime.datetime(2020, 4, 9)
devoirs = devoirDB.find({dbStruct['db_collections']['homework_fields']['deadline']:{'$gt':dateTest}}).sort([(dbStruct['db_collections']['homework_fields']['target'], 1)])
for dev in devoirs:
    print(dev)

# Three functions to manage the COGs 
@schoolBot.command()
async def load(ctx, extension):
    try:
        schoolBot.load_extension(f'cogs.{extension}')
    except commands.ExtensionNotFound:
        print(f"Extension {extension} is not found")
    except commands.ExtensionFailed:
        print(f"Extension {extension} failed to load")
    except commands.NoEntryPointError:
        print(f"Extension {extension} can not be loaded")
    except commands.ExtensionAlreadyLoaded:
        pass

@schoolBot.command()
async def unload(ctx, extension):
    try:
        schoolBot.unload_extension(f'cogs.{extension}')
    except commands.ExtensionNotLoaded as enl:
        print(f"Extension {extension} is not loaded")
    

@schoolBot.command()
async def reload(ctx, extension):
    try:
        schoolBot.reload_extension(f'cogs.{extension}')
    except commands.ExtensionNotLoaded as enl:
        print(f"Extension {extension} is not loaded")
        try:
            schoolBot.load_extension(f'cogs.{extension}')
        except commands.ExtensionNotFound:
            print(f"Extension {extension} is not found")
        except commands.ExtensionFailed:
            print(f"Extension {extension} failed to load")
        except commands.NoEntryPointError:
            print(f"Extension {extension} can not be loaded")
        except commands.ExtensionAlreadyLoaded:
            pass
    except commands.ExtensionNotFound as enl:
        print(f"Extension {extension} is not found")
    except commands.ExtensionFailed:
        print(f"Extension {extension} failed to load")
    except commands.NoEntryPointError as enl:
        print(f"Extension {extension} can not be loaded")

# Automatic load of all COGs listed in folder './cogs'
for filename in os.listdir("source_sloth/cogs"):
    if filename.endswith('.py'):
        try:
            schoolBot.load_extension(f'cogs.{filename[:-3]}')
        except commands.ExtensionNotFound:
            print(f"Extension {filename[:-3]} is not found")
        except commands.ExtensionFailed:
            print(f"Extension {filename[:-3]} failed to load")
        except commands.NoEntryPointError:
            print(f"Extension {filename[:-3]} can not be loaded")

# print(", ".join(schoolBot.cogs.keys()))

# schoolBot.run(TOKEN)