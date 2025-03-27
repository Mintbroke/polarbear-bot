import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import asyncio
from collections import defaultdict
import threading
import psycopg2

from datetime import date
from datetime import datetime
from zoneinfo import ZoneInfo

from web import keep_alive

#############################################################################################################
#-------------------------------------------PRE-DEFINED-VALUES----------------------------------------------#

# daily mine limit
DAILY_LIMIT = 20

# message for /list
commands_list = "/coin : Flip a coin\n"
commands_list += "/dice : Roll a dice\n"
commands_list += "/mine : Mine a SSAL COIN\n"
commands_list += "/stats : Check your stats\n"
commands_list += "/leaderboard : Check the leaderboard\n"
commands_list += "/pick [choice1] [choice2] [choice3] ... : Pick a random choice\n"
commands_list += "/remind [user] [time(minute)] [message] : Ping user with message after delay\n"

# Create an intents object
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent if necessary

# Create bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

def default_value():
    return {"coins" : 0, 
            "daily_count" : 0, 
            "last_mined" : "2000-01-01", 
            "crown_chance" : 1, 
            "crown_count" : 0}

# ssal coin dictionary
ssal_coins = defaultdict(default_value)

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
            SELECT id, username, coins, daily_count, last_mined, crown_chance, crown_count
            FROM ssal;
        """
        cur.execute(load_query)
        rows = cur.fetchall()

        for row in rows:
            userid, username, coins, daily_count, last_mined, crown_chance, crown_count = row
            ssal_coins[userid] = {
                "username": username,
                "coins": coins,
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
            INSERT INTO ssal (id, username, coins, daily_count, last_mined, crown_chance, crown_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET username = EXCLUDED.username,
                coins = EXCLUDED.coins,
                daily_count = EXCLUDED.daily_count,
                last_mined = EXCLUDED.last_mined,
                crown_chance = EXCLUDED.crown_chance,
                crown_count = EXCLUDED.crown_count;
        """
        cur.execute(save_query, (userid,
                                 user["username"],
                                 user["coins"], 
                                 user["daily_count"], 
                                 user["last_mined"], 
                                 user["crown_chance"], 
                                 user["crown_count"]))
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
@bot.tree.command(name="pick", description="/pick [choice1 choice2 choice3 ...]")
async def pick(interaction: discord.Interaction, options: str):
    options_list = options.split()
    await interaction.response.send_message(f"choices: {', '.join(options_list)}\nbot picks: {random.choice(options_list)}")
    #await interaction.followup.send(f"Bot picks: {random.choice(options_list)}")

# remind: /remind [user] [time(minute)] [message]
@bot.tree.command(name="remind", description="/remind [user] [time(minute)] [message]")
async def remind(interaction: discord.Interaction, user: discord.Member, delay: int, message: str):
    await interaction.response.defer()
    await interaction.followup.send(f"Bot will remind {user.mention} in {delay} minutes: {message}")
    await asyncio.sleep(delay * 60)    
    await interaction.channel.send(f"{user.mention} {message}")

# mine: /mine
@bot.tree.command(name="mine", description="/mine")
async def mine(interaction: discord.Interaction):
    userid = str(interaction.user.id)
    current_date = str(datetime.now(ZoneInfo("America/Los_Angeles")).date())
    if(ssal_coins[userid]["last_mined"] != current_date):
        ssal_coins[userid]["daily_count"] = 0
        ssal_coins[userid]["last_mined"] = current_date

    if(ssal_coins[userid]["daily_count"] < DAILY_LIMIT):
        ssal_coins[userid]["daily_count"] += 1
        ssal = random.randint(1, 2)
        if(ssal == 1):
            ssal_coins[userid]["coins"] += 1
            
            await interaction.response.send_message(f"\U0001F389\U0001F389\U0001F389 CONGRATULATOINS! {interaction.user.mention} GOT A SSAL COIN \U0001F389\U0001F389\U0001F389\n" \
                                                    f"Your current ssal coins: \n{ssal_coins[userid]}") #party popper
        else:
            await interaction.response.send_message(f"UNLUCKY U, YOU ARE NOT THE TRUE SSALSSOONGYEE\n" \
                                                    f"Your current ssal coins: \n{ssal_coins[userid]}")
        with lock:
            save_ssal_coins(userid)
    else:
        await interaction.response.send_message(f"YOU HAVE REACHED THE DAILY LIMIT OF {DAILY_LIMIT} REQUESTS")

@bot.tree.command(name="stats", description="/stats")
async def stats(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} \n{ssal_coins[interaction.user.id]}")

@bot.tree.command(name="leadedrboard", description="/leaderboard")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    sorted_ssal_coins = sorted(ssal_coins.items(), key=lambda user: user[1]["coins"], reverse=True)
    message = f"LEADERBOARD: \n"
    for index, user in enumerate(sorted_ssal_coins):
        message += f"{index + 1}. {user["username"]}: {user["coins"]}\n"
    await interaction.followup.send(f"{message}")

#---------------------------------------------BOT-FUNCTIONS-------------------------------------------------#
# #############################################################################################################

if __name__ == '__main__':
    keep_alive()
    
    # Run the bot using the token from an environment variable
    load_ssal_coins()
    bot.run(os.getenv('DISCORD_TOKEN'))

    conn.close()


