# admin.py

from discord.ext import commands

@bot.command(name='create_channel', help='internal use only')
@commands.has_role('admin')
async def create_channel(ctx, channel_name = 'chat'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name+'_1')
    existing_category = discord.utils.get(guild.categories, name='Brainwriting')
    existing_brainrole = discord.utils.get(guild.roles, name='Brainwriting')
    print(existing_brainrole.name)
    number_of_members = ctx.guild.member_count
    
    # Creating chats
    number_static_members = 2
    number_of_chats = number_of_members - number_static_members
    if not existing_category:
        await guild.create_category_channel('Brainwriting')
    for chat_number in range(1,number_of_chats+1):
        if not existing_channel:
            print(f'Creating a new role: {channel_name}_{chat_number}')
            user_role = await guild.create_role(name=channel_name+'_'+str(chat_number))

            print(f'Creating a new channel: {channel_name}_{chat_number}')
            text_chat = await guild.create_text_channel(channel_name+'_'+str(chat_number), category=existing_category)
            
            await text_chat.set_permissions(user_role, read_messages=True, send_messages=True)
            await text_chat.set_permissions(guild.default_role, read_messages=False, send_messages=False)
        else:
            print(f'{channel_name}_{chat_number} already exists.')
    
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
            
@bot.command(name='delete_channel', help='internal use only')
@commands.has_role('admin')
async def delete_channel(ctx):
    print('executing delete channel')
    guild = ctx.guild
    roles = await guild.fetch_roles()
    for role in roles:
        if role.name == '@everyone':
            pass
        elif role.name == 'Block Ideas':
            pass
        elif role.name == 'Block Hubot':
            pass
        else:
            try:
                print(f'deleting {role.name}')
                await role.delete()
            except:
                await ctx.send(f'it was not possible to delete the role {role.name}')
    print('creating default roles')
    admin = await guild.create_role(name='admin', colour=discord.Colour.gold())
    await guild.create_role(name='Bot', colour=discord.Colour.blue())
    await guild.create_role(name='Brainwriting', colour=discord.Colour.purple())
    try:
        members = await guild.fetch_members()
    except discord.ClientException:
        print('The members intent is not enabled.')
    except discord.HTTPException:
        print('Getting the members failed.')
    for member in members:
        print(member.name)

    #await me.add_roles(admin)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(f'Error, executing command')
