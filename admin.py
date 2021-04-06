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
        
    @commands.command(name='delete_roles', help='ADMIN: delete the roles created')
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

    @commands.command(name='create_roles', help='ADMIN: creates the default roles to the channel')
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

    @commands.command(name='create_channel', help='ADMIN: creates chats based on number of members')
    @commands.has_role('admin')
    async def create_channel(self, ctx, channel_name = 'chat', fixed_members=2):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name+'_1')
        existing_category = discord.utils.get(guild.categories, name=channel_name)
        existing_role = discord.utils.get(guild.roles, name=channel_name+'_1')
        botRole = discord.utils.get(guild.roles, name='Bot')

        log.info('executing create_channel\n')
        number_of_members = ctx.guild.member_count
        log.info(f'Number of Members: {number_of_members}')

        number_static_members = fixed_members
        number_of_chats = number_of_members - number_static_members

        if not existing_category:
            category = await guild.create_category_channel(channel_name)
        else:
            category = existing_category

        for chat_number in range(1,number_of_chats+1):
            if not existing_channel:
                log.info(f'Creating a new role: {channel_name}_{chat_number}')
                user_role = await guild.create_role(name=channel_name+'_'+str(chat_number))

                log.info(f'Creating a new channel: {channel_name}_{chat_number}')
                text_chat = await guild.create_text_channel(channel_name+'_'+str(chat_number), category=category)
                
                await text_chat.set_permissions(user_role, read_messages=True, send_messages=True)
                await text_chat.set_permissions(guild.default_role, read_messages=False, send_messages=False)
            else:
                log.error(f'{channel_name}_{chat_number} already exists.')
        
        counter = 1
        for member in guild.members:
            if botRole not in member.roles:
                role = discord.utils.get(guild.roles, name=channel_name+'_'+str(counter))
                log.info(f'add role {role.name} to member {member.name}')
                await member.add_roles(role)
                counter += 1

        """
        TODO: Externalize member output to chats
        counter = 0
        roles = await guild.fetch_roles()
        async for member in guild.fetch_members():
            if 'Bot' in member.roles:
                pass
            else:
                role = filter(role.name == 'chat_'+str(counter),roles)
                print(f'putting {role.name} on {member.name}')
                await member.add_roles(role)

                counter = counter + 1
        """ 

    @commands.command(name='delete_channel', help='ADMIN: deleta os canais de texto')
    @commands.has_role('admin')
    async def delete_channel(self, ctx, channel_name = 'chat', fixed_members=2):
        log.info('executing delete channel')
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name+'_1')
        existing_category = discord.utils.get(guild.categories, name=channel_name)

        roles = await guild.fetch_roles()
        botRole = discord.utils.get(guild.roles, name='Bot')
        
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
                    log.error(f'it was not possible to delete the role {role.name}')

        for member in guild.members:
            if botRole not in member.roles:
                for role in member.roles:
                    if role.name in self.default_roles:
                        pass
                    elif role.name in self.default_bots:
                        pass
                    else:
                        try:
                            await member.remove_roles(role)
                        except:
                            log.error(f'not possible to remove the role {role.name}')
        
        number_of_members = ctx.guild.member_count
        number_of_chats = number_of_members - fixed_members

        if existing_channel:
            for chat_number in range(1, number_of_chats+1):
                log.info(f'deleting chat {channel_name}_{str(chat_number)}')
                chat = discord.utils.get(guild.channels, name=channel_name+'_'+str(chat_number))    
                await chat.delete()

        if existing_category:
            log.info(f'deleting category {existing_category.name}')
            await existing_category.delete()
