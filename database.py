import sqlite3

connection = sqlite3.connect("messages.db")

connection.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL
)
""")

connection.commit()
connection.close()

print("Database created successfully!")
