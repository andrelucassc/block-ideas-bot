# bot.py
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Logging
import logging

# Modules
from brainwriting import Brainwriting
from admin import Admin
from database import *
from constants import *

# Mongo Things
database = Database()
#connection = database.get_connection()

# Logging Things
logging.basicConfig(filename='bot.log', level=logging.DEBUG)
log = logging.getLogger('bot')

# Discord Things
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#client = discord.Client()
intents = discord.Intents.default()
intents.members = True

help_command = commands.DefaultHelpCommand(no_category = 'no category')

bot = commands.Bot(command_prefix='!', help_command=help_command, intents=intents)

@bot.event
async def on_ready():
    print('Bot Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-----------')

""" @client.event
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
 """

bot.add_cog(Brainwriting())
log.info("Cog loaded: Brainwriting")
bot.add_cog(Admin())
log.info("Cog loaded: Admin")
bot.run(TOKEN)