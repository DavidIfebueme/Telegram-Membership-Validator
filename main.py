from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import psycopg2
from db_connection import connect_db
from admin import get_payments_list, mark_as_paid, show_pending_payments
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_API = os.getenv("TELEGRAM_BOT_API")
DATABASE_URL = os.getenv("DATABASE_URL")


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi. Welcome! To start, please provide the Telegram username of the account you joined the group with.")

def handle_username(update: Update, context: CallbackContext):
    username = update.message.text.strip()

    if not username.startswith("@"):
        username = f"@{username}"

    bot = context.bot

    try:
        user = bot.get_chat(username)
        chat_id = user.id
        print(f"Chat ID: {chat_id}")
        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO users (chat_id, username) VALUES (%s, %s) ON CONFLICT (chat_id) DO NOTHING",
            (chat_id, username)
        )

        # Check group membership
        group_id = "-4561253163"  # Replace with your group ID
        member = bot.get_chat_member(group_id, chat_id)
        if member.status in ['member', 'administrator', 'creator']:
            cursor.execute("SELECT paid FROM users WHERE chat_id = %s", (chat_id,))
            result = cursor.fetchone()

            if result and not result[0]:
                update.message.reply_text("Nice! Thanks for joining the group. Please provide your account details.")
                context.user_data['chat_id'] = chat_id
            else:
                update.message.reply_text("You've been paid already or you're not eligible.")
        else:
            update.message.reply_text("You are not a member of the group. Join the group broski")
        connection.close()
    except Exception as e:
        update.message.reply_text(f"Error: {e}")  # Show error details for debugging
    print(f"Exception: {e}") 


def handle_account_details(update: Update, context: CallbackContext):
    account_details = update.message.text
    chat_id = context.user_data.get('chat_id')

    if chat_id:
        connection = connect_db()
        cursor = connection.cursor()
        
        # Insert into payments_list, ensuring no duplicates
        cursor.execute(
            "INSERT INTO payments_list (chat_id, account_details) VALUES (%s, %s) ON CONFLICT (chat_id) DO NOTHING",
            (chat_id, account_details)
        )
        connection.commit()
        connection.close()
        
        update.message.reply_text("You have been added to the payments list. You'll receive payment soon.")
    else:
        update.message.reply_text("Something went wrong. Start again.")



def main():
    updater = Updater(TELEGRAM_BOT_API, use_context=True)
    dp = updater.dispatcher

    # Command to start the bot
    dp.add_handler(CommandHandler("start", start))

    # Handler for capturing usernames
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_username))

    # Command to show the pending payments list
    dp.add_handler(CommandHandler("get_payments_list", show_pending_payments))  # Updated function name

    # Command to mark users as paid
    dp.add_handler(CommandHandler("mark_as_paid", mark_as_paid, pass_args=True))  # Mark users as paid

    # Handler for capturing account details (requires custom logic to trigger this step)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_account_details))

    # Start polling for updates
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()        