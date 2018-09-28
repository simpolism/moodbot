# Work with Python 3.6
import discord
from secrets import TOKEN

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # delete messages <200 char in messages
    if message.channel.id == 396014169784057858:
        if len(message.content) < 200:
            try:
                await client.delete_message(message)
            except discord.Forbidden:
                print "ERROR: not permissioned to delete message"
    
    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
