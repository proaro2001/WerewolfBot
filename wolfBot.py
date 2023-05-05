BOT_TOKEN = "MTEwMzg3NDcyNjIwMTQwNTU4MA.GYTYnE.Kd71rBAZowAm76j77NycXEKsnV4Q04xzfJNlfs"
CHANNEL_ID = 1100690193012506635

from discord.ext import commands
import discord

# gameState ( temporary ), global variable
gameState = {
    """
    Role : User
    """
    # Village Team
    "Seer": None,
    "Witch": None,
    "Village1": None,
    "Village2": None,

    # Werewolf Team
    "Werewolf1": None,
    "Werewolf2": None
}

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
    # 2) send private message to this player
    await send_private_message( user, "Hi ")


###############################################
#              helper methods
###############################################

# helper method to send private message to user
async def send_private_message(user, message):
    dm_channel = await user.create_dm()
    await dm_channel.send(message)




if __name__ == '__main__':
    bot.run(BOT_TOKEN)

