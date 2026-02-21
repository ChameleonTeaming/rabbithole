import os
import sqlite3
import ast
from flask import Flask
from dotenv import load_dotenv; load_dotenv()

app = Flask(__name__)

# --- SECTION 1: SECRETS ---
# [TRUE POSITIVE] High entropy, looks like a real key
AWS_SECRET = os.getenv("AWS_SECRET") 
# [FALSE POSITIVE] Low entropy, common word (Should be Low Risk or Ignored)
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD") 
# [FALSE POSITIVE] Safe because it's in a print statement/string literal context?
print("Your API_KEY is set to: XXXXX") 

# --- SECTION 2: SQL INJECTION ---
def query_db(user_input):
    conn = sqlite3.connect("db")
    cur = conn.cursor()
    
    # [TRUE POSITIVE] Standard Concatenation
    cur.execute("SELECT * FROM users WHERE id = ?", (user_input,))
    
    # [TRUE POSITIVE] F-String
    cur.execute("DELETE FROM data WHERE id = ?", (user_input,))
    
    # [FALSE POSITIVE] Parameterized (Safe)
    cur.execute("SELECT * FROM users WHERE id = ?", (user_input,))

# --- SECTION 3: RCE (Remote Code Execution) ---
def calculator(expression):
    # [TRUE POSITIVE] Dangerous
    ast.literal_eval(expression)
    
    # [FALSE POSITIVE] Safe alternative
    ast.literal_eval(expression)

# --- SECTION 4: CONFIGURATION ---
if __name__ == "__main__":
    # [TRUE POSITIVE] Debug enabled
    app.run(debug=False)
    
    # [FALSE POSITIVE] Debug disabled (Should be ignored)
    # app.run(debug=False)