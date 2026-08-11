import discord
import discord.opus
import ctypes.util
from discord import app_commands
from discord.ext import commands, tasks
import discord.ext.voice_recv as voice_recv
import os
from dotenv import load_dotenv
import random
import asyncio
import struct
import time
import wave
import html
import json
import sqlite3
import calendar
import numpy as np
import queue
from collections import defaultdict
import threading
import urllib.error
import urllib.request
try:
    import psycopg2
except ImportError:
    psycopg2 = None
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

from moonshine_voice import Transcriber, TranscriptEventListener, get_model_for_language, ModelArch
from moonshine_voice.transcriber import LineCompleted

load_dotenv()

# Moonshine model is loaded on-demand when /transcribe is used
model_path = None
model_arch = None
moonshine_ready = False

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

# transcribe variables:
TRANSCRIBE = False
TRANSCRIBE_LOCK = asyncio.Lock()
transcribe_channel = None
active_transcriber = None  # Moonshine Transcriber instance
active_transcribe_sink = None  # Discord receive sink that owns Moonshine streams
TRANSCRIBE_DEBUG = os.getenv("TRANSCRIBE_DEBUG", "").lower() in ("1", "true", "yes")

GOAT_ID = int(os.getenv("GOAT_ID", "0"))
glaze_phrase = "so good so goat so smart so intelligent so rich so handsome so sexy so cute so courageous so adventurous so creative so amiable so charismatic so authentic so calm so cheerful so good looking so charming so compassionate so dynamic so adaptable so agreeable so amazing so keen so genius so clever so ambitious so bright so diligent so passionate so admirable so affable so affectionate so amicable so considerate so energetic so fabulous so generous so nice so buffed so cool so hot so insightful so thoughtful so brave so loyal so sincere so witty"
glaze_words = set(glaze_phrase.split(" "))
glaze_words.remove("so")

start_d_date = "2025-10-12"
end_d_date = "2027-04-12"

DEFAULT_BIRTHDAY_TIMEZONE = os.getenv("BIRTHDAY_TIMEZONE", "America/Los_Angeles")
try:
    DEFAULT_BIRTHDAY_ANNOUNCE_HOUR = int(os.getenv("BIRTHDAY_ANNOUNCE_HOUR", "9"))
except ValueError:
    DEFAULT_BIRTHDAY_ANNOUNCE_HOUR = 9
DEFAULT_BIRTHDAY_ANNOUNCE_HOUR = max(0, min(23, DEFAULT_BIRTHDAY_ANNOUNCE_HOUR))
DB_URL = os.getenv("DB_URL") or os.getenv("DATABASE_URL")
BIRTHDAY_SQLITE_PATH = os.getenv("BIRTHDAY_SQLITE_PATH", "birthdays.sqlite3")
try:
    BIRTHDAY_ADMIN_ID = int(os.getenv("BIRTHDAY_ADMIN_ID", "0"))
except ValueError:
    BIRTHDAY_ADMIN_ID = 0
BIRTHDAY_DB_READY = False
BIRTHDAY_DB_WARNED = False
BIRTHDAY_DB_LOCK = threading.Lock()

BIRTHDAY_CAKE = "\U0001F382"
BIRTHDAY_PARTY = "\U0001F389"
BIRTHDAY_SNOW = "\u2744\ufe0f"
BIRTHDAY_BEAR = "\U0001F43B\u200d\u2744\ufe0f"
BIRTHDAY_MESSAGES = [
    "happy birthday {mention}!! officially one year more goated {cake} {snow}",
    "{mention} birthday detected. arctic celebration mode: on {party} {bear}",
    "everybody chill for a sec and wish {mention} a happy birthday {cake} {snow}",
    "happy birthday {mention}! may your day be colder than average and way more goated {party}",
    "{mention} leveled up today. happy birthday from the ice shelf {cake} {bear}",
]


opus_lib = ctypes.util.find_library("opus")
print("ctypes.util.find_library('opus') ->", opus_lib)
if not opus_lib:
    linux_opus_lib = "/usr/lib/x86_64-linux-gnu/libopus.so.0"
    if os.path.exists(linux_opus_lib):
        opus_lib = linux_opus_lib
