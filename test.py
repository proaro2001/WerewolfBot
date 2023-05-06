BOT_TOKEN = "MTEwMzg3NDcyNjIwMTQwNTU4MA.GYTYnE.Kd71rBAZowAm76j77NycXEKsnV4Q04xzfJNlfs"
CHANNEL_ID = 1100690193012506635

from discord.ext import commands
from gtts import gTTS
from io import BytesIO
import discord
import random
import asyncio
import time

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


bot = commands.Bot(command_prefix=command_prefix, intents=intents)
event_called = False # bool value to check if /event executing, /end function turns it to false 

###############################################
@bot.event
async def on_ready():
    print("Werewolf Bot activated!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("WereWolf Bot activated!")

###############################################
@bot.command()
async def join(ctx):

     # Wait for reactions or messages to be added to the poll message
    def check(reaction, user):
        # The check function takes two parameters: reaction and user
        # It returns True if the reaction is the thumbs-up or stop emoji and the user is not the bot
        return str(reaction.emoji) in ["👍", "🚫"] and user != bot.user

    global event_called
    if event_called:
        print("Event called before")
        await ctx.send("Event command can only be called once. Please /end the previous event to start a new event")
        return

    # Define the poll message
    poll_message = "React with 👍 to join the game! Type 'stop' or react with 🚫 to stop joining."

    # Send the poll message to the channel
    poll = await ctx.send(poll_message)

    # Add the 👍 and 🚫 reactions to the poll message
    await poll.add_reaction("👍")
    await poll.add_reaction("🚫")

    # event has been called
    event_called = True

    while event_called:
            reaction, user = await bot.wait_for('reaction_add', check=check)
            if str(reaction.emoji) == "👍":
                await add_player(user)
                await ctx.send(f"{user.name} has joined the game!")
            elif str(reaction.emoji) == "🚫":
                await ctx.send(f"{user.name} has stopped joining the game.")
                
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
async def end(ctx):
    """
    End the event
    turn the global variable event_called to False
    """
    global event_called
    if not event_called:
        await ctx.send( "No event being hosted yet!" )
        return
    event_called = False
    await ctx.send( f"Names:\n{await get_name_list()}" )
    await clear()
    await ctx.send("Event Ended")

async def get_name_list():
    """
    return a name list of players in string
    """
    global players
    name_list = ''
    # name_list += (f"{i+1} :\t{players[i].name}\n" for i in range (0, len(players)) )
    name_list += ''.join(f"{i+1} :\t{players[i].name}\n" for i in range(0, len(players)))

    return name_list

async def clear():
    """
    clear the memory of GameState and players
    """
    global players, gameState
    players = []                    # empty the player list
    for key in gameState.keys():    # set all users to None again
        gameState[key] = None

###############################################
async def draw(user):
    """
    assign random role to the user
    """
    # draw role 
    # 1) get the user or user id who executing this command
    if not players or user not in players:
        print( "User didn't join event")
        await send_private_message( user, "Player didn't join event! Please Join the event to draw roles" )
        return
    # 2) assign player a random role
    role = await assign_random_role(user)
    print ( f"assigned {user} {role}" )
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
    random_num = random.randint( 0, len(remainding_role)-1 ) # get a random number
    random_role = remainding_role[random_num] # The role store in the gameState, :key
    user.death_status = False
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
    if user not in players:
        players.append( user )

async def remove_player ( user ):
    """remove player from a player list"""
    if user in players:
        players.remove( user )

###############################################
@bot.command()
async def play( ctx, game = "werewolf"):
    """"
    simulate playing werewolf
    """
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
    has_Potion = True
    has_Posion = True
    ###############################################
    async def wolfTurn():
        pass

    ###############################################
    async def switchTurn():
        pass

    ###############################################
    async def seerTurn():
        pass

    # extract info from players
    global players
    # if len(players) < 6:
    #     await ctx.send( f"Not enough player\nCurrent player:{len(players)}")

    # randomly assign role
    for user in players:
        await draw( user )

    # time to confirm their role and ability
    await ctx.send("The game is starting. You have 30 seconds to confirm your roles.", tts=True)
    time.sleep(15)
    await ctx.send( "15 seconds" )
    time.sleep(10)
    for i in range(10, 0, -1):
        await ctx.send( f"{i} seconds" )
        time.sleep(1)

    # Going Dark
    await ctx.send( "Alright, everyone. Please close your eyes and go back to sleep. It is now nighttime." , tts=True)
    time.sleep(5)
    # /say "Will the Werewolves please wake up and choose their target for the night?"
    time.sleep(5)
    # /say "Will the Witch please wake up and choose whether to use their potion or not?"
    time.sleep(5)
    # /say "Will the Seer please wake up and choose someone to check?"
    time.sleep(5)
    # /say "Will all players please wake up? It is now nighttime."
    time.sleep(5)
    # /say "Good morning, everyone. It appears that no one was killed last night. Please continue your discussion and try to identify the Werewolves."
    time.sleep(5)
    # /say "Good morning, everyone. Last night, [name of player] was killed. Please discuss and try to identify the Werewolves."
    time.sleep(5)
    # vote
    pass


if __name__ == '__main__':
    bot.run(BOT_TOKEN)

