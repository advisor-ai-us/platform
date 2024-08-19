from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update
from dotenv import load_dotenv
import os, sys, sqlite3

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config import *
from common_utils import *
from plugins.mental_health_advisor.utils import handle_incoming_user_message_to_mental_health_advisor

load_dotenv()  # This loads the variables from .env

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! I am your AI bot.')

# Function to handle messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    print(update)
    # Goal: Get the user email from the telegram user
    userName = update.message.from_user.username

    # Check if the central coordinator database exists
    db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
    if not os.path.exists(db_name):
        init_central_coordinator_db()
    # Look for the user name in the central coordinator database
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT email FROM users WHERE telegram_username = ?", (userName,))
    row = c.fetchone()
    conn.close()
    if row:
        userEmail = row[0]
        print(userEmail)
        user_message = update.message.text
        ai_response = ai_chat_logic(user_message, userEmail)  # Replace with your AI chat logic function
        await update.message.reply_text(ai_response)
    else:
        userEmail = None
        # userEmail not found in the database. Ask the user for his email and save it in the database
        await update.message.reply_text("Please enter your email:")
        # Save the user email in the database
        c.execute("INSERT INTO users (telegram_username, email) VALUES (?, ?)", (userName, userEmail))
        conn.commit()
        conn.close()

# Your AI chat logic
def ai_chat_logic(pUserMessage, pUserEmail):
    response = handle_incoming_user_message_to_mental_health_advisor(pUserEmail, pUserMessage)
    return f"{response['response']}"

def main():
    # Replace 'YOUR_TOKEN' with your bot token from BotFather
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Start command
    application.add_handler(CommandHandler("start", start))

    # Handle all messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()