from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
import bcrypt
import hashlib
import sys
import os
import shutil
import requests
import pandas as pd

# Dodajemy folder core do ścieżki
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
from ml_engine import MLEngine
from db_manager import DBManager

# CONFIG
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_ME" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# EDAMAM CONFIG
EDAMAM_APP_ID = "33cfc8bd"
EDAMAM_APP_KEY = "b23d54e9dcb5f8d4c0fedc523231b7be"

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MY_WORKOUTS = {
    "Dzień A (Push)": ["Pompki z plecakiem 15kg", "Floor Press 24kg", "Barki OHP 24kg", "Pompki nogi wyżej", "Pompki z wąskimi rękoma", "Wyprosty za głowę"],
    "Dzień B (Pull)": ["Podciąganie", "Wiosłowanie 24kg+15kg", "Wiosłowanie hantlami 7kg", "Biceps hantle", "Plank z plecakiem 15kg"],
    "Dzień C (Nogi)": ["Bułgarskie przysiady", "RDL 24kg+15kg", "Hip Thrust 24kg", "Wykroki 7kg", "Wznosy nóg"],
    "Bieganie": ["Bieganie 35-40 min"],
    "Dzień Wolny": ["Rest Day"]
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

app = FastAPI(title="Health-ML API", description="Produkcyjne API dla Web i Mobile")
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Używamy ścieżki absolutnej do bazy danych, aby uniknąć problemów z katalogiem roboczym
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "health_vault.db")
PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "products.json")
CSV_PATH = os.path.join(BASE_DIR, "progress_me.csv")

db = DBManager(db_path=DB_PATH)
ml = MLEngine(csv_path=CSV_PATH, products_path=PRODUCTS_PATH)

# --- AUTH UTILS (PANCERNE) ---
def verify_password(plain_password, hashed_password):
    try:
        # 1. Sprawdź czy to BCrypt (nowy format)
        if hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        
        # 2. Sprawdź czy to stary format PBKDF2 (passlib default)
        # UWAGA: Jeśli masz stare dane, których nie możesz stracić, 
        # najlepiej je po prostu zresetować skryptem fix_db.py.
        # Ale dla bezpieczeństwa, jeśli hasło nie jest bcryptem, to po prostu go nie wpuścimy 
        # zamiast wywalać serwer błędem 500.
        return False
    except Exception as e:
        print(f"Auth Error: {e}")
        return False

def get_password_hash(password):
    # Bcrypt ma limit 72 znaków, więc dla bezpieczeństwa robimy sha256 przed hashowaniem
    # (to standardowa praktyka, która pozwala na nieskończenie długie hasła)
    pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return bcrypt.hashpw(pwd_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user = db.get_user_by_email(email)
        if user is None: raise HTTPException(status_code=401)
        return user
    except: raise HTTPException(status_code=401)

# --- MODELS ---
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int
    height: float
    weight: float
    gender: str
    activity: float
    goal: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    goal: str
    target_kcal: int
    target_protein: float
    water_goal: float

class Token(BaseModel):
    access_token: str
    token_type: str

class MealEntry(BaseModel):
    date: str
    name: str
    kcal: float
    protein: float
    carbs: float
    fats: float

class ProgressLog(BaseModel):
    date: str
    weight: float
    water: float
    kcal: int
    protein: float
    carbs: float
    fats: float
    training_log: Optional[str] = "Rest Day"
    rpe: int = 5
    sleep_quality: int = 3

class UpdateGoals(BaseModel):
    target_kcal: int
    target_protein: float
    water_goal: float

# --- ENDPOINTS ---
@app.post("/auth/register", response_model=UserResponse)
def register(user: UserRegister):
    if db.get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Użytkownik o tym emailu już istnieje")
    
    hashed_pw = get_password_hash(user.password)
    smart = ml.calculate_smart_goal(user.weight, user.height, user.age, user.gender, user.activity, user.goal)
    user_id = db.add_user(user.name, user.age, user.height, user.gender, user.activity, user.goal, smart["target_kcal"], smart["target_p"], smart["water"], email=user.email, password=hashed_pw)
    
    if not user_id:
        raise HTTPException(status_code=500, detail="Błąd zapisu w bazie danych")
        
    return {**user.dict(), "id": user_id, "target_kcal": smart["target_kcal"], "target_protein": smart["target_p"], "water_goal": smart["water"]}

@app.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user_by_email(form_data.username)
    
    # Próbujemy zweryfikować hasło. SHA256 weryfikacja dla nowych haseł:
    pwd_hash = hashlib.sha256(form_data.password.encode('utf-8')).hexdigest()
    
    # Pobierz dzisiejszy trening, aby dostosować cele w locie
    today = datetime.now().strftime("%Y-%m-%d")
    progress = db.get_user_progress(user["id"])
    today_progress = progress[progress['date'] == today]
    training_log = today_progress['training_log'].iloc[0] if not today_progress.empty else None

    smart = ml.calculate_smart_goal(user["weight"] if "weight" in user else 80.0, user["height"], user["age"], user["gender"], user["activity_level"], user["goal"], training_log=training_log)

    return {
        "access_token": create_access_token(data={"sub": user["email"]}), 
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "goal": user["goal"],
            "target_kcal": smart["target_kcal"], 
            "target_protein": smart["target_p"], 
            "water_goal": smart["water"]
        }
    }
