import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import asyncio
from collections import defaultdict

from web import keep_alive

# Create an intents object
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent if necessary

# Create bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

commands_list = "/coin : Flip a coin\n"
commands_list += "/dice : Roll a dice\n"
commands_list += "/mine : Mine a SSAL COIN\n"
commands_list += "/pick [choice1] [choice2] [choice3] ... : Pick a random choice\n"
commands_list += "/remind [user] [time(minute)] [message] : Ping user with message after delay\n"

# ssal coin dictionary
ssal_coins = defaultdict(int)

def load_ssal_coins():
    global ssal_coins
    with open("ssal_coins.txt", "r", encoding="utf-8") as file:
        for line in file:
            # Strip whitespace and split the line into key and value.
            # This assumes each line is formatted like "user: coins"
            userid, coins = line.strip().split(": ")
            ssal_coins[userid] = int(coins)

def save_ssal_coins():
    global ssal_coins
    with open("ssal_coins.txt", "w", encoding="utf-8") as file:
        # Iterate through the defaultdict items and write each key-value pair
        for userid, coins in ssal_coins.items():
            file.write(f"{userid}: {coins}\n")

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

@bot.tree.command(name="mine", description="/mine")
async def mine(interaction: discord.Interaction):
    ssal = random.randint(1, 2)
    userid = str(interaction.user.id)
    if(ssal == 69):
        ssal_coins[userid] += 1
        save_ssal_coins()
        await interaction.response.send_message(f"\U0001F389\U0001F389\U0001F389 CONGRATULATOINS! {interaction.user.mention} GOT A SSAL COIN \U0001F389\U0001F389\U0001F389\n" \
                                                f"Your current ssal coins: {ssal_coins[userid]}") #party popper
    else:
        await interaction.response.send_message(f"Unlucky U, YOU ARE NOT THE TRUE SSALSSOONGYEE\n" \
                                                f"Your current ssal coins: {ssal_coins[userid]}")


if __name__ == '__main__':
    keep_alive()
    
    # Run the bot using the token from an environment variable
    load_ssal_coins
    bot.run(os.getenv('DISCORD_TOKEN'))


