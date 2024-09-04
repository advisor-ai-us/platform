from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
import os, sys, sqlite3, requests, asyncio, uuid, time, stripe, importlib

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config import *
from common_utils import *
from plugins.mental_health_advisor.utils import handle_incoming_user_message_to_mental_health_advisor
from werkzeug.security import generate_password_hash

load_dotenv()  # This loads the variables from .env

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [['Change Response Type']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text('Hello! I am your AI bot. The default response type is text, but you can change it. Use the button below to select a different response type.', reply_markup=reply_markup)
    #await set_response_type(update, context)

# Function to set response type
async def set_response_type(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Change Advisor", callback_data='change_advisor'),
         InlineKeyboardButton("Change Response Type", callback_data='change_response_type')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    current_advisor = context.user_data.get('current_advisor', 'Portfolio Performance')
    current_response_type = context.user_data.get('response_type', 'text')
    message_text = f'Currently talking to: {current_advisor}\n' \
                   f'Using: {current_response_type}\n\n' \
                   f'Choose an option:'

    if update.message:
        await update.message.reply_text(message_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)

async def change_advisor(update: Update, context: CallbackContext) -> None:
    plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')
    advisors = [d for d in os.listdir(plugins_dir) if os.path.isdir(os.path.join(plugins_dir, d))]
    
    keyboard = [
        [InlineKeyboardButton(advisor.replace('_', ' ').title(), callback_data=advisor)]
        for advisor in advisors
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text('Please choose a coach:', reply_markup=reply_markup)

async def change_response_type(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Text", callback_data='text'),
         InlineKeyboardButton("Audio", callback_data='audio'),
         InlineKeyboardButton("Video", callback_data='video')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text('Please choose a response type:', reply_markup=reply_markup)

# Function to handle button callback
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        await query.answer()
        
        if query.data == 'make_payment':
            await button_callback(update, context)
        elif query.data == 'change_advisor':
            await change_advisor(update, context)
        elif query.data == 'change_response_type':
            await change_response_type(update, context)
        elif query.data in [d for d in os.listdir(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')) if os.path.isdir(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins', d))]:
            context.user_data['current_advisor'] = query.data.replace('_', ' ').title()
            await query.edit_message_text(text=f"You've selected {context.user_data['current_advisor']} as your coach.")
        elif query.data in ['text', 'audio', 'video']:
            context.user_data['response_type'] = query.data
            await query.edit_message_text(text=f"You've selected {query.data} responses.")
        else:
            await set_response_type(update, context)
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
    ai_response = ai_chat_logic(user_message, userEmail, context)
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
            #await update.message.reply_text("An error occurred while generating the video. Here's your text response:\n\n" + ai_response)
            # print the error
            await update.message.reply_text(f"An error occurred while generating the video: {e}")

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
                #success_url='http://localhost:3003/acr/success?session_id={CHECKOUT_SESSION_ID}&client_secret={CLIENT_SECRET}',
                success_url='https://www.advisorai.us/acr/success?session_id={CHECKOUT_SESSION_ID}&client_secret={CLIENT_SECRET}',
                cancel_url='https://www.advisorai.us/acr/cancel',
                client_reference_id=user_email,
            )

            await update.message.reply_text(
                text=f"Please complete the payment using this link: {session.url}",
                reply_markup=None
            )

# Your AI chat logic
def ai_chat_logic(pUserMessage, pUserEmail, context):
    current_advisor = context.user_data.get('current_advisor', 'Portfolio Performance')
    advisor_function_name = f"handle_incoming_user_message_to_{current_advisor.lower().replace(' ', '_')}"
    
    try:
        advisor_module = importlib.import_module(f"plugins.{current_advisor.lower().replace(' ', '_')}.utils")
        advisor_function = getattr(advisor_module, advisor_function_name)
        response = advisor_function(pUserEmail, pUserMessage)
    except (ImportError, AttributeError):
        # Fallback to default handler if the specific one is not found
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

    # Handle change advisor button
    application.add_handler(CallbackQueryHandler(change_advisor, pattern='^change_advisor$'))

    # Handle change response type button
    application.add_handler(CallbackQueryHandler(change_response_type, pattern='^change_response_type$'))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()