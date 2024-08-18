import os
import sqlite3
import sqlite3, os, json, re
from openai import OpenAI
from flask import jsonify

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


def get_user_db(email):
    database_path = 'data/dev/' if os.getenv('FLASK_ENV') == 'development' else 'data/prod/'
    db_folder = os.path.join(database_path, email)
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