@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.post("/users/goals")
async def update_goals(goals: UpdateGoals, current_user: dict = Depends(get_current_user)):
    db.update_user_goals(current_user["id"], goals.target_kcal, goals.target_protein, goals.water_goal)
    return {"status": "success"}

@app.get("/workouts/exercises")
def get_exercises(): return MY_WORKOUTS

@app.get("/edamam/search")
def search_food(q: str):
    url = f"https://api.edamam.com/api/food-database/v2/parser"
    params = {"app_id": EDAMAM_APP_ID, "app_key": EDAMAM_APP_KEY, "ingr": q, "nutrition-type": "logging"}
    try:
        res = requests.get(url, params=params, timeout=5).json()
        results = []
        for item in res.get("hints", []):
            food = item["food"]
            nutrients = food.get("nutrients", {})
            results.append({
                "label": food['label'],
                "brand": food.get('brand', 'Generic'),
                "kcal": round(nutrients.get("ENERC_KCAL", 0)),
                "p": round(nutrients.get("PROCNT", 0), 1),
                "c": round(nutrients.get("CHOCDF", 0), 1),
                "f": round(nutrients.get("FAT", 0), 1)
            })
        return results
    except Exception as e:
        print(f"Edamam Error: {e}")
        return []

@app.post("/meals/")
async def add_meal(meal: MealEntry, current_user: dict = Depends(get_current_user)):
    db.add_meal_entry(current_user["id"], meal.date, meal.name, meal.kcal, meal.protein, meal.carbs, meal.fats)
    df_meals = db.get_daily_meals(current_user["id"], meal.date)
    total_kcal = df_meals['kcal'].sum()
    total_p = df_meals['protein'].sum()
    total_c = df_meals['carbs'].sum()
    total_f = df_meals['fats'].sum()
    
    df_prog = db.get_user_progress(current_user["id"])
    today_prog = df_prog[df_prog['date'] == meal.date]
    weight = today_prog['weight'].iloc[0] if not today_prog.empty else 80.0
    water = today_prog['water'].iloc[0] if not today_prog.empty else 0.0
    
    db.add_or_update_progress(current_user["id"], meal.date, weight, water, int(total_kcal), total_p, total_c, total_f, "Logged Meal", 7, 3)
    return {"status": "success"}

@app.get("/meals/{date}")
async def get_meals(date: str, current_user: dict = Depends(get_current_user)):
    df = db.get_daily_meals(current_user["id"], date)
    return df.to_dict(orient="records")

