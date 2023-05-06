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
bot = commands.Bot(command_prefix=command_prefix, intents=intents)
event_called = False # bool value to check if /event executing, /end function turns it to false 
emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]

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
                players.append(user)
                await ctx.send(f"{user.name} has joined the game!")
            elif str(reaction.emoji) == "🚫":
                await ctx.send(f"{user.name} has stopped joining the game.")
                
###############################################

###############################################

async def send_private_message(user, message):
    """
    send private message to specified user

    :param user: user = ctx.author
    :param massage: string
    """
    dm_channel = await user.create_dm()
    await dm_channel.send(message)

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
    global players
    # players = []
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
    # Witch bool
    has_heal_Potion = True
    has_posion_potion = True
    seat_num = 1           # seat number
    ###############################################
    async def getGameStateStr():
        """
        print the GameState in human readable format
        """
        gameStateStr = ''
        for key, value in gameState.items():
            gameStateStr += f"{key} : {value} \n"
        return gameStateStr
    
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

    # assign random role to players
    async def assign_random_role( user ):
        """
        Assign random role to user
        Check available spot and if the player joined the event
        assume len(players) == total_users

        :param user:            user = ctx.author
        :return random_role:    string
        """
        # get the list of remainding roles
        remainding_role = await get_remainding_role()

        # pick a random role 
        random_num = random.randint( 0, len(remainding_role)-1 ) # get a random number
        random_role = remainding_role[random_num] # The role store in the gameState, :key
        seat_num = seat_num
        gameState[random_role] = {user, False, seat_num}
        seat_num += 1   # update seat_num
        return random_role
    
    async def draw(user):
        """
        assign random role for all users who has a seat
        """
        # 1) assign player a random role
        role = await assign_random_role(user)
        print ( f"assigned {user.name} {role}" )
        # 3) send private message to this player
        if role != None:
            await send_private_message( user,  f"Your role is {role[0]}" )
        # debug message
        str_gameState = await getGameStateStr()
        print( str_gameState )
    


    ###############################################
    async def wolfTurn():
        werewolf_list = [userState for key, userState in gameState.items() if key.startswith("werewolf")]
        werewolfVoter = werewolf_list[0]
        user = werewolf_list[0]
        # voice message
        await ctx.send(f"Werewolf, please wake up", tts=True)

        poll_message = f"Please select a player to kill"
        dm_channel = await user.create_dm()
        poll = await dm_channel.send(poll_message)
        
        global emojis
        for emo in emojis:
            await poll.add_reaction(emo)
        
        reaction, user = await bot.wait_for('reaction_add')
        if user != bot.user and str(reaction.emoji) in emojis:
            chosen_player = None

            for player in gameState.value:
                if emojis[player[2]] == reaction.emoji:
                    chosen_player = player
                    break

            if chosen_player is None:
                await ctx.send("Error: couldn't find player with chosen emoji")
                return
            
            chosen_player[1] = True
        
        await ctx.send(f"Ok I got it, please close your eyes", tts=True)
        return


    ###############################################
    async def witchTurn():
        witch = gameState["Witch"]
        msg = "Witch, please wake up"
        await ctx.send(msg, tts = True)
        time.sleep(5)

        async def use_heal( ):
            # find who die tonight
            theDeath = None
            for user in players:
                if user.death_status:
                    theDeath = user
                    break
                
            witch_dm = await witch.create_dm()  # create dm with witch
            msg = f"Do you want to use heal potion for {theDeath.seat_number}?\nPress 👍 for YES\nPress 🚫 for NO"
            private_msg = witch_dm.send(msg)       # the message send to the witch
            await private_msg.add_reaction("👍")
            await private_msg.add_reaction("🚫")

            def check( reaction, user ):
                return user == witch and str(reaction.emoji) in ["👍", "🚫"] and user != bot.user
            
            while True:
                reaction, _ = await bot.wait_for("reaction_add", check=check)
                if str(reaction.emoji) == "👍":
                    theDeath.death_status = True
                elif str(reaction.emoji) == "🚫":
                    pass      
                  
        async def use_posion():
            witch_dm = await witch.create_dm()  # create dm with witch
            poll_message = f"Do you want to use poison ?\nPlease select a player number"
            dm_channel = await witch_dm.create_dm()
            poll = await dm_channel.send(poll_message)

            for emo in emojis:
                await poll.add_reaction(emo)
            
            reaction, user = await bot.wait_for('reaction_add')
            if user != bot.user and str(reaction.emoji) in emojis:
                chosen_player = None

                for player in gameState.value:
                    if emojis[player[2]] == reaction.emoji:
                        chosen_player = player
                        break

                if chosen_player is None:
                    await ctx.send("Error: couldn't find player with chosen emoji")
                    return
                
                chosen_player[1] = True

        await ctx.send(f"Ok I got it, please close your eyes", tts=True)
        return
            
        
    ###############################################
    async def seerTurn():
        seer = gameState["Seer"]
        msg = "Seer, please wake up"
        await ctx.send(msg, tts = True)
        time.sleep(5)

        async def see_role():
            seer = await seer.create_dm()  # create dm with witch
            poll_message = f"Which player's role you want to check?\nPlease select a player number"
            dm_channel = await seer.create_dm()
            poll = await dm_channel.send(poll_message)

            for emo in emojis:
               await poll.add_reaction(emo)
            
            reaction, seer = await bot.wait_for('reaction_add')
            if seer != bot.user and str(reaction.emoji) in emojis:
                chosen_player = None

                for player in gameState.value:
                    if emojis[player[2]] == reaction.emoji:
                        chosen_player = player
                        break

                if chosen_player is None:
                    await ctx.send("Error: couldn't find player with chosen emoji")
                    return
                
                # show the chosen player role
                if(chosen_player.role == "bad"):
                    msg = f"His/Her role is Bad"
                elif(chosen_player.role == "good"):
                    msg = f"His/Her role is Good"
                await dm_channel.send(msg)

        await ctx.send(f"Ok Seer, please close your eyes", tts=True)
        return
        
        
    ###############################################

    # extract info from players
    # if len(players) < 6:
    #     await ctx.send( f"Not enough player\nCurrent player:{len(players)}")
    #     return

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
    # /say "Will all players please wake up? It is now daytime."
    time.sleep(5)
    # /say "Good morning, everyone. It appears that no one was killed last night. Please continue your discussion and try to identify the Werewolves."
    time.sleep(5)
    # /say "Good morning, everyone. Last night, [name of player] was killed. Please discuss and try to identify the Werewolves."
    time.sleep(5)
    # vote
    pass

# vote
# kick the player out the map when he died

if __name__ == '__main__':
    bot.run(BOT_TOKEN)

