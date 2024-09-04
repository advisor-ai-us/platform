import sqlite3, os, json, re, logging
from openai import OpenAI
from flask import jsonify
from common_utils import *
from config import *
from .system_prompt import PORTFOLIO_PERFORMANCE_PROMPT
import datetime

def handle_incoming_user_message_to_portfolio_performance(userEmail, message):
    text_sent_to_ai_in_the_prompt = get_system_prompt_with_latest_assets(PORTFOLIO_PERFORMANCE_PROMPT, userEmail)
    text_sent_to_ai_in_the_prompt.append({"role": "user", "content": message})
    
    advisorPersonalityName = 'portfolio-performance'
    # get openai apikey and model from user database if available else use the default values
    db_name1 = os.path.join(DATABASE_PATH, "central-coordinator.db")
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
            responseData = {"MsgForUser": content, "graph_data": {}, "recommendations": []}

        # Ensure responseData is a dictionary before accessing keys
        prompt_details = text_sent_to_ai_in_the_prompt
        if isinstance(responseData, dict):
            MsgForUser = responseData.get('MsgForUser', 'An error occurred. Please try again.')
            if MsgForUser != "An error occurred. Please try again.":
                prompt_details.append({"role": "response", "content": content})

                save_conversation(userEmail, "user", message, advisorPersonalityName, None)
                save_conversation(userEmail, "assistant", MsgForUser, advisorPersonalityName, prompt_details)
    
                graph_data = responseData.get('graph_data')
                save_graph_data(userEmail, graph_data)
    
                # save recommendations data
                recommendations = responseData.get('recommendations')
                save_recommendations(userEmail, recommendations)

                # Handle asset updates
                update_assets = responseData.get('update_assets')
                if update_assets:
                    handle_asset_update(userEmail, update_assets)

                # save memory
                memory = responseData.get('memory')
                save_memory(userEmail, memory)
        else:
            MsgForUser = "An error occurred. Please try again."

        # Get graph data and recommendations from database and return it in the response
        db_name = get_user_db(userEmail)
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT key, value FROM graph_data")
        rows = c.fetchall()
        conn.close()

        # Get recommendations from database
        conn1 = sqlite3.connect(db_name)
        c1 = conn1.cursor()
        c1.execute("SELECT recommendation FROM recommendations")
        recommendations = c1.fetchall()
        conn1.close()

        # Get assets data from database
        conn2 = sqlite3.connect(db_name)
        c2 = conn2.cursor()
        c2.execute("SELECT id, parent_id, asset, qty, price, value, account, row_start, row_end FROM assets ORDER BY created_at ASC")
        assetsData = c2.fetchall()
        conn2.close()

        return {"response": MsgForUser, "responseData": content, "prompt_details": json.dumps(prompt_details), "graph_data": [{"key": key, "value": value} for key, value in rows], "recommendations": [recommendation[0] for recommendation in recommendations], "model": model, "assets": [{"id": row[0], "parent_id": row[1], "asset": row[2], "qty": row[3], "price": row[4], "value": row[5], "account": row[6], "row_start": row[7], "row_end": row[8]} for row in assetsData]}
    else:
        logging.error("Unexpected response format from OpenAI API")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

def get_system_prompt_with_latest_assets(systemPrompt, email):
    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM assets WHERE row_end IS NULL ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    if not rows:
        assets_data = "There are no assets known about the user."
    elif len(rows) > 0:
        assets_data = json.dumps([{"id": row[0], "parent_id": row[1], "asset": row[2], "qty": row[3], "price": row[4], "value": row[5], "account": row[6], "row_start": row[7], "row_end": row[8]} for row in rows])
        # assets_data = "["
        # for row in rows:
        #     assets_data += f'{{"asset": "{row[0]}", "qty": {row[1]}, "price": {row[2]}, "value": {row[3]}, "account": "{row[4]}"}}'
        #     if row != rows[-1]:
        #         assets_data += ", "
        # assets_data += "]"

    systemPrompt = systemPrompt.replace("[ASSETS_DATA]", assets_data)

    # Replace [USER_FACTS] from the system prompt with the latest facts known about the user
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT key, value FROM basic_memory")
    rows = c.fetchall()
    conn.close()

    if not rows:
        user_facts = "There are no facts known about the user."
    elif len(rows) > 0:
        user_facts = "The facts known about the user are: "
        for key, value in rows:
            user_facts += f"{key}: {value}, "

    systemPrompt = systemPrompt.replace("[USER_BASIC_MEMORY]", user_facts)

    return [{"role": "system", "content": systemPrompt}]

