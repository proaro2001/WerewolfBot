BOT_TOKEN = "MTEwMzg3NDcyNjIwMTQwNTU4MA.GYTYnE.Kd71rBAZowAm76j77NycXEKsnV4Q04xzfJNlfs"
CHANNEL_ID = 1100690193012506635

from discord.ext import commands
from gtts import gTTS
from io import BytesIO
import discord
import random
import asyncio

# declare variables
command_prefix = "/"                # what should the command start with
intents = discord.Intents.all()     # Intents to use all functions
players = []
# gameState ( temporary ), global variable
gameState = {
    # Village Team
    "Seer": None,
    "Witch": None,
    "Village1": None,
    "Village2": None,
    # Werewolf Team
    "Werewolf1": None,
    "Werewolf2": None
}
client = commands.Bot(command_prefix='/')
bot = commands.Bot(command_prefix=command_prefix, intents=intents)

@bot.event
async def on_ready():
    print("Werewolf Bot activated!")
    # trying to send a message in specific channel
    # channel ID is needed
    # not sure if we could create a new one and extract it's channel ID tho
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("WereWolf Bot activated!")

@bot.command()
async def join(ctx):
    # Define the poll message
    poll_message = "React with 👍 to join the game! Type 'stop' or react with 🚫 to stop joining."

    # Send the poll message to the channel
    poll = await ctx.send(poll_message)

    # Add the 👍 and 🚫 reactions to the poll message
    await poll.add_reaction("👍")
    await poll.add_reaction("🚫")

    # Wait for reactions or messages to be added to the poll message
    def check(reaction, user):
        # The check function takes two parameters: reaction and user
        # It returns True if the reaction is the thumbs-up or stop emoji and the user is not the bot
        return str(reaction.emoji) in ["👍", "🚫"] and user != bot.user

    # This loop waits for a reaction or message to be added to the poll message that meets the conditions in the check function
    join_ended = False
    while not join_ended:
        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            if str(reaction.emoji) == "👍":
                players.append(user)
                await ctx.send(f"{user.name} has joined the game!")
            elif str(reaction.emoji) == "🚫":
                await ctx.send(f"{user.name} has stopped joining the game.")
                join_ended = True
        except asyncio.TimeoutError:
            await ctx.send("Time's up! The join period has ended.")
            join_ended = True


@bot.command()
async def say(ctx, *, message):
    await ctx.send(message, tts=True)


###############################################
@bot.command()
async def end(ctx):
    await clear()

async def clear():
    """
    clear the memory of GameState and players
    """
    players.empty()                 # empty the player list
    for key in gameState.keys():    # set all users to None again
        gameState[key] = None

###############################################
@bot.command()
async def draw(ctx):
    # draw role 
    # 1) get the user or user id who executing this command
    user = ctx.author
    if not players or user not in players:
        print( "User didn't join event")
        await send_private_message( user, "Player didn't join event! Please Join the event to draw roles" )
        return
    # 2) assign player a random role
    await assign_random_role(user)
    print ( "assigned plyer a andom rol" )
    # 3) send private message to this player
    str_gameState = await getGameStateStr()
    await send_private_message( user,  str_gameState )

# assign random role to players
async def assign_random_role( user ):
    """
    Assign random role to user
    Check available spot and if the player joined the event
    """
    # get the list of remainding roles
    remainding_role = await get_remainding_role()
    # when no more role left
    if not remainding_role:
        print( "No more roles" ) # debug message
        await send_private_message(user, "No more seats")
        return
    # when user already exist
    if user in gameState.values():
        print( "Player already enrolled" )
        await send_private_message(user, "You already have a role")
        return
    # pick a random role 
    random_num = random.randint( 0, len(remainding_role) ) # get a random number
    random_role = remainding_role[random_num] # The role store in the gameState, :key
    gameState[random_role] = user

# helper method to get remainding roles 
async def get_remainding_role():
    """
    Return a list of remainding roles that are not being taken
    """
    remainding_role = []
    for role in gameState:
        if gameState[role] is None:
            remainding_role.append(role)
    return remainding_role

# helper method to send private message to user
async def send_private_message(user, message):
    dm_channel = await user.create_dm()
    await dm_channel.send(message)

async def getGameStateStr():
    """
    print the GameState in human readable format
    """
    gameStateStr = ''
    for key, value in gameState.items():
        gameStateStr += f"{key} : {value} \n"
    return gameStateStr
    # end of printGameState()

if __name__ == '__main__':
    bot.run(BOT_TOKEN)