import random
from EsproMusic import app

# Random emojis list
emojis = ["👍", "😘", "❤️", "🔥", "🥰", "🤩", "💘", "😏", "🤯", "⚡️", "🏆", "🤭", "🎉"]

async def react_to_message(chat_id: int, message_id: int):
    # Random emoji select
    random_emoji = random.choice(emojis)

    try:
        await app.set_message_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=[{"type": "emoji", "emoji": random_emoji}]
        )
        print(f"✅ Reaction {random_emoji} set successfully!")
    except Exception as e:
        print(f"❌ Failed to set reaction: {e}")