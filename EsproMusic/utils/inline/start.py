from pyrogram.types import InlineKeyboardButton

import config
from EsproMusic import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        # 🎵 Music + 💖 Waifu
        [
            InlineKeyboardButton(text="🎵 ᴍᴜsɪᴄ 🎶", callback_data="settings_back_helper"),
            InlineKeyboardButton(text="🔮 ᴡᴀɪғᴜ 🔮", callback_data="waifu_help"),
        ],
        # 🆘 Support + 📢 Updates
        [
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
            InlineKeyboardButton(text=_["S_B_3"], url=config.SUPPORT_CHANNEL),
        ],
        # ➕ Add To Group
        [
            InlineKeyboardButton(
                text="➕ ᴋɪᴅɴᴀᴘᴘᴇ ᴍᴇ ➕",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        # 👑 Owner
        [
            InlineKeyboardButton(text="🍸 ᴅᴇᴠᴇʟᴏᴘᴇʀ 🍸", user_id=config.OWNER_ID),
        ],
    ]
    return buttons