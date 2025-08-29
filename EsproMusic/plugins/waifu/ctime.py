from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message
from EsproMusic import app
from EsproMusic.misc import SUDOERS
from EsproMusic.core.mongo import mongodb
import config  # Import your config

# MongoDB collection for group user totals
group_user_totals_collection = mongodb.group_user_totals_collection

async def is_admin(client, chat_id: int, user_id: int) -> bool:
    """
    Check if the user is an admin or owner of the chat.
    Returns True if user is admin/owner or a SUDO user.
    """
    if user_id in SUDOERS:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        print(f"Error checking admin: {e}")
        return False


@app.on_message(filters.command("ctime") & filters.group)
async def set_ctime(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check permissions
    is_owner = user_id == config.OWNER_ID
    is_admin_user = await is_admin(client, chat_id, user_id) if not is_owner else True

    if not (is_owner or is_admin_user):
        await message.reply_text("⚠️ Only group admins or bot owner can set this.")
        return

    # Parse the ctime argument
    try:
        ctime = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply_text("⚠️ Please provide a number (e.g., /ctime 80).")
        return

    # Permission-based validation
    if is_owner:
        if not 1 <= ctime <= 200:
            await message.reply_text("⚠️ Bot owner can set ctime between 1 and 200.")
            return
    else:
        if not 80 <= ctime <= 200:
            await message.reply_text("⚠️ Admins can set ctime between 80 and 200.")
            return

    # Update MongoDB
    await group_user_totals_collection.update_one(
        {"group_id": str(chat_id)},
        {"$set": {"ctime": ctime}},
        upsert=True
    )

    await message.reply_text(f"✅ Message count threshold set to {ctime} for this group.")