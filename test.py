BOT_TOKEN = "MTEwMzg3NDcyNjIwMTQwNTU4MA.GYTYnE.Kd71rBAZowAm76j77NycXEKsnV4Q04xzfJNlfs"
CHANNEL_ID = 1100690193012506635

from discord.ext import commands
from gtts import gTTS
from io import BytesIO
import discord
import random
import asyncio

###############################################
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
# client = commands.Bot(command_prefix='/')
bot = commands.Bot(command_prefix=command_prefix, intents=intents)
event_called = False # bool value to check if /event executing, /end function turns it to false 

###############################################
@bot.event
async def on_ready():
    print("Werewolf Bot activated!")
    # trying to send a message in specific channel
    # channel ID is needed
    # not sure if we could create a new one and extract it's channel ID tho
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("WereWolf Bot activated!")

###############################################
@bot.command()
async def event(ctx, event_title, event_time, event_location, *note):

    async def add_reaction_to_msg( msg, reactions=["👍","👎"] ):
        """
        add reactions to a message

        :param msg: the message to add reactions with
        :param reactions: list of reactions to be added with default value "👍","👎"
        """
        for emoji in reactions:
            await msg.add_reaction(emoji)

    async def get_note(*note):
        """extract message from note"""
        note_str = ''
        for str in note:
            note_str += str + ' '
        return note_str
    
    global event_called
    if event_called:
        print("Event called before")
        await ctx.send("Event command can only be called once. Please /end the previous event to start a new event")
        return
    
    # note message
    note_str = await get_note(*note)   

    # Define the poll message
    poll_message = f"```Event:\t\t{event_title}\nTime:\t\t {event_time}\nLocation:\t {event_location}\nNote:\t\t {note_str}```"

    # Send the poll message to the channel
    poll = await ctx.send(poll_message)

    # add reaction to the message with defaul value
    await add_reaction_to_msg(poll)

    # set event being called
    event_called = True

    

    


###############################################
@bot.command()
async def say(ctx, *, message):
    """
    Robot start speaking for words in the message
    """
    await ctx.send(message, tts=True)

###############################################
@bot.command()
async def end(ctx):
    """
    End the event
    turn the global variable event_called to False
    """
    global event_called
    event_called = False

    await clear()
    ctx.send("Event Ended")

async def clear():
    """
    clear the memory of GameState and players
    """
    global players, gameState
    players = []                    # empty the player list
    for key in gameState.keys():    # set all users to None again
        gameState[key] = None

###############################################
@bot.command()
async def draw(ctx):
    """
    assign random role to the user
    """
    # draw role 
    # 1) get the user or user id who executing this command
    user = ctx.author
    if not players or user not in players:
        print( "User didn't join event")
        await send_private_message( user, "Player didn't join event! Please Join the event to draw roles" )
        return
    # 2) assign player a random role
    role = await assign_random_role(user)
    print ( "assigned plyer a andom rol" )
    # 3) send private message to this player
    if role != None:
        await send_private_message( user,  role )
    # debug message
    str_gameState = await getGameStateStr()
    print( str_gameState )

# assign random role to players
async def assign_random_role( user ):
    """
    Assign random role to user
    Check available spot and if the player joined the event

    :param user:            user = ctx.author
    :return random_role:    string
    """
    # get the list of remainding roles
    remainding_role = await get_remainding_role()
    # when no more role left
    if not remainding_role:
        print( "No more roles" ) # debug message
        await send_private_message(user, "No more seats")
        return None
    # when user already exist
    if user in gameState.values():
        print( "Player already enrolled" )
        await send_private_message(user, "You already have a role")
        return None
    # pick a random role 
    random_num = random.randint( 0, len(remainding_role) ) # get a random number
    random_role = remainding_role[random_num] # The role store in the gameState, :key
    gameState[random_role] = user
    return random_role

# helper method to get remainding roles 
async def get_remainding_role():
    """
    Return a list of remainding roles that are not being taken

    :return random_role: string
    """
    remainding_role = []
    for role in gameState:
        if gameState[role] is None:
            remainding_role.append(role)
    return remainding_role

###############################################

async def send_private_message(user, message):
    """
    send private message to specified user

    :param user: user = ctx.author
    :param massage: string
    """
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

async def add_player ( user ):
    """add user to player list"""
    players.append( user )

async def remove_player ( user ):
    """remove player from a player list"""
    players.remove( user )

###############################################
@bot.event
async def on_disconnect():
    pass

if __name__ == '__main__':
    bot.run(BOT_TOKEN)