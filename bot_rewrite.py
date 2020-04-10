import discord
from discord.ext import commands
import os
import json

schoolBot = commands.Bot(command_prefix='!')

# Three functions to manage the COGs 
@schoolBot.command()
async def load(ctx, extension):
    try:
        schoolBot.load_extension(f'cogs.{extension}')
        print(f"Loaded extension {extension}")
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
        print(f"Unloaded extension {extension}")
    except commands.ExtensionNotLoaded as enl:
        print(f"Extension {extension} is not loaded")
    

@schoolBot.command()
async def reload(ctx, extension):
    try:
        schoolBot.reload_extension(f'cogs.{extension}')
        print(f"Reloaded extension {extension}")
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

# Automatic load at start of all COGs listed in folder './cogs'
for filename in os.listdir("source_sloth/cogs"):
    if filename.endswith('.py'):
        try:
            schoolBot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded extension {filename[:-3]}")
        except commands.ExtensionNotFound:
            print(f"Extension {filename[:-3]} is not found")
        except commands.ExtensionFailed:
            print(f"Extension {filename[:-3]} failed to load")
        except commands.NoEntryPointError:
            print(f"Extension {filename[:-3]} can not be loaded")

# print(", ".join(schoolBot.cogs.keys()))

with open("source_sloth/bot_token.json") as tokenFile:
    schoolBot.run(json.load(tokenFile)['TOKEN'])