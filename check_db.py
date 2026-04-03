import sqlite3
import os

db_path = 'health_vault.db'
if not os.path.exists(db_path):
    print(f"File {db_path} NOT FOUND")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()
try:
    cur.execute("SELECT email, password FROM users;")
    rows = cur.fetchall()
    for row in rows:
        print(f"USER: {row[0]} | HASH: {row[1]}")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    conn.close()
