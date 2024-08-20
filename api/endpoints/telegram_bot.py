from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update, InputFile
from dotenv import load_dotenv
import os, sys, sqlite3, requests, asyncio

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config import *
from common_utils import *
from plugins.mental_health_advisor.utils import handle_incoming_user_message_to_mental_health_advisor
from werkzeug.security import generate_password_hash

load_dotenv()  # This loads the variables from .env

TAVUS_API_KEY = os.getenv('TAVUS_API_KEY')
TAVUS_API_URL = "https://tavusapi.com/v2/videos"

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! I am your AI bot.')

# Function to generate video
async def generate_video(text_message, video_template_id, recipient_email):
    # API request headers
    headers = {
        "x-api-key": TAVUS_API_KEY,
        "Content-Type": "application/json"
    }

    # Request body
    payload = {
        "background_url": "https://www.advisorai.us",
        "replica_id": video_template_id,
        "script": text_message,
        "video_name": recipient_email
    }

    # Make a POST request to Tavus API
    response = requests.request("POST", TAVUS_API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("video_id")
    else:
        return str(response.json())

async def get_video_link(video_id):
    url = f"https://tavusapi.com/v2/videos/{video_id}"
    headers = {"x-api-key": TAVUS_API_KEY}
    
    max_retries = 20  # Set a limit for retries (10 retries = 50 seconds total wait time)
    retry_delay = 30  # Wait 5 seconds between retries
    
    for _ in range(max_retries):
        response = requests.request("GET", url, headers=headers)
        result = response.json()
        
        # Check if the video is ready (download_url or stream_url should be available)
        if result.get("download_url"):
            return result
        
        # Check the status and log progress
        status = result.get("status")
        if status in ["queued", "processing"]:
            print(f"Video is still processing: {result.get('generation_progress')}% complete.")
        else:
            print(f"Unexpected status: {status}")
        
        # Wait before the next check
        await asyncio.sleep(retry_delay)
    
    return None  # Return None if video is still not ready after max retries

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

            try:
                video_id = await generate_video(ai_response, "r79e1c033f", userEmail)
                video_link_data = await get_video_link(video_id)

                if video_link_data:
                    video_link = video_link_data.get("download_url")
                    await update.message.reply_video(video_link)
                else:
                    await update.message.reply_text(ai_response)
            except Exception as e:
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