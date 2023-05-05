BOT_TOKEN = "MTEwMzg3NDcyNjIwMTQwNTU4MA.GYTYnE.Kd71rBAZowAm76j77NycXEKsnV4Q04xzfJNlfs"
CHANNEL_ID = 1100690193012506635

from discord.ext import commands
import discord

# declare variables
command_prefix = "/"                # what should the command start with
intents = discord.Intents.all()     # Intents to use all functions

bot = commands.Bot(command_prefix=command_prefix, intents=intents)

@bot.event
async def on_ready():
    print("Werewolf Bot activated!")
    # trying to send a message in specific channel
    # channel ID is needed
    # not sure if we could create a new one and extract it's channel ID tho
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Study Bot activated! (Test)")

@bot.command()
async def draw(ctx):
    # draw role 
    # 1) get the user or user id who executing this command
    user = ctx.author
    user_id = user.id

    # 2) send private message to this player
    send_private_message( user, "Hi This is private message test")

async def send_private_message(user, message):
    dm_channel = await user.create_dm()
    await dm_channel.send(message)

if __name__ == '__main__':
    bot.run(BOT_TOKEN)