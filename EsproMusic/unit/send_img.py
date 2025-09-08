import random
import asyncio
import time
from pyrogram import filters
from pyrogram.types import Message
from EsproMusic import app
from EsproMusic.core.mongo import mongodb
import config

LOG_CHAT_ID = config.LOGGER_ID

collection = mongodb.waifus  


# Store last spawned characters
last_characters = {}
first_correct_guesses = {}

RARITY_WEIGHTS = {
    "Common 🟠": (40, True),       # Most frequent
    "Legendary 🟡": (20, True),    # Less frequent than Common
    "Exclusive 💮": (12, True),    # Rare but obtainable
    "Limited 🔮": (8, True),       # Very rare
    "Celestial 🎐": (4, True),     # Extremely rare
}


async def delete_message(chat_id, message_id):
    await asyncio.sleep(300)  # 5 minutes
    try:
        await app.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")


@app.on_message(filters.command("spawn"))
async def send_image(client, message: Message):
    chat_id = message.chat.id

    # Fetch all characters from MongoDB
    all_characters = await collection.find(
        {"rarity": {"$in": [k for k, v in RARITY_WEIGHTS.items() if v[1]]}}
    ).to_list(length=None)

    if not all_characters:
        await message.reply_text("No characters found with allowed rarities in the database.")
        return

    # Filter characters with valid rarity
    available_characters = [
        c for c in all_characters
        if 'id' in c and c.get('rarity') is not None and RARITY_WEIGHTS.get(c['rarity'], (0, False))[1]
    ]

    if not available_characters:
        await message.reply_text("No available characters with the allowed rarities.")
        return

    # Weighted random selection
    cumulative_weights = []
    cumulative_weight = 0
    for character in available_characters:
        cumulative_weight += RARITY_WEIGHTS.get(character.get('rarity'), (1, False))[0]
        cumulative_weights.append(cumulative_weight)

    rand = random.uniform(0, cumulative_weight)
    selected_character = None
    for i, character in enumerate(available_characters):
        if rand <= cumulative_weights[i]:
            selected_character = character
            break

    if not selected_character:
        selected_character = random.choice(available_characters)

    # Store last spawned
    last_characters[chat_id] = selected_character
    last_characters[chat_id]['timestamp'] = time.time()

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    caption = (
        f"✨ A {selected_character['rarity']} Character Appears! ✨\n"
        f"🔍 Use /guess to claim this mysterious slave!\n"
        f"🥂 Hurry, before someone else snatches them!🤭"
    )

    # Send character (video or photo)
    if 'vid_url' in selected_character:
        sent = await app.send_video(chat_id, video=selected_character['vid_url'], caption=caption)
    else:
        sent = await app.send_photo(chat_id, photo=selected_character['img_url'], caption=caption)

    # Auto delete after 5 minutes
    asyncio.create_task(delete_message(chat_id, sent.id))