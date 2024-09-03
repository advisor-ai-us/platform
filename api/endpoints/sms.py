from flask import Flask, request, jsonify
from plivo import RestClient
import os, sys, sqlite3, logging, stripe
from dotenv import load_dotenv

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config import *
from common_utils import *
from plugins.mental_health_advisor.utils import handle_incoming_user_message_to_mental_health_advisor
from werkzeug.security import generate_password_hash

load_dotenv()  # This loads the variables from .env

app = Flask(__name__)
app.template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
logging.basicConfig(level=logging.DEBUG)

# Plivo credentials
auth_id = os.getenv('PLIVO_AUTH_ID')
auth_token = os.getenv('PLIVO_AUTH_TOKEN')
client = RestClient(auth_id, auth_token)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@app.route('/sms/test', methods=['GET'])
def sms_test():
    return jsonify(status="success", message="SMS webhook is working"), 200

@app.route('/sms/receive', methods=['POST', 'GET'])
def sms_webhook():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    incoming_msg = data.get('Text', '').lower()
    sender = data.get('From')

    # get the incoming message and sender from the url params. http://localhost:3005/sms/receive?Text=hi&From=9007547626
    # incoming_msg = request.values.get('Text', '')
    # sender = request.values.get('From')

    phone_number = sender

    db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT email, is_waitlist FROM users WHERE phone_number = ?", (phone_number,))
    row = c.fetchone()

    if row:
        userEmail, is_waitlist = row
        if is_waitlist:
            if handle_allow_user_to_free_chat(userEmail) == False:
                c.execute("SELECT waiting_for_discount FROM users WHERE email = ?", (userEmail,))
                waiting_for_discount = c.fetchone()[0]

                if waiting_for_discount:
                    response = handle_discount_code(userEmail, incoming_msg)
                    c.execute("UPDATE users SET waiting_for_discount = 0 WHERE email = ?", (userEmail,))
                else:
                    response, waiting_for_discount = handle_waitlist_user(userEmail)
                    if waiting_for_discount:
                        c.execute("UPDATE users SET waiting_for_discount = 1 WHERE email = ?", (userEmail,))
            else:
                response = handle_active_user(userEmail, incoming_msg)
        else:
            response = handle_active_user(userEmail, incoming_msg)
    else:
        response = handle_new_user(phone_number, incoming_msg)

    conn.commit()
    conn.close()

    client.messages.create(
        src=os.getenv('PLIVO_PHONE_NUMBER'),
        dst=phone_number,
        text=response
    )

    return jsonify(status="success"), 200

def handle_waitlist_user(userEmail):
    response = "You are on the waitlist and have reached your free chat limit. Do you have a discount code? If yes, please enter it now. If not, reply with 'no'."
    return response, True  # We're still waiting for a discount code at this point

def handle_discount_code(userEmail, discount_code):
    response = ""
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

        # print the discount code and is_valid in terminal
        #print(f"Discount code: {discount_code}, Is valid: {is_valid}")
        #return discount_code, is_valid

        if is_valid:
            discount_percentage = 20
            response += "Valid discount code! You'll receive a 20% discount."
        else:
            discount_percentage = 0
            response += "Invalid discount code. No discount will be applied."

    # Proceed with payment
    amount = int(os.getenv('STRIPE_PAYMENT_AMOUNT'))
    discounted_amount = amount * (100 - discount_percentage) // 100

    # Create Stripe Checkout session
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
        success_url='https://www.advisorai.us/acr/success?session_id={CHECKOUT_SESSION_ID}&client_secret={CLIENT_SECRET}',
        cancel_url='https://www.advisorai.us/acr/cancel',
        client_reference_id=userEmail,
    )

    response += f"\n\nPlease complete the payment using this link: {session.url}"
    return response

def handle_active_user(userEmail, user_message):
    ai_response = ai_chat_logic(user_message, userEmail)
    return ai_response

def handle_new_user(phone_number, user_message):
    if '@' in user_message and '.' in user_message:  # Simple email validation
        return register_new_user(phone_number, user_message)
    else:
        return "Welcome! Please enter your email to register:"

def register_new_user(phone_number, userEmail):
    db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT 1 FROM users WHERE email = ?", (userEmail,))
    existing_user = c.fetchone()

    if existing_user:
        c.execute("UPDATE users SET phone_number = ? WHERE email = ?", (phone_number, userEmail))
        conn.commit()
        conn.close()
        return f"Your phone number has been updated for the email {userEmail}."
    else:
        password = generate_password_hash("12345")
        c.execute("INSERT INTO users (phone_number, email, full_name, password, is_waitlist) VALUES (?, ?, ?, ?, 1)", (phone_number, userEmail, userEmail, password))
        conn.commit()
        conn.close()
        return f"Thank you! Your email {userEmail} has been registered."

def ai_chat_logic(pUserMessage, pUserEmail):
    response = handle_incoming_user_message_to_mental_health_advisor(pUserEmail, pUserMessage)
    return f"{response['response']}"

waiting_for_discount_codes = {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3005, debug=True)
