# bot.py
import os
from dotenv import load_dotenv

#from functions import create_session
import constants

import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_connect():
    print('connected\n')

@client.event
async def on_ready():
    print('ready\n')

@client.event
async def on_disconnect():
    print('disconnected\n')

@client.event
async def on_message_delete(message):
    print('eu vi oq você escreveu')

    #await message.channel.send('Eu vi oq vc escreveu')

@client.event
async def on_message(message):

    if message.author == client.user:
        return None
    elif message.content == "start":
        print(mensagem_inicio)
        await message.channel.send(mensagem_inicio)
    else:        
        await message.channel.send(constants.mensagem_confuso)
        await message.channel.send('https://media1.tenor.com/images/a9dd93dc3a2ad34c621b079b397c389d/tenor.gif?itemid=15745451')

    
    

client.run(TOKEN)