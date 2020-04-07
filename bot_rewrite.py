import discord
from discord.ext import commands
import os

TOKEN = "Njg5MTg0MTU5MDcxMzM4NTAy.Xm_K3g.-NejIbWzgY9SNV5lUf5LQAMPc4s"

client = commands.Bot(command_prefix='!')

@client.command()
async def load(ctx, extension):
    try:
        client.load_extension(f'cogs.{extension}')
    except commands.ExtensionNotFound:
        print(f"Extension {extension} is not found")
    except commands.ExtensionFailed:
        print(f"Extension {extension} failed to load")
    except commands.NoEntryPointError:
        print(f"Extension {extension} can not be loaded")
    except commands.ExtensionAlreadyLoaded:
        pass

@client.command()
async def unload(ctx, extension):
    try:
        client.unload_extension(f'cogs.{extension}')
    except commands.ExtensionNotLoaded as enl:
        print(f"Extension {extension} is not loaded")
    

@client.command()
async def reload(ctx, extension):
    try:
        client.reload_extension(f'cogs.{extension}')
    except commands.ExtensionNotLoaded as enl:
        print(f"Extension {extension} is not loaded")
        try:
            client.load_extension(f'cogs.{extension}')
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

for filename in os.listdir("./cogs"):
    if filename.endswith('.py'):
        try:
            client.load_extension(f'cogs.{filename[:-3]}')
        except commands.ExtensionNotFound:
            print(f"Extension {filename[:-3]} is not found")
        except commands.ExtensionFailed:
            print(f"Extension {filename[:-3]} failed to load")
        except commands.NoEntryPointError:
            print(f"Extension {filename[:-3]} can not be loaded")

# print(", ".join(client.cogs.keys()))

client.run(TOKEN)