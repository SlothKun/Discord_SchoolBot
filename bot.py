import discord
from discord.ext import commands
import os
import json

schoolBot = commands.Bot(command_prefix='!')


@schoolBot.event
async def on_ready():
    await schoolBot.change_presence(activity=discord.Game("J'envoi des devoirs, mais surtout de l'amour ❤"))
    print('logged in as')
    print(schoolBot.user.name)
    print(schoolBot.user.id)
    print('------')

DELETE_TIME = 2

# Three functions to manage the COGs 
@schoolBot.command()
async def load(ctx, extension):
    """Commande '!load [nom_extension]' : permet d'ajouter une extension"""
    try:
        schoolBot.load_extension(f'Cogs.{extension}')
        print(f"Loaded extension {extension}")
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
    """Commande '!unload [nom_extension]' : permet de retirer une extension"""
    try:
        schoolBot.unload_extension(f'Cogs.{extension}')
        print(f"Unloaded extension {extension}")
    except commands.ExtensionNotLoaded as e:
        print(f"Extension {extension} is not loaded")
        print(e)
    

@schoolBot.command()
async def reload(ctx, extension):
    """Commande '!reload [nom_extension]' : permet de recharger une extension"""
    try:
        schoolBot.reload_extension(f'Cogs.{extension}')
        print(f"Reloaded extension {extension}")
    except commands.ExtensionNotLoaded as e:
        print(f"Extension {extension} is not loaded")
        print(e)
        try:
            schoolBot.load_extension(f'Cogs.{extension}')
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

#TEMP BECAUSE
@schoolBot.command()
async def q(ctx):
    """Commande '!q' : permet de recharger automatiquement l'extension 'schoolCog'"""
    try:
        await reload(ctx, 'schoolCog')
        await ctx.send("SchoolCog reloaded", delete_after = DELETE_TIME)
    except:
        await ctx.send("SchoolCog failed to reload", delete_after = DELETE_TIME)
    await ctx.message.delete()

# Automatic load at start of all COGs listed in folder './cogs'
for filename in os.listdir("Cogs/"):
    if filename.endswith('.py'):
        try:
            schoolBot.load_extension(f'Cogs.{filename[:-3]}')
            print(f"Loaded extension {filename[:-3]}")
        except commands.ExtensionNotFound as e:
            print(f"Extension {filename[:-3]} is not found")
            print(e)
        except commands.ExtensionFailed as e:
           print(f"Extension {filename[:-3]} failed to load")
           print(e)
        except commands.NoEntryPointError as e:
            print(f"Extension {filename[:-3]} can not be loaded")
            print(e)

# print(", ".join(schoolBot.cogs.keys()))

with open("Config/Bot_Token.json") as tokenFile:
    schoolBot.run(json.load(tokenFile)['TOKEN'])
