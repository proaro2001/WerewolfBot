BOT_TOKEN = 'MTEwMDY4NjU0NTI5MzQyNjcyOQ.GKM2w7._2J3UQPMEviS2ttphJ6jPIfqKU2qgWowJPOP3s'
CHANNEL_ID = 1100690193012506635

"""
BOT_TOKEN:  Pass code to use the discord bot
CHANNEL_ID: The channel id to send message
"""

from discord.ext import commands
import discord

# declare variables
command_prefix = "/"                # what should the command start with
intents = discord.Intents.all()     # Intents to use all functions

bot = commands.Bot(command_prefix=command_prefix, intents=intents)

@bot.event
async def on_ready():
    print("Study Bot activated!")

    # trying to send a message in specific channel
    # channel ID is needed
    # not sure if we could create a new one and extract it's channel ID tho
    channel = bot.get_channel(CHANNEL_ID)
    # await channel.send("Study Bot activated! (Test)")

@bot.command()
async def hello (ctx):
    """
        ctx -> context
        In Discord, type "your command_prefix + function name"
        In this hello example with prefix == '!'
        Discord: /hello
    """
    await ctx.send("hello!")

@bot.command()
async def add(ctx, x, y):
    result = int(x) + int(y)
    await ctx.send(f"{x} + {y} = {result}")

@bot.command()
async def addALL(ctx, *arr):
    """
        *arr is an array of argument
        so you can do /addALL 5 6 7 8 9
    """

    result = 0
    for num in arr:
        result += int(num)
    
    await ctx.send(f"Result = {result}")

if __name__ == '__main__':
    bot.run(BOT_TOKEN)