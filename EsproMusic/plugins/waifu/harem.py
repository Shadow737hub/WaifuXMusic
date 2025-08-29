from pyrogram import Client
import asyncio
import math
import random
from html import escape

from pyrogram import enums, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from EsproMusic.unit.rarity import rarity_map2
from EsproMusic import app
from EsproMusic.misc import SUDOERS
from EsproMusic.core.mongo import mongodb
import config

# MongoDB collections
collection = mongodb.character_collection
user_collection = mongodb.user_collection

# Support channel
SUPPORT_CHANNEL = config.SUPPORT_CHAT

# Use rarity_map2 for emojis (define as per your setup)
rarity_map2 = {
    "⚪️ Comman": "⚪️",
    "🟠 Nobel": "🟠",
    "⭐ Legendary": "⭐",
    "🌟 Limited Edition": "🌟",
    "💎 Exclusive": "💎"
}

async def check_support_channel(client, user_id: int) -> bool:
    if user_id == config.OWNER_ID or user_id in SUDOERS:
        return True
    try:
        await client.get_chat_member(SUPPORT_CHANNEL, user_id)
        return True
    except Exception:
        return False

async def fetch_user_characters(user_id: int):
    user = await user_collection.find_one({"id": user_id})
    if not user or 'characters' not in user:
        return None, 'You have not guessed any characters yet.'
    characters = [c for c in user['characters'] if 'id' in c]
    if not characters:
        return None, 'No valid characters found in your collection.'
    return characters, None

