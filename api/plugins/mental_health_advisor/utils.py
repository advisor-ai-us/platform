import sqlite3, os, json, re
from openai import OpenAI
from flask import jsonify
from common_utils import *
from .system_prompt import MENTAL_HEALTH_ADVISOR_PROMPT

def handle_incoming_user_message_to_mental_health_advisor(userEmail, message, advisorPersonalityName):
    text_sent_to_ai_in_the_prompt = get_system_prompt_with_latest_health_data(userEmail)
    text_sent_to_ai_in_the_prompt.append({"role": "user", "content": message})

    database_path = '../data/dev/'

    # get openai apikey and model from user database if available else use the default values
    db_name1 = os.path.join(database_path, "central-coordinator.db")
    conn1 = sqlite3.connect(db_name1)
    c1 = conn1.cursor()
    c1.execute("SELECT openai_api_key, openai_model FROM users WHERE email = ?", (userEmail,))
    row1 = c1.fetchone()
    conn1.close()

    # if openai apikey and model are available in the database use them else use the default values
    if row1 and row1[0] and row1[1]:
        apiKey = row1[0]
        model = row1[1]
    else:
        apiKey = OPENAI_API_KEY
        model = OPENAI_MODEL

    response = get_response_from_openai(apiKey, model, text_sent_to_ai_in_the_prompt)

    if isinstance(response, str):
        # This means an error occurred
        logging.error(f"Error in OpenAI API call: {response}")
        return jsonify({"error": "An error occurred while processing your request. Please try again later."}), 500

    if response.choices and response.choices[0].message.content:
        responseData = ''
        content = response.choices[0].message.content
        responseData = extract_json_from_text(content)

        if not responseData:
            logging.error("JSON part not found or error parsing JSON in the response")
            responseData = {"MsgForUser": content}

        # Ensure responseData is a dictionary before accessing keys
        phq9 = []
        prompt_details = text_sent_to_ai_in_the_prompt
        if isinstance(responseData, dict):
            MsgForUser = responseData.get('MsgForUser', 'An error occurred. Please try again.')
            if MsgForUser != "An error occurred. Please try again.":
                prompt_details.append({"role": "response", "content": content})

                save_conversation(userEmail, "user", message, advisorPersonalityName, None)
                save_conversation(userEmail, "assistant", MsgForUser, advisorPersonalityName, prompt_details)

                # save MsgForApplication
                MsgForApplication = responseData.get('MsgForApplication')
                save_health_status(userEmail, MsgForApplication)
            else:
                MsgForUser = "An error occurred. Please try again."

            # Get phq9 data from database
            db_name = get_user_db(userEmail)
            conn = sqlite3.connect(db_name)
            c = conn.cursor()

            # Check if the table 'phq9' exists
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phq9';")
            table_exists = c.fetchone()

            if table_exists:
                # Fetch data from the 'phq9' table if it exists
                c.execute("SELECT question, answer, score, created_at FROM phq9 ORDER BY created_at DESC")
                phq9 = c.fetchall()

            conn.close()

        return jsonify({"response": MsgForUser, "responseData": content, "model": model, "prompt_details": json.dumps(prompt_details), "phq9Data": [{"question": row[0], "answer": row[1], "score": row[2], "createdAt": row[3]} for row in phq9]})

def save_health_status(email, health_status):
    try:
        if not health_status or not health_status[0].get('tool_name'):
            return

        db_name = get_user_db(email)
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        for status in health_status:
            table_name = status.get('tool_name')
            c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT NOT NULL,
                            answer TEXT NOT NULL,
                            score INTEGER NOT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

            c.execute(f"INSERT INTO {table_name} (question, answer, score) VALUES (?, ?, ?)", (status.get('question'), status.get('answer'), status.get('score')))

        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error saving health status: {e}")



def get_system_prompt_with_latest_health_data(email):
    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Check if the table 'phq9' exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phq9';")
    table_exists = c.fetchone()

    if not table_exists:
        # Return the default message if the table does not exist
        health_data = "There are no health data known about the user."
    else:
        # Fetch data from the 'phq9' table if it exists
        c.execute("SELECT question, answer, created_at FROM phq9 ORDER BY created_at DESC")
        rows = c.fetchall()

        if not rows:
            health_data = "There are no health data known about the user."
        else:
            health_data = "The health data known about the user are: "
            for question, answer, created_at in rows:
                health_data += f"Question: {question}, Answer: {answer}, Created At: {created_at}, "

    conn.close()

    # Use the imported MENTAL_HEALTH_ADVISOR_PROMPT
    updated_prompt = MENTAL_HEALTH_ADVISOR_PROMPT.replace("[HEALTH_DATA]", health_data)

    return [{"role": "system", "content": updated_prompt}]