# bot.py
import os
from dotenv import load_dotenv

#from functions import create_session
from constants import *

import discord
from discord.ext import commands

from database import *
from brainwriting import Brainwriting

# Mongo Things
database = Database()
#connection = database.get_connection()

# Discord Things
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
intents = discord.Intents.default()
intents.members = True

help_command = commands.DefaultHelpCommand(no_category = 'Admin')

bot = commands.Bot(command_prefix='!', help_command=help_command, intents=intents)

@bot.event
async def on_ready():
    print('Bot Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-----------')

@client.event
async def on_message(message):

    if message.author == client.user:
        return None
    elif message.content == "test":
        brain_session = BrainSession()
        await message.channel.send(brain_session.iniciar_sessao())
        database.put_message(message, connection)
    elif message.content == "insert":
        #database.put_message(message, connection)
        return None
    else:        
        database.put_message(message, connection)
        #await message.channel.send(mensagem_confuso)
        #await message.channel.send('https://media1.tenor.com/images/a9dd93dc3a2ad34c621b079b397c389d/tenor.gif?itemid=15745451')

bot.add_cog(Brainwriting())
bot.run(TOKEN)