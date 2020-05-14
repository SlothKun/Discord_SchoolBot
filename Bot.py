from discord.ext import commands
import discord
import os
import json

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("J'envoi des devoirs, mais surtout de l'amour ❤"))
    print('logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def load(ctx, extension):
    try:
        bot.load_extension(f'Cogs.{extension}')
        print(f"Extension {extension} loaded")
    except commands.ExtensionNotFound:
        print(f"Extension {extension} is not found")
    except commands.ExtensionFailed:
        print(f"Extension {extension} failed to load")
    except commands.NoEntryPointError:
        print(f"Extension {extension} can not be loaded")
    except commands.ExtensionAlreadyLoaded:
        pass

@bot.command()
async def unload(ctx, extension):
    try:
        bot.unload_extension(f'Cogs.{extension}')
    except commands.ExtensionNotLoaded as enl:
        print(f"Extension {extension} is not loaded")

@bot.command()
async def reload(ctx, extension):
    try:
        bot.reload_extension(f'Cogs.{extension}')
    except commands.ExtensionNotLoaded as enl:
        print(f"Extension {extension} is not loaded")
        try:
            bot.load_extension(f'Cogs.{extension}')
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

for filename in os.listdir("Cogs/"):
    if filename.endswith('.py'):
        try:

            bot.load_extension(f'Cogs.{filename[:-3]}')
            print(f'Cogs.{filename[:-3]} loaded')
        except commands.ExtensionNotFound:
            print(f"Extension {filename[:-3]} is not found")
        except commands.ExtensionFailed:
            print(f"Extension {filename[:-3]} failed to load")
        except commands.NoEntryPointError:
            print(f"Extension {filename[:-3]} can not be loaded")

with open("Config/Bot_Token.json") as tokenFile:
    bot.run(json.load(tokenFile)['TOKEN'])