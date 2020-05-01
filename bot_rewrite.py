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
        print(e)
    except commands.ExtensionNotFound as e:
        print(f"Extension {extension} is not found")
        print(e)
    except commands.ExtensionFailed as e:
        print(f"Extension {extension} failed to load")
        print(e)
    except commands.NoEntryPointError as e:
        print(f"Extension {extension} can not be loaded")
        print(e)
    except commands.ExtensionAlreadyLoaded:
        pass

@schoolBot.command()
async def unload(ctx, extension):
    try:
        schoolBot.unload_extension(f'cogs.{extension}')
        print(f"Unloaded extension {extension}")
        print(e)
    except commands.ExtensionNotLoaded as e:
        print(f"Extension {extension} is not loaded")
        print(e)
    

@schoolBot.command()
async def reload(ctx, extension):
    try:
        schoolBot.reload_extension(f'cogs.{extension}')
        print(f"Reloaded extension {extension}")
    except commands.ExtensionNotLoaded as e:
        print(f"Extension {extension} is not loaded")
        print(e)
        try:
            schoolBot.load_extension(f'cogs.{extension}')
        except commands.ExtensionNotFound as e:
            print(f"Extension {extension} is not found")
            print(e)
        except commands.ExtensionFailed as e:
            print(f"Extension {extension} failed to load")
            print(e)
        except commands.NoEntryPointError as e:
            print(f"Extension {extension} can not be loaded")
            print(e)
        except commands.ExtensionAlreadyLoaded:
            pass
    except commands.ExtensionNotFound as e:
        print(f"Extension {extension} is not found")
        print(e)
    except commands.ExtensionFailed as e:
        print(f"Extension {extension} failed to load")
        print(e)
    except commands.NoEntryPointError as e:
        print(f"Extension {extension} can not be loaded")
        print(e)

#TEMP BECAUSE FAIGNASSE
@schoolBot.command()
async def q(ctx):
    try:
        await reload(ctx, 'schoolCog')
        await ctx.send("SchoolCog reloaded")
    except:
        await ctx.send("SchoolCog failed to reload")

# Automatic load at start of all COGs listed in folder './cogs'
for filename in os.listdir("cogs"):
    if filename.endswith('.py'):
        try:
            schoolBot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded extension {filename[:-3]}")
        except commands.ExtensionNotFound as e:
            print(f"Extension {filename[:-3]} is not found")
            print(e)
     #   except commands.ExtensionFailed as e:
     #       print(f"Extension {filename[:-3]} failed to load")
     #       print(e)
        except commands.NoEntryPointError as e:
            print(f"Extension {filename[:-3]} can not be loaded")
            print(e)

# print(", ".join(schoolBot.cogs.keys()))

with open("config/bot_token.json") as tokenFile:
    schoolBot.run(json.load(tokenFile)['TOKEN'])