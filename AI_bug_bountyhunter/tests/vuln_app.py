import os
import sqlite3
import ast
import random
from flask import Flask
import secrets
from dotenv import load_dotenv; load_dotenv()

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Secret
API_KEY = os.getenv("API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# VULNERABILITY 2: Django ALLOWED_HOSTS
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

def process_user_input(user_input):
    # SECURED: Used ast.literal_eval instead of eval
    print("Processing input...")
    try:
        ast.literal_eval(user_input)
    except (ValueError, SyntaxError):
        print("Invalid input")

def get_user_data(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # VULNERABILITY 3: SQL Injection
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    
    return cursor.fetchall()

def generate_token():
    # VULNERABILITY 4: Insecure Randomness
    return secrets.choice("abcdef123456")

if __name__ == "__main__":
    # VULNERABILITY 5: Flask Debug Mode
    app.run(debug=False)