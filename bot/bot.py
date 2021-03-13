# bot.py
import os
from dotenv import load_dotenv

from functions import create_session
#import constant

import discord
from discord.ext import commands

#### Constants ####

mensagem_inicio = """
Vamos começar a sessão de Brainstorming!
""" 

mensagem_fim = """
A sessão foi finalizada! Muito obrigado!
"""

mensagem_bemvindo = """
Seja bem vindo a área de teste do projeto de TCC!
Author: André
"""

mensagem_avoid_block = """
Foi detectado uma mensagem que não está de acordo com as políticas da sessão de brainstorming!
"""

mensagem_confuso = """
Não entendi muito bem o que você quiz dizer!
"""

#### Fim Constants ####

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
    elif message.content == "start":
        create_session(message)
    else:        
        await message.channel.send(mensagem_confuso)
        await message.channel.send('https://media1.tenor.com/images/a9dd93dc3a2ad34c621b079b397c389d/tenor.gif?itemid=15745451')

    
    

client.run(TOKEN)