def save_graph_data(email, graph_data):
    if graph_data:
        db_name = get_user_db(email)
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        for key, value in graph_data.items():
            if key == "line_chart" and value.get("x_axis") and value.get("y_axis"):
                c.execute("SELECT 1 FROM graph_data WHERE key = ?", ("line_chart_labels",))
                exists = c.fetchone()
                if exists:
                    c.execute("UPDATE graph_data SET value = ? WHERE key = ?", (json.dumps(value["x_axis"]), "line_chart_labels"))
                else:
                    c.execute("INSERT INTO graph_data (key, value) VALUES (?, ?)", ("line_chart_labels", json.dumps(value["x_axis"])))

                c.execute("SELECT 1 FROM graph_data WHERE key = ?", ("line_chart_values",))
                exists = c.fetchone()
                if exists:
                    c.execute("UPDATE graph_data SET value = ? WHERE key = ?", (json.dumps(value["y_axis"]), "line_chart_values"))
                else:
                    c.execute("INSERT INTO graph_data (key, value) VALUES (?, ?)", ("line_chart_values", json.dumps(value["y_axis"])))

            elif key == "pie_chart" and value.get("labels") and value.get("data"):
                c.execute("SELECT 1 FROM graph_data WHERE key = ?", ("pie_chart_labels",))
                exists = c.fetchone()
                if exists:
                    c.execute("UPDATE graph_data SET value = ? WHERE key = ?", (json.dumps(value["labels"]), "pie_chart_labels"))
                else:
                    c.execute("INSERT INTO graph_data (key, value) VALUES (?, ?)", ("pie_chart_labels", json.dumps(value["labels"])))

                c.execute("SELECT 1 FROM graph_data WHERE key = ?", ("pie_chart_data",))
                exists = c.fetchone()
                if exists:
                    c.execute("UPDATE graph_data SET value = ? WHERE key = ?", (json.dumps(value["data"]), "pie_chart_data"))
                else:
                    c.execute("INSERT INTO graph_data (key, value) VALUES (?, ?)", ("pie_chart_data", json.dumps(value["data"])))

        conn.commit()
        conn.close()
    else:
        print("Graph data key is missing in responseData")

def save_recommendations(email, recommendations):
    if recommendations:
        db_name = get_user_db(email)
        conn1 = sqlite3.connect(db_name)
        c1 = conn1.cursor()
        c1.execute("DELETE FROM recommendations")
        conn1.commit()
        conn1.close()
        
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        for recommendation in recommendations:
            c.execute("INSERT INTO recommendations (recommendation) VALUES (?)", (recommendation["recommendation"],))
        conn.commit()
        conn.close()

