import os
import requests
import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message

from EsproMusic import app
from EsproMusic.misc import SUDOERS
from EsproMusic.core.mongo import mongodb
import config  # Import OWNER_ID, SUPPORT_CHAT, CHARA_CHANNEL_ID from here

# MongoDB collections
collection = mongodb.character_collection
user_collection = mongodb.user_collection

# Wrong format message
WRONG_FORMAT_TEXT = """Wrong ❌ format...
Use: /upload reply character-name anime-name rarity-number

Example:
    /upload reply muzan-kibutsuji Demon-slayer 3
"""

# Rarity map
rarity_map = {
    1: "⚪️ Common",
    2: "🟠 Noble",
    3: "🔥 Legendary",
    4: "💎 Limited Edition",
    5: "💠 Exclusive"
}

upload_lock = asyncio.Lock()

# Find next available character ID
async def find_available_id():
    cursor = collection.find().sort('id', 1)
    ids = []
    async for doc in cursor:
        if 'id' in doc:
            ids.append(int(doc['id']))
    ids.sort()
    for i in range(1, len(ids) + 2):
        if i not in ids:
            return str(i).zfill(2)
    return str(len(ids) + 1).zfill(2)

# Upload file to Catbox
def upload_to_catbox(file_path):
    url = "https://catbox.moe/user/api.php"
    with open(file_path, "rb") as file:
        resp = requests.post(url, data={"reqtype": "fileupload"}, files={"fileToUpload": file})
    if resp.status_code == 200 and resp.text.startswith("https"):
        return resp.text
    raise Exception(f"Upload failed: {resp.text}")

# ----------------- Commands ----------------- #

@app.on_message(filters.command(["find"]) & filters.user(list(SUDOERS)))
async def find_id(client: Client, message: Message):
    available_id = await find_available_id()
    await message.reply_text(f"Next available ID: {available_id}")

@app.on_message(filters.command(["upload"]) & filters.user(list(SUDOERS)))
async def gupload(client: Client, message: Message):
    global upload_lock

    if upload_lock.locked():
        return await message.reply_text("Another upload is in progress. Please wait.")

    async with upload_lock:
        reply = message.reply_to_message
        if not reply or not (reply.photo or reply.document or reply.video):
            return await message.reply_text("Please reply to a photo, document, or video.")

        args = message.text.split()
        if len(args) != 4:
            return await message.reply_text(WRONG_FORMAT_TEXT)

        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()
        try:
            rarity = int(args[3])
            rarity_text = rarity_map[rarity]
        except (ValueError, KeyError):
            return await message.reply_text("Invalid rarity. Check your command or rarity map.")

        available_id = await find_available_id()
        character = {'name': character_name, 'anime': anime, 'rarity': rarity_text, 'id': available_id}

        processing_msg = await message.reply("<ᴘʀᴏᴄᴇꜱꜱɪɴɢ>....")
        path = await reply.download()

        try:
            catbox_url = upload_to_catbox(path)
            if reply.photo or reply.document:
                character['img_url'] = catbox_url
                await client.send_photo(
                    chat_id=config.CHARA_CHANNEL_ID,
                    photo=catbox_url,
                    caption=f"Character Name: {character_name}\nAnime Name: {anime}\nRarity: {rarity_text}\nID: {available_id}\nAdded by [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                )
            elif reply.video:
                character['vid_url'] = catbox_url
                await client.send_video(
                    chat_id=config.CHARA_CHANNEL_ID,
                    video=catbox_url,
                    caption=f"Character Name: {character_name}\nAnime Name: {anime}\nRarity: {rarity_text}\nID: {available_id}\nAdded by [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                )

            await collection.insert_one(character)
            await message.reply_text(f"✅ Added Character ID {available_id} by {message.from_user.first_name}")

        except Exception as e:
            await message.reply_text(f"Upload failed: {str(e)}")
        finally:
            os.remove(path)
            await processing_msg.delete()