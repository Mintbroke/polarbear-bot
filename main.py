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
    ssal = random.randint(1, 100)
    if(ssal == 69):
        ssal_coins[interaction.user] += 1
        await interaction.response.send_message(f"\U0001F389\U0001F389\U0001F389 CONGRATULATOINS! {interaction.user.mention} GOT A SSAL COIN \U0001F389\U0001F389\U0001F389\n" \
                                                f"Your current ssal coins: {ssal_coins[interaction.user]}") #party popper
    else:
        await interaction.response.send_message(f"Unlucky U, YOU ARE NOT THE TRUE SSALSSOONGYEE\n" \
                                                f"Your current ssal coins: {ssal_coins[interaction.user]}")




if __name__ == '__main__':
    keep_alive()
    
    # Run the bot using the token from an environment variable
    bot.run(os.getenv('DISCORD_TOKEN'))