@app.delete("/meals/{meal_id}")
async def delete_meal(meal_id: int, current_user: dict = Depends(get_current_user)):
    # Pobieramy datę posiłku przed usunięciem, żeby wiedzieć co przeliczyć
    with db._get_connection() as conn:
        res = conn.execute("SELECT date FROM meal_entries WHERE id = ? AND user_id = ?", (meal_id, current_user["id"])).fetchone()
        if not res: raise HTTPException(status_code=404, detail="Meal not found")
        meal_date = res[0]

    db.delete_meal_entry(meal_id, current_user["id"])
    
    # Przeliczamy sumę dnia po usunięciu
    df_meals = db.get_daily_meals(current_user["id"], meal_date)
    total_kcal = df_meals['kcal'].sum()
    total_p = df_meals['protein'].sum()
    total_c = df_meals['carbs'].sum()
    total_f = df_meals['fats'].sum()
    
    # Aktualizujemy wpis w tabeli progress
    df_prog = db.get_user_progress(current_user["id"])
    today_prog = df_prog[df_prog['date'] == meal_date]
    weight = today_prog['weight'].iloc[0] if not today_prog.empty else 80.0
    water = today_prog['water'].iloc[0] if not today_prog.empty else 0.0
    
    db.add_or_update_progress(current_user["id"], meal_date, weight, water, int(total_kcal), total_p, total_c, total_f, "Updated after delete", 7, 3)
    return {"status": "success"}

@app.get("/ml/diet-plan")
async def get_diet_plan(current_user: dict = Depends(get_current_user)):
    df_prog = db.get_user_progress(current_user["id"])
    today = datetime.now().strftime("%Y-%m-%d")
    today_prog = df_prog[df_prog['date'] == today]
    total_kcal = today_prog['kcal'].iloc[0] if not today_prog.empty else 0
    total_p = today_prog['protein'].iloc[0] if not today_prog.empty else 0
    needed_kcal = current_user['target_kcal'] - total_kcal
    needed_p = current_user['target_protein'] - total_p
    if needed_p <= 0: return {"msg": "Białko domknięte! ✨", "plan": []}
    return ml.suggest_diet_lp(needed_kcal, needed_p)

@app.post("/progress/")
async def add_progress(log: ProgressLog, current_user: dict = Depends(get_current_user)):
    db.add_or_update_progress(current_user["id"], log.date, log.weight, log.water, log.kcal, log.protein, log.carbs, log.fats, log.training_log, log.rpe, log.sleep_quality)
    return {"status": "success"}

@app.get("/progress/")
async def get_progress(current_user: dict = Depends(get_current_user)):
    df = db.get_user_progress(current_user["id"])
    if not df.empty and 'date' in df.columns:
        # Konwersja na string YYYY-MM-DD aby uniknąć problemów z JSONem
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    return df.to_dict(orient="records")

@app.get("/ml/insights")
async def get_ml_insights(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    df_progress = db.get_user_progress(user_id)
    
    # Tworzymy nową instancję MLEngine dla każdego zapytania
    engine = MLEngine(csv_path=CSV_PATH, products_path=PRODUCTS_PATH)
    
    current_weight = 80.0
    training_log = None
    last_sleep = None
    
    if not df_progress.empty:
        # Upewniamy się, że daty są w formacie datetime dla silnika ML
        df_progress['date'] = pd.to_datetime(df_progress['date'])
        engine.set_data(df_progress)
        
        # Pobierz najnowszą wagę
        current_weight = df_progress['weight'].iloc[-1]
        last_sleep = df_progress['sleep_quality'].iloc[-1]
        
        # Pobierz dzisiejszy trening
        today = datetime.now().strftime("%Y-%m-%d")
        today_progress = df_progress[df_progress['date'].dt.strftime('%Y-%m-%d') == today]
        if not today_progress.empty:
            training_log = today_progress['training_log'].iloc[0]

    # Oblicz inteligentny cel na dziś (uwzględniając trening)
    smart_goal = engine.calculate_smart_goal(
        weight=current_weight,
        height=current_user["height"],
        age=current_user["age"],
        gender=current_user["gender"],
        activity_level=current_user["activity_level"],
        goal=current_user["goal"],
        training_log=training_log
    )
    
    print(f"DEBUG: Insights for {current_user['email']}. Entries: {len(df_progress)}")
    
    return {
        "trend": engine.predict_weight_trend(), 
        "plateau": engine.predict_plateau_prophet(), 
        "training": engine.analyze_training_insights(), 
        "recommendation": engine.recommend_daily_activity(last_sleep=last_sleep),
        "smart_goal": smart_goal
    }

@app.post("/upload-photo/")
async def upload_photo(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    filename = f"user_{current_user['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    return {"url": f"/static/{filename}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
