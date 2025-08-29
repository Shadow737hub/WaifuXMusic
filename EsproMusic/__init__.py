# ------------------------------ IMPORTS ---------------------------------
import os
from pyrogram import Client, filters as f
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

# ----------------------- ESPRO MUSIC SETUP -------------------------------
from EsproMusic.core.bot import Loy
from EsproMusic.core.dir import dirr
from EsproMusic.core.git import git
from EsproMusic.core.userbot import Userbot

dirr()
git()

app = Loy()             # Your main bot client
userbot = Userbot()     # Your userbot

from EsproMusic.core.platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

# --------------------------- PLOG FUNCTION -------------------------------
async def PLOG(text: str):
    await app.send_message(
        chat_id=GLOG,
        text=text
    )
# ---------------------------- END OF CODE ------------------------------# ------------------------------ IMPORTS ---------------------------------
import os
from pyrogram import Client, filters as f
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

# ----------------------- ESPRO MUSIC SETUP -------------------------------
from EsproMusic.core.bot import Loy
from EsproMusic.core.dir import dirr
from EsproMusic.core.git import git
from EsproMusic.core.userbot import Userbot

dirr()
git()

app = Loy()             # Your main bot client
userbot = Userbot()     # Your userbot

from EsproMusic.core.platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

# --------------------------- PLOG FUNCTION -------------------------------
async def PLOG(text: str):
    await app.send_message(
        chat_id=GLOG,
        text=text
    )
# ---------------------------- END OF CODE ------------------------------