BOT_TOKEN = "MTEwMzg3NDcyNjIwMTQwNTU4MA.GYTYnE.Kd71rBAZowAm76j77NycXEKsnV4Q04xzfJNlfs"
CHANNEL_ID = 1100690193012506635

from discord.ext import commands
import discord

# declare variables
command_prefix = "/"                # what should the command start with
intents = discord.Intents.all()     # Intents to use all functions
players = []

bot = commands.Bot(command_prefix=command_prefix, intents=intents)

@bot.event
async def on_ready():
    print("Werewolf Bot activated!")
    # trying to send a message in specific channel
    # channel ID is needed
    # not sure if we could create a new one and extract it's channel ID tho
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("WereWolf Bot ")

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

    

if __name__ == '__main__':
    bot.run(BOT_TOKEN)