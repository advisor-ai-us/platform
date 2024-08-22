from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
import os, sys, sqlite3, requests, asyncio, uuid, time

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config import *
from common_utils import *
from plugins.mental_health_advisor.utils import handle_incoming_user_message_to_mental_health_advisor
from werkzeug.security import generate_password_hash

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

load_dotenv()  # This loads the variables from .env

TAVUS_API_KEY = os.getenv('TAVUS_API_KEY')
TAVUS_API_URL = "https://tavusapi.com/v2/videos"

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    #keyboard = [['Change Response Type']]  # Adding the custom keyboard with 'Change Response Type'
    #reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text('Hello! I am your AI bot. Use the button below to change your response type.')
    await set_response_type(update, context)

# Function to generate video
async def generate_video(text_message, video_template_id, recipient_email):
    # API request headers
    headers = {
        "x-api-key": TAVUS_API_KEY,
        "Content-Type": "application/json"
    }

    # Request body
    payload = {
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

def text_to_speech_file(text: str) -> str:
    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        # female voice XrExE9yKIg1WjnnlVkGX
        # male voice pNInz6obpgDQGcFmaJgB
        voice_id="XrExE9yKIg1WjnnlVkGX",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5", # use the turbo model for low latency
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Create mp3_temp directory if it doesn't exist
    mp3_temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mp3_temp")
    os.makedirs(mp3_temp_dir, exist_ok=True)

    # Generating a filename with current timestamp for the output MP3 file
    current_timestamp = int(time.time())
    save_file_path = os.path.join(mp3_temp_dir, f"response_{current_timestamp}.mp3")
   
    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    # print(f"{save_file_path}: A new audio file was saved successfully!")

    # Return the path of the saved audio file
    return save_file_path

# Function to set response type
async def set_response_type(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Text", callback_data='text'),
         InlineKeyboardButton("Audio", callback_data='audio'),
         InlineKeyboardButton("Video", callback_data='video')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose your preferred response type:', reply_markup=reply_markup)

# Function to handle button callback
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['response_type'] = query.data
    await query.edit_message_text(text=f"You've selected {query.data} responses.")


# Function to handle messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    
    if user_message == 'Change Response Type':  # Check if the user pressed the 'Change Response Type' button
        await set_response_type(update, context)  # Call the existing set_response_type function to show the inline keyboard
        return

    #print(update)
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

            response_type = context.user_data.get('response_type', 'text')

            if response_type == 'text':
                await update.message.reply_text(ai_response)
            elif response_type == 'audio':
                audio_file_path = text_to_speech_file(ai_response)

                # The following line will put the audio in auto repeat mode in the telegram app
                # await update.message.reply_audio(audio=open(audio_file_path, "rb"))
                # The following line will not put the audio in auto repeat mode in the telegram app
                with open(audio_file_path, "rb") as audio:
                    await update.message.reply_voice(voice=audio)
            elif response_type == 'video':
                try:
                    # r084238898 uses the base video model of a woman
                    # The different IDs are available at: https://platform.tavus.io/videos/create
                    video_id = await generate_video(ai_response, "r084238898", userEmail)
                    video_link_data = await get_video_link(video_id)

                    if video_link_data:
                        video_link = video_link_data.get("download_url")
                        await update.message.reply_video(video_link)
                    else:
                        await update.message.reply_text("Failed to generate video. Here's your text response:\n\n" + ai_response)
                except Exception as e:
                    await update.message.reply_text("An error occurred while generating the video. Here's your text response:\n\n" + ai_response)
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

    # Set response type command
    #application.add_handler(CommandHandler("set_response_type", set_response_type))

    # Handle button callback
    application.add_handler(CallbackQueryHandler(button))

    # Handle all messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()