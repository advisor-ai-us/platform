from flask import jsonify, request
import sqlite3
from common_utils import get_user_db
from http_endpoint import app, decode_token_and_get_email

@app.route('/acr/get_phq9', methods=['GET'])
def get_phq9():
    email = request.args.get('email')
    token = request.args.get('token')

    if not email or not token:
        return jsonify({"error": "Email and token are required"}), 400

    if not decode_token_and_get_email(token) == email:
        return jsonify({"error": "Invalid token"}), 401

    db_name = get_user_db(email)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # check if the phq9 table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phq9'")
    row = c.fetchone()

    if not row:
        return jsonify({"error": "PHQ9 table not found"}), 404

    c.execute("SELECT question, answer, score, created_at FROM phq9 ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    return jsonify([{"question": row[0], "answer": row[1], "score": row[2], "createdAt": row[3]} for row in rows])
