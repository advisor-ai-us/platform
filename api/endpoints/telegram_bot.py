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
from werkzeug.security import generate_password_hash

load_dotenv()  # This loads the variables from .env

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! I am your AI bot.')

# Function to handle messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    print(update)
    userName = update.message.from_user.username

    db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
    if not os.path.exists(db_name):
        init_central_coordinator_db()
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT email FROM users WHERE telegram_username = ?", (userName,))
    row = c.fetchone()

    if row:
        userEmail = row[0]
        
        # check handle_allow_user_to_free_chat
        if handle_allow_user_to_free_chat(userEmail):
            user_message = update.message.text
            ai_response = ai_chat_logic(user_message, userEmail)
            await update.message.reply_text(ai_response)
        else:
            await update.message.reply_text("You have reached your free chat limit. Please pay using stripe to continue.")
    else:
        user_message = update.message.text
        if 'waiting_for_email' in context.user_data and context.user_data['waiting_for_email']:
            # User is providing their email
            if '@' in user_message and '.' in user_message:  # Simple email validation
                password = generate_password_hash("12345")
                c.execute("INSERT INTO users (telegram_username, email, full_name, password) VALUES (?, ?, ?, ?)", (userName, user_message, userName, password))
                conn.commit()
                context.user_data['waiting_for_email'] = False
                await update.message.reply_text(f"Thank you! Your email {user_message} has been registered.")
            else:
                await update.message.reply_text("That doesn't look like a valid email. Please try again:")
        else:
            # Ask for email
            context.user_data['waiting_for_email'] = True
            await update.message.reply_text("Please enter your email:")

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