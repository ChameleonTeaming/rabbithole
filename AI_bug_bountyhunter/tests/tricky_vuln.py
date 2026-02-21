import os
import sqlite3

def tricky_eval(user_input):
    # Tricky: eval is split across lines (Regex often fails this)
    func = eval
    func(user_input)

def tricky_sql(username):
    conn = sqlite3.connect('db')
    cur = conn.cursor()
    # Tricky: f-string SQL injection
    cur.execute("SELECT * FROM users WHERE name = ?", (username,))

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    # Tricky: Debug is a kwarg, not simple assignment
    app.run(host='0.0.0.0', port=5000, debug=False)
