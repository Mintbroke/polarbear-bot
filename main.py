import discord
import discord.opus
import ctypes.util
from discord import app_commands
from discord.ext import commands
import os
import random
import asyncio
from collections import defaultdict
import threading
#import psycopg2
from gtts import gTTS
from pydub import AudioSegment
import emoji
import re

from datetime import date
from datetime import datetime
from zoneinfo import ZoneInfo

from web import keep_alive

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import io

#from io import BytesIO

#from polarbear_enhanced import EnhancedPolarBearBot
#############################################################################################################
#-------------------------------------------PRE-DEFINED-VALUES----------------------------------------------#
#pb = EnhancedPolarBearBot()

# vc variables:
VOICE = False
VOICE_LOCK = asyncio.Lock()
VOICE_SPEED_LOCK = asyncio.Lock()
AUTHOR_LOCK = asyncio.Lock()
previous_author = None
voice_speed = 1.5

GOAT_ID = int(os.getenv("GOAT_ID"))
glaze_phrase = "so good so goat so smart so intelligent so rich so handsome so sexy so cute so courageous so adventurous so creative so amiable so charismatic so authentic so calm so cheerful so good looking so charming so compassionate so dynamic so adaptable so agreeable so amazing so keen so genius so clever so ambitious so bright so diligent so passionate so admirable so affable so affectionate so amicable so considerate so energetic so fabulous so generous so nice so buffed so cool so hot so insightful so thoughtful so brave so loyal so sincere so witty"
glaze_words = set(glaze_phrase.split(" "))
glaze_words.remove("so")

start_d_date = "2025-10-12"
end_d_date = "2027-04-12"


opus_lib = ctypes.util.find_library("opus")
print("ctypes.util.find_library('opus') →", opus_lib)
if not opus_lib:
    opus_lib = "/usr/lib/x86_64-linux-gnu/libopus.so.0"
discord.opus.load_opus(opus_lib)
print(discord.opus.is_loaded())

EMOJI_RE = re.compile(r'<a?:(?P<name>\w+):\d+>')

# daily mine limit
DAILY_LIMIT = 20

# message for /list
commands_list = "NORMAL COMMANDS: \n"
commands_list += "/coin : Flip a coin\n"
commands_list += "/dice : Roll a dice\n"
commands_list += "/pick [choice1, choice2, choice3, ...] : Pick a random choice\n"
commands_list += "/remind [user] [time(minute)] [message] : Ping user with message after delay\n"
commands_list += "/voice : Switch on/off for message to speech function in vc\n"
commands_list += "/voice_speed : /voice_speed [speed]\n"

'''
commands_list += "\nSSAL COMMANDS: \n"
commands_list += "/mine : Mine a SSAL COIN\n"
commands_list += "/menu : Show the shop menu\n"
commands_list += "/buy [choice] : Buy the corresponding item from menu\n"
commands_list += "/stats : Check your stats\n"
commands_list += "/leaderboard : Check the leaderboard\n"
commands_list += "/refresh : Load the newest Database\n"
'''

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
ai_lock = asyncio.Lock()

'''
# database
print(os.getenv("DB_URL"))
conn = psycopg2.connect(os.getenv("DB_URL"))
'''
#-------------------------------------------PRE-DEFINED-VALUES----------------------------------------------#
#############################################################################################################
'''
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
'''
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

@bot.tree.command(name="add_word", description="/add_word [word]")
async def pick(interaction: discord.Interaction, word: str):
    glaze_words.add(word.lower())
    await interaction.response.send_message(f"glaze word {word} added!", ephemeral=True)


def lerp(a, b, t):  # linear interpolate
    return int(a + (b - a) * t)

