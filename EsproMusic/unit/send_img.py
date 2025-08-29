import random
import asyncio
import time
from pyrogram import Client, filters
from EsproMusic import app, last_characters, first_correct_guesses, collection

RARITY_WEIGHTS = {
    "Common 🟠": (40, True),
    "Legendary 🟡": (20, True),
    "Exclusive 💮": (12, True),
    "Limited 🔮": (8, True),
    "Celestial 🎐": (4, True),
}

# ---------------- Delete message after 5 minutes ---------------- #
async def delete_message(chat_id, message_id):
    await asyncio.sleep(300)  # 5 minutes
    try:
        await app.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

# ---------------- Spawn character ---------------- #
@app.on_message(filters.command("spawn"))
async def send_image(client, message):
    chat_id = message.chat.id

    # Fetch all characters from MongoDB
    all_characters = await collection.find(
        {"rarity": {"$in": [k for k, v in RARITY_WEIGHTS.items() if v[1]]}}
    ).to_list(length=None)

    if not all_characters:
        return await message.reply("No characters found with allowed rarities in the database.")

    # Filter valid characters
    available_characters = [
        c for c in all_characters
        if 'id' in c and c.get('rarity') is not None and RARITY_WEIGHTS.get(c['rarity'], (0, False))[1]
    ]

    if not available_characters:
        return await message.reply("No available characters with the allowed rarities.")

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

    # Store last character
    last_characters[chat_id] = selected_character
    last_characters[chat_id]['timestamp'] = time.time()

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    caption_text = f"""✨ A {selected_character['rarity']} Character Appears! ✨
🔍 Use /guess to claim this mysterious slave!
🥂 Hurry, before someone else snatches them!🤭"""

    # Send image or video
    if 'vid_url' in selected_character:
        sent_message = await message.reply_video(
            video=selected_character['vid_url'],
            caption=caption_text
        )
    else:
        sent_message = await message.reply_photo(
            photo=selected_character['img_url'],
            caption=caption_text
        )

    # Schedule deletion after 5 minutes
    asyncio.create_task(delete_message(chat_id, sent_message.id))