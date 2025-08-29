# ------------------------------ IMPORTS ---------------------------------
import os
from functools import lru_cache
from pyrogram import filters as f
from pyrogram.types import *

# -------------------------- GLOBAL VARIABLES ----------------------------
locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}
last_user = {}
warned_users = {}
user_cooldowns = {}
user_nguess_progress = {}
user_guess_progress = {}
normal_message_counts = {}

# -------------------------- POWER SETUP ---------------------------------
from EsproMusic.unit.ban import *
from EsproMusic.unit.sudo import *
from EsproMusic.unit.react import *
from EsproMusic.unit.send_img import *
from EsproMusic.unit.rarity import *

# -------------------------- LAZY CLIENT SETUP ---------------------------
import EsproMusic.core.platforms as platforms

@lru_cache(maxsize=1)
def get_clients():
    from EsproMusic.core.bot import Loy
    from EsproMusic.core.userbot import Userbot
    from EsproMusic.core.dir import dirr
    from EsproMusic.core.git import git

    # Setup dirs and git
    dirr()
    git()

    # Init bot + userbot
    app = Loy()
    userbot = Userbot()

    # APIs
    Apple = platforms.AppleAPI()
    Carbon = platforms.CarbonAPI()
    SoundCloud = platforms.SoundAPI()
    Spotify = platforms.SpotifyAPI()
    Resso = platforms.RessoAPI()
    Telegram = platforms.TeleAPI()
    YouTube = platforms.YouTubeAPI()

    return app, userbot, Apple, Carbon, SoundCloud, Spotify, Resso, Telegram, YouTube

# ------------------------- EXPORT FOR MODULES ---------------------------
app, userbot, Apple, Carbon, SoundCloud, Spotify, Resso, Telegram, YouTube = get_clients()

# --------------------------- PLOG FUNCTION -------------------------------
async def PLOG(text: str):
    from info import GLOG   # Make sure GLOG is defined in info.py
    await app.send_message(
        chat_id=GLOG,
        text=text
    )

# ---------------------------- END OF CODE -------------------------------