def handle_asset_update(userEmail, update_assets):
    action = update_assets.get('action')
    asset = update_assets.get('asset')
    qty = update_assets.get('qty')
    price = update_assets.get('price')
    value = update_assets.get('value')
    account = update_assets.get('account')
    
    db_name = get_user_db(userEmail)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    current_time_ms = int(datetime.datetime.now().timestamp() * 1000)

    if action == 'add_asset':
        c.execute("INSERT INTO assets (parent_id, asset, qty, price, value, account, row_start) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                  (0, asset, qty, price, value, account, current_time_ms))
        conn.commit()

        last_id = c.lastrowid
        c.execute("UPDATE assets SET parent_id = ? WHERE id = ?", (last_id, last_id))
        conn.commit()
        conn.close()

        logging.info(f"Added new asset for user {userEmail}: {asset}")
    elif action == 'edit_asset':
        c.execute("SELECT id, parent_id FROM assets WHERE asset = ? AND row_end IS NULL", (asset,))
        row = c.fetchone()
        if row:
            asset_id = row[0]
            parent_id = row[1]

            c.execute("UPDATE assets SET row_end = ? WHERE id = ?", (current_time_ms, asset_id))
            conn.commit()

            c.execute("INSERT INTO assets (parent_id, asset, qty, price, value, account, row_start) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                      (parent_id, asset, qty, price, value, account, current_time_ms))
            conn.commit()
            conn.close()

            logging.info(f"Edited asset for user {userEmail}: {asset}")
        else:
            logging.error(f"Asset not found for user {userEmail}: {asset}")

    elif action == 'delete_asset':
        c.execute("SELECT id FROM assets WHERE asset = ? AND row_end IS NULL", (asset,))
        row = c.fetchone()
        if row:
            asset_id = row[0]

            c.execute("UPDATE assets SET row_end = ? WHERE id = ?", (current_time_ms, asset_id))
            conn.commit()
            conn.close()

            logging.info(f"Deleted asset for user {userEmail}: {asset}")
        else:
            logging.error(f"Asset not found for user {userEmail}: {asset}")

def save_memory(email, memory):
    if memory:
        action = memory.pop('Action', None)  # Remove the action key and get its value
        
        if action:
            # Database operations
            db_name = get_user_db(email)
            conn1 = sqlite3.connect(db_name)
            c1 = conn1.cursor()

            # Check if memory contains multiple key-value pairs or a single key-value pair
            if 'key' in memory and 'value' in memory:
                # Handle single key-value pair
                key = memory.get('key')
                value = memory.get('value')
                
                if not isinstance(key, str):
                    key = str(key)
                if not isinstance(value, str):
                    value = str(value)

                # Check if the key already exists in the memory table
                c1.execute("SELECT 1 FROM basic_memory WHERE key = ?", (key,))
                exists = c1.fetchone()

                if action == 'add':
                    if exists:
                        # If the key exists, update the value
                        c1.execute("UPDATE basic_memory SET value = ? WHERE key = ?", (value, key))
                    else:
                        # If the key does not exist, insert a new key-value pair
                        c1.execute("INSERT INTO basic_memory (key, value) VALUES (?, ?)", (key, value))
                elif action == 'edit':
                    if exists:
                        # If the key exists, update the value
                        c1.execute("UPDATE basic_memory SET value = ? WHERE key = ?", (value, key))
                    else:
                        print(f"Key '{key}' does not exist in the basic_memory table to edit.")
                elif action == 'delete':
                    if exists:
                        # If the key exists, delete the row
                        c1.execute("DELETE FROM basic_memory WHERE key = ?", (key,))
                    else:
                        print(f"Key '{key}' does not exist in the basic_memory table to delete.")
            
            else:
                # Handle multiple key-value pairs
                for key, value in memory.items():
                    if not isinstance(key, str):
                        key = str(key)
                    if not isinstance(value, str):
                        value = str(value)

                    # Check if the key already exists in the memory table
                    c1.execute("SELECT 1 FROM basic_memory WHERE key = ?", (key,))
                    exists = c1.fetchone()

                    if action == 'add':
                        if exists:
                            # If the key exists, update the value
                            c1.execute("UPDATE basic_memory SET value = ? WHERE key = ?", (value, key))
                        else:
                            # If the key does not exist, insert a new key-value pair
                            c1.execute("INSERT INTO basic_memory (key, value) VALUES (?, ?)", (key, value))
                    elif action == 'edit':
                        if exists:
                            # If the key exists, update the value
                            c1.execute("UPDATE basic_memory SET value = ? WHERE key = ?", (value, key))
                        else:
                            print(f"Key '{key}' does not exist in the basic_memory table to edit.")
                    elif action == 'delete':
                        if exists:
                            # If the key exists, delete the row
                            c1.execute("DELETE FROM basic_memory WHERE key = ?", (key,))
                        else:
                            print(f"Key '{key}' does not exist in the basic_memory table to delete.")

            conn1.commit()
            conn1.close()
        else:
            print("Action key is missing in the memory object")
    else:
        print("Memory key is missing in responseData")

    if memory:
        action = memory.pop('Action', None)  # Remove the action key and get its value
        if action:
            # Database operations
            db_name = get_user_db(email)
            conn1 = sqlite3.connect(db_name)
            c1 = conn1.cursor()

            for key, value in memory.items():
                if not isinstance(key, str):
                    key = str(key)
                if not isinstance(value, str):
                    value = str(value)

                # Check if the key already exists in the memory table
                c1.execute("SELECT 1 FROM basic_memory WHERE key = ?", (key,))
                exists = c1.fetchone()

                if action == 'add':
                    if exists:
                        # If the key exists, update the value
                        c1.execute("UPDATE basic_memory SET value = ? WHERE key = ?", (value, key))
                    else:
                        # If the key does not exist, insert a new key-value pair
                        c1.execute("INSERT INTO basic_memory (key, value) VALUES (?, ?)", (key, value))
                elif action == 'edit':
                    if exists:
                        # If the key exists, update the value
                        c1.execute("UPDATE basic_memory SET value = ? WHERE key = ?", (value, key))
                    else:
                        print(f"Key '{key}' does not exist in the basic_memory table to edit.")
                elif action == 'delete':
                    if exists:
                        # If the key exists, delete the row
                        c1.execute("DELETE FROM basic_memory WHERE key = ?", (key,))
                    else:
                        print(f"Key '{key}' does not exist in the basic_memory table to delete.")

            conn1.commit()
            conn1.close()
        else:
            print("Action key is missing in the memory object")
    else:
        print("Memory key is missing in responseData")