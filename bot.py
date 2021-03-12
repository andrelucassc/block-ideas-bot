# bot.py
import os
from dotenv import load_dotenv

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

    await message.channel.send('Eu vi oq vc escreveu')

@client.event
async def on_message(message):
    if message.author == client.user:
        return None
    
    print('Boa noite mestre!')

    await message.channel.send('Por favor mande uma mensagem utilizando a sintaxe de comandos')


client.run(TOKEN)