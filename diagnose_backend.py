import sys
import os

# Dodaj ścieżki do core i backend
sys.path.append(os.path.join(os.getcwd(), "core"))
sys.path.append(os.path.join(os.getcwd(), "backend"))

from db_manager import DBManager
from ml_engine import MLEngine
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def test_registration():
    try:
        print("Inicjalizacja DB i ML...")
        db = DBManager(db_path="health_vault.db")
        ml = MLEngine(csv_path="progress_me.csv", products_path="data/products.json")
        
        email = "test@example.com"
        password = "test"
        hashed_pw = pwd_context.hash(password)
        
        print(f"Obliczanie celów ML dla wagi 60kg...")
        smart = ml.calculate_smart_goal(60, 125, 25, "mężczyzna", 1.5, "masa")
        print(f"Obliczone cele: {smart}")
        
        print("Próba zapisu do bazy...")
        user_id = db.add_user(
            "Test User", 25, 125, "mężczyzna", 1.5, "masa",
            smart["target_kcal"], smart["target_p"], smart["water"],
            email=email, password=hashed_pw
        )
        
        if user_id:
            print(f"SUKCES! Utworzono użytkownika o ID: {user_id}")
        else:
            print("BŁĄD: add_user zwrócił None (prawdopodobnie email już istnieje)")
            
    except Exception as e:
        print(f"FATALNY BŁĄD: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_registration()
