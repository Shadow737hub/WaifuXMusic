# EsproMusic/__init__.py

from pyrogram import filters as f
from pyrogram.types import *

# Export globals
from EsproMusic.core.globals import (
    locks, message_counters, spam_counters, last_characters,
    sent_characters, first_correct_guesses, message_counts,
    last_user, warned_users, user_cooldowns,
    user_nguess_progress, user_guess_progress, normal_message_counts
)

# Export clients
from EsproMusic.core.clients import (
    app, userbot, Apple, Carbon, SoundCloud, Spotify,
    Resso, Telegram, YouTube
)

# Power setup
from EsproMusic.unit.ban import *
from EsproMusic.unit.sudo import *
from EsproMusic.unit.react import *
from EsproMusic.unit.send_img import *
from EsproMusic.unit.rarity import *

# Logging function
async def PLOG(text: str):
    from info import GLOG
    await app.send_message(chat_id=GLOG, text=text)