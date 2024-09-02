from flask import Flask, request, jsonify
from plivo import RestClient
import os, sys, sqlite3, logging
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

@app.route('/sms/test', methods=['GET'])
def sms_test():
    return jsonify(status="success", message="SMS webhook is working"), 200

@app.route('/sms/', methods=['POST', 'GET'])
def sms_webhook():
    # incoming_msg = request.values.get('Text', '').lower()
    # sender = request.values.get('From')
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    incoming_msg = data.get('Text', '').lower()
    sender = data.get('From')

    print(f"Incoming message: {incoming_msg}")
    print(f"Sender: {sender}")

    # Extract the phone number from the sender
    phone_number = sender

    db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT email, is_waitlist FROM users WHERE phone_number = ?", (phone_number,))
    row = c.fetchone()

    if row:
        userEmail, is_waitlist = row
        if is_waitlist and handle_allow_user_to_free_chat(userEmail) == False:
            response = handle_waitlist_user(userEmail)
        else:
            response = handle_active_user(userEmail, incoming_msg)
    else:
        response = handle_new_user(phone_number, incoming_msg)

    conn.close()

    # Send response back to the user
    client.messages.create(
        src=os.getenv('PLIVO_PHONE_NUMBER'),
        dst=phone_number,
        text=response
    )

    return jsonify(status="success"), 200

def handle_waitlist_user(userEmail):
    return "You are on the waitlist and have reached your free chat limit. Please make a payment of $50 to continue."

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3005, debug=True)
