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
            InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper"),
            InlineKeyboardButton(text="💖 Waifu", url=f"https://t.me/{app.username}?start=waifu"),
        ],
        # 🆘 Support + 📢 Updates
        [
            InlineKeyboardButton(text="🆘 Support", url=config.SUPPORT_CHAT),
            InlineKeyboardButton(text="📢 Updates", url=config.SUPPORT_CHANNEL),
        ],
        # ➕ Add To Group
        [
            InlineKeyboardButton(
                text="➕ Add me to your group",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        # 👑 Owner
        [
            InlineKeyboardButton(text="👑 Owner", user_id=config.OWNER_ID),
        ],
    ]
    return buttons