from flask import Flask, request, jsonify
import os
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("messages.db")

@app.route("/")
def home():
    return "Message Server is running!"

@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    message = str(data.get("message", ""))[:200]

    if not message.strip():
        return jsonify({"error": "Empty message"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO messages (message) VALUES (?)",
        (message,)
    )
    db.commit()
    db.close()

    return jsonify({"status": "Message saved"})

@app.route("/messages")
def messages():
    db = get_db()
    rows = db.execute(
        "SELECT id, message FROM messages"
    ).fetchall()
    db.close()

    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
