import sqlite3
import pandas as pd

conn = sqlite3.connect('health_vault.db')
cur = conn.cursor()

email = "abc@gmail.com"
cur.execute("SELECT id FROM users WHERE email = ?", (email,))
user = cur.fetchone()

if user:
    user_id = user[0]
    print(f"User ID: {user_id}")
    df = pd.read_sql_query("SELECT * FROM progress WHERE user_id = ?", conn, params=(user_id,))
    print(f"Progress entries count: {len(df)}")
    print(df[['date', 'weight', 'kcal']])
else:
    print("User not found")

conn.close()
