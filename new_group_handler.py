from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from telegram.error import BadRequest
import psycopg2
from db_connection import connect_db

def handle_bot_added(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.type in ["group", "supergroup"]:
        try:
            connection = connect_db()
            cursor = connection.cursor()

            # Fetch group members
            members_added = 0
            for member in bot.get_chat_administrators(chat.id):
                user = member.user
                cursor.execute(
                    "INSERT INTO users (chat_id, username, paid) VALUES (%s, %s, %s) ON CONFLICT (chat_id) DO NOTHING",
                    (user.id, user.username or "Unknown", True),
                )
                members_added += 1

            connection.commit()
            connection.close()

            # Notify success
            context.bot.send_message(
                chat_id=chat.id,
                text=f"Successfully added {members_added} existing members to the database."
            )
        except Exception as e:
            context.bot.send_message(chat_id=chat.id, text=f"Error syncing members: {e}")
