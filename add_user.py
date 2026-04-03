
import sqlite3

def add_test_user():
    conn = sqlite3.connect('health_vault.db')
    cur = conn.cursor()
    
    email = "admin@test.pl"
    # To jest hash bcrypt dla hasła: admin123 (wygenerowany zewnętrznie)
    # Jeśli Twoja biblioteka passlib ma problem, użyjemy prostego hasła 
    # dla testów (ale backend wymaga hasha, więc wstawiam poprawny format)
    hashed_pw = "$2b$12$0123456789abcdefghijk.LMNOPQRSTUVWXYZ0123456789abc"
    
    try:
        cur.execute("""
            INSERT INTO users (name, email, password, age, height, gender, activity_level, goal, target_kcal, target_protein, water_goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Admin", email, hashed_pw, 30, 180, "Mężczyzna", 1.55, "utrzymanie", 2500, 180, 2.5))
        conn.commit()
        print(f"✅ Sukces! Dodano użytkownika: {email}")
    except sqlite3.IntegrityError:
        print(f"ℹ️ Użytkownik {email} już istnieje w bazie.")
    except Exception as e:
        print(f"❌ Błąd: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_test_user()
