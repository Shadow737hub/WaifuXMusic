# ------------------------------ IMPORTS ---------------------------------
import os
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

# ----------------------- LAZY IMPORT CLIENTS ----------------------------
# ❌ Direct app = Loy() banane se circular import hota hai
# ✅ Iske jagah ek wrapper bana dete hain jo on-demand load kare

from functools import lru_cache

@lru_cache(maxsize=1)
def get_clients():
    from EsproMusic.core.bot import Loy
    from EsproMusic.core.userbot import Userbot
    from EsproMusic.core.dir import dirr
    from EsproMusic.core.git import git
    from EsproMusic.core.platforms import *

    dirr()
    git()

    app = Loy()
    userbot = Userbot()

    Apple = AppleAPI()
    Carbon = CarbonAPI()
    SoundCloud = SoundAPI()
    Spotify = SpotifyAPI()
    Resso = RessoAPI()
    Telegram = TeleAPI()
    YouTube = YouTubeAPI()

    return app, userbot, Apple, Carbon, SoundCloud, Spotify, Resso, Telegram, YouTube

# 🪄 Export default vars (backward compatibility ke liye)
app, userbot, Apple, Carbon, SoundCloud, Spotify, Resso, Telegram, YouTube = get_clients()

# --------------------------- PLOG FUNCTION -------------------------------
async def PLOG(text: str):
    from info import GLOG
    await app.send_message(chat_id=GLOG, text=text)

# ---------------------------- END OF CODE -------------------------------