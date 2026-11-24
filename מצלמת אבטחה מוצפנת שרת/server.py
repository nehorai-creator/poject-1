import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# הגדרת נתיב מסד הנתונים
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "dataBase.db")

# פונקציה ליצירת מסד הנתונים והטבלה אם אינם קיימים
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# הפעלה ראשונית של יצירת המסד
init_db()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        print(f"\n[+] משתמש חדש נרשם בהצלחה: {username}")
        return jsonify({"status": "success", "message": "Account created successfully!"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Username already exists!"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    if user and check_password_hash(user[0], password):
        print(f"\n[+] התחברות מוצלחת עבור: {username}")
        return jsonify({"status": "success", "message": "Login successful!"}), 200

    print(f"\n[-] ניסיון התחברות שנכשל עבור: {username}")
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  השרת הופעל בהצלחה וממתין לחיבורים!")
    print("  כתובת השרת: http://127.0.0.1:5000")
    print("  (השאר חלון זה פתוח, והפעל כעת את main.py)")
    print("=" * 50 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=False)