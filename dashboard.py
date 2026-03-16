import streamlit as st
import pandas as pd
import datetime
import os
import json
import requests
from ml_engine import MLEngine

# --- CONFIG & STYLES ---
st.set_page_config(page_title="Health-ML Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- ML ENGINE ---
if "ml" not in st.session_state:
    st.session_state.ml = MLEngine()

# --- EDAMAM CONFIG (Keys stored safely in .streamlit/secrets.toml) ---
try:
    EDAMAM_APP_ID = st.secrets["EDAMAM_APP_ID"]
    EDAMAM_APP_KEY = st.secrets["EDAMAM_APP_KEY"]
except:
    EDAMAM_APP_ID = ""
    EDAMAM_APP_KEY = ""

# --- INITIAL SESSION STATE ---
if "extra_meals" not in st.session_state: st.session_state.extra_meals = []
if "api_results" not in st.session_state: st.session_state.api_results = []
if "last_query" not in st.session_state: st.session_state.last_query = ""
if "current_workout" not in st.session_state: st.session_state.current_workout = []
if "api_session" not in st.session_state:
    st.session_state.api_session = requests.Session()

# --- CONSTANTS (MY PROFILE) ---
MY_DATA = {
    "weight": 78.1,
    "target_kcal": 1900,
    "protein_goal": 180,
    "water_goal": 2.5,
    "db": "progress_me.csv"
}

MY_MEALS = [
    {"name": "High Protein Milk Product", "kcal": 130, "p": 20.0, "c": 12.0, "f": 0.6},
    {"name": "Soy Protein GymBeam (30g)", "kcal": 109, "p": 25.8, "c": 1.2, "f": 0.1},
    {"name": "Twaróg Chudy Mlekovita (230g)", "kcal": 202, "p": 41.4, "c": 8.1, "f": 0.5},
]

MY_WORKOUTS = {
    "Dzień A (Push)": ["Pompki z plecakiem 15kg", "Floor Press 24kg", "Barki OHP 24kg", "Pompki nogi wyżej", "Pompki diamentowe", "Wyprosty za głowę"],
    "Dzień B (Pull)": ["Podciąganie", "Wiosłowanie 24kg+15kg", "Wiosłowanie hantlami 7kg", "Biceps hantle", "Plank z plecakiem 15kg"],
    "Dzień C (Nogi)": ["Bułgarskie przysiady", "RDL 24kg+15kg", "Hip Thrust 24kg", "Wykroki 7kg", "Wznosy nóg"],
    "Dzień Wolny / Cardio": ["Bieganie 35-40 min", "Rozciąganie Statyczne", "Picie ziół"]
}

# --- PROFILE MANAGEMENT ---
st.sidebar.title("👤 PROFIL")
profile_type = st.sidebar.radio("Użytkownik:", ["Mój Profil (info.md)", "Nowy Użytkownik (Custom)"])
skip_defaults = st.sidebar.checkbox("Pomiń domyślne (441 kcal)", value=False)

if profile_type == "Mój Profil (info.md)":
    active_data = MY_DATA
    active_meals = [] if skip_defaults else MY_MEALS
    active_workouts = MY_WORKOUTS
else:
    if os.path.exists("user_config.json"):
        with open("user_config.json", "r") as f:
            u_cfg = json.load(f)
    else:
        u_cfg = {"weight": 80.0, "target_kcal": 2000, "protein_goal": 150, "water_goal": 2.0, "workouts": {}}
    
    st.sidebar.subheader("⚙️ Konfiguracja")
    u_w = st.sidebar.number_input("Waga (kg)", value=float(u_cfg["weight"]))
    u_kcal = st.sidebar.number_input("Kcal", value=int(u_cfg["target_kcal"]))
    u_p = st.sidebar.number_input("Białko (g)", value=int(u_cfg["protein_goal"]))
    
    active_data = {"weight": u_w, "target_kcal": u_kcal, "protein_goal": u_p, "water_goal": 2.0, "db": "progress_user.csv"}
    active_meals = []
    active_workouts = u_cfg.get("workouts", {"Dzień A": ["Przysiady"], "Dzień B": ["Pompki"], "Dzień C": ["Bieganie"]})

# --- GLOBAL STYLES ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e2130; padding: 20px; border-radius: 12px; border: 1px solid #00d4ff; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    [data-testid="stMetricLabel"] { color: #00d4ff !important; font-size: 1.1rem !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; font-weight: bold !important; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; font-weight: bold; }
    .product-preview { 
        background-color: #1e2130; 
        color: #ffffff !important; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #00d4ff; 
        margin-bottom: 15px;
    }
    .product-preview b { color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ---
def load_products():
    try:
        with open("data/products.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError: return {}

@st.cache_data(ttl=3600)
def search_edamam_products(query):
    if not query or len(query) < 3 or not EDAMAM_APP_ID:
        return []
    
    url = "https://api.edamam.com/api/food-database/v2/parser"
    params = {
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY,
        "ingr": query,
        "nutrition-type": "cooking"
    }
    
    try:
        response = st.session_state.api_session.get(url, params=params, timeout=5)
        if response.status_code == 200:
            hints = response.json().get("hints", [])
            results = []
            for h in hints:
                food = h.get("food", {})
                name = food.get("label")
                brand = food.get("brand", "Generic")
                nutriments = food.get("nutrients", {})
                
                results.append({
                    "display_name": f"🌐 {name} ({brand})",
                    "full_name": name,
                    "kcal": float(nutriments.get("ENERC_KCAL", 0)),
                    "p": float(nutriments.get("PROCNT", 0)),
                    "c": float(nutriments.get("CHOCDF", 0)),
                    "f": float(nutriments.get("FAT", 0))
                })
            return results
    except: pass
    return []

PRODUCTS_DB = load_products()

def save_progress(w, water, cals, p, c, f, workout, items, db_file, rpe=8, sleep=4, workout_details=None):
    today = str(datetime.date.today())
    # 1. Główny log progress_me.csv
    ingredients = ", ".join([i["name"] for i in items]) if items else "Logged"
    new_data = pd.DataFrame([{
        "Data": today, "Waga": w, "Woda": water, "Kcal": cals, "Bialko": p, "Wegle": c, "Tluszcze": f, 
        "Trening": workout, "Skladniki": ingredients, "RPE": rpe, "Sen_Jakosc": sleep
    }])
    if not os.path.isfile(db_file): new_data.to_csv(db_file, index=False)
    else: new_data.to_csv(db_file, mode='a', header=False, index=False)

    # 2. Szczegółowy log workout_history.csv
    if workout_details:
        history_file = "workout_history.csv"
        df_workout = pd.DataFrame(workout_details)
        df_workout['Data'] = today
        if not os.path.isfile(history_file): df_workout.to_csv(history_file, index=False)
        else: df_workout.to_csv(history_file, mode='a', header=False, index=False)
# --- UI LOGIC ---
st.sidebar.divider()
current_weight = st.sidebar.number_input("Pomiar wagi (kg)", value=float(active_data["weight"]), step=0.1)
water_drank = st.sidebar.slider("Woda (L)", 0.0, 5.0, 1.5)

base_p = sum(m["p"] for m in active_meals)
extra_p = sum(m["p"] for m in st.session_state.extra_meals)
extra_c = sum(m["c"] for m in st.session_state.extra_meals)
extra_f = sum(m["f"] for m in st.session_state.extra_meals)
total_p = base_p + extra_p
total_c = sum(m["c"] for m in active_meals) + extra_c
total_f = sum(m["f"] for m in active_meals) + extra_f
total_kcal = sum(m["kcal"] for m in active_meals) + sum(m["kcal"] for m in st.session_state.extra_meals)

st.title("🚀 Health-ML Optimizer")

# --- METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Energia (Kcal)", f"{total_kcal:.0f}", f"{active_data['target_kcal'] - total_kcal:.0f} left")
m2.metric("Białko (g)", f"{total_p:.1f}", f"Cel: {active_data['protein_goal']}")
m3.metric("Waga (kg)", f"{current_weight}", f"{round(current_weight - active_data['weight'], 1)} shift")
m4.metric("Hydracja (L)", f"{water_drank}", f"{round(active_data['water_goal'] - water_drank, 1)} to go")

with st.expander("📝 DZIENNY LOG", expanded=True):
    if st.session_state.extra_meals:
        st.table(pd.DataFrame(st.session_state.extra_meals))
        if st.button("🗑️ WYCZYŚĆ LOG"):
            st.session_state.extra_meals = []
            st.rerun()
    else: st.info("Dodaj coś poniżej.")

st.sidebar.divider()
st.sidebar.subheader("🧠 ML INPUTS")
daily_rpe = st.sidebar.select_slider("RPE (Trudność)", options=list(range(1, 11)), value=7)
daily_sleep = st.sidebar.select_slider("Sen (Jakość)", options=list(range(1, 6)), value=4)

if st.sidebar.button("💾 ZAPISZ DZIEŃ"):
    workout_log = st.session_state.get("workout_status", "Rest Day")
    details = st.session_state.current_workout if workout_log != "Rest Day" else None
    save_progress(current_weight, water_drank, total_kcal, total_p, total_c, total_f, workout_log, st.session_state.extra_meals, active_data["db"], daily_rpe, daily_sleep, details)
    st.sidebar.success("Zapisano!")
    st.session_state.extra_meals = []
    st.session_state.current_workout = []
    st.rerun()


st.divider()
st.header("🧠 AI Insights & Recommendations")
ai_col1, ai_col2, ai_col3 = st.columns(3)

with ai_col1:
    st.subheader("📉 Weight Trend (ML)")
    trend = st.session_state.ml.predict_weight_trend()
    if trend:
        st.metric("Prognoza (7 dni)", f"{trend['target_weight']} kg", f"{trend['weekly_change']} kg/week")
    else:
        st.info("Zbierz min. 3 dni pomiarów, aby zobaczyć trend.")

with ai_col2:
    st.subheader("🍗 Diet Optimizer")
    diet_sugg = st.session_state.ml.suggest_diet(
        target_kcal=active_data['target_kcal'] - total_kcal,
        target_protein=active_data['protein_goal'] - total_p
    )
    if isinstance(diet_sugg, dict) and diet_sugg['plan']:
        st.write("Aby dobić makro, zjedz dziś:")
        for item in diet_sugg['plan']:
            st.success(f"✔️ {item['product']} - {item['amount']}g")
    else:
        st.write("Makroskładniki są już blisko celu lub brak pasujących produktów.")

with ai_col3:
    st.subheader("💤 Sleep Analysis")
    sleep_impact = st.session_state.ml.analyze_sleep_impact()
    st.info(f"{sleep_impact}")
    st.caption("Korelacja Pearsona: RPE vs Sen. Im lepszy sen, tym powinno być lżej (ujemna korelacja).")

st.divider()
col_left, col_mid, col_right = st.columns([1, 1, 1])

with col_left:
    st.header("🍱 Mielarka Sugestii")
    st.caption("Błyskawiczne API Edamam (wymaga klucza).")
    search_query = st.text_input("🔍 Szukaj produktu:", placeholder="Np. Chicken, Skyr...")
    
    if search_query != st.session_state.last_query:
        st.session_state.api_results = []
        st.session_state.last_query = search_query

    if search_query:
        local_matches = []
        if PRODUCTS_DB:
            for p_name, p_info in PRODUCTS_DB.items():
                if search_query.lower() in p_name.lower():
                    local_matches.append({"display_name": f"🏠 [Lokalnie] {p_name}", "full_name": p_name, "kcal": p_info["kcal"], "p": p_info["p"], "c": p_info["c"], "f": p_info["f"]})
        
        if not EDAMAM_APP_ID:
            st.warning("⚠️ Brak klucza API Edamam w kodzie. Edytuj dashboard.py!")
        elif st.button("🌐 SZUKAJ W GLOBALNEJ BAZIE"):
            with st.spinner("Pobieram dane (Turbo)..."):
                st.session_state.api_results = search_edamam_products(search_query)

        # ALL RESULTS: API FIRST, THEN LOCAL
        all_results = st.session_state.api_results + local_matches
        
        if all_results:
            options = {res["display_name"]: res for res in all_results}
            choice = st.selectbox("Wybierz wynik (Globalne na górze):", list(options.keys()))
            if choice:
                prod = options[choice]
                
                gram_input = st.number_input("Waga Twojej porcji (g)", value=100, step=10, min_value=1, key="gram_in")
                mult = gram_input / 100.0
                p_kcal = round(prod["kcal"] * mult, 1)
                p_p = round(prod["p"] * mult, 1)
                p_c = round(prod["c"] * mult, 1)
                p_f = round(prod["f"] * mult, 1)

                st.markdown(f"""
                <div class='product-preview'>
                    <b>KALKULATOR PORCJI ({gram_input}g):</b><br>
                    🔥 Energia: <b>{p_kcal} kcal</b><br>
                    🍖 Białko: <b>{p_p}g</b> | 🍞 Węgle: <b>{p_c}g</b> | 🥑 Tłuszcze: <b>{p_f}g</b>
                    <br><small style='color: #888;'>Dane na 100g: {prod['kcal']} kcal | B: {prod['p']} | W: {prod['c']} | T: {prod['f']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("✅ DODAJ I ZAPISZ W BAZIE"):
                    # 1. Add to daily log
                    st.session_state.extra_meals.append({
                        "name": f"{prod['full_name']} ({gram_input}g)", 
                        "kcal": p_kcal, "p": p_p, "c": p_c, "f": p_f
                    })
                    
                    # 2. Auto-save to local JSON if it's from API
                    if "🌐" in prod["display_name"]:
                        new_local_db = load_products()
                        if prod["full_name"] not in new_local_db:
                            new_local_db[prod["full_name"]] = {
                                "kcal": prod["kcal"],
                                "p": prod["p"],
                                "c": prod["c"],
                                "f": prod["f"]
                            }
                            with open("data/products.json", "w", encoding="utf-8") as f:
                                json.dump(new_local_db, f, indent=4, ensure_ascii=False)
                            st.success(f"Produkt {prod['full_name']} został dopisany do bazy lokalnej!")
                    
                    st.rerun()
    else: st.info("Wpisz nazwę.")

with col_mid:
    st.header("🥗 Dodaj Ręcznie")
    m_name = st.text_input("Nazwa produktu/posiłku", key="m_name", placeholder="Np. Obiad u babci")
    m_kcal = st.number_input("Kcal (opcjonalnie)", min_value=0, step=1)
    c1, c2, c3 = st.columns(3)
    m_p = c1.number_input("Białko (g)", min_value=0.0, step=0.1)
    m_c = c2.number_input("Węgle (g)", min_value=0.0, step=0.1)
    m_f = c3.number_input("Tłuszcz (g)", min_value=0.0, step=0.1)
    
    # Auto-wyliczanie kcal jeśli nie podano
    if m_kcal == 0 and (m_p > 0 or m_c > 0 or m_f > 0):
        m_kcal = int(m_p * 4 + m_c * 4 + m_f * 9)
        st.caption(f"Wyliczone kcal: {m_kcal}")

    if st.button("➕ DODAJ POSIŁEK"):
        if m_name or m_kcal > 0:
            name = m_name if m_name else "Ręczny wpis"
            st.session_state.extra_meals.append({"name": name, "kcal": m_kcal, "p": m_p, "c": m_c, "f": m_f})
            st.rerun()

with col_right:
    st.header("🏋️ Trening")
    selected_day = st.selectbox("Dzień:", list(active_workouts.keys()))
    workout_summary = []
    
    for ex in active_workouts[selected_day]:
        checked = st.checkbox(ex, key=f"chk_{ex}")
        if checked:
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
            s = c1.number_input("sets", min_value=1, step=1, key=f"s_{ex}", value=3)
            w = c2.number_input("kg", min_value=0.0, step=0.5, key=f"w_{ex}", value=0.0)
            r = c3.number_input("reps", min_value=0, step=1, key=f"r_{ex}", value=0)
            rpe = c4.number_input("RPE", min_value=1, max_value=10, step=1, key=f"rpe_{ex}", value=8)
            workout_summary.append(f"{ex}({s}x{w}kg x {r} @RPE{rpe})")
            # Zachowujemy dane do zapisu strukturalnego
            if "current_workout" not in st.session_state: st.session_state.current_workout = []
            st.session_state.current_workout.append({"ex": ex, "sets": s, "w": w, "r": r, "rpe": rpe})

    st.session_state.workout_status = ", ".join(workout_summary) if workout_summary else "Rest Day"

st.divider()
if os.path.isfile(active_data["db"]):
    st.header("📈 Historia")
    history_df = pd.read_csv(active_data["db"])
    st.line_chart(history_df.set_index("Data")["Waga"])
