import time
from pyrogram import filters
from pyrogram.types import Message

from EsproMusic import app
from EsproMusic.misc import SUDOERS
from EsproMusic.core.mongo import mongodb
from EsproMusic.unit.rarity import rarity_map  # Make sure you have rarity_map here

# MongoDB collections
collection = mongodb.character_collection
user_collection = mongodb.user_collection

SUDO_USERS = SUDOERS

# ---------------- Delete Character ---------------- #
@app.on_message(filters.command("delete") & filters.user(list(SUDO_USERS)))
async def delete_handler(client, message: Message):
    try:
        args = message.text.split()
        if len(args) != 2:
            return await message.reply_text("Incorrect format... Please use: /gdelete ID")

        character_id = args[1]
        character = await collection.find_one_and_delete({'id': character_id})

        if character:
            result = await user_collection.update_many(
                {'characters.id': character_id},
                {'$pull': {'characters': {'id': character_id}}}
            )
            await message.reply_text(
                f"Character with ID {character_id} deleted successfully.\n"
                f"Removed from {result.modified_count} user collections."
            )
        else:
            await message.reply_text(f"Character with ID {character_id} not found.")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")


# ---------------- Update Character ---------------- #
@app.on_message(filters.command("gupdate") & filters.user(list(SUDO_USERS)))
async def update(client, message: Message):
    try:
        args = message.text.split()
        if len(args) != 4:
            return await message.reply_text("Incorrect format. Use: /gupdate id field new_value")

        character_id = args[1]
        field_to_update = args[2]
        new_value = args[3]

        valid_fields = ['img_url', 'vid_url', 'name', 'anime', 'rarity']
        if field_to_update not in valid_fields:
            return await message.reply_text(f"Invalid field. Use one of: {', '.join(valid_fields)}")

        if field_to_update in ['name', 'anime']:
            new_value = new_value.replace('-', ' ').title()
        elif field_to_update == 'rarity':
            try:
                new_value = rarity_map[int(new_value)]
            except (KeyError, ValueError):
                return await message.reply_text("Invalid rarity number.")

        result = await collection.update_one({'id': character_id}, {'$set': {field_to_update: new_value}})
        if result.modified_count == 0:
            return await message.reply_text("Character not found or no changes made.")

        users_cursor = user_collection.find({'characters.id': character_id})
        total_users = await user_collection.count_documents({'characters.id': character_id})
        if total_users == 0:
            return await message.reply_text("Character updated successfully ✅")

        progress_msg = await message.reply_text("Updating: 0% completed...")
        updated_count = 0
        next_progress_update = 10

        async for user in users_cursor:
            await user_collection.update_one(
                {'_id': user['_id'], 'characters.id': character_id},
                {'$set': {f'characters.$.{field_to_update}': new_value}}
            )
            updated_count += 1
            progress = (updated_count / total_users) * 100
            if progress >= next_progress_update:
                await progress_msg.edit_text(f"Updating: {int(progress)}% completed...")
                next_progress_update += 10
                time.sleep(1)

        await progress_msg.edit_text("Updating: 100% completed.")
        await message.reply_text(f"Successfully updated ✅\nTotal users updated: {updated_count}/{total_users}")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")


# ---------------- Update Multiple Characters ---------------- #
@app.on_message(filters.command("maxupdate") & filters.user(list(SUDO_USERS)))
async def update_multiple(client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 4:
            return await message.reply_text("Incorrect format. Use: /maxupdate id1,id2,id3 field new_value")

        character_ids = args[1].split(',')
        field_to_update = args[2]
        new_value = ' '.join(args[3:])

        valid_fields = ['img_url', 'vid_url', 'name', 'anime', 'rarity']
        if field_to_update not in valid_fields:
            return await message.reply_text(f"Invalid field. Use one of: {', '.join(valid_fields)}")

        if field_to_update in ['name', 'anime']:
            new_value = new_value.replace('-', ' ').title()
        elif field_to_update == 'rarity':
            try:
                new_value = rarity_map[int(new_value)]
            except (KeyError, ValueError):
                return await message.reply_text("Invalid rarity number.")

        total_characters = len(character_ids)
        updated_characters = 0
        total_users_updated = 0
        progress_msg = await message.reply_text("Updating: 0% completed...")
        next_progress_update = 10

        for i, character_id in enumerate(character_ids, start=1):
            result = await collection.update_one({'id': character_id}, {'$set': {field_to_update: new_value}})
            if result.modified_count == 0:
                continue

            users_cursor = user_collection.find({'characters.id': character_id})
            async for user in users_cursor:
                await user_collection.update_one(
                    {'_id': user['_id'], 'characters.id': character_id},
                    {'$set': {f'characters.$.{field_to_update}': new_value}}
                )
                total_users_updated += 1

            updated_characters += 1
            progress = (i / total_characters) * 100
            if progress >= next_progress_update:
                await progress_msg.edit_text(f"Updating: {int(progress)}% completed...")
                next_progress_update += 10
                time.sleep(1)

        await progress_msg.edit_text("Updating: 100% completed.")
        await message.reply_text(
            f"Successfully updated ✅\nTotal characters updated: {updated_characters}/{total_characters}\n"
            f"Total users updated: {total_users_updated}"
        )

    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")


# ---------------- Find Anime IDs ---------------- #
@app.on_message(filters.command("findani") & filters.user(list(SUDO_USERS)))
async def find_anime_ids(client, message: Message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return await message.reply_text("Please provide an anime name. Usage: /findani {anime name}")

        anime_name = args[1].strip().lower()
        characters_cursor = collection.find({"anime": {"$regex": f"^{anime_name}$", "$options": "i"}}, {"id": 1})
        character_ids = [str(char['id']) async for char in characters_cursor]

        if not character_ids:
            return await message.reply_text(f"No characters found for anime: {anime_name}")

        ids_list = ",".join(character_ids)
        await message.reply_text(f"Character IDs for '{anime_name}':\n{ids_list}")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")