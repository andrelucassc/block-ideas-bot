try:
    await text_chat.set_permissions(existing_brainrole, read_messages=True, send_messages=False)
except discord.InvalidData:
    print('data')
except discord.InvalidArgument:
    print('args')
except discord.LoginFailure:
    print('login')
except discord.ConnectionClosed:
    print('coms')
except discord.PrivilegedIntentsRequired:
    print('intents')
except discord.NoMoreItems:
    print('items?')
except discord.GatewayNotFound:
    print('gate')
except discord.Forbidden:
    print('forbids')
except discord.NotFound:
    print('found')
except discord.DiscordServerError:
    print('server error')