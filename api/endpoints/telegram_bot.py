from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
import os, sys, sqlite3, requests, asyncio, uuid, time, stripe

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

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [['Change Response Type']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text('Hello! I am your AI bot. The default response type is text, but you can change it. Use the button below to select a different response type.', reply_markup=reply_markup)
    #await set_response_type(update, context)

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
    if query:
        await query.answer()
        
        if query.data == 'make_payment':
            await button_callback(update, context)
        else:
            context.user_data['response_type'] = query.data
            await query.edit_message_text(text=f"You've selected {query.data} responses.")
    elif update.message and update.message.text == 'Change Response Type':
        await set_response_type(update, context)

# Function to handle messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text

    if user_message == 'Change Response Type':
        await set_response_type(update, context)
        return

    userName = update.message.from_user.username

    db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT email, is_waitlist FROM users WHERE telegram_username = ?", (userName,))
    row = c.fetchone()

    if row:
        userEmail, is_waitlist = row
        if is_waitlist and handle_allow_user_to_free_chat(userEmail) == False:
            await handle_waitlist_user(update, context, userEmail)
        else:
            await handle_active_user(update, context, userEmail, user_message)
    else:
        await handle_new_user(update, context, userName, user_message)

    conn.close()

async def handle_waitlist_user(update: Update, context: CallbackContext, userEmail: str):
    if 'waiting_for_discount_code' in context.user_data and context.user_data['waiting_for_discount_code']:
        await button_callback(update, context)
        return

    context.user_data['user_email'] = userEmail  # Store the user's email in the context
    keyboard = [
        [InlineKeyboardButton("Make Payment", callback_data='make_payment')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "You are on the waitlist and have reached your free chat limit. Please make a payment of $50 to continue.",
        reply_markup=reply_markup
    )

async def handle_active_user(update: Update, context: CallbackContext, userEmail: str, user_message: str):
    ai_response = ai_chat_logic(user_message, userEmail)
    #await update.message.reply_text(ai_response)
    response_type = context.user_data.get('response_type', 'text')
    if response_type == 'text':
        await update.message.reply_text(ai_response)
    elif response_type == 'audio':
        audio_file_path = text_to_speech_file(ai_response)
        
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

async def handle_new_user(update: Update, context: CallbackContext, userName: str, user_message: str):
    if 'waiting_for_email' in context.user_data and context.user_data['waiting_for_email']:
        if '@' in user_message and '.' in user_message:  # Simple email validation
            await register_new_user(update, context, userName, user_message)
        else:
            await update.message.reply_text("That doesn't look like a valid email. Please try again:")
    else:
        context.user_data['waiting_for_email'] = True
        await update.message.reply_text("Please enter your email:")

async def register_new_user(update: Update, context: CallbackContext, userName: str, userEmail: str):
    db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT 1 FROM users WHERE email = ?", (userEmail,))
    existing_user = c.fetchone()
    
    if existing_user:
        await update.message.reply_text("This email is already registered. Please use a different email.")
    else:
        password = generate_password_hash("12345")
        c.execute("INSERT INTO users (telegram_username, email, full_name, password, is_waitlist) VALUES (?, ?, ?, ?, 1)", (userName, userEmail, userName, password))
        conn.commit()
        context.user_data['waiting_for_email'] = False
        await update.message.reply_text(f"Thank you! Your email {userEmail} has been registered.")
        #await handle_waitlist_user(update, context, userEmail)

    conn.close()

async def button_callback(update: Update, context: CallbackContext) -> None:
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == 'make_payment':
            try:
                user = update.effective_user
                db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute("SELECT email FROM users WHERE telegram_username = ?", (user.username,))
                user_email = c.fetchone()[0]
                conn.close()

                # Ask for discount code
                await query.edit_message_text("Do you have a discount code? If yes, please enter it now. If not, type 'no'.")
                context.user_data['waiting_for_discount_code'] = True
                return

            except Exception as e:
                await query.edit_message_text(text=f"Sorry, there was an error processing your request: {str(e)}")
        else:
            context.user_data['response_type'] = query.data
            await query.edit_message_text(text=f"You've selected {query.data} responses.")
    elif update.message:
        if context.user_data.get('waiting_for_discount_code'):
            discount_code = update.message.text.strip()
            context.user_data['waiting_for_discount_code'] = False

            if discount_code.lower() == 'no':
                discount_percentage = 0
            else:
                # Validate discount code
                db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute("SELECT 1 FROM referral_codes WHERE referred_code = ? AND is_active = 1", (discount_code,))
                is_valid = c.fetchone() is not None
                conn.close()

                if is_valid:
                    discount_percentage = 20
                    await update.message.reply_text("Valid discount code! You'll receive a 20% discount.")

                    # # Insert a row into user_referral_relationship table
                    # db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
                    # conn = sqlite3.connect(db_name)
                    # c = conn.cursor()
                    # c.execute("INSERT INTO user_referral_relationship (referred_code, user_email) VALUES (?, ?)", 
                    #         (discount_code, user_email))
                    # conn.commit()
                    # conn.close()
                else:
                    discount_percentage = 0
                    await update.message.reply_text("Invalid discount code. No discount will be applied.")

            # Proceed with payment
            amount = int(os.getenv('STRIPE_PAYMENT_AMOUNT'))
            discounted_amount = amount * (100 - discount_percentage) // 100

            user_email = context.user_data.get('user_email')
            if not user_email:
                db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute("SELECT email FROM users WHERE telegram_username = ?", (update.message.from_user.username,))
                user_email = c.fetchone()[0]
                conn.close()

            # if discount code is applied, then insert into user_referral_relationship table
            if discount_percentage > 0:
                db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute("INSERT INTO user_referral_relationship (referred_code, user_email) VALUES (?, ?)", 
                          (discount_code, user_email))
                conn.commit()
                # conn.close()

                # Increment signup_count in referral_codes for the referrer
                c.execute("SELECT referrer_owner_email FROM referral_codes WHERE referred_code = ?", (discount_code,))
                row = c.fetchone()
                
                if row:
                    referrer_owner_email = row[0]
                    referrer_db_name = get_user_db(referrer_owner_email)
                    
                    referrer_conn = sqlite3.connect(referrer_db_name)
                    referrer_cursor = referrer_conn.cursor()

                    referrer_cursor.execute("UPDATE referrals SET signup_count = signup_count + 1 WHERE referred_code = ?", (discount_code,))
                    referrer_conn.commit()
                    referrer_conn.close()

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Chat Subscription',
                        },
                        'unit_amount': discounted_amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://localhost:3003/acr/success?session_id={CHECKOUT_SESSION_ID}&client_secret={CLIENT_SECRET}',
                #success_url='https://www.advisorai.us/acr/success?session_id={CHECKOUT_SESSION_ID}&client_secret={CLIENT_SECRET}',
                cancel_url='https://www.advisorai.us/acr/cancel',
                client_reference_id=user_email,
            )

            await update.message.reply_text(
                text=f"Please complete the payment using this link: {session.url}",
                reply_markup=None
            )

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

    # Handle payment button callback
    application.add_handler(CallbackQueryHandler(button_callback))

    # Handle "Change Response Type" button
    application.add_handler(MessageHandler(filters.Regex('^Change Response Type$'), button))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()