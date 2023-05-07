BOT_TOKEN = "MTEwMzg3NDcyNjIwMTQwNTU4MA.GYTYnE.Kd71rBAZowAm76j77NycXEKsnV4Q04xzfJNlfs"
CHANNEL_ID = 1100690193012506635

from discord.ext import commands
from gtts import gTTS
from io import BytesIO
import discord
import random
import asyncio
import time


class Player:
    def __init__(self, user, role=None, seat=0, emo=None):
        self.user = user
        self.role = role
        self.seat = seat
        self.emo = emo
        self.death = False
        self.mostVote = False

# Bot variables
command_prefix = "/"                # what should the command start with
intents = discord.Intents.all()     # Intents to use all functions
bot = commands.Bot(command_prefix=command_prefix, intents=intents)

# Game variables
event_called = False
players = []
discord_users = []
emojis = []
roles = []
killed = []
isGameEnded = False


@bot.event
async def on_ready():
    print("Werewolf Bot activated!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("WereWolf Bot activated!")

@bot.command()
async def test(ctx):
    user = ctx.author
    for i in range(6):
        discord_users.append(user)
    print( f"Appended {user.name} to discord_users 6 times\ndiscord_users = {discord_users}")


@bot.command()
async def join(ctx):

    def check(reaction, user):
        return str(reaction.emoji) in ["👍", "🚫"] and user != bot.user

    global event_called
    if event_called:
        await ctx.send("Function has been called")
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
                discord_users.append(user)
                await ctx.send(f"{user.name} has joined the game!")
            elif str(reaction.emoji) == "🚫":
                await ctx.send(f"{user.name} has stopped joining the game.")
                event_called = False

@bot.command()
async def play( ctx, game = "werewolf"):
    has_Heal    = True
    has_Posion  = True
    # assign users
    # set the game State to all false first to for remaing roles
    await six_ppl_game()      # reset to six people game in default
    global players, discord_users, emojis, killed
    seat_num = 1
    for user in discord_users:
        players.append( Player( user, await draw(user), seat_num, emojis[seat_num-1]))
        seat_num += 1
    # time to confirm their role and ability
    await ctx.send("The game is starting. You have 30 seconds to confirm your roles.", tts=True)
    await ctx.send( "5 seconds" )
    # Going Dark
    await ctx.send( "Alright, everyone. Please close your eyes and go back to sleep. It is now nighttime." , tts=True)

    
    while isGameEnded == False:
        await ctx.send(" Please close your eyes")
        time.sleep(5)
        await wolfTurn(ctx)
        time.sleep(5)
        has_Heal, has_Posion = await witchTurn(ctx, has_Heal, has_Posion)
        time.sleep(5)
        await seerTurn(ctx)
        time.sleep(5)

        # remove dead player from emoji
        # set player death to True
        dead_list = ''
        for dead in killed:
            emojis.remove(dead.emo)
            dead.death = True
            dead_list +=str(dead.user.name) + ","
        # say who died
        # morning_msg = 'No one died yesterday!' if not killed else f"Yesterday, {(dead.user.emo for dead in killed)} dead!"
        if not killed:
            morning_msg = '```No one died yesterday!```'
        else:
            morning_msg = f'```Yesterday, {dead_list} got killed```'
        await ctx.send(morning_msg, tts=True)
        

        # pick a random people if no one died\
        speak_index = random.randint( 1, len(emojis) - 1 )
        msg = f"Please start with player {emojis[speak_index]} for speaking"
        await ctx.send(msg, tts=True)
        killed = [] # empty killed
        # vote state
        await waitToVote(ctx, user)
        # determine win state
        msg = await determineWinningState(ctx)
        await ctx.send(msg, tts=True)
        for player in players:
            player.mostVote = False
    
    await ctx.send("GAME IS ENDED")
    return


async def waitToVote(ctx, user):
    global players
    def check(reaction, user):
        return str(reaction.emoji) in ["👍"] and user != bot.user
    
    poll_message = "React with 👍 when you guys are ready to vote"
    poll = await ctx.send(poll_message)
    await poll.add_reaction("👍")

    reaction, user = await bot.wait_for('reaction_add', check=check)
    if str(reaction.emoji) == "👍":
        poll_message = "A poll is sending to each survivor"
        await ctx.send(poll_message, tts=True)
        isVotedMoreThanOnce = False
        await vote(ctx, isVotedMoreThanOnce, user)
    return


async def callVote(ctx, user, isVotedMoreThanOnce):
    global players
    voteResult = []     # for message
    seat_freq = {}
    for player in players:
        if player.death == False and player.mostVote == False:
            vote_seat, vote_msg = await gatherVotes(ctx, player, isVotedMoreThanOnce)
            voteResult.append(vote_msg)

            if vote_seat in seat_freq:
                seat_freq[vote_seat] += 1
            elif vote_seat == 0:
                continue
            else:
                seat_freq[vote_seat] = 1
    
    max_freq = max(seat_freq.values())
    most_vote = []
    for seat, freq in seat_freq.items():
        if(freq == max_freq):
            most_vote.append(seat)
    voteResult.append(f"The player(s) with most votes: {most_vote}")
    msg = "```Here are vote results of today: \n"
    for voteMsg in voteResult:
        msg += voteMsg + "\n"
    msg += "```"
    await ctx.send(msg)
    return most_vote
    

async def vote(ctx, isVotedMoreThanOnce, user):
    global players, emojis
    most_vote = await callVote(ctx, user, isVotedMoreThanOnce)

    if len(most_vote) > 1 and isVotedMoreThanOnce == False:
        # vote once more time
        msg = "There are more than one player with most votes, please vote one more time"
        await ctx.send(msg, tts=True)
        isVotedMoreThanOnce = True
        for num in most_vote:
            for player in players:
                if num == player.seat:
                    player.mostVote = True
        
        await vote(ctx, isVotedMoreThanOnce, user)
    elif isVotedMoreThanOnce == True and len(most_vote) > 1:
        msg = "There are still more than one player with most votes, so there is no one die today"
        await ctx.send(msg, tts=True)
    elif len(most_vote) == 1:
        msg = f"Number {most_vote}, you are voted to be killed. Please say your last words"
        await ctx.send(msg, tts=True)
        msg = "Please react 😇 when you finished your speech"
        poll = await ctx.send(msg)
        await poll.add_reaction("😇")
        def check(reaction, user):
            return user != bot.user and str(reaction.emoji) == "😇" 
        reaction, user = await bot.wait_for('reaction_add', check=check)
        msg = "Thank you for your amazing speech. You are now time to die"
        await ctx.send(msg, tts=True)
        chosen_player = None
        # Kill the player
        for player in players:
            if most_vote[0] == player.seat:
                chosen_player = player
        emojis.remove(chosen_player.emo)
        chosen_player.death = True
    else: 
        print("Error: vote(ctx, isVotedMoreThanOnce, user) function error")
    return


async def gatherVotes(ctx, youAreTheOneToVote, isVotedMoreThanOnce):    
    msg = f"```Player Number:  {youAreTheOneToVote.emo}\n"    
    msg += "Please vote to player to kill or React 🚫 to not vote```"
    dm_channel = await youAreTheOneToVote.user.create_dm()
    poll = await dm_channel.send(msg)

    # create a temp emojis
    global emojis, players
    remaining_emojis = []
    for player in players:
        if isVotedMoreThanOnce == False:
            if player.death == False:
                remaining_emojis.append(player.emo)
        else:
            if player.death == False and player.mostVote == True:
                remaining_emojis.append(player.emo)
    
    remaining_emojis.append("🚫")

    for emo in remaining_emojis:
        await poll.add_reaction(emo)


    reaction, user = await bot.wait_for('reaction_add')
    if user != bot.user and reaction.emoji in emojis:
        chosen_player = None
        for player in players:
            if player.emo == str(reaction.emoji) and player.death == False:
                chosen_player = player
                break
    
    msg = ""
    if str(reaction.emoji) == "🚫":
        msg = "Okay, your vote is collected!"
        return_msg = f"{youAreTheOneToVote.emo} ➡️ 🚫"
        dm_channel = await player.user.create_dm()
        await dm_channel.send(msg)
        return 0, return_msg
    else: 
        msg = "Okay, your vote is gathered and sent. Hope he/she die today!!"
        dm_channel = await youAreTheOneToVote.user.create_dm()
        await dm_channel.send(msg)
        return_msg = f"{youAreTheOneToVote.emo} ➡️ {chosen_player.emo}"
        return chosen_player.seat, return_msg


async def determineWinningState(ctx):
    wolf_count = 0
    good_count = 0
    global isGameEnded, players
    for player in players:
        if player.death == False:
            if player.role.startswith("Werewolf"):
                wolf_count += 1
            else:
                good_count += 1
    if wolf_count == 0:
        msg = "Congratulations! Humans Win!"
        isGameEnded = True
    elif wolf_count >= good_count:
        msg = "Congratulations! Werewolfs Win!"
        isGameEnded = True
    else:
        msg = "Game is continued. Now we are time to sleep"
        isGameEnded = False
    return msg
    

async def six_ppl_game():
    global roles, emojis, killed,isGameEnded
    roles = [ "Seer", "Witch", "Village1","Village2","Werewolf1","Werewolf2"]
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
    killed = []
    isGameEnded = False

async def wolfTurn(ctx):
    # pick wolf voter
    werewolfVoter = next(player for player in players if player.role.startswith("Werewolf"))
    # send group message
    await ctx.send(f"Werewolf, please wake up", tts=True)

    # send private message
    poll_message = f"```You are the Werewolf voter. Please select a player to kill```"
    dm_channel = await werewolfVoter.user.create_dm()
    poll = await dm_channel.send(poll_message)


    global emojis
    for emoji in emojis:
        await poll.add_reaction(emoji)
    # wait for pick and kill
    def check(reaction, werewolfVoter):
        return werewolfVoter != bot.user and str(reaction.emoji) in emojis

    reaction, werewolfVoter = await bot.wait_for('reaction_add', check=check)
    chosen_player = None
    for player in players:
        if player.emo == str(reaction.emoji):
            chosen_player = player
            break
    
    if chosen_player is None:
        await ctx.send("Error: couldn't find player with chosen emoji")
        return
    
    global killed
    killed.append(chosen_player)
    await ctx.send(f"Ok I got it, please close your eyes", tts=True)
    return

async def witchTurn(ctx, has_Heal, has_Posion):
    witch = next( player for player in players if player.role == "Witch")

    async def use_heal():
        nonlocal witch
        global killed
        theDeath = killed[0]
        
        # message and poll reaction
        witch_dm = await witch.user.create_dm()
        msg = f"```Do you want to use heal potion for Player {theDeath.emo}?\nPress 👍 for YES\nPress 🔙 to go back```"
        private_msg = await witch_dm.send(msg)
        await private_msg.add_reaction("👍")
        await private_msg.add_reaction("🔙")

        def check( reaction, user ):
            return user == witch.user and str(reaction.emoji) in ["👍", "🔙"]
        
        while True:
            reaction, _ = await bot.wait_for("reaction_add", check=check)
            if str(reaction.emoji) == "👍":
                killed.pop()
                return True
            elif str(reaction.emoji) == "🔙":
                return False     
                
    async def use_posion():
        nonlocal witch
        witch_dm = await witch.user.create_dm()  # create dm with witch
        poll_message = f"```Hello Witch!\nDo you want to use poison ?\nSelect a player number to use your posion\n"
        poll_message += "Select 🔙 to go back```"
        poll = await witch_dm.send(poll_message)
        
        for emo in emojis:
            await poll.add_reaction(emo)
        await poll.add_reaction("🔙")
        # get reaction, assume always kill one player
        reaction, user = await bot.wait_for('reaction_add')
        if user != bot.user and reaction.emoji == "🔙":
            return False
        if user != bot.user and str(reaction.emoji) in emojis:
            chosen_player = next( player for player in players if player.emo == reaction.emoji)
            global killed
            if chosen_player not in killed:
                killed.append(chosen_player)
            return True
      
    async def action():
        # list of potion
        nonlocal has_Heal, has_Posion, witch
        potions_reactions = ["🙅🏻‍♂️"]
        if has_Heal:
            potions_reactions.append("💊")
        if has_Posion:
            potions_reactions.append("🧪")

        async def prompt():
            # send prompt
            nonlocal potions_reactions, witch
            to_witch_message = "```Do you want to use heal potion, posion potion, or do nothing?\n"
            to_witch_message += "💊 for Heal\n🧪 for Posion\n🙅🏻‍♂️ to do Nothing```"
            witch_dm = await witch.user.create_dm()
            private_msg = await witch_dm.send(to_witch_message)
            # add potions reactions
            for choice in potions_reactions:
                await private_msg.add_reaction(choice)



        # choice action
        acted = False
        while not acted:
            await prompt()
            reaction, user = await bot.wait_for('reaction_add')
            if user != bot.user and reaction.emoji == "🙅🏻‍♂️":
                return 0
            elif user != bot.user and reaction.emoji == "💊":
                acted = await use_heal()
                has_Heal = not acted
            elif user != bot.user and reaction.emoji == "🧪":
                acted = await use_posion()
                has_Posion = not acted

    msg = "Witch, please wake up"
    await ctx.send(msg, tts = True)

    if witch.death:
        time.sleep(random.randint( 5, 15 ))
    else:
        await action()
    await ctx.send(f"Ok I got it, please close your eyes", tts=True)
    return ( has_Heal, has_Posion )

async def seerTurn(ctx):
    seer = next( player for player in players if player.role == "Seer")
    msg = f"Seer, please wake up"
    await ctx.send(msg, tts=True)
    
    async def see_role():
        nonlocal seer
        # send private message
        poll_message = f"```Hello Seer!\nSelect a number to check the player's identity```"
        dm_channel = await seer.user.create_dm()
        poll = await dm_channel.send(poll_message)

        # create a temp emojis
        remaining_emojis = []
        for player in players:
            remaining_emojis.append(player.emo)
            await poll.add_reaction(player.emo)

        # wait for pick and kill
        def check(reaction, user):
            return user != bot.user and str(reaction.emoji) in remaining_emojis

        reaction, seer = await bot.wait_for('reaction_add', check=check)
        chosen_player = None
        for player in players:
            if player.emo == str(reaction.emoji):
                chosen_player = player
                break
        
        if chosen_player is None:
            await ctx.send("Error: couldn't find player with chosen emoji")
            return
        
        if chosen_player.role.startswith("Werewolf"):
            role_msg = f"This player's role is BAD"
        else:
            role_msg = f"This player's role is GOOD"
        await dm_channel.send(role_msg)
       
    # handle case if seer died or not
    if not seer.death:
        await see_role()
    else:
        time.sleep(random.randint( 5, 15 ))
    
    await ctx.send(f"Ok Seer, I got it, please close your eyes", tts=True)
    return
    

async def draw(user):
    global roles
    
    if not roles:
        print("ERROR: ROLES NOT ENOUGH")
        return
    
    random_num = random.randint( 0, len(roles)-1 ) # get a random number
    role = roles[random_num]    # extra role
    roles.remove(role)          # remove role from global "roles"

    print ( f"assigned {user.name} {role}" )    # debug statement
    # 2) send private message to this player
    if role != None:
        await send_private_message( user,  f"Your role is {role}" )
    return role

async def send_private_message(user, message):
    dm_channel = await user.create_dm()
    await dm_channel.send(message)
    

if __name__ == '__main__':
    bot.run(BOT_TOKEN)

