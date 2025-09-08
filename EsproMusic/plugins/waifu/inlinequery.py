import re
import time
from html import escape
from cachetools import TTLCache
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultPhoto,
    InlineQueryResultVideo
)
from EsproMusic import app  # Aapke bot ka main client
from EsproMusic.unit.inline import *


# Cache setup
all_characters_cache = TTLCache(maxsize=10000, ttl=36000)  # Cache for all characters
user_collection_cache = TTLCache(maxsize=10000, ttl=60)    # Cache for user collections


@app.on_inline_query()
async def inlinequery(client: Client, inline_query: InlineQuery):
    query = inline_query.query
    offset = int(inline_query.offset) if inline_query.offset else 0

    # --- User collection search ---
    if query.startswith("collection."):
        user_id, *search_terms = query.split(" ")[0].split(".")[1], " ".join(query.split(" ")[1:])
        if user_id.isdigit():
            user = user_collection_cache.get(user_id) or await get_user_collection(user_id)
            if user:
                user_collection_cache[user_id] = user  # Cache the result
                all_characters = list(
                    {char["id"]: char for char in user["characters"] if "id" in char}.values()
                )  # Deduplicate by ID

                if search_terms:
                    regex = re.compile(" ".join(search_terms), re.IGNORECASE)
                    all_characters = [
                        char for char in all_characters
                        if regex.search(char["name"]) or regex.search(char["anime"])
                    ]
            else:
                all_characters = []
        else:
            all_characters = []
    else:
        # --- General character search ---
        if query:
            all_characters = await search_characters(query)
        else:
            all_characters = all_characters_cache.get("all_characters") or await get_all_characters()
            all_characters_cache["all_characters"] = all_characters

    # --- Filter characters ---
    if ".AMV" in query:
        all_characters = [char for char in all_characters if "vid_url" in char]
    else:
        all_characters = [char for char in all_characters if "img_url" in char]

    # --- Pagination ---
    characters = all_characters[offset:offset + 50]
    next_offset = str(offset + len(characters)) if len(characters) == 50 else ""

    # --- Results ---
    results = []
    for character in characters:
        # Caption bana rahe
        if query.startswith("collection.") and "user" in locals():
            user_character_count = sum(
                1 for char in user["characters"]
                if "id" in char and char["id"] == character["id"]
            )
            caption = (
                f"<b>👤 Check out <a href='tg://user?id={user['id']}'>{escape(user.get('first_name', 'User'))}</a>'s character:</b>\n\n"
                f"🌸 <b>{character['name']} (x{user_character_count})</b>\n"
                f"🏖️ From: <b>{character['anime']}</b>\n"
                f"🔮 Rarity: <b>{character['rarity']}</b>\n\n"
                f"🆔️ <b>{character['id']}</b>\n\n"
            )
        else:
            caption = (
                f"<b>Discover this amazing character:</b>\n\n"
                f"🌸 <b>{character['name']}</b>\n"
                f"🏖️ From: <b>{character['anime']}</b>\n"
                f"🔮 Rarity: <b>{character['rarity']}</b>\n"
                f"🆔️ <b>{character['id']}</b>\n\n"
            )

        # Agar video hai
        if "vid_url" in character:
            thumbnail_url = character.get("thum_url", "https://envs.sh/6Y3.jpg")
            results.append(
                InlineQueryResultVideo(
                    id=f"{character['id']}_{time.time()}",
                    video_url=character["vid_url"],
                    mime_type="video/mp4",
                    thumb_url=thumbnail_url,
                    title=character["name"],
                    description=f"From: {character['anime']} | Rarity: {character['rarity']}",
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML
                )
            )
        elif "img_url" in character:
            results.append(
                InlineQueryResultPhoto(
                    id=f"{character['id']}_{time.time()}",
                    photo_url=character["img_url"],
                    thumb_url=character["img_url"],
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML
                )
            )

    # Inline query ka answer
    await inline_query.answer(
        results=results,
        cache_time=5,
        next_offset=next_offset,
        is_personal=True
    )