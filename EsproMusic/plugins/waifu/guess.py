import asyncio
import time
from html import escape
from datetime import datetime
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from EsproMusic import app
from EsproMusic.core.mongo import mongodb

# MongoDB collections
user_collection = mongodb.user_collection
top_global_groups_collection = mongodb.top_global_groups_collection

# Keep track of last character posted per chat
last_characters = {}  # chat_id: character_info
first_correct_guesses = {}  # chat_id: user_id
user_guess_progress = {}  # user_id: {"date": today, "count": N}

async def check_cooldown(user_id: int) -> bool:
    # Implement your cooldown check logic here
    return False

async def get_remaining_cooldown(user_id: int) -> int:
    # Implement remaining cooldown time
    return 0

async def react_to_message(chat_id: int, message_id: int):
    # Optional: add a reaction to the message
    pass

@app.on_message(filters.command(["guess", "protecc", "collect", "grab", "hunt", "slave"]))
async def guess(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    today = datetime.utcnow().date()

    if await check_cooldown(user_id):
        remaining_time = await get_remaining_cooldown(user_id)
        await message.reply_text(
            f"⚠️ You are still in cooldown. Please wait {remaining_time} seconds before using any commands."
        )
        return

    if chat_id not in last_characters or 'name' not in last_characters[chat_id]:
        await message.reply_text("❌ Character guess not available.")
        return

    if chat_id in first_correct_guesses:
        await message.reply_text("❌ Character guess not available.")
        return

    if last_characters[chat_id].get('ranaway', False):
        await message.reply_text("❌ THE CHARACTER HAS ALREADY RUN AWAY!")
        return

    guess_text = ' '.join(message.command[1:]).lower() if len(message.command) > 1 else ''

    if "()" in guess_text or "&" in guess_text:
        await message.reply_text("Nahh, you can't use this type of words in your guess ❌")
        return

    name_parts = last_characters[chat_id]['name'].lower().split()

    if sorted(name_parts) == sorted(guess_text.split()) or any(part == guess_text for part in name_parts):
        first_correct_guesses[chat_id] = user_id

        # Cancel expire session task if exists
        for task in asyncio.all_tasks():
            if task.get_name() == f"expire_session_{chat_id}":
                task.cancel()
                break

        timestamp = last_characters[chat_id].get('timestamp')
        time_taken_str = f"{int(time.time() - timestamp)} seconds" if timestamp else "Unknown time"

        # Track user guess progress
        if user_id not in user_guess_progress or user_guess_progress[user_id]["date"] != today:
            user_guess_progress[user_id] = {"date": today, "count": 0}
        user_guess_progress[user_id]["count"] += 1

        # Update user in MongoDB
        user = await user_collection.find_one({'id': user_id})
        if user:
            update_fields = {}
            if message.from_user.username != user.get('username'):
                update_fields['username'] = message.from_user.username
            if message.from_user.first_name != user.get('first_name'):
                update_fields['first_name'] = message.from_user.first_name
            if update_fields:
                await user_collection.update_one({'id': user_id}, {'$set': update_fields})
            await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
        else:
            await user_collection.insert_one({
                'id': user_id,
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'characters': [last_characters[chat_id]],
                'balance': 0
            })

        # Update group count
        if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            group_name = message.chat.title or f"Group_{chat_id}"
            await top_global_groups_collection.update_one(
                {'chat_id': chat_id},
                {'$set': {'group_name': group_name}, '$inc': {'count': 1}},
                upsert=True
            )

        # Update user balance
        user = await user_collection.find_one({'id': user_id})
        new_balance = user.get('balance', 0) + 40
        await user_collection.update_one({'id': user_id}, {'$set': {'balance': new_balance}})

        keyboard = [[InlineKeyboardButton("See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]]
        await message.reply_text(
            f'🌟 <b><a href="tg://user?id={user_id}">{escape(message.from_user.first_name)}</a></b>, you\'ve captured a new character! 🎊\n\n'
            f'📛 𝗡𝗔𝗠𝗘: <b>{last_characters[chat_id]["name"]}</b>\n'
            f'🌈 𝗔𝗡𝗜𝗠𝗘: <b>{last_characters[chat_id]["anime"]}</b>\n'
            f'✨ 𝗥𝗔𝗥𝗜𝗧𝗬: <b>{last_characters[chat_id]["rarity"]}</b>\n'
            f'⏱️ 𝗧𝗜𝗠𝗘 𝗧𝗔𝗞𝗘𝗡: <b>{time_taken_str}</b>\n\n'
            f'This character has been added to your Harem. Use /harem to see your collection.',
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    else:
        message_id = last_characters[chat_id].get('message_id')
        keyboard = [[InlineKeyboardButton("See Media Again", url=f"https://t.me/c/{str(chat_id)[4:]}/{message_id}")]] if message_id else None
        await message.reply_text(
            '❌ Not quite right, brave guesser! Try again and unveil the mystery character! 🕵️‍♂️',
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
        )