from pyrogram import filters, Client
from pyrogram.types import Message
import html

from EsproMusic import app
from EsproMusic.misc import SUDOERS
from EsproMusic.core.mongo import mongodb

# database collection
user_collection = mongodb.user_collection


# Helper to fetch balance/tokens
async def get_balance(user_id: int):
    user_data = await user_collection.find_one({'id': user_id}, {'balance': 1, 'tokens': 1})
    if user_data:
        return user_data.get('balance', 0), user_data.get('tokens', 0)
    return 0, 0


# ------------------ BALANCE COMMAND ------------------ #
@app.on_message(filters.command("balance"))
async def balance(client: Client, message: Message):
    user_id = message.from_user.id
    user_balance, user_tokens = await get_balance(user_id)
    response = (
        f"{html.escape(message.from_user.first_name)} \n◈⌠ {user_balance} coins⌡\n"
        f"◈ ⌠ {user_tokens} Tokens⌡"
    )
    await message.reply_text(response)


# ------------------ PAY COMMAND ------------------ #
@app.on_message(filters.command("pay"))
async def pay(client: Client, message: Message):
    sender_id = message.from_user.id
    args = message.command

    if len(args) < 2:
        return await message.reply_text("Usage: /pay <amount> [@username/user_id] or reply to a user.")

    try:
        amount = int(args[1])
        if amount <= 0:
            raise ValueError
    except ValueError:
        return await message.reply_text("Invalid amount. Please enter a positive number.")

    recipient_id = None
    recipient_name = None

    if message.reply_to_message:
        recipient_id = message.reply_to_message.from_user.id
        recipient_name = message.reply_to_message.from_user.first_name
    elif len(args) > 2:
        try:
            recipient_id = int(args[2])
        except ValueError:
            recipient_username = args[2].lstrip("@")
            user_data = await user_collection.find_one({'username': recipient_username}, {'id': 1, 'first_name': 1})
            if user_data:
                recipient_id = user_data['id']
                recipient_name = user_data.get('first_name', recipient_username)
            else:
                return await message.reply_text("Recipient not found. Check username or reply to a user.")

    if not recipient_id:
        return await message.reply_text("Recipient not found. Reply to a user or provide valid user ID/username.")

    # Ensure both sender & recipient exist in DB
    await user_collection.update_one({'id': sender_id}, {'$setOnInsert': {'balance': 0, 'tokens': 0}}, upsert=True)
    await user_collection.update_one({'id': recipient_id}, {'$setOnInsert': {'balance': 0, 'tokens': 0}}, upsert=True)

    sender_balance, _ = await get_balance(sender_id)
    if sender_balance < amount:
        return await message.reply_text("Insufficient balance.")

    await user_collection.update_one({'id': sender_id}, {'$inc': {'balance': -amount}})
    await user_collection.update_one({'id': recipient_id}, {'$inc': {'balance': amount}})

    updated_sender_balance, _ = await get_balance(sender_id)
    updated_recipient_balance, _ = await get_balance(recipient_id)

    recipient_display = html.escape(recipient_name or str(recipient_id))
    sender_display = html.escape(message.from_user.first_name or str(sender_id))

    await message.reply_text(
        f"✅ You paid {amount} coins to {recipient_display}.\n"
        f"💰 Your New Balance: {updated_sender_balance} coins"
    )

    await client.send_message(
        chat_id=recipient_id,
        text=f"🎉 You received {amount} coins from {sender_display}!\n"
             f"💰 Your New Balance: {updated_recipient_balance} coins"
    )


# ------------------ KILL COMMAND (SUDOERS ONLY) ------------------ #
@app.on_message(filters.command("kill") & filters.user(list(SUDOERS)))
async def kill_handler(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Please reply to a user's message to use the /kill command.")

    user_id = message.reply_to_message.from_user.id
    command_args = message.text.split()

    if len(command_args) < 2:
        return await message.reply_text(
            "Please specify an option: `c` to delete character, `f` to delete full data, or `b` to delete balance."
        )

    option = command_args[1]

    try:
        if option == 'f':
            await user_collection.delete_one({"id": user_id})
            await message.reply_text("✅ The full data of the user has been deleted.")

        elif option == 'c':
            if len(command_args) < 3:
                return await message.reply_text("Please specify a character ID to remove.")

            char_id = command_args[2]
            user = await user_collection.find_one({"id": user_id})

            if user and 'characters' in user:
                characters = user['characters']
                updated_characters = [c for c in characters if c.get('id') != char_id]

                if len(updated_characters) == len(characters):
                    return await message.reply_text(f"No character with ID {char_id} found.")

                await user_collection.update_one({"id": user_id}, {"$set": {"characters": updated_characters}})
                await message.reply_text(f"✅ Character with ID {char_id} has been removed.")
            else:
                return await message.reply_text("No characters found in the user's collection.")

        elif option == 'b':
            if len(command_args) < 3:
                return await message.reply_text("Please specify an amount to deduct from balance.")

            try:
                amount = int(command_args[2])
            except ValueError:
                return await message.reply_text("Invalid amount. Please enter a number.")

            user_data = await user_collection.find_one({"id": user_id}, {"balance": 1})
            if user_data and "balance" in user_data:
                current_balance = user_data["balance"]
                new_balance = max(0, current_balance - amount)
                await user_collection.update_one({"id": user_id}, {"$set": {"balance": new_balance}})
                await message.reply_text(f"✅ {amount} has been deducted. New balance: {new_balance}")
            else:
                return await message.reply_text("The user has no balance to deduct.")

        else:
            return await message.reply_text("Invalid option. Use `c`, `f`, or `b {amount}`.")

    except Exception as e:
        print(f"Error in /kill command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")