
import sqlite3

def fix_db():
    conn = sqlite3.connect('health_vault.db')
    cur = conn.cursor()
    
    # Pelny hash dla admin123
    full_hash = "$2b$12$28ur0MSnKffuIh9JM1UBG.cFXMjIxQCHzkhjkmStM5XyJPb6/P4fm"
    
    cur.execute("UPDATE users SET password = ? WHERE email = ?", (full_hash, "admin@test.pl"))
    conn.commit()
    
    cur.execute("SELECT email, password FROM users WHERE email = 'admin@test.pl'")
    row = cur.fetchone()
    print(f"VERIFIED DB: {row[0]} -> {row[1]}")
    conn.close()

if __name__ == "__main__":
    fix_db()