if opus_lib:
    discord.opus.load_opus(opus_lib)
else:
    print("Opus library not found; voice features may be unavailable.")
print(discord.opus.is_loaded())

EMOJI_RE = re.compile(r'<a?:(?P<name>\w+):\d+>')
GOOGLE_TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"
TRANSLATE_CONFIG_WARNED = False

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
commands_list += "/transcribe : Toggle live voice-to-text transcription in vc\n"
commands_list += "/birthday_set [month] [day] : Save your birthday\n"
commands_list += "/birthday_remove : Remove your birthday\n"
commands_list += "/birthday_next : Show upcoming birthdays\n"
commands_list += "/birthday_channel [channel] [timezone] [announce_hour] : Set birthday announcement channel\n"

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
#------------------------------------------BIRTHDAY-DATABASE------------------------------------------------#
def birthday_db_uses_postgres():
    return bool(DB_URL and psycopg2 is not None)


def birthday_param():
    return "%s" if birthday_db_uses_postgres() else "?"


def connect_birthday_db():
    global BIRTHDAY_DB_WARNED

    if birthday_db_uses_postgres():
        return psycopg2.connect(DB_URL)

    if DB_URL and psycopg2 is None and not BIRTHDAY_DB_WARNED:
        print("DB_URL found, but psycopg2 is not installed. Falling back to SQLite.")
        BIRTHDAY_DB_WARNED = True

    conn = sqlite3.connect(BIRTHDAY_SQLITE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def close_birthday_cursor(cur):
    try:
        cur.close()
    except Exception:
        pass


def birthday_db_backend_label():
    if birthday_db_uses_postgres():
        return "Postgres"
    return f"SQLite ({BIRTHDAY_SQLITE_PATH})"


def init_birthday_db():
    global BIRTHDAY_DB_READY

    if BIRTHDAY_DB_READY:
        return

    with BIRTHDAY_DB_LOCK:
        if BIRTHDAY_DB_READY:
            return

        conn = connect_birthday_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS birthdays (
                    guild_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
                    day INTEGER NOT NULL CHECK (day BETWEEN 1 AND 31),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS birthday_settings (
                    guild_id TEXT PRIMARY KEY,
                    channel_id TEXT,
                    timezone TEXT NOT NULL,
                    announce_hour INTEGER NOT NULL CHECK (announce_hour BETWEEN 0 AND 23),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS birthday_announcements (
                    guild_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    sent_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, user_id, year)
                )
            """)
            conn.commit()
            BIRTHDAY_DB_READY = True
            print(f"Birthday database connected using {birthday_db_backend_label()}.")
        finally:
            close_birthday_cursor(cur)
            conn.close()


def birthday_write(sql, params=()):
    init_birthday_db()
    with BIRTHDAY_DB_LOCK:
        conn = connect_birthday_db()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            rowcount = cur.rowcount
            conn.commit()
            return rowcount
        finally:
            close_birthday_cursor(cur)
            conn.close()


def birthday_fetch_one(sql, params=()):
    init_birthday_db()
    with BIRTHDAY_DB_LOCK:
        conn = connect_birthday_db()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            return cur.fetchone()
        finally:
            close_birthday_cursor(cur)
            conn.close()


def birthday_fetch_all(sql, params=()):
    init_birthday_db()
    with BIRTHDAY_DB_LOCK:
        conn = connect_birthday_db()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            close_birthday_cursor(cur)
            conn.close()


def save_birthday(guild_id, user_id, month, day):
    ph = birthday_param()
    birthday_write(f"""
        INSERT INTO birthdays (guild_id, user_id, month, day, created_at, updated_at)
        VALUES ({ph}, {ph}, {ph}, {ph}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (guild_id, user_id) DO UPDATE SET
            month = EXCLUDED.month,
            day = EXCLUDED.day,
            updated_at = CURRENT_TIMESTAMP
    """, (guild_id, user_id, month, day))


def remove_birthday(guild_id, user_id):
    ph = birthday_param()
    return birthday_write(
        f"DELETE FROM birthdays WHERE guild_id = {ph} AND user_id = {ph}",
        (guild_id, user_id),
    )


def save_birthday_settings(guild_id, channel_id, timezone, announce_hour):
    ph = birthday_param()
    birthday_write(f"""
        INSERT INTO birthday_settings (
            guild_id, channel_id, timezone, announce_hour, created_at, updated_at
        )
        VALUES ({ph}, {ph}, {ph}, {ph}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (guild_id) DO UPDATE SET
            channel_id = EXCLUDED.channel_id,
            timezone = EXCLUDED.timezone,
            announce_hour = EXCLUDED.announce_hour,
            updated_at = CURRENT_TIMESTAMP
    """, (guild_id, channel_id, timezone, announce_hour))


def get_birthday_settings(guild_id):
    ph = birthday_param()
    row = birthday_fetch_one(
        f"SELECT channel_id, timezone, announce_hour FROM birthday_settings WHERE guild_id = {ph}",
        (guild_id,),
    )
    if not row:
        return {
            "channel_id": None,
            "timezone": DEFAULT_BIRTHDAY_TIMEZONE,
            "announce_hour": DEFAULT_BIRTHDAY_ANNOUNCE_HOUR,
        }

    return {
        "channel_id": row[0],
        "timezone": row[1],
        "announce_hour": row[2],
    }


def get_all_birthdays(guild_id):
    ph = birthday_param()
    return birthday_fetch_all(
        f"SELECT user_id, month, day FROM birthdays WHERE guild_id = {ph}",
        (guild_id,),
    )


def get_birthdays_for_local_date(guild_id, local_date):
    ph = birthday_param()
    include_leap_day = (
        local_date.month == 2 and
        local_date.day == 28 and
        not calendar.isleap(local_date.year)
    )

    if include_leap_day:
        return birthday_fetch_all(f"""
            SELECT user_id, month, day
            FROM birthdays
            WHERE guild_id = {ph}
              AND (
                (month = {ph} AND day = {ph})
                OR (month = 2 AND day = 29)
              )
        """, (guild_id, local_date.month, local_date.day))

    return birthday_fetch_all(f"""
        SELECT user_id, month, day
        FROM birthdays
        WHERE guild_id = {ph} AND month = {ph} AND day = {ph}
    """, (guild_id, local_date.month, local_date.day))


def was_birthday_announced(guild_id, user_id, year):
    ph = birthday_param()
    row = birthday_fetch_one(f"""
        SELECT 1
        FROM birthday_announcements
        WHERE guild_id = {ph} AND user_id = {ph} AND year = {ph}
    """, (guild_id, user_id, year))
    return row is not None


def mark_birthday_announced(guild_id, user_id, year):
    ph = birthday_param()
    birthday_write(f"""
        INSERT INTO birthday_announcements (guild_id, user_id, year, sent_at)
        VALUES ({ph}, {ph}, {ph}, CURRENT_TIMESTAMP)
        ON CONFLICT (guild_id, user_id, year) DO NOTHING
    """, (guild_id, user_id, year))


def validate_birthday(month, day):
    try:
        date(2000, month, day)
        return True
    except ValueError:
        return False


def validate_timezone(timezone):
    try:
        ZoneInfo(timezone)
        return True
    except Exception:
        return False


def is_birthday_admin(interaction):
    guild_permissions = getattr(interaction.user, "guild_permissions", None)
    has_manage_guild = bool(guild_permissions and guild_permissions.manage_guild)
    has_birthday_admin_id = BIRTHDAY_ADMIN_ID and interaction.user.id == BIRTHDAY_ADMIN_ID
    is_guild_owner = interaction.guild and interaction.guild.owner_id == interaction.user.id
    return has_manage_guild or has_birthday_admin_id or is_guild_owner


def birthday_date_for_year(month, day, year):
    if month == 2 and day == 29 and not calendar.isleap(year):
        return date(year, 2, 28)
    return date(year, month, day)


def next_birthday_date(month, day, today):
    next_date = birthday_date_for_year(month, day, today.year)
    if next_date < today:
        next_date = birthday_date_for_year(month, day, today.year + 1)
    return next_date


def format_birthday(month, day):
    return f"{calendar.month_name[month]} {day}"


def format_birthday_member(guild, user_id):
    try:
        member = guild.get_member(int(user_id))
    except ValueError:
        member = None

    if member:
        return discord.utils.escape_markdown(member.display_name)
    return f"<@{user_id}>"


def get_upcoming_birthdays(guild, limit):
    guild_id = str(guild.id)
    settings = get_birthday_settings(guild_id)
    try:
        today = datetime.now(ZoneInfo(settings["timezone"])).date()
    except Exception:
        today = datetime.now(ZoneInfo(DEFAULT_BIRTHDAY_TIMEZONE)).date()

    upcoming = []
    for user_id, month, day in get_all_birthdays(guild_id):
        target_date = next_birthday_date(month, day, today)
        upcoming.append({
            "user_id": user_id,
            "name": format_birthday_member(guild, user_id),
            "month": month,
            "day": day,
            "date": target_date,
            "days_until": (target_date - today).days,
        })

    upcoming.sort(key=lambda b: (b["date"], b["name"].casefold()))
    return upcoming[:limit]


async def resolve_birthday_channel(guild, channel_id):
    if not channel_id:
        return None

    try:
        channel_id_int = int(channel_id)
    except ValueError:
        return None

    channel = guild.get_channel(channel_id_int) or bot.get_channel(channel_id_int)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id_int)
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            return None

    if not hasattr(channel, "send"):
        return None
    return channel


async def announce_birthdays_for_guild(guild):
    guild_id = str(guild.id)
    settings = get_birthday_settings(guild_id)
    channel = await resolve_birthday_channel(guild, settings["channel_id"])
    if channel is None:
        return

    try:
        now = datetime.now(ZoneInfo(settings["timezone"]))
    except Exception:
        now = datetime.now(ZoneInfo(DEFAULT_BIRTHDAY_TIMEZONE))

    if now.hour < settings["announce_hour"]:
        return

    rows = get_birthdays_for_local_date(guild_id, now.date())
    for user_id, month, day in rows:
        if was_birthday_announced(guild_id, user_id, now.year):
            continue

        message = random.choice(BIRTHDAY_MESSAGES).format(
            mention=f"<@{user_id}>",
            cake=BIRTHDAY_CAKE,
            party=BIRTHDAY_PARTY,
            snow=BIRTHDAY_SNOW,
            bear=BIRTHDAY_BEAR,
        )
        try:
            await channel.send(
                message,
                allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False),
            )
            mark_birthday_announced(guild_id, user_id, now.year)
        except discord.HTTPException as e:
            print(f"Birthday announcement failed for guild {guild_id}, user {user_id}: {e}")


@tasks.loop(minutes=1)
async def birthday_announcements():
    for guild in bot.guilds:
        try:
            await announce_birthdays_for_guild(guild)
        except Exception as e:
            print(f"Birthday check failed for guild {guild.id}: {type(e).__name__}: {e}")


@birthday_announcements.before_loop
async def before_birthday_announcements():
    await bot.wait_until_ready()


#------------------------------------------BIRTHDAY-DATABASE------------------------------------------------#
#############################################################################################################
#############################################################################################################
#---------------------------------------------BOT-FUNCTIONS-------------------------------------------------#

@bot.event
async def on_ready():
    try:
        init_birthday_db()
    except Exception as e:
        print(f"Birthday database failed to initialize: {type(e).__name__}: {e}")
    if not birthday_announcements.is_running():
        birthday_announcements.start()
    await bot.tree.sync()
    print("Slash commands synced!")
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

@bot.tree.command(name="list", description="Command list for bot")
async def list_commands(interaction: discord.Interaction):
    await interaction.response.send_message(commands_list, ephemeral=True)


@bot.tree.command(name="birthday_set", description="Save your birthday")
@app_commands.describe(month="Month number, 1-12", day="Day of the month")
async def birthday_set(
    interaction: discord.Interaction,
    month: app_commands.Range[int, 1, 12],
    day: app_commands.Range[int, 1, 31],
):
    if interaction.guild is None:
        await interaction.response.send_message("birthdays are server-only for now.", ephemeral=True)
        return

    if not validate_birthday(month, day):
        await interaction.response.send_message("that date does not exist, even in the arctic.", ephemeral=True)
        return

    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    try:
        save_birthday(guild_id, user_id, int(month), int(day))
        settings = get_birthday_settings(guild_id)
    except Exception as e:
        print(f"birthday_set failed: {type(e).__name__}: {e}")
        await interaction.response.send_message("birthday database is being icy right now.", ephemeral=True)
        return

    message = f"saved your birthday as {format_birthday(int(month), int(day))} {BIRTHDAY_SNOW}"
    if not settings["channel_id"]:
        message += "\nadmins can turn on announcements with `/birthday_channel`."
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="birthday_remove", description="Remove your saved birthday")
async def birthday_remove(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("birthdays are server-only for now.", ephemeral=True)
        return

    try:
        deleted = remove_birthday(str(interaction.guild.id), str(interaction.user.id))
    except Exception as e:
        print(f"birthday_remove failed: {type(e).__name__}: {e}")
        await interaction.response.send_message("birthday database is being icy right now.", ephemeral=True)
        return

    if deleted:
        await interaction.response.send_message("removed your birthday.", ephemeral=True)
    else:
        await interaction.response.send_message("you did not have a birthday saved.", ephemeral=True)


@bot.tree.command(name="birthday_next", description="Show upcoming birthdays")
@app_commands.describe(limit="How many birthdays to show")
async def birthday_next(
    interaction: discord.Interaction,
    limit: app_commands.Range[int, 1, 25] = 10,
):
    if interaction.guild is None:
        await interaction.response.send_message("birthdays are server-only for now.", ephemeral=True)
        return

    try:
        upcoming = get_upcoming_birthdays(interaction.guild, int(limit))
    except Exception as e:
        print(f"birthday_next failed: {type(e).__name__}: {e}")
        await interaction.response.send_message("birthday database is being icy right now.", ephemeral=True)
        return

    if not upcoming:
        await interaction.response.send_message("no birthdays saved yet.", ephemeral=True)
        return

    lines = ["upcoming birthdays:"]
    for index, birthday in enumerate(upcoming, start=1):
        stored_date = format_birthday(birthday["month"], birthday["day"])
        observed_date = format_birthday(birthday["date"].month, birthday["date"].day)
        date_text = stored_date
        if observed_date != stored_date:
            date_text = f"{stored_date} (observed {observed_date})"

        days_until = birthday["days_until"]
        if days_until == 0:
            when = "today"
        elif days_until == 1:
            when = "tomorrow"
        else:
            when = f"in {days_until} days"

        lines.append(f"{index}. {birthday['name']} - {date_text} - {when}")

    await interaction.response.send_message(
        "\n".join(lines),
        allowed_mentions=discord.AllowedMentions.none(),
    )


@bot.tree.command(name="birthday_channel", description="Set birthday announcement channel")
@app_commands.describe(
    channel="Channel for birthday announcements",
    timezone="IANA timezone, like America/Los_Angeles",
    announce_hour="Hour to announce birthdays, 0-23",
)
async def birthday_channel(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    timezone: str = DEFAULT_BIRTHDAY_TIMEZONE,
    announce_hour: app_commands.Range[int, 0, 23] = DEFAULT_BIRTHDAY_ANNOUNCE_HOUR,
):
    if interaction.guild is None:
        await interaction.response.send_message("birthdays are server-only for now.", ephemeral=True)
        return

    if not is_birthday_admin(interaction):
        await interaction.response.send_message(
            "you need to be the server owner, have Manage Server, or have birthday admin access.",
            ephemeral=True,
        )
        return

    if not validate_timezone(timezone):
        await interaction.response.send_message(
            "that timezone does not look valid. try something like `America/Los_Angeles`.",
            ephemeral=True,
        )
        return

    bot_member = interaction.guild.me
    if bot_member and not channel.permissions_for(bot_member).send_messages:
        await interaction.response.send_message(
            f"i cannot send messages in {channel.mention} yet.",
            ephemeral=True,
        )
        return

    try:
        save_birthday_settings(
            str(interaction.guild.id),
            str(channel.id),
            timezone,
            int(announce_hour),
        )
    except Exception as e:
        print(f"birthday_channel failed: {type(e).__name__}: {e}")
        await interaction.response.send_message("birthday database is being icy right now.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"birthday announcements will go to {channel.mention} at {int(announce_hour):02d}:00 {timezone}.",
        ephemeral=True,
    )


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
                vc = interaction.guild.voice_client
                if vc is None:
                    vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
                elif vc.channel != channel:
                    await vc.move_to(channel)
                await interaction.response.send_message(f"Polarbear bot will now speak on message if sender is in vc!")
            else:
                await interaction.response.send_message(f"You need to be in vc first!")
        else:
            VOICE = False
            vc = interaction.guild.voice_client
            if vc and vc.is_connected() and not TRANSCRIBE:
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
    if(d_message.author.bot):
        return

    await send_translation_if_foreign(d_message)

    if(d_message.author.id == GOAT_ID):
        channel = d_message.channel
        if(any(word in d_message.content.lower() for word in glaze_words)):
            await channel.send(f"{d_message.author.mention} {glaze_phrase}")
    if(not VOICE or len(d_message.content) > 200 or any(link in d_message.content.lower() for link in link_set)):
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
            if vc is None:
                return
            vc.play(source)

def contains_foreign_letters(text: str):
    return any(ch.isalpha() and ord(ch) > 127 for ch in text)

async def translate_to_english(text: str):
    return await asyncio.to_thread(translate_to_english_sync, text)

def get_google_translate_api_key():
    return os.getenv("GOOGLE_TRANSLATE_API_KEY") or os.getenv("GOOGLE_CLOUD_TRANSLATE_API_KEY")

def translate_to_english_sync(text: str):
    global TRANSLATE_CONFIG_WARNED

    api_key = get_google_translate_api_key()
    if not api_key:
        if not TRANSLATE_CONFIG_WARNED:
            print("Google Cloud Translation disabled: set GOOGLE_TRANSLATE_API_KEY.")
            TRANSLATE_CONFIG_WARNED = True
        return None

    payload = {
        "q": text,
        "target": "en",
        "format": "text",
    }
    model = os.getenv("GOOGLE_TRANSLATE_MODEL")
    if model:
        payload["model"] = model

    request = urllib.request.Request(
        GOOGLE_TRANSLATE_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "X-goog-api-key": api_key,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"Google Cloud Translation HTTP error {e.code}: {error_body}")
        return None
    except Exception as e:
        print(f"Google Cloud Translation error: {e}")
        return None

    translations = body.get("data", {}).get("translations", [])
    if not translations:
        return None

    translated = translations[0].get("translatedText", "")
    return html.unescape(translated).strip()

async def send_translation_if_foreign(message: discord.Message):
    content = replace_mentions_and_emojis(message).strip()
    if not content or not contains_foreign_letters(content):
        return

    translated = await translate_to_english(content)
    if not translated:
        return

    if translated.casefold() == content.casefold():
        return

    if len(translated) > 1900:
        translated = translated[:1900] + "..."

    await message.channel.send(f"Translation: {translated}")

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


# ---- Transcription helpers ----

async def get_or_create_transcripts_channel(guild: discord.Guild) -> discord.TextChannel:
    for ch in guild.text_channels:
        if ch.name == "live-transcripts":
            return ch
    try:
        return await guild.create_text_channel("live-transcripts")
    except discord.Forbidden:
        return None


async def _shutdown_active_transcribe_sink():
    global active_transcribe_sink
    sink = active_transcribe_sink
    active_transcribe_sink = None
    if sink is not None:
        await bot.loop.run_in_executor(None, sink.cleanup)


async def _close_active_transcriber():
    global active_transcriber
    transcriber = active_transcriber
    active_transcriber = None
    if transcriber is not None:
        await bot.loop.run_in_executor(None, transcriber.close)


def _load_moonshine_model():
    """Load the Moonshine model into memory. Called when transcription starts."""
    global model_path, model_arch, moonshine_ready
    if moonshine_ready:
        return True
    try:
        model_path, model_arch = get_model_for_language("en")
        moonshine_ready = True
        print(f"Moonshine model loaded: {model_path} (arch={model_arch})")
        return True
    except Exception as e:
        moonshine_ready = False
        print(f"Moonshine model failed to load: {e}")
        return False


def _unload_moonshine_model():
    """Unload the Moonshine model from memory. Called when transcription stops."""
    global model_path, model_arch, moonshine_ready
    model_path = None
    model_arch = None
    moonshine_ready = False
    print("Moonshine model unloaded from memory.")


def _pcm_stereo_s16le_to_float32_mono(pcm_bytes: bytes) -> np.ndarray:
    """Convert 48 kHz stereo s16le PCM to mono float32 ndarray for Moonshine."""
    samples = np.frombuffer(pcm_bytes, dtype=np.int16)
    # Take left channel only from interleaved L R L R ...
    return samples[0::2].astype(np.float32) / 32768.0


class _UserTranscriptListener(TranscriptEventListener):
    """Per-stream listener that posts completed lines to the Discord channel."""

    def __init__(self, display_name: str, bot_loop: asyncio.AbstractEventLoop):
        self._name = display_name
        self._bot_loop = bot_loop

    def on_line_completed(self, event: LineCompleted):
        text = event.line.text.strip()
        if text and transcribe_channel is not None:
            print(f"[transcribe] {self._name}: {text}")
            if TRANSCRIBE_DEBUG and event.line.audio_data:
                asyncio.run_coroutine_threadsafe(
                    self._send_with_wav(text, event.line.audio_data),
                    self._bot_loop,
                )
            else:
                asyncio.run_coroutine_threadsafe(
                    transcribe_channel.send(f"**{self._name}**: {text}"),
                    self._bot_loop,
                )

    async def _send_with_wav(self, text: str, audio_data: list[float]):
        """Send transcription text along with the debug WAV of what Moonshine heard."""
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            pcm = struct.pack(f"<{len(audio_data)}h",
                              *(max(-32768, min(32767, int(s * 32768))) for s in audio_data))
            wf.writeframes(pcm)
        buf.seek(0)
        await transcribe_channel.send(
            f"**{self._name}**: {text}",
            file=discord.File(buf, filename=f"{self._name}_{int(time.time())}.wav"),
        )


class TranscribeSink(voice_recv.AudioSink):
    """Sink that receives decoded PCM and feeds it to Moonshine streams."""

    _STOP = object()

    def __init__(self, transcriber: Transcriber, bot_loop: asyncio.AbstractEventLoop):
        super().__init__()
        self._transcriber = transcriber
        self._bot_loop = bot_loop
        self._lock = threading.Lock()
        self._queue = queue.Queue()  # (uid, display_name, pcm_bytes)
        self._streams = {}  # uid -> moonshine Stream
        self._closing = threading.Event()
        self._streams_closed = False
        self._worker = threading.Thread(target=self._process_loop, daemon=True)
        self._worker.start()

    def _process_loop(self):
        while True:
            item = self._queue.get()
            if item is self._STOP:
                break
            if self._closing.is_set():
                continue
            uid, display_name, pcm_bytes = item
            try:
                audio_f32 = _pcm_stereo_s16le_to_float32_mono(pcm_bytes)
                with self._lock:
                    if self._closing.is_set():
                        continue
                    if uid not in self._streams:
                        stream = self._transcriber.create_stream()
                        listener = _UserTranscriptListener(display_name, self._bot_loop)
                        stream.add_listener(listener)
                        stream.start()
                        self._streams[uid] = stream
                    self._streams[uid].add_audio(audio_f32, 48000)
            except Exception as e:
                print(f"[transcribe] worker error for {display_name} ({uid}): {type(e).__name__}: {e}")
        self._close_streams()

    def _close_streams(self):
        with self._lock:
            if self._streams_closed:
                return
            self._streams_closed = True
            streams = list(self._streams.values())
            self._streams.clear()

        for stream in streams:
            try:
                stream.stop()
            except Exception:
                pass
            try:
                stream.close()
            except Exception:
                pass

    def wants_opus(self) -> bool:
        return False

    def write(self, user, data: voice_recv.VoiceData):
        if self._closing.is_set() or user is None or not TRANSCRIBE or not moonshine_ready:
            return
        if not data.pcm:
            return
        self._queue.put((user.id, user.display_name, data.pcm))

    def cleanup(self):
        if self._closing.is_set():
            return
        self._closing.set()
        self._queue.put(self._STOP)
        if threading.current_thread() is not self._worker:
            self._worker.join()
        self._close_streams()


@bot.tree.command(name="transcribe", description="Toggle live voice-to-text transcription in vc")
async def transcribe(interaction: discord.Interaction):
    global TRANSCRIBE, transcribe_channel, active_transcriber, active_transcribe_sink

    member = interaction.user
    async with TRANSCRIBE_LOCK:
        if not TRANSCRIBE:
            # --- Turn ON ---
            if not member.voice:
                await interaction.response.send_message("You need to be in a voice channel first!", ephemeral=True)
                return

            channel = member.voice.channel
            vc = interaction.guild.voice_client

            # Connect or upgrade to VoiceRecvClient
            if vc is None:
                vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
            elif not isinstance(vc, voice_recv.VoiceRecvClient):
                # Reconnect with recv-capable client
                await vc.disconnect()
                vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
            elif vc.channel != channel:
                await vc.move_to(channel)

            transcribe_channel = await get_or_create_transcripts_channel(interaction.guild)
            if transcribe_channel is None:
                await interaction.response.send_message(
                    "Could not find or create `#live-transcripts`. "
                    "Please create the channel manually or give the bot Manage Channels permission.",
                    ephemeral=True,
                )
                return

            await interaction.response.defer()

            # Load the model on demand
            loaded = await bot.loop.run_in_executor(None, _load_moonshine_model)
            if not loaded:
                await interaction.followup.send(
                    "Moonshine model failed to load — transcription unavailable.",
                    ephemeral=True,
                )
                return

            try:
                if vc.is_listening():
                    vc.stop_listening()
                await _shutdown_active_transcribe_sink()
                await _close_active_transcriber()

                active_transcriber = await bot.loop.run_in_executor(
                    None,
                    lambda: Transcriber(
                        model_path=model_path,
                        model_arch=model_arch,
                        options={
                            "vad_threshold": "0.3",
                            "vad_max_segment_duration": "20",
                        },
                    ),
                )
                active_transcribe_sink = TranscribeSink(active_transcriber, bot.loop)
                TRANSCRIBE = True
                vc.listen(active_transcribe_sink)
            except Exception as e:
                TRANSCRIBE = False
                if vc.is_listening():
                    vc.stop_listening()
                await _shutdown_active_transcribe_sink()
                await _close_active_transcriber()
                await interaction.followup.send(
                    f"Failed to start transcription: {type(e).__name__}: {e}",
                    ephemeral=True,
                )
                return

            await interaction.followup.send(
                f"Transcription started! Writing to {transcribe_channel.mention}"
            )
        else:
            # --- Turn OFF ---
            TRANSCRIBE = False
            vc = interaction.guild.voice_client
            if vc and isinstance(vc, voice_recv.VoiceRecvClient) and vc.is_listening():
                vc.stop_listening()

            await _shutdown_active_transcribe_sink()
            await _close_active_transcriber()
            await bot.loop.run_in_executor(None, _unload_moonshine_model)
            transcribe_channel = None

            if vc and vc.is_connected() and not VOICE:
                await vc.disconnect()

            await interaction.response.send_message("Transcription stopped!")


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


