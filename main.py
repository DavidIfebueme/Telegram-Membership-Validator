from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import psycopg2
from db_connection import connect_db
from admin import get_payments_list, mark_as_paid, show_pending_payments
from new_group_handler import handle_bot_added
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_API = os.getenv("TELEGRAM_BOT_API")
DATABASE_URL = os.getenv("DATABASE_URL")


USERNAME, ACCOUNT_DETAILS = range(2)  # Define states

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi. Welcome! To start, please provide the Telegram username of the account you joined the group with.")
    return USERNAME

def handle_username(update: Update, context: CallbackContext):
    username = update.message.text.strip()

    if not username.startswith("@"):
        username = f"@{username}"

    user_id = update.effective_user.id
    bot = context.bot

    try:
        group_id = "-4561253163"
        member = bot.get_chat_member(group_id, user_id)
        chat_id = user_id

        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO users (chat_id, username) VALUES (%s, %s) ON CONFLICT (chat_id) DO NOTHING",
            (chat_id, username)
        )

        if member.status in ['member', 'administrator', 'creator']:
            cursor.execute("SELECT paid FROM users WHERE chat_id = %s", (chat_id,))
            result = cursor.fetchone()

            if result and not result[0]:
                update.message.reply_text("Nice! Thanks for joining the group. Please provide your account details.")
                context.user_data['chat_id'] = chat_id
                return ACCOUNT_DETAILS
            else:
                update.message.reply_text("You've been paid already or you're not eligible.")
                return ConversationHandler.END
        else:
            update.message.reply_text("You are not a member of the group. Join the group broski.")
            return ConversationHandler.END
    except Exception as e:
        update.message.reply_text(f"Error: {e}")
        return ConversationHandler.END

def handle_account_details(update: Update, context: CallbackContext):
    account_details = update.message.text
    chat_id = context.user_data.get('chat_id')

    if chat_id:
        connection = connect_db()
        cursor = connection.cursor()
        
        cursor.execute(
            "INSERT INTO payments_list (chat_id, account_details) VALUES (%s, %s) ON CONFLICT (chat_id) DO NOTHING",
            (chat_id, account_details)
        )
        connection.commit()
        connection.close()
        
        update.message.reply_text("You have been added to the payments list. You'll receive payment soon.")
    else:
        update.message.reply_text("Something went wrong. Start again.")
    return ConversationHandler.END


def main():
    updater = Updater(TELEGRAM_BOT_API, use_context=True)
    dp = updater.dispatcher

    # Conversation handler for user interactions
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME: [MessageHandler(Filters.text & ~Filters.command, handle_username)],
            ACCOUNT_DETAILS: [MessageHandler(Filters.text & ~Filters.command, handle_account_details)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add conversation handler
    dp.add_handler(conv_handler)

    # Add admin command handlers
    dp.add_handler(CommandHandler("get_payments_list", get_payments_list))
    dp.add_handler(CommandHandler("show_pending_payments", show_pending_payments))
    dp.add_handler(CommandHandler("mark_as_paid", mark_as_paid))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, handle_bot_added))


    # Start polling for updates
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()        