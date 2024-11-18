from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from telegram.ext import ChatMemberHandler
from telegram.error import BadRequest
import psycopg2
from db_connection import connect_db

def add_members_to_db(update: Update, context: CallbackContext):
    bot = context.bot
    chat_id = update.effective_chat.id

    try:
        # Check if the bot is added to the group
        if update.my_chat_member.new_chat_member.status in ["member", "administrator"]:
            update.message.reply_text("Validaor bot here! Performing initial sweep...")

            connection = connect_db()
            cursor = connection.cursor()

            # Fetch all members
            members_added = 0
            try:
                for member in bot.get_chat_administrators(chat_id):
                    user = member.user
                    cursor.execute(
                        "INSERT INTO users (chat_id, username, paid) VALUES (%s, %s, %s) ON CONFLICT (chat_id) DO NOTHING",
                        (user.id, user.username or "Unknown", True),
                    )
                    members_added += 1
            except Exception as e:
                print(f"Error fetching members: {e}")

            connection.commit()
            connection.close()

            update.message.reply_text(f"Synced {members_added} members with `paid=True`.")
            print("Initial sweep completed")
            print(f"Nuumber of members added to the database: {members_added}")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")
