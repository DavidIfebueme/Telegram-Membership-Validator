from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import psycopg2
from db_connection import connect_db

def get_payments_list(update: Update, context: CallbackContext):
    bot_owner_id = 6333448623  
    if update.message.from_user.id == bot_owner_id:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM payments_list")
        payments = cursor.fetchall()
        connection.close()

        if payments:
            update.message.reply_text("\n".join([str(payment) for payment in payments]))
        else:
            update.message.reply_text("No pending payments.")
    else:
        update.message.reply_text("You're not David!'")
  

def show_pending_payments(update: Update, context: CallbackContext):
    # Ensure only the bot owner can use this command
    if update.effective_user.id != YOUR_TELEGRAM_ID:
        update.message.reply_text("Unauthorized access.")
        return

    connection = connect_db()
    cursor = connection.cursor()
    
    # Fetch pending payments
    cursor.execute("""
        SELECT users.username, payments_list.account_details
        FROM users
        INNER JOIN payments_list ON users.chat_id = payments_list.chat_id
        WHERE users.paid = FALSE
    """)
    results = cursor.fetchall()
    connection.close()

    # Format the results
    if results:
        payments_info = "\n".join([f"Username: {row[0]}, Account: {row[1]}" for row in results])
        update.message.reply_text(f"Pending Payments:\n{payments_info}")
    else:
        update.message.reply_text("No pending payments at the moment.")

def mark_as_paid(update: Update, context: CallbackContext):
    if update.effective_user.id != YOUR_TELEGRAM_ID:
        update.message.reply_text("Unauthorized access.")
        return

    # Assuming you pass usernames or chat IDs as arguments
    usernames_or_ids = context.args
    if not usernames_or_ids:
        update.message.reply_text("Please provide usernames or chat IDs to mark as paid.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    for identifier in usernames_or_ids:
        cursor.execute(
            """
            UPDATE users
            SET paid = TRUE
            WHERE username = %s OR chat_id = %s
            """,
            (identifier, identifier)
        )
        cursor.execute("DELETE FROM payments_list WHERE chat_id = %s", (identifier,))
    connection.commit()
    connection.close()

    update.message.reply_text("Marked specified users as paid.")