@app.on_message(filters.command(["harem", "collection"]))
async def harem_handler(client, message: Message):
    user_id = message.from_user.id
    if not await check_support_channel(client, user_id):
        keyboard = [[InlineKeyboardButton("Join Support Channel", url=f"{SUPPORT_CHANNEL}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            f"Please join our support channel to use this command!",
            reply_markup=reply_markup
        )
        return

    page = 0
    user = await user_collection.find_one({"id": user_id})
    filter_rarity = user.get('filter_rarity', None) if user else None
    msg = await display_harem(client, message, user_id, page, filter_rarity, is_initial=True)

    await asyncio.sleep(180)
    try:
        await msg.delete()
    except Exception:
        pass

async def display_harem(client, message, user_id, page, filter_rarity, is_initial=False, callback_query=None):
    try:
        if not is_initial and not await check_support_channel(client, user_id):
            keyboard = [[InlineKeyboardButton("Join Support Channel", url=f"{SUPPORT_CHANNEL}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await callback_query.message.edit_text(
                f"Please join our support channel to view your harem!",
                reply_markup=reply_markup
            )
            return

        characters, error = await fetch_user_characters(user_id)
        if error:
            if is_initial:
                await message.reply_text(error)
            else:
                await callback_query.message.edit_text(error)
            return

        total_characters = len(characters)
        amv_characters = len([c for c in characters if 'vid_url' in c])

        characters = sorted(characters, key=lambda x: (x.get('anime', ''), x.get('id', '')))
        if filter_rarity:
            characters = [c for c in characters if c.get('rarity') == filter_rarity]
            if not characters:
                keyboard = [[InlineKeyboardButton("Remove Filter", callback_data=f"remove_filter:{user_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if is_initial:
                    await message.reply_text(
                        f"No characters found with rarity: **{filter_rarity}**. Click below to remove filter.",
                        reply_markup=reply_markup
                    )
                else:
                    await callback_query.message.edit_text(
                        f"No characters found with rarity: **{filter_rarity}**. Click below to remove filter.",
                        reply_markup=reply_markup
                    )
                return

        character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}
        unique_characters = list({c['id']: c for c in characters}.values())
        total_pages = max(math.ceil(len(unique_characters) / 15), 1)

        if page < 0 or page >= total_pages:
            page = 0

        harem_message = f"<b>{escape(message.from_user.first_name)}'s Harem - Page {page+1}/{total_pages}</b>\n"
        if filter_rarity:
            harem_message += f"<b>Filtered by: {filter_rarity}</b>\n"

        current_characters = unique_characters[page * 15:(page + 1) * 15]
        current_grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

        for anime, chars in current_grouped_characters.items():
            harem_message += f'\n<b>{anime} {len(chars)}/{await collection.count_documents({"anime": anime})}</b>\n'
            for character in chars:
                count = character_counts[character['id']]
                rarity_emoji = rarity_map2.get(character.get('rarity'), '')
                harem_message += f'◈⌠{rarity_emoji}⌡ {character["id"]} {character["name"]} ×{count}\n'

        keyboard = [[InlineKeyboardButton(f"Slaves ({total_characters})", switch_inline_query_current_chat=f"collection.{user_id}")]]
        if total_pages > 1:
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"harem:{page-1}:{user_id}:{filter_rarity or 'None'}"))
            if page < total_pages - 1:
                nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"harem:{page+1}:{user_id}:{filter_rarity or 'None'}"))
            keyboard.append(nav_buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)
        image_character = random.choice(characters) if characters else None

        if is_initial:
            if image_character:
                if 'vid_url' in image_character:
                    return await message.reply_video(video=image_character['vid_url'], caption=harem_message, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                elif 'img_url' in image_character:
                    return await message.reply_photo(photo=image_character['img_url'], caption=harem_message, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
            return await message.reply_text(harem_message, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        else:
            if image_character:
                media_url = image_character.get('vid_url') or image_character.get('img_url')
                await callback_query.message.edit_media(
                    media=enums.InputMediaPhoto(media_url, caption=harem_message),
                    reply_markup=reply_markup
                )
            else:
                await callback_query.message.edit_text(harem_message, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)

    except Exception as e:
        print(f"Error in display_harem: {e}")
        if is_initial:
            await message.reply_text("An error occurred. Please try again later.")
        else:
            await callback_query.message.edit_text("An error occurred. Please try again later.")


@app.on_callback_query(filters.regex(r"^remove_filter"))
async def remove_filter_callback(client: app, callback_query: CallbackQuery):
    try:
        _, user_id = callback_query.data.split(':')
        user_id = int(user_id)

        if callback_query.from_user.id != user_id:
            return await callback_query.answer("It's not your Harem!", show_alert=True)

        if not await check_support_channel(client, user_id):
            keyboard = [[InlineKeyboardButton("Join Support Channel", url=f"{SUPPORT_CHANNEL}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await callback_query.message.edit_text(
                f"Please join our support channel to use this feature!",
                reply_markup=reply_markup
            )
            return

        await user_collection.update_one({"id": user_id}, {"$set": {"filter_rarity": None}}, upsert=True)
        await callback_query.message.delete()
        await callback_query.answer("Filter removed. Showing all rarities.", show_alert=True)
    except Exception as e:
        print(f"Error in remove_filter callback: {e}")


@app.on_callback_query(filters.regex(r"^harem"))
async def harem_callback(client: app, callback_query: CallbackQuery):
    try:
        _, page, user_id, filter_rarity = callback_query.data.split(':')
        page, user_id = int(page), int(user_id)
        filter_rarity = None if filter_rarity == 'None' else filter_rarity

        if callback_query.from_user.id != user_id:
            return await callback_query.answer("It's not your Harem!", show_alert=True)

        await display_harem(client, callback_query.message, user_id, page, filter_rarity, is_initial=False, callback_query=callback_query)
    except Exception as e:
        print(f"Error in harem callback: {e}")


@app.on_message(filters.command("hmode"))
async def hmode_handler(client: Client, message: Message):
    user_id = message.from_user.id

    # Check support channel membership
    if not await check_support_channel(client, user_id):
        keyboard = [[InlineKeyboardButton("Join Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL.lstrip('@')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            f"Please join our support channel {SUPPORT_CHANNEL} to use this command!",
            reply_markup=reply_markup
        )
        return

    # Build rarity selection keyboard
    keyboard = []
    row = []
    for i, (rarity, emoji) in enumerate(rarity_map2.items(), 1):
        row.append(InlineKeyboardButton(emoji, callback_data=f"set_rarity:{user_id}:{rarity}"))
        if i % 4 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("All", callback_data=f"set_rarity:{user_id}:None")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Select a rarity to filter your harem:", reply_markup=reply_markup)

@app.on_callback_query(filters.regex(r"^set_rarity"))
async def set_rarity_callback(client: Client, callback_query: CallbackQuery):
    try:
        _, user_id, filter_rarity = callback_query.data.split(':')
        user_id = int(user_id)
        filter_rarity = None if filter_rarity == 'None' else filter_rarity

        if callback_query.from_user.id != user_id:
            await callback_query.answer("It's not your Harem!", show_alert=True)
            return

        # Check support channel membership
        if not await check_support_channel(client, user_id):
            keyboard = [[InlineKeyboardButton("Join Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL.lstrip('@')}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await callback_query.message.edit_text(
                f"Please join our support channel {SUPPORT_CHANNEL} to use this feature!",
                reply_markup=reply_markup
            )
            return

        # Update user's filter_rarity in MongoDB
        await user_collection.update_one({"id": user_id}, {"$set": {"filter_rarity": filter_rarity}}, upsert=True)

        # Edit message to show which rarity is set
        if filter_rarity:
            await callback_query.message.edit_text(f"Rarity filter set to: **{filter_rarity}**")
        else:
            await callback_query.message.edit_text("Rarity filter cleared. Showing all rarities.")

        await callback_query.answer(f"Rarity filter set to {filter_rarity if filter_rarity else 'All'}", show_alert=True)

    except Exception as e:
        print(f"Error in set_rarity callback: {e}")