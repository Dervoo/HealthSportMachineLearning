import sqlite3
import hashlib
import bcrypt
from datetime import datetime, timedelta
import random

def get_password_hash(password):
    pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return bcrypt.hashpw(pwd_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed():
    conn = sqlite3.connect('health_vault.db')
    cur = conn.cursor()
    
    email = "abc@gmail.com"
    password = "123"
    hashed_pw = get_password_hash(password)
    
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    
    if not user:
        cur.execute("""
            INSERT INTO users (name, email, password, age, height, gender, activity_level, goal, target_kcal, target_protein, water_goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("ABC User", email, hashed_pw, 28, 175, "Mężczyzna", 1.55, "masa", 2800, 160, 3.0))
        user_id = cur.lastrowid
    else:
        user_id = user[0]

    today = datetime(2026, 4, 3).date()
    
    workouts = [
        "Pompki z plecakiem 15kg(3x15.0kg x 12,12,12); Podciąganie(3x0.0kg x 8,8,8)",
        "Bieganie (400 kcal)",
        "Bułgarskie przysiady(3x24.0kg x 10,10,10); RDL 24kg+15kg(3x39.0kg x 12,12,12)",
        "Rest Day",
        "Pompki z plecakiem 15kg(4x15.0kg x 10,10,10,10)",
        "Podciąganie(4x0.0kg x 6,6,6,6); Wiosłowanie 24kg+15kg(3x39.0kg x 10,10,10)",
        "Bieganie (350 kcal)",
        "Rest Day",
        "Barki OHP 24kg(3x24.0kg x 8,8,8); Floor Press 24kg(3x24.0kg x 12,12,12)",
        "Pompki nogi wyżej(3x0.0kg x 15,15,15)",
        "Dipsy(3x15.0kg x 10,10,10); Podciąganie podchwytem(3x0.0kg x 8,8,8)"
    ]

    cur.execute("DELETE FROM progress WHERE user_id = ?", (user_id,))
    cur.execute("DELETE FROM meal_entries WHERE user_id = ?", (user_id,))

    for i in range(10, -1, -1): # Od 10 dni temu do dzisiaj (łącznie 11 dni)
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        weight = 75.0 - (i * 0.1) + random.uniform(-0.05, 0.05)
        water = 3.0
        kcal = 2850
        protein = 170
        training = workouts[i % len(workouts)]
        
        cur.execute("""
            INSERT INTO progress (user_id, date, weight, water, kcal, protein, carbs, fats, training_log, rpe, sleep_quality, water_raw, herbs_raw)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date_str, weight, water, kcal, protein, 300, 70, training, 7, 4, water, 0.0))
        
        cur.execute("""
            INSERT INTO meal_entries (user_id, date, name, kcal, protein, carbs, fats)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date_str, "Śniadanie białkowe", 800, 50, 80, 20))
        cur.execute("""
            INSERT INTO meal_entries (user_id, date, name, kcal, protein, carbs, fats)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date_str, "Obiad regeneracyjny", 1200, 70, 150, 30))
        cur.execute("""
            INSERT INTO meal_entries (user_id, date, name, kcal, protein, carbs, fats)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date_str, "Kolacja potreningowa", 850, 50, 70, 20))
            
    conn.commit()
    conn.close()
    print(f"ZAKOŃCZONO: 11 dni danych dla {email} (do {today})")

if __name__ == "__main__":
    seed()
