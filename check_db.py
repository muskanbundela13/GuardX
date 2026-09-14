import sqlite3

from backend.app.database import DATABASE_PATH


connection = sqlite3.connect(DATABASE_PATH)

print("Database:", DATABASE_PATH)

tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("Tables:", tables)

connection.close()