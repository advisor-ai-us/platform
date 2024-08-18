import sqlite3
from common_utils import get_user_db
from .system_prompt import MENTAL_HEALTH_ADVISOR_PROMPT

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