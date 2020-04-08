import discord
import asyncio

TOKEN = "Njg5MTg0MTU5MDcxMzM4NTAy.Xm_K3g.-NejIbWzgY9SNV5lUf5LQAMPc4s" # ici le token

client = discord.Client() # l'objet de la lib

@client.event # Vérification de la connexion du bot
async def on_ready():
    print('logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message():








client.run(TOKEN)