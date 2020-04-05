import os
import discord
import asyncio

TOKEN = "Njg5MTg0MTU5MDcxMzM4NTAy.Xm_K3g.-NejIbWzgY9SNV5lUf5LQAMPc4s"
client = discord.Client()






"""
async def send_file_to_rec(channel_out, channel_in, message):
    try:
        list = message.attachments
        file = await list[0].to_file()
        await channel_out.send(content=f"{message.author.nick} : {message.content}", file=file)
        me = await client.get_user(122372446761254912)
        print(me)
        await client.send_message(me, "test")
        await message.delete()
        bot_msg = await channel_in.send(content=f"<@{message.author.id}>, le message a bien été envoyé")
        await asyncio.sleep(3)
        await bot_msg.delete()

    except Exception as e:
        if str(e) == "list index out of range":
            await channel_out.send(content=f"{message.author.nick} : {message.content}")
            await message.delete()
            bot_msg = await channel_in.send(content=f"<@{message.author.id}>, le message a bien été envoyé")
            await asyncio.sleep(3)
            await bot_msg.delete()
"""




@client.event
async def on_ready():
    print('logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #if client.private_channels:
    if message.content:
        print(message.author.id)
        print(client.get_user(message.author.id))
        await message.author.send("lol")
        """
        sarah = client.get_user(170267883182489600)
        await sarah.send("yo, c'est un test, envoi moi un message si tu l'as reçu (c'est sloth)")
        me = client.get_user(122372446761254912)
        await me.send("lol")
        """
    """
    channel_in = client.get_channel(message.channel.id)
    if message.channel.id == 689145093164498981:
        channel = client.get_channel(689149391738765332)
        await send_file_to_rec(channel, channel_in, message)
    elif message.channel.id == 689148224782598174:
        channel = client.get_channel(689149590540517438)
        await send_file_to_rec(channel, channel_in, message)
    """

client.run(TOKEN)