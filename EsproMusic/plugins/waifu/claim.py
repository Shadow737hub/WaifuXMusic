import asyncio
from datetime import datetime, timedelta
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from EsproMusic import app
from EsproMusic.core.mongo import mongodb

# MongoDB collections
user_collection = mongodb.user_collection
collection = mongodb.character_collection

# Support channel ID
SUPPORT_CHAT = "WaifuxDb"

# Claim lock to prevent double claims
claim_lock = {}

async def format_time_delta(delta: timedelta) -> str:
    seconds = delta.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s" if hours or minutes or seconds else "0s"

async def get_unique_characters(user_id: int, target_rarities=['⚪️ Common', '🟠 Nobel']):
    try:
        user_data = await user_collection.find_one({'id': user_id}, {'characters.id': 1})
        claimed_ids = [char['id'] for char in user_data.get('characters', [])] if user_data else []

        pipeline = [
            {'$match': {'rarity': {'$in': target_rarities}, 'id': {'$nin': claimed_ids}}},
            {'$sample': {'size': 1}}
        ]
        cursor = collection.aggregate(pipeline)
        characters = await cursor.to_list(length=None)
        return characters if characters else []
    except Exception as e:
        print(f"Error retrieving unique characters: {e}")
        return []

@app.on_message(filters.command(["hclaim", "claim", "sclaim"]))
async def mclaim(client, message: Message):
    user_id = message.from_user.id
    mention = message.from_user.mention

    if user_id in claim_lock:
        await message.reply_text("⚠️ Your claim request is already being processed. Please wait.")
        return

    claim_lock[user_id] = True
    try:
        # Ensure the user is in the support chat
        if str(message.chat.id) != SUPPORT_CHAT:
            join_button = InlineKeyboardMarkup([[InlineKeyboardButton("Join Here", url=f"https://t.me/{SUPPORT_CHAT}")]])
            return await message.reply_text(
                "🔔 Please join our support channel to claim your daily character 🔔",
                reply_markup=join_button
            )

        # Fetch or create user
        user_data = await user_collection.find_one({'id': user_id})
        if not user_data:
            user_data = {
                'id': user_id,
                'username': message.from_user.username,
                'characters': [],
                'last_daily_reward': None
            }
            await user_collection.insert_one(user_data)

        # Check if already claimed today
        last_claimed_date = user_data.get('last_daily_reward')
        if last_claimed_date and last_claimed_date.date() == datetime.utcnow().date():
            remaining_time = timedelta(days=1) - (datetime.utcnow() - last_claimed_date)
            formatted_time = await format_time_delta(remaining_time)
            return await message.reply_text(f"⏳ You've already claimed today! Next reward in: `{formatted_time}`")

        # Fetch a unique character
        unique_characters = await get_unique_characters(user_id)
        if not unique_characters:
            return await message.reply_text("🚫 No characters available to claim at the moment. Please try again later.")

        # Update user with the new character and claim time
        await user_collection.update_one(
            {'id': user_id},
            {'$push': {'characters': {'$each': unique_characters}}, '$set': {'last_daily_reward': datetime.utcnow()}}
        )

        # Send character(s) to user
        for character in unique_characters:
            await message.reply_photo(
                photo=character['img_url'],
                caption=(
                    f"🎊 Congratulations {mention}! 🎉\n"
                    f"🍂 Name : {character['name']}\n"
                    f"🎭 Rarity : {character['rarity']}\n"
                    f"⛩️ Anime : {character['anime']}\n"
                    f"🥂 Come back tomorrow to claim another character!"
                )
            )

    except Exception as e:
        print(f"Error in mclaim command: {e}")
        await message.reply_text("❌ An unexpected error occurred.")

    finally:
        claim_lock.pop(user_id, None)