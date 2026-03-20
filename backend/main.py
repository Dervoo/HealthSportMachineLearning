from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
import sys
import os
import shutil

# Dodajemy folder core do ścieżki
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
from ml_engine import MLEngine
from db_manager import DBManager

# CONFIG
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_ME" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Folder na zdjęcia (Mobile-ready)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

app = FastAPI(title="Health-ML API", description="Produkcyjne API dla Web i Mobile")

# Serwowanie zdjęć
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

# Konfiguracja CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DBManager(db_path="../health_vault.db")
ml = MLEngine(csv_path="../progress_me.csv", products_path="../data/products.json")

# --- MODELS ---
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int
    height: float
    gender: str
    activity: float
    goal: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    goal: str

class Token(BaseModel):
    access_token: str
    token_type: str

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

class UserGoalRequest(BaseModel):
    weight: float
    height: float
    age: int
    gender: str
    activity: float
    goal: str

# --- AUTH UTILS ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user

# --- ENDPOINTS ---
@app.get("/")
def read_root():
    return {"status": "online", "message": "Health-ML API v2 is running"}

@app.post("/auth/register", response_model=UserResponse)
def register(user: UserRegister):
    if db.get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(user.password)
    # Obliczamy początkowe cele przez ML
    smart = ml.calculate_smart_goal(user.weight, user.height, user.age, user.gender, user.activity, user.goal)
    
    user_id = db.add_user(
        user.name, user.age, user.height, user.gender, user.activity, user.goal,
        smart["target_kcal"], smart["target_p"], smart["water"],
        email=user.email, password=hashed_pw
    )
    return {**user.dict(), "id": user_id}

@app.post("/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.post("/progress/")
async def add_progress(log: ProgressLog, current_user: dict = Depends(get_current_user)):
    db.add_or_update_progress(
        current_user["id"], log.date, log.weight, log.water, log.kcal, 
        log.protein, log.carbs, log.fats, log.training_log, log.rpe, log.sleep_quality
    )
    return {"status": "success"}

@app.get("/progress/")
async def get_progress(current_user: dict = Depends(get_current_user)):
    df = db.get_user_progress(current_user["id"])
    return df.to_dict(orient="records")

@app.get("/ml/insights")
async def get_ml_insights(current_user: dict = Depends(get_current_user)):
    df_progress = db.get_user_progress(current_user["id"])
    ml.set_data(df_progress)
    
    return {
        "trend": ml.predict_weight_trend(),
        "plateau": ml.predict_plateau_prophet(),
        "training": ml.analyze_training_insights(),
        "recommendation": ml.recommend_daily_activity(
            last_sleep=df_progress['sleep_quality'].iloc[-1] if not df_progress.empty else None
        )
    }

@app.post("/upload-photo/")
async def upload_photo(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    # Generowanie unikalnej nazwy pliku
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_{current_user['id']}_{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"info": "Photo uploaded", "url": f"/static/{filename}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