def make_progress_png(percent: float, width: int = 720, height: int = 72, padding: int = 10):
    percent = max(0.0, min(100.0, percent))
    p = percent / 100.0

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    base = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    x0, y0 = padding, padding
    x1, y1 = width - padding, height - padding
    w = x1 - x0
    h = y1 - y0
    r = h // 2

    # Colors (Discord dark friendly)
    track_color = (36, 38, 44, 255)
    shadow_color = (0, 0, 0, 120)
    divider_color = (255, 255, 255, 35)

    # Gradient colors (teal → blue)
    g0 = (80, 220, 170, 255)
    g1 = (80, 140, 255, 255)

    # Shadow
    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0, y0 + 3, x1, y1 + 3), radius=r, fill=shadow_color)
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    base.alpha_composite(shadow)

    d = ImageDraw.Draw(base)

    # Track
    d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=track_color)

    # ---- Gradient Fill ----
    fill_w = int(w * p)
    if fill_w > 0:
        grad = Image.new("RGBA", (fill_w, h), (0, 0, 0, 0))
        gp = grad.load()

        for xx in range(fill_w):
            t = xx / max(1, fill_w - 1)
            rcol = lerp(g0[0], g1[0], t)
            gcol = lerp(g0[1], g1[1], t)
            bcol = lerp(g0[2], g1[2], t)
            for yy in range(h):
                gp[xx, yy] = (rcol, gcol, bcol, 255)

        fill_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        fill_layer.alpha_composite(grad, dest=(x0, y0))

        mask = Image.new("L", (width, height), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle((x0, y0, x0 + fill_w, y1), radius=r, fill=255)

        base = Image.composite(fill_layer, base, mask)

    # ---- 10% Dividers ----
    for i in range(1, 10):
        x = x0 + int(w * (i / 10))
        d.line((x, y0 + 8, x, y1 - 8), fill=divider_color, width=2)

    # Export
    buf = io.BytesIO()
    base.save(buf, format="PNG")
    buf.seek(0)
    return buf


@bot.tree.command(name="count_down", description="/count_down")
async def pick(interaction: discord.Interaction):
    target = datetime.strptime(end_d_date, "%Y-%m-%d")
    start = datetime.strptime(start_d_date, "%Y-%m-%d")
    now = datetime.now()
    delta = target - now
    total_delta = target - start
    percentage_done = (1 - delta.days / total_delta.days) * 100

    png = make_progress_png(percentage_done)
    file = discord.File(png, filename="progress.png")

    embed = discord.Embed(
        title=f"{delta.days} Days Left!",
        description=f"**{percentage_done:.2f}%** Complete!"
    )
    embed.set_image(url="attachment://progress.png")

    await interaction.response.send_message(embed=embed, file=file)

#@bot.tree.command(name="chat", description="/chat [message]")
async def chat(msg: discord.Message, message: str):
    async with ai_lock:
        print(f"Generating response for: {message}")
        try:  
            content = await pb.chat(message)
            await msg.reply(
                content,
                mention_author=False,
                allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False),
            )
        except Exception as e:
            print(f"LLM Error: {e}")
            await msg.reply(
                "Sorry, my brain is a bit oozy rn...",
                mention_author=False,
                allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False),
            )


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
    async with VOICE_LOCK:
        if(not VOICE):
            if(member.voice):
                VOICE = True
                channel = member.voice.channel
                vc: discord.VoiceClient = interaction.guild.voice_client
                if vc is None:
                    vc = await channel.connect()
                elif vc.channel != channel:
                    await vc.move_to(channel)
                await interaction.response.send_message(f"Polarbear bot will now speak on message if sender is in vc!")
            else:
                await interaction.response.send_message(f"You need to be in vc first!")
        else:
            VOICE = False
            vc: discord.VoiceClient = interaction.guild.voice_client
            if vc and vc.is_connected():
                await vc.disconnect()
            await interaction.response.send_message("Polarbear bot will no longer play voice on message now!")


link_set = set(['http://', 'https://', 'www.', '.com', '.net', '.org', '.io', '.gg', '.edu', '.gov'])
@bot.event
async def on_message(d_message: discord.Message):
    '''
    if(bot.user.mentioned_in(d_message) and not d_message.mention_everyone):
        print(f"received message for bot: {d_message.content}")
        text = d_message.content
        text = re.sub(fr'<@!?{bot.user.id}>', '', text).strip()
        await chat(d_message, text)
    else:
        print("no bot ping")
    '''
    if(d_message.author.id == GOAT_ID):
        channel = d_message.channel
        if(any(word in d_message.content.lower() for word in glaze_words)):
            await channel.send(f"{d_message.author.mention} {glaze_phrase}")
    if(d_message.author.bot or not VOICE or len(d_message.content) > 200 or any(link in d_message.content.lower() for link in link_set)):
        return
    global previous_author
    async with VOICE_LOCK:
        member = d_message.author
        if(VOICE):
            vc: discord.VoiceClient = d_message.guild.voice_client
            message = ""
            if(previous_author == None or member != previous_author):
                message += f"{d_message.author.display_name} said "
                async with AUTHOR_LOCK:
                    previous_author = member
            message += f"{replace_mentions_and_emojis(d_message)}"
            filename = "voice_message.mp3"
            tts = gTTS(text=message, lang="en", slow=False)
            tts.save(filename)
            sound = AudioSegment.from_file(filename, format="mp3")
            async with VOICE_SPEED_LOCK:
                faster = sound._spawn(sound.raw_data, overrides={
                    "frame_rate": int(sound.frame_rate * voice_speed)
                }).set_frame_rate(sound.frame_rate)
            fast_filename = "fast.mp3"
            faster.export(fast_filename, format="mp3")
            if vc and vc.is_playing():
                vc.stop()

            source = discord.FFmpegPCMAudio(fast_filename)
            vc.play(source)

def replace_mentions_and_emojis(message):
    content = message.content
    for user in message.mentions:
        content = content.replace(user.mention, "@"+user.display_name)

    for role in message.role_mentions:
        content = content.replace(role.mention, "@"+role.name)

    for channel in message.channel_mentions:
        content = content.replace(channel.mention, "@"+channel.name)

    def _replace_custom(match):
        return match.group("name")
    content = EMOJI_RE.sub(_replace_custom, content)

    demojized = emoji.demojize(content)
    content = re.sub(r':(\w+):', r'\1', demojized)

    return content

@bot.tree.command(name="voice_speed", description="/voice_speed [speed]")
async def change_voice_speed(interaction: discord.Interaction, speed: float):
    async with VOICE_SPEED_LOCK:
        global voice_speed
        voice_speed = speed
        await interaction.response.send_message(f"Polarbear bot voice speed is now: {speed}")


#---------------------------------------------BOT-FUNCTIONS-------------------------------------------------#
#############################################################################################################
'''
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
'''
if __name__ == '__main__':
    #keep_alive()
    #asyncio.run(testAI())
    # Run the bot using the token from an environment variable
    #load_ssal_coins()
    bot.run(os.getenv('DISCORD_TOKEN'))

    #conn.close()


