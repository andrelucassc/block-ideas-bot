# admin.py
from discord.ext import commands
import discord
import logging
from database import Database
import datetime

# Logging Things
log = logging.getLogger('admin')

class Admin(commands.Cog):
    """Admin Commands - Internal Use Only"""
    def __init__(self):
        self.default_roles = ['admin', 'Bot', 'Brainwriting']
        self.default_bots = ['Block Hubot', 'Block Ideas']
        self.number_static_members = 2
        
    @commands.command(name='deletar_cargos', help='ADMIN: !deletar_cargos - deleta cargos do servidor')
    @commands.has_role('admin')
    async def delete_roles(self, ctx):
        """Delete the Roles from the Guild that do not involve the defaults"""
        guild = ctx.guild
        roles = await guild.fetch_roles()
        log.info(f'deleting roles from {guild.name}')
        for role in roles:
            if role.name == '@everyone':
                pass
            elif role.name in self.default_roles:
                pass
            elif role.name in self.default_bots:
                pass
            else:
                try:
                    log.info(f'deleting {role.name}')
                    await role.delete()
                except:
                    await ctx.send(f'it was not possible to delete the role {role.name}')

    @commands.command(name='criar_cargos', help='ADMIN: !iniciar_cargos - Cria cargos do servidor')
    @commands.has_role('admin')
    async def create_roles(self, ctx):
        """Creates the default roles: admin, Bot and Brainwriting"""
        guild = ctx.guild

        existing_object_roles = await guild.fetch_roles()
        existing_roles = []
        for role in existing_object_roles:
            existing_roles.append(role.name)

        missing_roles = [role for role in self.default_roles if role not in existing_roles]

        log.info(f'CREATE_ROLES: creating default roles')
        log.debug(f'CREATE_ROLES: default roles: {self.default_roles}')
        log.debug(f'CREATE_ROLES: missing roles: {missing_roles}')
        log.debug(f'CREATE_ROLES: existing roles: {existing_roles}')
        for role in missing_roles:
            try:
                await guild.create_role(name=role, colour=discord.Colour.gold())
            except:
                await ctx.send(f'not possible to create {role} role')      

    @commands.command(name='criar_canais', help='ADMIN: !criar_canais [nome_chat] [N°_pessoas]:padrão=3')
    @commands.has_role('admin')
    async def create_channel(self, ctx, channel_name = 'chat', participantes=3):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name+'_1')
        existing_category = discord.utils.get(guild.categories, name=channel_name)
        existing_role = discord.utils.get(guild.roles, name=channel_name+'_1')
        botRole = discord.utils.get(guild.roles, name='Bot')
        brainwritingRole = discord.utils.get(guild.roles, name='Brainwriting')

        log.info('executing create_channel\n')
        number_of_members = ctx.guild.member_count
        log.debug(f'Number of Members in Server: {number_of_members}')

        await ctx.send(f'Criando chats. Membros do Servidor: {number_of_members}. Participantes: {participantes}')

        number_of_chats = participantes

        if not existing_category:
            category = await guild.create_category_channel(channel_name)
        else:
            category = existing_category

        for chat_number in range(1,number_of_chats+1):
            if not existing_channel:
                log.debug(f'Creating a new role: {channel_name}_{chat_number}')
                user_role = await guild.create_role(name=channel_name+'_'+str(chat_number))

                log.debug(f'Creating a new channel: {channel_name}_{chat_number}')
                text_chat = await guild.create_text_channel(channel_name+'_'+str(chat_number), category=category)
                
                await text_chat.set_permissions(user_role, read_messages=True, send_messages=True)
                await text_chat.set_permissions(guild.default_role, read_messages=False, send_messages=False)
            else:
                log.error(f'{channel_name}_{chat_number} already exists.')
        
        counter = 1
        for member in guild.members:
            if brainwritingRole in member.roles:
                role = discord.utils.get(guild.roles, name=channel_name+'_'+str(counter))
                log.debug(f'add role {role.name} to member {member.name}')
                await member.add_roles(role)
                counter += 1

    @commands.command(name='deletar_canais', help='ADMIN: !deletar_canais [nome_chat] [N°_pessoas]:padrão=3')
    @commands.has_role('admin')
    async def delete_channel(self, ctx, channel_name = 'chat', participantes=2):
        log.info('executing delete channel')
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name+'_1')
        existing_category = discord.utils.get(guild.categories, name=channel_name)

        roles = await guild.fetch_roles()
        botRole = discord.utils.get(guild.roles, name='Bot')
        brainwritingRole = discord.utils.get(guild.roles, name='Brainwriting')
        
        for role in roles:
            if role.is_default() == False and role.name not in self.default_roles and role.name not in self.default_bots: #is_default=@everyone
                try:
                    log.debug(f'deleting {role.name}')
                    await role.delete()
                except:
                    log.warning(f'delete Error the role {role.name}')

        for member in guild.members:
            if brainwritingRole in member.roles:
                for role in member.roles:
                    if role.is_default() == False and role.name not in self.default_roles and role.name not in self.default_bots:
                        try:
                            await member.remove_roles(role)
                        except:
                            log.error(f'remove ERROR the role {role.name} from {member.name}')
        
        number_of_members = ctx.guild.member_count
        number_of_chats = participantes

        if existing_channel:
            for chat_number in range(1, number_of_chats+1):
                log.debug(f'deleting chat {channel_name}_{str(chat_number)}')
                chat = discord.utils.get(guild.channels, name=channel_name+'_'+str(chat_number))    
                await chat.delete()

        if existing_category:
            log.debug(f'deleting category {existing_category.name}')
            await existing_category.delete()
            await ctx.send('Processo Concluído')
    
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            ctx.send("Argumento não aceito pelo bot.")
