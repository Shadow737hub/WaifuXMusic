from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from EsproMusic import app
from EsproMusic.core.mongo import mongodb

# MongoDB users collection
user_collection = mongodb.users


@app.on_message(filters.command("fav"))
async def fav_command(client, message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        await message.reply_text("Please provide a character ID. ❌")
        return

    character_id = message.command[1]

    # Fetch user from MongoDB
    user = await user_collection.find_one({"id": user_id})
    if not user:
        await message.reply_text("You have not guessed any characters yet. ❌")
        return

    # Find character in user's collection
    character = next((c for c in user.get("characters", []) if c["id"] == character_id), None)
    if not character:
        await message.reply_text("This character is not in your collection. ❌")
        return

    # Inline keyboard
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"fav_yes_{character_id}_{user_id}"),
                InlineKeyboardButton("❎ No", callback_data="fav_no")
            ]
        ]
    )

    caption = f"Add {character['name']} to favorites?"

    # Send media with buttons
    if 'vid_url' in character:
        await message.reply_video(video=character['vid_url'], caption=caption, reply_markup=keyboard)
    elif 'img_url' in character:
        await message.reply_photo(photo=character['img_url'], caption=caption, reply_markup=keyboard)
    else:
        await message.reply_text("This character has no media (image or video) associated with it. ❌")


# Handle "Yes" click
@app.on_callback_query(filters.regex(r"fav_yes_(.+?)_(\d+)"))
async def fav_yes(client, callback_query: CallbackQuery):
    character_id, user_id = callback_query.data.split("_")[2], int(callback_query.data.split("_")[3])

    # Ensure only the correct user can add
    if callback_query.from_user.id != user_id:
        await callback_query.answer("This button is not for you! ❌", show_alert=True)
        return

    # Fetch user and update favorites
    user = await user_collection.find_one({"id": user_id})
    if not user:
        await callback_query.message.reply_text("User not found. ❌")
        return

    character = next((c for c in user.get("characters", []) if c["id"] == character_id), None)
    if not character:
        await callback_query.message.reply_text("Character not found in your collection. ❎")
        return

    # Add to favorites (without overwriting old ones)
    favorites = user.get("favorites", [])
    if character_id not in favorites:
        favorites.append(character_id)

    await user_collection.update_one({"id": user_id}, {"$set": {"favorites": favorites}})

    await callback_query.message.edit_caption(f"{character['name']} has been added to your favorites! ✅")
    await callback_query.answer("Character added to favorites. ✅")


# Handle "No" click
@app.on_callback_query(filters.regex(r"fav_no"))
async def fav_no(client, callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.answer("Action canceled.")