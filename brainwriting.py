import discord
from discord.ext import commands
import os

class Brainwriting(commands.Cog):
    """Category of Brainwriting"""
    def __init__(self):
        self.bool = True
        self.token = os.getenv('TOKEN') 

    def is_session_ok(self):
        return self.bool
    
    def kill_session(self):
        self.bool = False
        message = "Finalizando Sessão"
        return message

    def iniciar_sessao(self):
        #message = "Iniciando sessão de brainwriting. Preciso de algumas informações para iniciar:\nEm síntese, qual o problema estamos a resolver?"
        message = "Iniciando sessão de brainwriting."
        print(message)
        return message
    
    @commands.command(name='start', help='starts brainwriting session')
    async def startBrainwriting(self, ctx):
        await ctx.send(self.iniciar_sessao())
        guild = ctx.guild
        author = ctx.author.name

        client = discord.Client()

        @client.event
        async def on_message(message):

            if message.author == client.user:
                return None
            else:        
                database.put_message(message, connection)

        client.run(self.token)
    
    @commands.command(name='stop', help='stops brainwriting session')
    async def stopBrainwriting(self, ctx):
        await ctx.send(self.kill_session())
        guild = ctx.guild
        author = ctx.author.name

        await client.close()
        
