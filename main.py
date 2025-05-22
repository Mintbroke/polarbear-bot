import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import asyncio
from collections import defaultdict
import threading
import psycopg2
from gtts import gTTS

from datetime import date
from datetime import datetime
from zoneinfo import ZoneInfo

from web import keep_alive

#############################################################################################################
#-------------------------------------------PRE-DEFINED-VALUES----------------------------------------------#
VOICE = False
VOICE_LOCK = threading.Lock()

# daily mine limit
DAILY_LIMIT = 20

# message for /list
commands_list = "NORMAL COMMANDS: \n"
commands_list += "/coin : Flip a coin\n"
commands_list += "/dice : Roll a dice\n"
commands_list += "/pick [choice1, choice2, choice3, ...] : Pick a random choice\n"
commands_list += "/remind [user] [time(minute)] [message] : Ping user with message after delay\n"
commands_list += "/voice : Switch on/off for message to speech function in vc\n"

commands_list += "\nSSAL COMMANDS: \n"
commands_list += "/mine : Mine a SSAL COIN\n"
commands_list += "/menu : Show the shop menu\n"
commands_list += "/buy [choice] : Buy the corresponding item from menu\n"
commands_list += "/stats : Check your stats\n"
commands_list += "/leaderboard : Check the leaderboard\n"
commands_list += "/refresh : Load the newest Database\n"


# Create an intents object
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent if necessary

# Create bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

def default_value():
    return {"username" : None,
            "coins" : 0, 
            "multiplier" : 1,
            "daily_count" : 0, 
            "last_mined" : "2000-01-01", 
            "crown_chance" : 1, 
            "crown_count" : 0}

# ssal coin dictionary
ssal_coins = defaultdict(default_value)

# ssal menu
ssal_menu = ["ssal_multiplier"]
ssal_price = {"ssal_multiplier" : 100}

# thread 
lock = threading.Lock()

# database
print(os.getenv("DB_URL"))
conn = psycopg2.connect(os.getenv("DB_URL"))

#-------------------------------------------PRE-DEFINED-VALUES----------------------------------------------#
#############################################################################################################

#############################################################################################################
#-------------------------------------------DATABASE-LOAD-SAVE----------------------------------------------#
def load_ssal_coins():
    global ssal_coins

    with conn.cursor() as cur:
        load_query = """
            SELECT id, username, coins, multiplier, daily_count, last_mined, crown_chance, crown_count
            FROM ssal;
        """
        cur.execute(load_query)
        rows = cur.fetchall()

        for row in rows:
            userid, username, coins, multiplier, daily_count, last_mined, crown_chance, crown_count = row
            ssal_coins[userid] = {
                "username": username,
                "coins": coins,
                "multiplier": multiplier,
                "daily_count": daily_count,
                "last_mined": str(last_mined),
                "crown_chance": crown_chance,
                "crown_count": crown_count
            }
        print(f"ssal loaded:\n{ssal_coins}")


def save_ssal_coins(userid : str):
    global ssal_coins

    user = ssal_coins[userid]
    with conn.cursor() as cur:
        save_query = """
            INSERT INTO ssal (id, username, coins, multiplier, daily_count, last_mined, crown_chance, crown_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET username = EXCLUDED.username,
                coins = EXCLUDED.coins,
                multiplier = EXCLUDED.multiplier,
                daily_count = EXCLUDED.daily_count,
                last_mined = EXCLUDED.last_mined,
                crown_chance = EXCLUDED.crown_chance,
                crown_count = EXCLUDED.crown_count;
        """
        cur.execute(save_query, (userid,
                                 user["username"],
                                 user["coins"], 
                                 user["multiplier"],
                                 user["daily_count"], 
                                 user["last_mined"], 
                                 user["crown_chance"], 
                                 user["crown_count"]
                                )
                    )
        
        conn.commit()
        print(f"User {user["username"]} with id {userid} updated successfully")

#-------------------------------------------DATABASE-LOAD-SAVE----------------------------------------------#
#############################################################################################################

#############################################################################################################
#---------------------------------------------BOT-FUNCTIONS-------------------------------------------------#

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Slash commands synced!")
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

@bot.tree.command(name="list", description="Command list for bot")
async def list(interaction: discord.Interaction):
    await interaction.response.send_message(commands_list, ephemeral=True)

# coin flip: /coin
@bot.tree.command(name="coin", description="flip a coin")
async def coin(interaction: discord.Interaction):
    await interaction.response.send_message(f"bot flips: {random.choice(['Heads', 'Tails'])}")

# roll dice: /dice
@bot.tree.command(name="dice", description="roll a dice")
async def dice(interaction: discord.Interaction):
    await interaction.response.send_message(f"bot rolls: {random.randint(1, 6)}")

# random choice: /pick [choice1 choice2 choice3 ...]
@bot.tree.command(name="pick", description="/pick [choice1, choice2, choice3, ...]")
async def pick(interaction: discord.Interaction, options: str):
    options_list = options.split(", ")
    await interaction.response.send_message(f"choices: {', '.join(options_list)}\nbot picks: {random.choice(options_list)}")
    #await interaction.followup.send(f"Bot picks: {random.choice(options_list)}")

# remind: /remind [user] [time(minute)] [message]
@bot.tree.command(name="remind", description="/remind [user] [time(minute)] [message]")
async def remind(interaction: discord.Interaction, user: discord.Member, delay: int, message: str):
    await interaction.response.defer()
    await interaction.followup.send(f"Bot will remind {user.mention} in {delay} minutes: {message}")
    await asyncio.sleep(delay * 60)    
    await interaction.channel.send(f"{user.mention} {message}")

