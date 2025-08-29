
HELP_DATA = {
    "balance": {
        "HELP_NAME": "Bᴀʟ Aɴᴅ Pᴀʏ",
        "HELP": """
💰 **Balance Commands**:
- `/balance` → Check your balance.
- `/balance @username` → Check another user's balance.
- `/balance user_id` → Check balance using user ID.

💳 **Payment Commands**:
- `/pay amount @username` → Send coins to a user.
- `/pay amount user_id` → Send coins using user ID.
- `/pay amount` (reply to a user) → Send coins to the replied user.

⚠ **Note**:
- You must have enough balance to send coins.
- Payments are final and cannot be reversed.
"""
    },
    "check": {
        "HELP_NAME": "Cʜᴇᴄᴋ",
        "HELP": """
Use `/check <character_id>` to view details of a character.

- Displays character ID, name, anime, and rarity.
- Shows an image or video if available.
- Use the 'Who Have It' button to see the top 10 owners.
"""
    },
    "guess": {
        "HELP_NAME": "Gᴜᴇss",
        "HELP": """
Use `/guess <character_name>` to guess the mystery character.

- Earn 40 coins for a correct guess.
- The first correct guess captures the character.
- If incorrect, you can try again.
- A 'See Harem' button lets you view your collected characters.
"""
    },
    "harem": {
        "HELP_NAME": "Hᴀʀᴇᴍ",
        "HELP": """
Use `/harem` or `/collection` to view your collected characters.

- Navigate pages using the buttons.
- Filter by rarity using the filter button.
- Use "Collection" button for detailed inline view.

Characters are grouped by anime and show the count you own.
"""
    },
    "inline": {
        "HELP_NAME": "Iɴʟɪɴᴇ",
        "HELP": """
Use inline queries to search for characters or view collections.

- `@Waifuxx_bot query` → Search for characters.
- `@Waifuxx_bot collection.<user_id>` → View a user's character collection.
- `@Waifuxx_bot collection.<user_id> <name>` → Search within a user's collection.

Results include character name, anime, rarity, and image.
"""
    },
    "favorites": {
        "HELP_NAME": "Fᴀᴠᴏʀɪᴛᴇs",
        "HELP": """
Add your favorite characters to your collection.

- `/fav <character_id>` → Add a character to your favorites.
- Click "✅ Yes" to confirm or "❎ No" to cancel.
- Your favorite characters will be saved for quick access.

Note: You can only favorite characters that are in your collection.
"""
    },
    "claim": {
        "HELP_NAME": "Cʟᴀɪᴍ",
        "HELP": """
Claim a free character every day! 🌟

- `/hclaim` or `/claim` → Claim your daily character.
- You must be in the required channel to claim.
- If you've already claimed today, you'll see the time remaining for the next claim.
- Characters are unique and not repeated from your collection.
- Return tomorrow for another claim! 🌸
"""
    },
    "gift": {
        "HELP_NAME": "Gɪғᴛ",
        "HELP": """
🎁 **Gift System**  
Send characters to other users using the `/gift` command.

**Commands:**
- `/gift <character_id>` (Reply to a user's message)  
  ┗ Gift a character to another user.

**How it works:**
1. Reply to a user's message.
2. Use `/gift <character_id>` to send a character.
3. The receiver gets a confirmation message.
4. The gift is auto-canceled if not confirmed within 1 hour.
"""
    },
    "rankings": {
        "HELP_NAME": "Rᴀɴᴋɪɴɢs",
        "HELP": """
🏆 **Rankings & Leaderboards**  
Check out the top users and groups in different categories!

**Commands:**
- `/rank`  
  ┗ View the Top 10 Users with the most characters.

**Categories:**
1. **Top Users** → Users with the highest number of characters.
2. **Top Groups** → Groups that have guessed the most characters.
3. **CTOP** → Users ranked by the highest coin balance.

**How it works:**
- `/rank` will display the top 10 users based on character count.
- You can switch between Top Users, Top Groups, and MTOP using the buttons.
- Rankings update dynamically as users collect characters or earn coins.
"""
    },
    "sips": {
        "HELP_NAME": "Sɪᴘs",
        "HELP": """
Use this command to search for characters by name.

Commands:
- /sips <character_name> → Search for a character by name.
- Pagination buttons will appear if multiple results are found.

Each result includes:
- Character name
- Anime name
- Character ID
- Rarity indicator
"""
    },
    "shop": {
        "HELP_NAME": "Sʜᴏᴘ",
        "HELP": """
🛒 Shop Commands:
- /shop - Open the shop menu.
- /hshopmenu - Alternative command to open the shop.
- /hshop - Another way to access the shop.
- /addshop <id> <price> - Add a character to the shop (Admin only).

🛍 How It Works:
1. Use /shop to browse characters.
2. Click "Buy" to purchase a character.
3. Click "Next" to view more characters.
4. Make sure you have enough balance!

🔹 Enjoy shopping!
"""
    }
}