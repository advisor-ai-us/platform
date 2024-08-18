from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update
from dotenv import load_dotenv
import os, sys

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from plugins.mental_health_advisor.utils import handle_incoming_user_message_to_mental_health_advisor

load_dotenv()  # This loads the variables from .env

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! I am your AI bot.')

# Function to handle messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    print(update)
    user_message = update.message.text
    ai_response = ai_chat_logic(user_message)  # Replace with your AI chat logic function
    await update.message.reply_text(ai_response)

# Your AI chat logic
def ai_chat_logic(user_message):
    userEmail = "kedia.vikas@gmail.com"
    response = handle_incoming_user_message_to_mental_health_advisor(userEmail, user_message)
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