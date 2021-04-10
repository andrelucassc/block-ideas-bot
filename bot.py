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
from metrics import Metrics

# Logging Things
logging.basicConfig(filename='bot.log', level=logging.INFO)
log = logging.getLogger('bot')

# Discord Things
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
discord.VoiceClient.warn_nacl = False

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

bot.add_cog(Brainwriting())
log.info("Cog loaded: Brainwriting")
bot.add_cog(Admin())
log.info("Cog loaded: Admin")
bot.add_cog(Metrics())
log.info("Cog loaded: Metrics")
bot.run(TOKEN)