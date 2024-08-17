import os
import sqlite3

def get_user_db(email):
    database_path = 'databases/dev/' if os.getenv('FLASK_ENV') == 'development' else 'databases/prod/'
    db_folder = os.path.join(database_path, email)
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        
    db_name = os.path.join(db_folder, "all_user_data.db")
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # Create necessary tables (basic_memory, conversation_history, user_settings, etc.)
    # ... (copy the table creation code from the original get_user_db function)

    conn.close()
    return db_name
