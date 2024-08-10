from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
from openai import OpenAI
from openai import AzureOpenAI
import os
import re
import hmac
import hashlib
import base64
import json
import time
import datetime
import sqlite3
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import fitz

from system_prompts import PORTFOLIO_PERFORMANCE_PROMPT, DASHBOARD_PROMPT, STOCK_PICKER_DISCUSSION, STOCK_PICKER_SYSTEM_REPORT

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL')

OPENAI_AZURE_API_VERSION = os.getenv('OPENAI_AZURE_API_VERSION')
OPENAI_AZURE_API_BASE_URL = os.getenv('OPENAI_AZURE_API_BASE_URL')
OPENAI_AZURE_API_KEY = os.getenv('OPENAI_AZURE_API_KEY')
OPENAI_AZURE_API_ENGINE = os.getenv('OPENAI_AZURE_API_ENGINE')

# Enable CORS only in development environment
if os.getenv('FLASK_ENV') == 'development':
    database_path = 'databases/dev/'
    CORS(app)
else:
    database_path = 'databases/prod/'

def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

def generate_token(payload, secret):
    header = {"alg": "HS256", "typ": "JWT"}
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = hmac.new(secret.encode(), f"{header_encoded}.{payload_encoded}".encode(), hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

def decode_token_and_get_email(token):
    try:
        header_encoded, payload_encoded, signature_encoded = token.split('.')
        payload = json.loads(base64.urlsafe_b64decode(payload_encoded + '==').decode())
        return payload.get('userEmail')
    except (ValueError, KeyError):
        return None

def get_response_from_ai_gpt_4_32k(messages):
    client = AzureOpenAI(
        api_key=OPENAI_AZURE_API_KEY,
        api_version=OPENAI_AZURE_API_VERSION,
        azure_endpoint=OPENAI_AZURE_API_BASE_URL
    )

    try:
        responseFromAi = client.chat.completions.create(
            model=OPENAI_AZURE_API_ENGINE,
            messages=messages
        )
    except Exception as e:
        responseFromAi = str(e)

    return responseFromAi

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

# Create users database if it doesn't exist
def init_users_db():
    db_name = os.path.join(database_path, "central-coordinator.db")
    if not os.path.exists(database_path):
        os.makedirs(database_path)
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
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

init_users_db()

def get_user_db(email):
    db_folder = os.path.join(database_path, email)
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        
    #props_db_name = os.path.join(db_folder, "memory.db")
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
                 display_on_page TEXT DEFAULT NULL,
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

    return db_name

def get_system_prompt_with_latest_facts(systemPrompt, email):    
    # replace the placeholder with the latest facts known about the user and the dashboard data. placeholder is [USER_FACTS] and [DASHBOARD_DATA]
    db_name = get_user_db(email)
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

    # Get dashboard data from database
    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT key, value FROM dashboard")
    rows = c.fetchall()
    conn.close()

    if not rows:
        dashboard_data = "\"dashboard\": {\"goal\": { \"box_content\": \"not enough information\", }, \"recommendations\": { \"box_content\": \"not enough information\", }, \"assets/liabilities\": { \"box_content\": \"not enough information\", }, \"income/expense\": { \"box_content\": \"not enough information\", } }"
    elif len(rows) > 0:
        dashboard_data = "dashboard: "
        for key, value in rows:
            dashboard_data += f'{{"{key}": {{"box_content": "{value}"}}}} '

    systemPrompt = systemPrompt.replace("[USER_FACTS]", user_facts)
    systemPrompt = systemPrompt.replace("[DASHBOARD_DATA]", dashboard_data)

    return [{"role": "system", "content": systemPrompt}]
      
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

def get_system_prompt_with_financial_documents(systemPrompt, email, stock):
    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    table_name = f"{stock}_stock_pdfs"
    try:
        c.execute(f"SELECT heading, pdf_content FROM {table_name}")
        rows = c.fetchall()
    except sqlite3.OperationalError:
        rows = []

    conn.close()

    if not rows:
        financial_documents = "There are no financial documents available for this stock."
    elif len(rows) > 0:
        financial_documents = json.dumps([{"heading": row[0], "pdf_content": row[1]} for row in rows])

    systemPrompt = systemPrompt.replace("[STOCK_NAME]", stock)
    systemPrompt = systemPrompt.replace("[FINANCIAL_DOCUMENTS]", financial_documents)

    return [{"role": "system", "content": systemPrompt}]

def save_conversation(email, role, content, display_on_page, text_sent_to_ai_in_the_prompt):
    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    prompt_details = json.dumps(text_sent_to_ai_in_the_prompt) if role == "assistant" else None
    c.execute("INSERT INTO conversation_history (role, content, display_on_page, prompt_details) VALUES (?, ?, ?, ?)", (role, content, display_on_page, prompt_details))
    conn.commit()
    conn.close()

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

def extract_analysis_json_from_text(text):
    # Initialize a counter for open and close braces
    open_braces = 0
    json_str = ""
    inside_json = False
    
    try:
        for char in text:
            if char == '{':
                open_braces += 1
                inside_json = True
            if inside_json:
                json_str += char
            if char == '}':
                open_braces -= 1
            if inside_json and open_braces == 0:
                break
        
        if json_str:
            return json.loads(json_str)
        else:
            logging.error("ERROR: JSON part not found in the response")
            return None
    except (ValueError, json.JSONDecodeError) as e:
        logging.error(f"ERROR: JSON decoding failed with error: {e}")
        return None

@app.route('/acr/ai_request', methods=['GET', 'POST'])
def ai_request():
    if request.method == 'GET':
        userEmail = request.args.get('userEmail')
        message = request.args.get('message')
        token = request.args.get('token')
        display_on_page = request.args.get('display_on_page')
        stock = request.args.get('stock')
    elif request.method == 'POST':
        data = request.get_json()
        userEmail = data.get('userEmail')
        message = data.get('message')
        token = data.get('token')
        display_on_page = data.get('display_on_page')
        stock = data.get('stock')

    if not userEmail:
        return jsonify({"error": "Email parameter is required"}), 400

    if not message:
        return jsonify({"error": "Message parameter is required"}), 400

    if not token:
        return jsonify({"error": "Token parameter is required"}), 400

    if not decode_token_and_get_email(token) == userEmail:
        return jsonify({"error": "Invalid token"}), 401

    response = None
    if display_on_page == 'dashboard':
        response = ai_request_on_dashboard(userEmail, message, display_on_page)

    elif display_on_page == 'portfolio-performance':
        response = ai_request_PORTFOLIO_PERFORMANCE(userEmail, message, display_on_page)

    elif display_on_page == 'stock-picker-discussion':
        response = ai_request_stock_picker_discussion(userEmail, message, display_on_page, stock)

    elif display_on_page == 'stock-picker-system-report':
        response = ai_request_stock_picker_system_report(userEmail, message, display_on_page, stock)

    return response

def ai_request_on_dashboard(userEmail, message, display_on_page):
  text_sent_to_ai_in_the_prompt = get_system_prompt_with_latest_facts(DASHBOARD_PROMPT, userEmail)
  text_sent_to_ai_in_the_prompt.append({"role": "user", "content": message})

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

  if response.choices[0].message.content:
    responseData = ''
    content = response.choices[0].message.content
    responseData = extract_json_from_text(content)

    if not responseData:
        logging.error("JSON part not found or error parsing JSON in the response")
        responseData = {"MsgForUser": content, "memory": {}}

    # Ensure responseData is a dictionary before accessing keys
    prompt_details = text_sent_to_ai_in_the_prompt
    if isinstance(responseData, dict):
        MsgForUser = responseData.get('MsgForUser', 'An error occurred. Please try again.')
        if MsgForUser != "An error occurred. Please try again.":
            prompt_details.append({"role": "response", "content": content})

            save_conversation(userEmail, "user", message, display_on_page, None)
            save_conversation(userEmail, "assistant", MsgForUser, display_on_page, prompt_details)

            memory = responseData.get('memory')
            save_memory(userEmail, memory)

            # save dashboard data
            dashboard = responseData.get('dashboard')
            save_dashboard_data(userEmail, dashboard)
    else:
        MsgForUser = "An error occurred. Please try again."

    # Get dashboard data from database and return it in the response
    db_name = get_user_db(userEmail)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT key, value FROM dashboard")
    rows = c.fetchall()
    conn.close()

    return jsonify({"response": MsgForUser, "responseData": content, "prompt_details": json.dumps(prompt_details), "dashboard": [{"key": key, "value": value} for key, value in rows], "model": model})
  else:
    return jsonify({"response": response})

def ai_request_PORTFOLIO_PERFORMANCE(userEmail, message, display_on_page):
    text_sent_to_ai_in_the_prompt = get_system_prompt_with_latest_assets(PORTFOLIO_PERFORMANCE_PROMPT, userEmail)
    text_sent_to_ai_in_the_prompt.append({"role": "user", "content": message})
    
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
            responseData = {"MsgForUser": content, "graph_data": {}, "recommendations": []}

        # Ensure responseData is a dictionary before accessing keys
        prompt_details = text_sent_to_ai_in_the_prompt
        if isinstance(responseData, dict):
            MsgForUser = responseData.get('MsgForUser', 'An error occurred. Please try again.')
            if MsgForUser != "An error occurred. Please try again.":
                prompt_details.append({"role": "response", "content": content})

                save_conversation(userEmail, "user", message, display_on_page, None)
                save_conversation(userEmail, "assistant", MsgForUser, display_on_page, prompt_details)
    
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
        c2.execute("SELECT id, parent_id, asset, qty, price, value, account, row_start, row_end FROM assets ORDER BY created_at DESC")
        assetsData = c2.fetchall()
        conn2.close()

        return jsonify({"response": MsgForUser, 
                        "responseData": content, 
                        "prompt_details": json.dumps(prompt_details), 
                        "graph_data": [{"key": key, "value": value} for key, value in rows], 
                        "recommendations": [recommendation[0] for recommendation in recommendations], 
                        "model": model,
                        "assets": [{"id": row[0], "parent_id": row[1], "asset": row[2], "qty": row[3], "price": row[4], "value": row[5], "account": row[6], "row_start": row[7], "row_end": row[8]} for row in assetsData]
                    })
    else:
        logging.error("Unexpected response format from OpenAI API")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500
        
def ai_request_stock_picker_discussion(userEmail, message, display_on_page, stock):
    text_sent_to_ai_in_the_prompt = get_system_prompt_with_financial_documents(STOCK_PICKER_DISCUSSION, userEmail, stock)
    text_sent_to_ai_in_the_prompt.append({"role": "user", "content": message})

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
        try:
            if response.startswith("Error code:"):
                json_part = response.split(" - ", 1)[1].replace("'", '"').replace("None", "null")
                response_dict = json.loads(json_part)
                error_message = response_dict.get('error', {}).get('message', 'An unknown error occurred.')
        except AttributeError:
            if "Request too large" in response:
                error_message = "The request is too large. Please try again with a smaller request."
            else:
                error_message = "An error occurred while processing your request. Please try again later."

        return jsonify({"response": error_message})

    if response.choices and response.choices[0].message.content:
        responseData = ''
        content = response.choices[0].message.content
        responseData = extract_json_from_text(content)

        if not responseData:
            logging.error("JSON part not found or error parsing JSON in the response")
            responseData = {"MsgForUser": content}

        # Ensure responseData is a dictionary before accessing keys
        prompt_details = text_sent_to_ai_in_the_prompt
        if isinstance(responseData, dict):
            MsgForUser = responseData.get('MsgForUser', 'An error occurred. Please try again.')
            if MsgForUser != "An error occurred. Please try again.":
                prompt_details.append({"role": "response", "content": content})

                save_conversation(userEmail, "user", message, display_on_page, None)
                save_conversation(userEmail, "assistant", MsgForUser, display_on_page, prompt_details)

                # save recommendation
                # recommendation = responseData.get('recommendation')
                # save_stock_recommendations(userEmail, recommendation, stock)

                # # Handle justifications
                # justification = responseData.get('justification')
                # save_stock_recommendation_jusitifications(userEmail, justification, stock)

                # save report data
                recommendation = responseData.get('recommendation')
                recommendation = recommendation if recommendation else None

                justification = responseData.get('justification')
                justification = justification if justification else None

                discount_rate = responseData.get('discount_rate')
                discount_rate = discount_rate if discount_rate else None

                net_present_value = responseData.get('net_present_value')
                net_present_value = net_present_value if net_present_value else None

                comparison = responseData.get('comparison')
                comparison = comparison if comparison else None

                graph_data_x_axis = responseData.get('graph_data').get('line_chart').get('x_axis') if responseData.get('graph_data') else None
                graph_data_y_axis = responseData.get('graph_data').get('line_chart').get('y_axis') if responseData.get('graph_data') else None

                # save stock report data
                save_stock_report_data(userEmail, stock, recommendation, justification, discount_rate, net_present_value, comparison, graph_data_x_axis, graph_data_y_axis)
        else:
            MsgForUser = "An error occurred. Please try again."

        # Get recommendation and justification from database and return it in the response
        db_name = get_user_db(userEmail)
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT recommendation, justification, discount_rate, net_present_value, comparison, graph_data_x_axis, graph_data_y_axis FROM stock_reports WHERE stock_name = ?", (stock,))
        reportRow = c.fetchone()
        conn.close()

        recommendationData = reportRow[0] if reportRow else None
        reportData = {
            "recommendation": recommendationData,
            "justification": reportRow[1] if reportRow else None,
            "discount_rate": reportRow[2] if reportRow[2] else None,
            "net_present_value": reportRow[3] if reportRow[3] else None,
            "comparison": reportRow[4] if reportRow[4] else None,
            "graph_data_x_axis": json.loads(reportRow[5]) if reportRow[5] else None,
            "graph_data_y_axis": json.loads(reportRow[6]) if reportRow[6] else None
        }

        # create a table if not already created to store the stock reports data. This table will store the user_id, stock_name, created_at
        db_name = os.path.join(database_path, "central-coordinator.db")
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS stock_reports
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        user_name TEXT NOT NULL,
                        stock_name TEXT NOT NULL,
                        recommendation TEXT DEFAULT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

        # insert the stock name and user_id into the stock_reports table. user_id is the id of the user in the users table where the email is the user's email
        c.execute("SELECT id, full_name FROM users WHERE email = ?", (userEmail,))
        row = c.fetchone()
        user_id = row[0] if row else None
        user_name = row[1] if row else None

        if user_id:
            # check if the stock name already exists in the stock_reports table for the user_id
            c.execute("SELECT 1 FROM stock_reports WHERE user_id = ? AND stock_name = ?", (user_id, stock))
            exists = c.fetchone()

            if exists:
                c.execute("UPDATE stock_reports SET recommendation = ? WHERE user_id = ? AND stock_name = ?", (recommendationData, user_id, stock))
            else:
                c.execute("INSERT INTO stock_reports (user_id, user_name, stock_name, recommendation) VALUES (?, ?, ?, ?)", (user_id, user_name, stock, recommendationData))

        conn.commit()
        conn.close()

        return jsonify({"response": MsgForUser, "responseData": content, "model": model, "reportRow": reportData, "prompt_details": json.dumps(prompt_details)})
    else:
        logging.error("Unexpected response format from OpenAI API")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

def ai_request_stock_picker_system_report(userEmail, message, display_on_page, stock):
    text_sent_to_ai_in_the_prompt = get_system_prompt_with_financial_documents(STOCK_PICKER_SYSTEM_REPORT, userEmail, stock)
    text_sent_to_ai_in_the_prompt.append({"role": "user", "content": message})

    # get openai apikey and model
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
        prompt_details = text_sent_to_ai_in_the_prompt
        if isinstance(responseData, dict):
            MsgForUser = responseData.get('MsgForUser', 'An error occurred. Please try again.')
            if MsgForUser != "An error occurred. Please try again.":
                prompt_details.append({"role": "response", "content": content})

                save_conversation(userEmail, "user", message, display_on_page, None)
                save_conversation(userEmail, "assistant", MsgForUser, display_on_page, prompt_details)
        else:
            MsgForUser = "An error occurred. Please try again."

        return jsonify({"response": MsgForUser, "responseData": content, "model": model, "prompt_details": json.dumps(prompt_details)})

def save_stock_report_data(email, stock, recommendation, justification, discount_rate, net_present_value, comparison, graph_data_x_axis, graph_data_y_axis):
    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    current_time_ms = int(datetime.datetime.now().timestamp() * 1000)

    # if graph_data_x_axis and graph_data_y_axis are lists, convert them to strings
    if isinstance(graph_data_x_axis, list):
        graph_data_x_axis = json.dumps(graph_data_x_axis)

    if isinstance(graph_data_y_axis, list):
        graph_data_y_axis = json.dumps(graph_data_y_axis)

    c.execute("SELECT 1 FROM stock_reports WHERE stock_name = ?", (stock,))
    exists = c.fetchone()

    if exists:
        c.execute("UPDATE stock_reports SET recommendation = ?, justification = ?, discount_rate = ?, net_present_value = ?, comparison = ?, graph_data_x_axis = ?, graph_data_y_axis = ? WHERE stock_name = ?", (recommendation, justification, discount_rate, net_present_value, comparison, graph_data_x_axis, graph_data_y_axis, stock))
    else:
        c.execute("INSERT INTO stock_reports (stock_name, recommendation, justification, discount_rate, net_present_value, comparison, graph_data_x_axis, graph_data_y_axis, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (stock, recommendation, justification, discount_rate, net_present_value, comparison, graph_data_x_axis, graph_data_y_axis, current_time_ms))

    conn.commit()
    conn.close()

@app.route('/acr/stock/report', methods=['GET'])
def get_stock_report():
    stock = request.args.get('stock')
    userEmail = request.args.get('userEmail')
    token = request.args.get('token')
    reportOfUid = request.args.get('reportOfUid')

    if not token:
        return jsonify({"error": "Token parameter is required"}), 400

    if not stock:
        return jsonify({"error": "Stock parameter is required"}), 400

    if not userEmail:
        return jsonify({"error": "Email parameter is required"}), 400

    if not decode_token_and_get_email(token) == userEmail:
        return jsonify({"error": "Invalid token"}), 401

    if reportOfUid:
        db_name = os.path.join(database_path, "central-coordinator.db")
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT email FROM users WHERE id = ?", (reportOfUid,))
        row = c.fetchone()
        conn.close()

        reportOfEmail = row[0] if row else None
    else:
        reportOfEmail = userEmail

    if not reportOfEmail:
        return jsonify({"error": "Invalid reportOfUid"}), 400

    db_name = get_user_db(reportOfEmail)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    #c.execute("SELECT recommendation, justification FROM stock_reports WHERE stock_name = ?", (stock,))
    c.execute("SELECT recommendation, justification, discount_rate, net_present_value, comparison, graph_data_x_axis, graph_data_y_axis FROM stock_reports WHERE stock_name = ?", (stock,))
    reportRow = c.fetchone()
    conn.close()

    if not reportRow:
        reportData = {
            "recommendation": None,
            "justification": None,
            "discount_rate": None,
            "net_present_value": None,
            "comparison": None,
            "graph_data_x_axis": None,
            "graph_data_y_axis": None
        }
    else:
        reportData = {
            "recommendation": reportRow[0] if reportRow else None,
            "justification": reportRow[1] if reportRow else None,
            "discount_rate": reportRow[2] if reportRow[2] else None,
            "net_present_value": reportRow[3] if reportRow[3] else None,
            "comparison": reportRow[4] if reportRow[4] else None,
            "graph_data_x_axis": json.loads(reportRow[5]) if reportRow[5] else None,
            "graph_data_y_axis": json.loads(reportRow[6]) if reportRow[6] else None
        }

    # Get the all user_id from the stock_reports table where the stock_name is the stock.
    db_name = os.path.join(database_path, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT user_id, user_name, recommendation FROM stock_reports WHERE stock_name = ?", (stock,))
    rows = c.fetchall()
    conn.close()

    return jsonify({"reportData": reportData, "enhancedReportList": [{"id": row[0], "name": row[1], "recommendation": row[2]} for row in rows]})

@app.route('/acr/stock/recommendations', methods=['GET'])
def get_stock_recommendations():
    userEmail = request.args.get('userEmail')
    token = request.args.get('token')

    if not token:
        return jsonify({"error": "Token parameter is required"}), 400

    if not userEmail:
        return jsonify({"error": "Email parameter is required"}), 400

    if not decode_token_and_get_email(token) == userEmail:
        return jsonify({"error": "Invalid token"}), 401

    db_name = os.path.join(database_path, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    #c.execute("SELECT stock_name, recommendation FROM stock_reports WHERE user_id = 1")
    c.execute("SELECT stock_name, recommendation FROM stock_reports GROUP BY stock_name")
    rows = c.fetchall()
    conn.close()

    return jsonify({"recommendations": [{"stock": row[0], "recommendation": row[1]} for row in rows]})

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
        c.execute("SELECT id FROM assets WHERE asset = ? AND row_end IS NULL", (asset,))
        row = c.fetchone()
        if row:
            asset_id = row[0]
            c.execute("UPDATE assets SET qty = ?, price = ?, value = ?, account = ? WHERE id = ?", (qty, price, value, account, asset_id))
            conn.commit()
            conn.close()

            logging.info(f"Edited asset for user {userEmail}: {asset}")
        else:
            logging.error(f"Asset not found for user {userEmail}: {asset}")

def save_dashboard_data(email, dashboard):
    if dashboard:
        # Database operations
        db_name = get_user_db(email)
        conn1 = sqlite3.connect(db_name)
        c1 = conn1.cursor()

        for key, value in dashboard.items():
            if isinstance(value, dict) and 'box_content' in value:
                # Check if the key already exists in the dashboard table
                c1.execute("SELECT 1 FROM dashboard WHERE key = ?", (key,))
                exists = c1.fetchone()

                if exists:
                    # If the key exists, update the value
                    c1.execute("UPDATE dashboard SET value = ? WHERE key = ?", (value['box_content'], key))
                else:
                    # If the key does not exist, insert a new key-value pair
                    c1.execute("INSERT INTO dashboard (key, value) VALUES (?, ?)", (key, value['box_content']))
            else:
                print(f"Invalid value for key '{key}': Expected a dictionary with 'box_content'")

        conn1.commit()
        conn1.close()
    else:
        print("Dashboard key is missing in responseData")

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

@app.route('/acr/get_ig_analysis', methods=['POST'])
def get_ig_analysis():
    data = request.get_json()
    token = data.get('token')
    email = data.get('email')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    # Get graph data from database
    db_name = get_user_db(email)
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

    return jsonify({"graph_data": [{"key": key, "value": value} for key, value in rows], "recommendations": [recommendation[0] for recommendation in recommendations]})

@app.route('/acr/get_conversation', methods=['GET', 'POST'])
def get_conversation():
  if request.method == 'GET':
    userEmail = request.args.get('userEmail')
    token = request.args.get('token')
    display_on_page = request.args.get('display_on_page')
  elif request.method == 'POST':
    data = request.get_json()
    userEmail = data.get('userEmail')
    token = data.get('token'),
    display_on_page = data.get('display_on_page')

  if not userEmail:
    return jsonify({"error": "Email parameter is required"}), 400

  if not token:
    return jsonify({"error": "Token parameter is required"}), 400

  if not decode_token_and_get_email(token) == userEmail:
    return jsonify({"error": "Invalid token"}), 401

  db_name = get_user_db(userEmail)
  conn = sqlite3.connect(db_name)
  c = conn.cursor()
  c.execute("SELECT role, content, prompt_details FROM conversation_history WHERE display_on_page = ? ORDER BY timestamp", (display_on_page,))
  rows = c.fetchall()
  conn.close()

  # get data from props table
  db_name = get_user_db(userEmail)
  conn1 = sqlite3.connect(db_name)
  c1 = conn1.cursor()
  c1.execute("SELECT key, value FROM basic_memory")
  rows1 = c1.fetchall()
  conn1.close()

  # get data from dashboard table
  db_name = get_user_db(userEmail)
  conn2 = sqlite3.connect(db_name)
  c2 = conn2.cursor()
  c2.execute("SELECT key, value FROM dashboard")
  rows2 = c2.fetchall()
  conn2.close()

  if not rows:
    return jsonify({"conversation": []})
  else:
    return jsonify({"conversation": [{"role": role, "content": content, "prompt_details": prompt_details} for role, content, prompt_details in rows], "basic_memory": [{"key": key, "value": value} for key, value in rows1], "dashboard": [{"key": key, "value": value} for key, value in rows2]})

@app.route('/acr/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        userEmail = request.args.get('email')
        fullName = request.args.get('fullName')
        password = request.args.get('password')
    elif request.method == 'POST':
        data = request.get_json()
        userEmail = data.get('email')
        fullName = data.get('fullName')
        password = data.get('password')

    if not userEmail or not fullName or not password:
        return jsonify({"error": "Email, full name, and password are required"}), 400

    hashed_password = generate_password_hash(password)

    db_name = os.path.join(database_path, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (email, full_name, password) VALUES (?, ?, ?)", (userEmail, fullName, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    finally:
        conn.close()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/acr/join_waitlist', methods=['POST'])
def join_waitlist():
    data = request.get_json()
    full_name = data.get('fullName')
    email = data.get('email')
    password = data.get('password')
    about_yourself = data.get('aboutYourself')
    biggest_problem = data.get('biggestProblem')
    invite_code = data.get('inviteCode')

    if not full_name or not email or not about_yourself or not biggest_problem:
        return jsonify({"error": "All fields are required"}), 400

    if invite_code and invite_code != 'jaikalima':
        return jsonify({"error": "Invalid invite code"}), 400

    db_name = os.path.join(database_path, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Check if the invite code is not empty and invite code='jaikalima' then set is_waitlist to False else True
    if invite_code and invite_code == 'jaikalima':
        is_waitlist = False
    else:
        is_waitlist = True

    try:
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (email, full_name, password, about_yourself, biggest_problem, is_waitlist) VALUES (?, ?, ?, ?, ?, ?)", (email, full_name, hashed_password, about_yourself, biggest_problem, is_waitlist))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    finally:
        conn.close()

    return jsonify({"message": "Successfully joined the waitlist"}), 201

@app.route('/acr/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        userEmail = request.args.get('email')
        password = request.args.get('password')
    elif request.method == 'POST':
        data = request.get_json()
        userEmail = data.get('email')
        password = data.get('password')

    if not userEmail or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db_name = os.path.join(database_path, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT password, full_name, is_waitlist FROM users WHERE email = ?", (userEmail,))
    row = c.fetchone()
    conn.close()

    # Check if the user is in the waitlist
    if row and row[2]:
        return jsonify({"error": "User is in the waitlist"}), 403
    elif row and check_password_hash(row[0], password):
        secret_key = md5_hash(password)
        payload = {
            'userEmail': userEmail,
            'exp': time.time() + 86400  # 24 hours expiration
        }
        token = generate_token(payload, secret_key)
        return jsonify({"message": "Login successful", "token": token, "fullName": row[1], "userEmail": userEmail}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route('/acr/validate_token', methods=['GET', 'POST'])
def validate_token():
    if request.method == 'GET':
        token = request.args.get('token')
    elif request.method == 'POST':
        data = request.get_json()
        token = data.get('token')

    if not token:
        return jsonify({"error": "Token is required", "valid": False}), 400

    userEmail = decode_token_and_get_email(token)

    if userEmail:
        db_name = os.path.join(database_path, "central-coordinator.db")
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        c.execute("SELECT full_name FROM users WHERE email = ?", (userEmail,))
        row = c.fetchone()
        conn.close()

        if row:
            return jsonify({"userEmail": userEmail, "fullName": row[0], "valid": True}), 200
        else:
            return jsonify({"error": "User not found", "valid": False}), 404
    else:
        return jsonify({"error": "Invalid token", "valid": False}), 401

@app.route('/acr/download_db', methods=['GET'])
def download_db():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token parameter is required"}), 400

    userEmail = decode_token_and_get_email(token)
    if not userEmail:
        return jsonify({"error": "Invalid token"}), 401

    db_name = get_user_db(userEmail)

    return send_file(db_name, as_attachment=True, download_name=f"{userEmail}_data.db")

@app.route('/acr/settings', methods=['POST'])
def get_settings():
    data = request.get_json()
    token = data.get('token')
    email = data.get('email')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    db_name = os.path.join(database_path, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT openai_api_key, openai_model FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({"openai_api_key": row[0], "openai_model": row[1]}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/acr/settings/openai', methods=['POST'])
def openai_settings():
    data = request.get_json()
    api_key = data.get('apiKey')
    model = data.get('model')
    token = data.get('token')
    email = data.get('email')

    if not api_key or not model or not token or not email:
        return jsonify({"error": "apiKey and model are required"}), 400

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    db_name = os.path.join(database_path, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("UPDATE users SET openai_api_key = ?, openai_model = ? WHERE email = ?", (api_key, model, email))
    conn.commit()
    conn.close()

    return jsonify({"message": "OpenAI settings updated successfully"}), 200

@app.route('/acr/assets', methods=['GET'])
def get_assets():
    token = request.args.get('token')
    email = request.args.get('email')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT id, parent_id, asset, qty, price, value, account, row_start, row_end FROM assets ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    slider_min = rows[-1][7] if rows else 0
    slider_max = int(datetime.datetime.now().timestamp() * 1000)
    return jsonify({"rows": [{"id": row[0], "parent_id": row[1], "asset": row[2], "qty": row[3], "price": row[4], "value": row[5], "account": row[6], "row_start": row[7], "row_end": row[8]} for row in rows], "slider_info": {"slider_min": slider_min, "slider_max": slider_max}})

@app.route('/acr/assets/add', methods=['POST']) 
def add_asset():
    data = request.get_json()
    token = data.get('token')
    email = data.get('email')
    asset = data.get('asset')
    qty = data.get('qty')
    price = data.get('price')
    value = data.get('value')
    account = data.get('account')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    if not asset or not qty or not price:
        return jsonify({"error": "Asset, quantity, and price are required"}), 400

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Insert the new row with a placeholder for parent_id
    current_time_ms = int(datetime.datetime.now().timestamp() * 1000)
    c.execute("INSERT INTO assets (parent_id, asset, qty, price, value, account, row_start) VALUES (?, ?, ?, ?, ?, ?, ?)", (0, asset, qty, price, value, account, current_time_ms))
    conn.commit()

    # Get the last inserted row ID
    last_id = c.lastrowid

    # Update the parent_id to be the same as the primary key id of the inserted row
    c.execute("UPDATE assets SET parent_id = ? WHERE id = ?", (last_id, last_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Asset added successfully"}), 201

@app.route('/acr/assets/edit', methods=['POST'])
def edit_asset():
    data = request.get_json()
    token = data.get('token')
    email = data.get('email')
    asset_id = data.get('id')
    asset = data.get('asset')
    qty = data.get('qty')
    price = data.get('price')
    value = data.get('value')
    account = data.get('account')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    if not asset_id:
        return jsonify({"error": "Asset ID is required"}), 400

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
    row = c.fetchone()

    if not row:
        return jsonify({"error": "Asset not found"}), 404

    current_time_ms = int(datetime.datetime.now().timestamp() * 1000)
    c.execute("UPDATE assets SET row_end = ? WHERE id = ?", (current_time_ms, asset_id))
    conn.commit()

    c.execute("INSERT INTO assets (parent_id, asset, qty, price, value, account, row_start) VALUES (?, ?, ?, ?, ?, ?, ?)", (row[1], asset, qty, price, value, account, current_time_ms))
    conn.commit()
    conn.close()

    return jsonify({"message": "Asset updated successfully"}), 200

@app.route('/acr/assets/delete', methods=['POST'])
def delete_asset():
    data = request.get_json()
    token = data.get('token')
    email = data.get('email')
    asset_id = data.get('id')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    if not asset_id:
        return jsonify({"error": "Asset ID is required"}), 400

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
    row = c.fetchone()

    if not row:
        return jsonify({"error": "Asset not found"}), 404

    current_time_ms = int(datetime.datetime.now().timestamp() * 1000)
    c.execute("UPDATE assets SET row_end = ? WHERE id = ?", (current_time_ms, asset_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Asset deleted successfully"}), 200

@app.route('/acr/accounts', methods=['GET'])
def get_accounts():
    token = request.args.get('token')
    email = request.args.get('email')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT id, name, account_number, is_it_active FROM accounts ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    return jsonify([{"id": row[0], "name": row[1], "account_number": row[2], "is_it_active": row[3]} for row in rows])

@app.route('/acr/accounts/add', methods=['POST'])
def add_account():
    data = request.get_json()
    token = data.get('token')
    email = data.get('email')
    name = data.get('name')
    account_number = data.get('account_number')
    is_it_active = data.get('is_it_active')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    if not name or not account_number or not is_it_active:
        return jsonify({"error": "Name, account number, and active status are required"}), 400

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("INSERT INTO accounts (name, account_number, is_it_active) VALUES (?, ?, ?)", (name, account_number, is_it_active))
    conn.commit()
    conn.close()

    return jsonify({"message": "Account added successfully"}), 201

@app.route('/acr/accounts/edit', methods=['POST'])
def edit_account():
    data = request.get_json()
    token = data.get('token')
    email = data.get('email')
    account_id = data.get('id')
    name = data.get('name')
    account_number = data.get('account_number')
    is_it_active = data.get('is_it_active')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
    row = c.fetchone()

    if not row:
        return jsonify({"error": "Account not found"}), 404

    c.execute("UPDATE accounts SET name = ?, account_number = ?, is_it_active = ? WHERE id = ?", (name, account_number, is_it_active, account_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Account updated successfully"}), 200

@app.route('/acr/accounts/delete', methods=['POST'])
def delete_account():
    data = request.get_json()
    token = data.get('token')
    email = data.get('email')
    account_id = data.get('id')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
    row = c.fetchone()

    if not row:
        return jsonify({"error": "Account not found"}), 404

    c.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Account deleted successfully"}), 200

@app.route('/acr/stock/upload-pdf', methods=['POST'])
def upload_pdf():
    token = request.form.get('token')
    email = request.form.get('userEmail')
    stock = request.form.get('stock')
    heading = request.form.get('heading')
    files = request.files.getlist('files')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    if not files or len(files) == 0:
        return jsonify({"error": "No files uploaded"}), 400

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Dynamically create table name based on stock
    table_name = f"{stock}_stock_pdfs"
    c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   heading TEXT DEFAULT NULL,
                   pdf_name TEXT NOT NULL,
                   pdf_content TEXT NOT NULL,
                   pdf_file_data BLOB DEFAULT NULL,
                   created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                 )''')

    # Save PDFs and their content in the database
    for file in files:
        timestamp = int(datetime.datetime.now().timestamp())
        pdf_name = f"{timestamp}_{file.filename}"

        # Read the file content as binary data
        pdf_file_data = file.read()

        # Reset the file pointer to the beginning
        file.seek(0)

        # Extract the content of the PDF file
        pdf_content = ""
        with fitz.open(stream=pdf_file_data, filetype="pdf") as doc:
            for page in doc:
                pdf_content += page.get_text()

        c.execute(f"INSERT INTO {table_name} (heading, pdf_name, pdf_content, pdf_file_data) VALUES (?, ?, ?, ?)",
                  (heading, pdf_name, pdf_content, pdf_file_data))

    conn.commit()
    conn.close()

    return jsonify({"message": "PDFs uploaded successfully"}), 201

@app.route('/acr/stock/get-pdfs', methods=['GET'])
def get_pdfs():
    token = request.args.get('token')
    email = request.args.get('userEmail')
    stock = request.args.get('stock')
    reportOfUid = request.args.get('reportOfUid')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    if reportOfUid:
        db_name = os.path.join(database_path, "central-coordinator.db")
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT email FROM users WHERE id = ?", (reportOfUid,))
        row = c.fetchone()
        conn.close()

        reportOfEmail = row[0] if row else None
    else:
        reportOfEmail = email

    if not reportOfEmail:
        return jsonify({"error": "Invalid reportOfUid"}), 400

    db_name = get_user_db(reportOfEmail)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    table_name = f"{stock}_stock_pdfs"
    try:
        c.execute(f"SELECT id, heading, pdf_name, pdf_content, created_at FROM {table_name}")
        rows = c.fetchall()
        conn.close()

        return jsonify([{
            "id": row[0],
            "heading": row[1],
            "pdf_name": row[2],
            "pdf_content": row[3],
            "created_at": row[4]
        } for row in rows])
    except sqlite3.OperationalError:
        if reportOfUid:
            # return blank
            return jsonify([])
        else:
            db_name = os.path.join(database_path, "central-coordinator.db")
            conn = sqlite3.connect(db_name)
            c = conn.cursor()
            c.execute("SELECT email FROM users WHERE id = 1")
            row = c.fetchone()
            conn.close()

            central_coordinator_email = row[0] if row else None

            if not central_coordinator_email:
                return jsonify({"error": "Central coordinator email not found"}), 404

            central_coordinator_db_name = get_user_db(central_coordinator_email)
            conn = sqlite3.connect(central_coordinator_db_name)
            c = conn.cursor()

            table_name = f"{stock}_stock_pdfs"
            c.execute(f"SELECT heading, pdf_name, pdf_content, pdf_file_data FROM {table_name}")
            rows = c.fetchall()
            conn.close()

            # Insert the PDFs into the current user's database
            db_name = get_user_db(reportOfEmail)
            conn = sqlite3.connect(db_name)
            c = conn.cursor()

            c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            heading TEXT DEFAULT NULL,
                            pdf_name TEXT NOT NULL,
                            pdf_content TEXT NOT NULL,
                            pdf_file_data BLOB DEFAULT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                            )''')

            for row in rows:
                c.execute(f"INSERT INTO {table_name} (heading, pdf_name, pdf_content, pdf_file_data) VALUES (?, ?, ?, ?)", (row[0], row[1], row[2], row[3]))

            conn.commit()
            conn.close()

            # Get the PDFs from the current user's database
            conn = sqlite3.connect(db_name)
            c = conn.cursor()
            c.execute(f"SELECT id, heading, pdf_name, pdf_content, created_at FROM {table_name}")
            rows = c.fetchall()
            conn.close()

            return jsonify([{
                "id": row[0],
                "heading": row[1],
                "pdf_name": row[2],
                "pdf_content": row[3],
                "created_at": row[4]
            } for row in rows])

@app.route('/acr/stock/get-pdf/<int:pdf_id>', methods=['GET'])
def get_pdf(pdf_id):
    email = request.args.get('userEmail')
    stock = request.args.get('stock')

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    table_name = f"{stock}_stock_pdfs"
    c.execute(f"SELECT pdf_file_data FROM {table_name} WHERE id = ?", (pdf_id,))
    pdf_data = c.fetchone()

    conn.close()

    if pdf_data and pdf_data[0]:
        return pdf_data[0], 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'inline; filename={pdf_id}.pdf'
        }
    else:
        return jsonify({"error": "PDF not found"}), 404

@app.route('/acr/stock/pdf/update-heading', methods=['POST'])
def update_pdf_heading():
    data = request.get_json()
    token = data.get('token')
    email = data.get('userEmail')
    stock = data.get('stock')
    pdf_id = data.get('id')
    heading = data.get('heading')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    if not pdf_id:
        return jsonify({"error": "PDF ID is required"}), 400

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    table_name = f"{stock}_stock_pdfs"
    c.execute(f"UPDATE {table_name} SET heading = ? WHERE id = ?", (heading, pdf_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "PDF heading updated successfully"}), 200

@app.route('/acr/stock/pdf/delete', methods=['POST'])
def delete_pdf():
    data = request.get_json()
    token = data.get('token')
    email = data.get('userEmail')
    stock = data.get('stock')
    pdf_id = data.get('id')

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    if not pdf_id:
        return jsonify({"error": "PDF ID is required"}), 400

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    table_name = f"{stock}_stock_pdfs"
    # c.execute(f"SELECT pdf_path FROM {table_name} WHERE id = ?", (pdf_id,))
    # row = c.fetchone()

    # if not row:
    #     return jsonify({"error": "PDF not found"}), 404

    #pdf_path = row[0]
    #os.remove(pdf_path)

    c.execute(f"DELETE FROM {table_name} WHERE id = ?", (pdf_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "PDF deleted successfully"}), 200

@app.route('/acr/stock/add', methods=['POST'])
def add_stock():
    data = request.get_json()
    token = data.get('token')
    email = data.get('userEmail')
    stock = data.get('stockName')
    
    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    db_name = os.path.join(database_path, "central-coordinator.db")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS stock_reports
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        user_name TEXT NOT NULL,
                        stock_name TEXT NOT NULL,
                        recommendation TEXT DEFAULT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    c.execute("SELECT id, full_name FROM users WHERE email = ?", (email,))
    row = c.fetchone()

    if not row:
        return jsonify({"error": "User not found"}), 404

    user_id = row[0]
    user_name = row[1]

    c.execute("SELECT 1 FROM stock_reports WHERE user_id = ? AND stock_name = ?", (user_id, stock))
    row = c.fetchone()

    if row:
        return jsonify({"error": "Stock already exists"}), 400

    c.execute("INSERT INTO stock_reports (user_id, user_name, stock_name) VALUES (?, ?, ?)", (user_id, user_name, stock))
    conn.commit()
    conn.close()

    # insert the stock into the stock_reports table of the user's database
    user_db_name = get_user_db(email)
    conn = sqlite3.connect(user_db_name)
    c = conn.cursor()

    c.execute("INSERT INTO stock_reports (stock_name) VALUES (?)", (stock,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Stock added successfully"}), 201    

@app.route('/acr/get_tab_settings', methods=['POST'])
def get_tab_settings():
    data = request.get_json()
    email = data.get('email')
    token = data.get('token')

    if not email or not token:
        return jsonify({"error": "Email and token are required"}), 400

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT value FROM user_settings WHERE key = ?", ('tab_settings',))
    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({"settings": row[0]})
    else:
        return jsonify({"settings": None})

@app.route('/acr/save_tab_settings', methods=['POST'])
def save_tab_settings():
    data = request.get_json()
    email = data.get('email')
    token = data.get('token')
    settings = data.get('settings')

    if not email or not token or not settings:
        return jsonify({"error": "Email, token, and settings are required"}), 400

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
              ('tab_settings', settings))
    conn.commit()
    conn.close()

    return jsonify({"message": "Settings saved successfully"})


if __name__ == '__main__':
    init_users_db()
    app.run(host='0.0.0.0', port=3003, debug=True)
