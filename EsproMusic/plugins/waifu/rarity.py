from EsproMusic import app
from EsproMusic.core.mongo import mongodb
from pyrogram import filters, enums

# Use the characters collection from MongoDB
collection = mongodb.character_collection

@app.on_message(filters.command("rarity"))
async def rarity_count(client, message):
    try:
        # Fetch distinct rarities from the characters collection
        distinct_rarities = await collection.distinct('rarity')

        if not distinct_rarities:
            await message.reply_text("⚠️ No rarities found in the database.")
            return

        # Optional: sort rarities alphabetically
        distinct_rarities = sorted([r for r in distinct_rarities if r])

        response_message = "✨ <b>Character Count by Rarity</b> ✨\n\n"

        for rarity in distinct_rarities:
            count = await collection.count_documents({'rarity': rarity})
            response_message += f"◈ {rarity} — <b>{count}</b> character(s)\n"

        await message.reply_text(response_message, parse_mode=enums.ParseMode.HTML)

    except Exception as e:
        await message.reply_text(f"⚠️ Error: {str(e)}")