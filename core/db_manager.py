import sqlite3
import pandas as pd
import os
from datetime import datetime

class DBManager:
    def __init__(self, db_path="health_vault.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Tabela użytkowników
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT UNIQUE,
                    password TEXT,
                    age INTEGER,
                    height REAL,
                    gender TEXT,
                    activity_level REAL,
                    goal TEXT,
                    target_kcal INTEGER,
                    target_protein REAL,
                    water_goal REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Migracja dla istniejących baz danych (dodanie email i password jeśli nie istnieją)
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
                cursor.execute("ALTER TABLE users ADD COLUMN password TEXT")
            except:
                pass
            # Tabela postępów
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    weight REAL,
                    water REAL,
                    kcal INTEGER,
                    protein REAL,
                    carbs REAL,
                    fats REAL,
                    training_log TEXT,
                    rpe INTEGER,
                    sleep_quality INTEGER,
                    water_raw REAL,
                    herbs_raw REAL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            # Migracja dla istniejących baz danych
            try:
                cursor.execute("ALTER TABLE progress ADD COLUMN water_raw REAL")
                cursor.execute("ALTER TABLE progress ADD COLUMN herbs_raw REAL")
            except:
                pass
            conn.commit()

    def add_user(self, name, age, height, gender, activity, goal, kcal, protein, water, email=None, password=None):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (name, age, height, gender, activity_level, goal, target_kcal, target_protein, water_goal, email, password)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, age, height, gender, activity, goal, kcal, protein, water, email, password))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_user_by_email(self, email):
        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM users WHERE email = ?", conn, params=(email,))
            return df.iloc[0].to_dict() if not df.empty else None

    def get_user_by_name(self, name):
        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM users WHERE name = ?", conn, params=(name,))
            return df.iloc[0].to_dict() if not df.empty else None

    def get_all_users(self):
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM users", conn)

    def add_or_update_progress(self, user_id, date, weight, water, kcal, protein, carbs, fats, training, rpe, sleep, water_raw=0.0, herbs_raw=0.0):
        """Dodaje nowy wpis lub aktualizuje istniejący dla danej daty (UPSERT)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Sprawdź czy wpis już istnieje
            cursor.execute("SELECT id FROM progress WHERE user_id = ? AND date = ?", (user_id, date))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("""
                    UPDATE progress SET 
                        weight = ?, water = ?, kcal = ?, protein = ?, carbs = ?, fats = ?, 
                        training_log = ?, rpe = ?, sleep_quality = ?, water_raw = ?, herbs_raw = ?
                    WHERE id = ?
                """, (weight, water, kcal, protein, carbs, fats, training, rpe, sleep, water_raw, herbs_raw, exists[0]))
            else:
                cursor.execute("""
                    INSERT INTO progress (user_id, date, weight, water, kcal, protein, carbs, fats, training_log, rpe, sleep_quality, water_raw, herbs_raw)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, date, weight, water, kcal, protein, carbs, fats, training, rpe, sleep, water_raw, herbs_raw))
            conn.commit()

    def get_user_progress(self, user_id):
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM progress WHERE user_id = ? ORDER BY date ASC", conn, params=(user_id,))

    def get_global_data(self):
        """Pobiera dane wszystkich użytkowników do 'mielenia'."""
        with self._get_connection() as conn:
            return pd.read_sql_query("""
                SELECT p.*, u.age, u.gender, u.activity_level, u.goal 
                FROM progress p 
                JOIN users u ON p.user_id = u.id
            """, conn)

if __name__ == "__main__":
    db = DBManager()
    print("Database initialized.")
