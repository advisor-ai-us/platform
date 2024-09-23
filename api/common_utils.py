import sqlite3, os, json, re, time, requests, asyncio
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
                  role TEXT DEFAULT 'member',
                  username TEXT UNIQUE,
                  telegram_username TEXT UNIQUE,
                  whatsapp_number TEXT UNIQUE,
                  phone_number TEXT UNIQUE,
                  full_name TEXT NOT NULL,
                  password TEXT NOT NULL,
                  openai_api_key TEXT DEFAULT NULL,
                  openai_model TEXT DEFAULT NULL,
                  about_yourself TEXT,
                  biggest_problem TEXT,
                  is_waitlist BOOLEAN DEFAULT FALSE,
                  waiting_for_discount INTEGER DEFAULT 0,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    # Create a table to store the creator data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS creators
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              full_name TEXT NOT NULL,
              age INTEGER,
              gender TEXT,
              education TEXT,
              occupation TEXT,
              location TEXT,
              languages TEXT,
              profile_photo BLOB,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(id))''')
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

    if role == "user":
        c.execute("UPDATE conversation_history SET is_read = true WHERE role = 'assistant' AND advisorPersonalityName = ?", (advisorPersonalityName,))
    elif role == "assistant":
        c.execute("UPDATE conversation_history SET is_read = false WHERE role = 'user' AND advisorPersonalityName = ?", (advisorPersonalityName,))

    prompt_details = json.dumps(text_sent_to_ai_in_the_prompt) if role == "assistant" else None
    is_read = False
    c.execute("INSERT INTO conversation_history (role, content, advisorPersonalityName, prompt_details, is_read) VALUES (?, ?, ?, ?, ?)", (role, content, advisorPersonalityName, prompt_details, is_read))
    conn.commit()
    conn.close()

    handle_client_chat_mapping(email, advisorPersonalityName, role)

def handle_client_chat_mapping(email, advisorPersonalityName, role):
    # Connect to the central coordinator database
    central_coordinator_db_name = os.path.join(DATABASE_PATH, "central-coordinator.db")
    conn = sqlite3.connect(central_coordinator_db_name)
    c = conn.cursor()

    # Get creator email from users table based on advisorPersonalityName as username
    c.execute("SELECT email FROM users WHERE username = ? AND role = 'creator'", (advisorPersonalityName,))
    creator_row = c.fetchone()

    if creator_row:
        creator_email = creator_row[0]
        
        # Connect to the user's database
        user_db_name = get_user_db(creator_email)
        user_conn = sqlite3.connect(user_db_name)
        user_c = user_conn.cursor()

        # Check if the client email and chat id is already in the table
        user_c.execute("SELECT * FROM creator_client_chat_mapping WHERE client_email = ? AND advisorPersonalityName = ?", (email, advisorPersonalityName))
        existing_row = user_c.fetchone()

        if not existing_row:
            # If not found, insert the row
            user_c.execute("INSERT INTO creator_client_chat_mapping (client_email, advisorPersonalityName) VALUES (?, ?)", (email, advisorPersonalityName))
            user_conn.commit()
        else:
            # If found, update the last_chat_timestamp
            user_c.execute("UPDATE creator_client_chat_mapping SET last_chat_timestamp = CURRENT_TIMESTAMP WHERE client_email = ? AND advisorPersonalityName = ?", (email, advisorPersonalityName))
            user_conn.commit()

        user_conn.close()

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

    # Return the path of the saved audio file
    return save_file_path

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
                 is_read BOOLEAN DEFAULT FALSE,
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

    # Create a table to store the creator_client_chat_mapping data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS creator_client_chat_mapping
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_email TEXT NOT NULL,
                    advisorPersonalityName TEXT NOT NULL,
                    is_creator_overtaken BOOLEAN DEFAULT FALSE,
                    last_chat_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

    return db_name
