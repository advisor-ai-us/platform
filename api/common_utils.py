import sqlite3, os, json, re
from openai import OpenAI
from flask import jsonify

from config import *

# Create users database if it doesn't exist
def init_central_coordinator_db():
    db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
    if not os.path.exists(DATABASE_PATH):
        os.makedirs(DATABASE_PATH)
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  telegram_username TEXT UNIQUE,
                  full_name TEXT NOT NULL,
                  password TEXT NOT NULL,
                  openai_api_key TEXT DEFAULT NULL,
                  openai_model TEXT DEFAULT NULL,
                  about_yourself TEXT,
                  biggest_problem TEXT,
                  is_waitlist BOOLEAN DEFAULT FALSE,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    # Create a table to store the refferal data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS referral_codes
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_owner_email TEXT NOT NULL,
                    referred_code TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    # Create a table to store user refferal relationship
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_referral_relationship
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referred_code TEXT NOT NULL,
                    user_email TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    # Create a table to store payment intents
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS payment_intents
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT DEFAULT NULL,
                    payment_intent_id TEXT NOT NULL,
                    user_email TEXT NOT NULL,
                    status TEXT NOT NULL,
                    client_secret TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_response_from_openai(api_key, model, messages):
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response
    except Exception as e:
        return str(e)


def extract_json_from_text(text):
    try:
        # Use regex to find the JSON object within the text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            json_part = match.group(0)
            return json.loads(json_part)
        else:
            print("ERROR: JSON part not found in the response")
            return None
    except (ValueError, json.JSONDecodeError):
        return None


def save_conversation(email, role, content, advisorPersonalityName, text_sent_to_ai_in_the_prompt):
    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    prompt_details = json.dumps(text_sent_to_ai_in_the_prompt) if role == "assistant" else None
    c.execute("INSERT INTO conversation_history (role, content, advisorPersonalityName, prompt_details) VALUES (?, ?, ?, ?)", (role, content, advisorPersonalityName, prompt_details))
    conn.commit()
    conn.close()

def handle_allow_user_to_free_chat(email):
    central_coordinator_db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
    conn = sqlite3.connect(central_coordinator_db_name)
    c = conn.cursor()
    # check if the user is in the payment intents table with status = 'succeeded'
    c.execute("SELECT COUNT(*) FROM payment_intents WHERE user_email = ? AND status = 'succeeded'", (email,))
    payment_intent_count = c.fetchone()[0]
    conn.close()

    # if row found in payment intents table, return True
    if payment_intent_count > 0:
        return True
    
    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # Fetch the count of user messages
    c.execute("SELECT COUNT(*) FROM conversation_history WHERE role = 'user'")
    user_message_count = c.fetchone()[0]
    
    conn.close()

    # Ensure that user_message_count is an integer
    user_message_count = int(user_message_count)

    # Compare the counts
    if user_message_count >= int(FREE_CHAT_COUNT):
        return False
    else:
        return True

def get_user_db(email):
    db_folder = os.path.join(DATABASE_PATH, email)
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        
    db_name = os.path.join(db_folder, "all_user_data.db")
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS basic_memory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 key TEXT NOT NULL,
                 value TEXT NOT NULL, 
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversation_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 role TEXT NOT NULL,
                 content TEXT NOT NULL,
                 advisorPersonalityName TEXT DEFAULT NULL,
                 prompt_details TEXT DEFAULT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_settings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  key TEXT UNIQUE NOT NULL,
                  value TEXT NOT NULL,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()


    # Create a table to store the dashboard data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dashboard 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  key TEXT NOT NULL, 
                  value TEXT NOT NULL, 
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    
    # Create a table to store the assets data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS assets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 parent_id INTEGER NOT NULL,
                 asset TEXT NOT NULL,
                 qty TEXT NOT NULL,
                 price TEXT NOT NULL,
                 value TEXT DEFAULT NULL,
                 account TEXT DEFAULT NULL,
                 row_start INTEGER NOT NULL,
                 row_end INTEGER DEFAULT NULL,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    # Create a table to store the account data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 account_number TEXT NOT NULL,
                 is_it_active TEXT NOT NULL,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    # Create a table to store the graph data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS graph_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 key TEXT NOT NULL,
                 value TEXT NOT NULL,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    # Create a table to store the recommendations data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recommendations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 recommendation TEXT NOT NULL,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    # Create a table to store the stock reports data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stock_reports
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_name TEXT NOT NULL,
                recommendation TEXT DEFAULT NULL,
                justification TEXT DEFAULT NULL,
                discount_rate TEXT DEFAULT NULL,
                net_present_value TEXT DEFAULT NULL,
                comparison TEXT DEFAULT NULL,
                graph_data_x_axis TEXT DEFAULT NULL,
                graph_data_y_axis TEXT DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    # Create a table to store the refferal data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS referrals
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referred_code TEXT NOT NULL,
                    signup_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    return db_name