@bot.tree.command(name="voice", description="/voice")
async def voice(interaction: discord.Interaction):
    global VOICE
    member = interaction.user
    with VOICE_LOCK:
        VOICE = not VOICE
        if(VOICE):
            if(member.voice):
                channel = member.voice.channel
                vc: discord.VoiceClient = interaction.guild.voice_client
                if vc is None:
                    vc = await channel.connect()
                elif vc.channel != channel:
                    await vc.move_to(channel)
                await interaction.response.send_message(f"Polarbear bot will now speak on message if sender is in vc!")
        else:
            vc: discord.VoiceClient = interaction.guild.voice_client
            if vc:
                await vc.disconnect()
            await interaction.response.send_message("Polarbear bot will no longer play voice on message now!")

@bot.event
async def on_message(message: discord.Message):
    if(message.author.bot):
        return
    with VOICE_LOCK:
        member = message.author
        if(VOICE and member.voice):
            vc: discord.VoiceClient = message.guild.voice_client
            message = f"{message.author.display_name} said {message.content}"
            filename = "voice_message.mp3"
            tts = gTTS(text=message, lang="en", slow=False)
            tts.save(filename)
            if vc.is_playing():
                vc.stop()

            source = discord.FFmpegPCMAudio(filename)
            vc.play(source)




#---------------------------------------------BOT-FUNCTIONS-------------------------------------------------#
#############################################################################################################

#############################################################################################################
#----------------------------------------------SSAL-MUKING--------------------------------------------------#

# mine: /mine
@bot.tree.command(name="mine", description="/mine")
async def mine(interaction: discord.Interaction):
    userid = str(interaction.user.id)
    ssal_coins[userid]["username"] = str(interaction.user.display_name)
    current_date = str(datetime.now(ZoneInfo("America/Los_Angeles")).date())
    if(ssal_coins[userid]["last_mined"] != current_date):
        ssal_coins[userid]["daily_count"] = 0
        ssal_coins[userid]["last_mined"] = current_date

    if(ssal_coins[userid]["daily_count"] < DAILY_LIMIT):
        ssal_coins[userid]["daily_count"] += 1
        ssal = random.randint(1, 2)
        if(ssal == 1):
            ssal_coins[userid]["coins"] += 1 * ssal_coins[userid]["multiplier"]
            
            await interaction.response.send_message(f"\U0001F389\U0001F389\U0001F389 CONGRATULATOINS! {interaction.user.mention} GOT {ssal_coins[userid]["multiplier"]} SSAL COINS \U0001F389\U0001F389\U0001F389\n" \
                                                    f"Stats: \n{ssal_coins[userid]}") # emote: party popper
        else:
            await interaction.response.send_message(f"UNLUCKY U, YOU ARE NOT THE TRUE SSALSSOONGYEE\n" \
                                                    f"Stats: \n{ssal_coins[userid]}")
        with lock:
            save_ssal_coins(userid)
    else:
        await interaction.response.send_message(f"YOU HAVE REACHED THE DAILY LIMIT OF {DAILY_LIMIT} REQUESTS")

# buy: /buy [choice]
@bot.tree.command(name="buy", description="/buy [choice]")
async def buy(interaction: discord.Interaction, choice: int):
    userid = str(interaction.user.id)
    choice -= 1
    if((choice < 0 or choice >= len(ssal_menu)) or ssal_menu[choice] not in ssal_menu):
        await interaction.response.send_message(f"INVALID CHOICE")

    else:
        price = ssal_price[ssal_menu[choice]] * ssal_coins[userid]["multiplier"]
        if(ssal_coins[userid]["coins"] < price):
            await interaction.response.send_message(f"NOT ENOUGH COINS")
        else:
            ssal_coins[userid]["coins"] -= price
            ssal_coins[userid]["multiplier"] *= 2
            with lock:
                save_ssal_coins(userid)
            await interaction.response.send_message(f"{interaction.user.mention} HAS SUCCESSFULLY PURCHASED {ssal_menu[choice]}\n" \
                                                    f"Stats: {ssal_coins[userid]}")

# menu: /menu
@bot.tree.command(name="menu", description="/menu")
async def mine(interaction: discord.Interaction):
    userid = str(interaction.user.id)
    menu_str = "MENU: \n"
    for index, item in enumerate(ssal_menu):
        menu_str += f"{index + 1}. {item}: {ssal_price[item] * ssal_coins[userid]["multiplier"]} coins\n"

    await interaction.response.send_message(f"{menu_str}")

# stats: /stats
@bot.tree.command(name="stats", description="/stats")
async def stats(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} \n{ssal_coins[str(interaction.user.id)]}")

# leaderboard: /leaderboard
@bot.tree.command(name="leaderboard", description="/leaderboard")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    sorted_ssal_coins = sorted(ssal_coins.items(), key=lambda user: user[1]["coins"], reverse=True)
    sorted_ssal_coins_dict = dict(sorted_ssal_coins)
    
    message = f"LEADERBOARD: \n"
    for index, (id, user) in enumerate(sorted_ssal_coins_dict.items()):
        message += f"{index + 1}. {user["username"]}: {user["coins"]} coins\n"
    
    await interaction.followup.send(f"{message}")

# refresh: /refresh
@bot.tree.command(name="refresh", description="/refresh")
async def refresh(interaction: discord.Interaction):
    await interaction.response.defer()
    load_ssal_coins()
    await interaction.followup.send(f"Database has been refreshed!")

#----------------------------------------------SSAL-MUKING--------------------------------------------------#
#############################################################################################################

if __name__ == '__main__':
    keep_alive()
    
    # Run the bot using the token from an environment variable
    load_ssal_coins()
    bot.run(os.getenv('DISCORD_TOKEN'))

    conn.close()


