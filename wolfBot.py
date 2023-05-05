BOT_TOKEN = "MTEwMzg3NDcyNjIwMTQwNTU4MA.GYTYnE.Kd71rBAZowAm76j77NycXEKsnV4Q04xzfJNlfs"
CHANNEL_ID = 1100690193012506635

from discord.ext import commands
import discord
import random

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
    """
    Creates a poll for users to join a game
    """
    # Define the poll message
    poll_message = "React with 👍 to join the game!"
    
    # Send the poll message to the channel
    poll = await ctx.send(poll_message)
    
    # Add the 👍 reaction to the poll message
    await poll.add_reaction("👍")
    
    # Wait for reactions to be added to the poll message
    def check(reaction, user):
        # The check function takes two parameters: reaction and user
        # It returns True if the reaction is the thumbs-up emoji and the user is not the bot
        return str(reaction.emoji) == "👍" and user != bot.user
    
    # Continuously wait for reactions to be added to the poll message
    while True:
        try:
            # Wait for a reaction that meets the conditions in the check function
            reaction, user = await bot.wait_for('reaction_add', check=check)
            # If the user is not already in the list of players, add them
            if user not in players:
                players.append(user)
                # Get the user's direct message ID and name in the channel
                dm_channel = await user.create_dm()
                dm_id = dm_channel.id
                username = user.display_name
                
                # Send a confirmation message to the user's direct message channel
                confirmation_message = f"Thanks for joining the game, {username}! Your direct message ID is {dm_id}."
                await dm_channel.send(confirmation_message)
                
                # Print debug messages
                print(f"{username} has joined the game!")
                print(f"Direct message ID: {dm_id}")
        except:
            # If an exception occurs, stop waiting for reactions and exit the loop
            break

@bot.command()
async def draw(ctx):
    # draw role 
    # 1) get the user or user id who executing this command
    user = ctx.author
    # 2) assign player a random role
    assign_random_role(user)
    # 3) send private message to this player
    await send_private_message( user,  gameState)

###############################################
#              helper methods
###############################################
# helper method to assign random role
async def assign_random_role( user ):
    # get the list of remainding roles
    remainding_role = get_remainding_role()
    # when no more role left
    if not remainding_role:
        print( "No more roles" ) # debug message
        send_private_message(user, "No more seats")
        return
    # when user already exist
    if user in gameState.values():
        print( "Player already enrolled" )
        send_private_message(user, "You already have a role")
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
        if gameState[role] is not None:
            remainding_role.append(role)
    return remainding_role

# helper method to send private message to user
async def send_private_message(user, message):
    dm_channel = await user.create_dm()
    await dm_channel.send(message)

if __name__ == '__main__':
    bot.run(BOT_TOKEN)

