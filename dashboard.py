import streamlit as st
import pandas as pd
import re
import datetime
import os
import json

# --- CONFIG & STYLES ---
st.set_page_config(page_title="Health-ML Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- INITIAL SESSION STATE ---
if "extra_meals" not in st.session_state: st.session_state.extra_meals = []
if "temp_suggestion" not in st.session_state: st.session_state.temp_suggestion = None
if "exercise_opinion" not in st.session_state: st.session_state.exercise_opinion = None

# --- CONSTANTS (MY PROFILE) ---
MY_DATA = {
    "weight": 78.1,
    "target_kcal": 1900,
    "protein_goal": 180,
    "water_goal": 2.5,
    "db": "progress_me.csv"
}

MY_MEALS = [
    {"name": "Soy Protein GymBeam", "kcal": 109, "p": 26, "c": 1, "f": 0},
    {"name": "Twarog Chudy Mlekovita", "kcal": 202, "p": 41.5, "c": 8, "f": 0.5},
    {"name": "High Protein Milk Product", "kcal": 130, "p": 20, "c": 12, "f": 0.5},
]

MY_WORKOUTS = {
    "Dzień A (Push)": ["Pompki z plecakiem 15kg", "Floor Press 24kg", "Barki OHP 24kg", "Pompki nogi wyżej", "Pompki diamentowe", "Wyprosty za głowę"],
    "Dzień B (Pull)": ["Podciąganie", "Wiosłowanie 24kg+15kg", "Wiosłowanie hantlami 7kg", "Biceps hantle", "Plank z plecakiem 15kg"],
    "Dzień C (Nogi)": ["Bułgarskie przysiady", "RDL 24kg+15kg", "Hip Thrust 24kg", "Wykroki 7kg", "Wznosy nóg"],
    "Dzień Wolny / Cardio": ["Bieganie 35-40 min", "Rozciąganie Statyczne", "Picie ziół"]
}

# --- PROFILE MANAGEMENT ---
st.sidebar.title("👤 PROFIL")
profile_type = st.sidebar.radio("Wybierz użytkownika:", ["Mój Profil (info.md)", "Nowy Użytkownik (Custom)"])

if profile_type == "Mój Profil (info.md)":
    active_data = MY_DATA
    active_meals = MY_MEALS
    active_workouts = MY_WORKOUTS
else:
    if os.path.exists("user_config.json"):
        with open("user_config.json", "r") as f:
            u_cfg = json.load(f)
    else:
        u_cfg = {"weight": 80.0, "target_kcal": 2000, "protein_goal": 150, "water_goal": 2.0, "workouts": {}}

    st.sidebar.subheader("⚙️ Konfiguracja")
    u_w = st.sidebar.number_input("Twoja waga (kg)", value=float(u_cfg["weight"]))
    u_kcal = st.sidebar.number_input("Cel Kcal", value=int(u_cfg["target_kcal"]))
    u_p = st.sidebar.number_input("Cel Białka (g)", value=int(u_cfg["protein_goal"]))
    u_water = st.sidebar.number_input("Cel Wody (L)", value=float(u_cfg["water_goal"]))
    
    with st.sidebar.expander("📝 Edytuj Plany Treningowe"):
        u_wa = st.text_area("Dzień A (oddziel przecinkiem)", ",".join(u_cfg["workouts"].get("Dzień A", ["Przysiady", "Pompki"])))
        u_wb = st.text_area("Dzień B (oddziel przecinkiem)", ",".join(u_cfg["workouts"].get("Dzień B", ["Podciąganie", "Wiosłowanie"])))
        u_wc = st.text_area("Dzień C (oddziel przecinkiem)", ",".join(u_cfg["workouts"].get("Dzień C", ["Bieganie", "Rozciąganie"])))

    if st.sidebar.button("💾 ZAPISZ KONFIGURACJĘ"):
        new_cfg = {
            "weight": u_w, "target_kcal": u_kcal, "protein_goal": u_p, "water_goal": u_water,
            "workouts": {"Dzień A": [x.strip() for x in u_wa.split(",")], "Dzień B": [x.strip() for x in u_wb.split(",")], "Dzień C": [x.strip() for x in u_wc.split(",")]}
        }
        with open("user_config.json", "w") as f:
            json.dump(new_cfg, f)
        st.sidebar.success("Konfiguracja zapisana!")
        st.rerun()

    active_data = {"weight": u_w, "target_kcal": u_kcal, "protein_goal": u_p, "water_goal": u_water, "db": "progress_user.csv"}
    active_meals = []
    active_workouts = u_cfg.get("workouts", {"Dzień A": ["Brak"], "Dzień B": ["Brak"], "Dzień C": ["Brak"]})
    if "Dzień Wolny / Cardio" not in active_workouts:
        active_workouts["Dzień Wolny / Cardio"] = ["Odpoczynek"]

# --- GLOBAL STYLES ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e2130; padding: 20px; border-radius: 12px; border: 1px solid #00d4ff; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    [data-testid="stMetricLabel"] { color: #00d4ff !important; font-size: 1.1rem !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; font-weight: bold !important; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ---
def save_progress(w, water, cals, p, c, f, workout, ingredients, db_file):
    new_data = pd.DataFrame([{"Data": str(datetime.date.today()), "Waga": w, "Woda": water, "Kcal": cals, "Bialko": p, "Wegle": c, "Tluszcze": f, "Trening": workout, "Skladniki": ingredients}])
    if not os.path.isfile(db_file): new_data.to_csv(db_file, index=False)
    else: new_data.to_csv(db_file, mode='a', header=False, index=False)

def evaluate_exercise(ex_name, weight, target_kcal, current_p, p_goal):
    ex = ex_name.lower()
    score = 0
    opinion = ""
    
    # Cardio vs Strength
    is_cardio = any(x in ex for x in ["bieg", "rower", "pływ", "cardio", "spacer"])
    is_strength = any(x in ex for x in ["przysiad", "martwy", "wyciskanie", "pompk", "hantl", "sztang"])
    
    if is_cardio:
        if weight > 100:
            opinion = "[TEZA] ODRADZANE. Przy wadze >100kg stawy (kolana, kręgosłup) są nadmiernie obciążone podczas biegania. [SZCZEGÓŁY] Wybierz rower stacjonarny lub basen. [PRO TIP] Spaceruj pod nachyleniem zamiast biegać."
        else:
            opinion = "[TEZA] ZALECANE. Dobry wybór na podbicie deficytu. [SZCZEGÓŁY] Utrzymuj tętno tlenowe. [PRO TIP] Rób to rano na czczo dla lepszej mobilizacji kwasów tłuszczowych."
    
    elif is_strength:
        if target_kcal < 1500:
            opinion = "[TEZA] RYZYKOWNE. Zbyt niski bilans kaloryczny na ciężki trening siłowy. [SZCZEGÓŁY] Grozi katabolizmem mięśniowym. [PRO TIP] Zmniejsz objętość, zachowaj intensywność."
        elif current_p < (p_goal * 0.7):
             opinion = "[TEZA] MAŁO EFEKTYWNE. Masz za mało białka w systemie. [SZCZEGÓŁY] Mięśnie nie mają z czego się budować. [PRO TIP] Zjedz porcję skyru/odżywki zaraz po treningu."
        else:
            opinion = "[TEZA] IDEALNE. Masz energię i budulec. [SZCZEGÓŁY] Skup się na progresji ciężaru. [PRO TIP] Stosuj rest-pause w ostatnich seriach."
    else:
        opinion = "[ANALIZA] Ćwiczenie ogólne. ML nie widzi przeciwskazań ani specyficznych korzyści. Monitoruj tętno."
        
    return opinion

def parse_suggestion(input_text):
    text = input_text.lower()
    products_db = {
        "kurczak": {"name": "Pierś z kurczaka", "p": 22.0, "c": 0.0, "f": 1.5},
        "skyr": {"name": "Skyr naturalny", "p": 12.0, "c": 4.0, "f": 0.0},
        "tunczyk": {"name": "Tuńczyk w wodzie", "p": 24.0, "c": 0.0, "f": 1.0},
        "ryz": {"name": "Ryż biały", "p": 7.0, "c": 77.0, "f": 1.0}
    }
    weight_match = re.search(r"(\d+)\s*g", text)
    weight = float(weight_match.group(1)) if weight_match else 100.0
    detected_meal = None
    for key, val in products_db.items():
        if key in text: detected_meal = val.copy()
    if detected_meal:
        multiplier = weight / 100.0
        detected_meal["name"] = f"{detected_meal['name']} ({int(weight)}g)"
        detected_meal["p"] = round(detected_meal["p"] * multiplier, 1)
        detected_meal["c"] = round(detected_meal["c"] * multiplier, 1)
        detected_meal["f"] = round(detected_meal["f"] * multiplier, 1)
        detected_meal["kcal"] = round((detected_meal["p"] * 4) + (detected_meal["c"] * 4) + (detected_meal["f"] * 9), 1)
        return detected_meal
    return None

# --- UI LOGIC ---
st.sidebar.divider()
current_weight = st.sidebar.number_input("Pomiar wagi (kg)", value=float(active_data["weight"]), step=0.1)
water_drank = st.sidebar.slider("Woda (L)", 0.0, 5.0, 1.5)

# --- AGGREGATION ---
base_p = sum(m["p"] for m in active_meals)
extra_p = sum(m["p"] for m in st.session_state.extra_meals)
total_p = base_p + extra_p
total_kcal = sum(m["kcal"] for m in active_meals) + sum(m["kcal"] for m in st.session_state.extra_meals)

st.title("🚀 Health-ML Optimizer")

# --- METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Energia (Kcal)", f"{total_kcal}", f"{active_data['target_kcal'] - total_kcal} left")
m2.metric("Białko (g)", f"{total_p}", f"Cel: {active_data['protein_goal']}")
m3.metric("Waga (kg)", f"{current_weight}", f"{round(current_weight - active_data['weight'], 1)} shift")
m4.metric("Hydracja (L)", f"{water_drank}", f"{round(active_data['water_goal'] - water_drank, 1)} to go")

if st.sidebar.button("💾 ZAPISZ DZIEŃ"):
    save_progress(current_weight, water_drank, total_kcal, total_p, 0, 0, "Logged", "Items", active_data["db"])
    st.sidebar.success("Zapisano!")
    st.session_state.extra_meals = []

st.divider()
col_left, col_right = st.columns([1, 1])

with col_left:
    st.header("🍱 Mielarka Sugestii")
    query = st.text_input("Zapytaj o produkt (np. 300g kurczak)")
    if st.button("ANALIZUJ PRODUKT"):
        meal = parse_suggestion(query)
        if meal:
            st.session_state.temp_suggestion = meal
            st.info(f"🔍 {meal['name']} | {meal['kcal']} kcal")
        else: st.warning("Nie rozpoznano.")

    if st.session_state.temp_suggestion:
        if st.button("✅ DODAJ POSIŁEK"):
            st.session_state.extra_meals.append(st.session_state.temp_suggestion)
            st.session_state.temp_suggestion = None
            st.rerun()

with col_right:
    st.header("🏋️ Plan Treningowy")
    selected_day = st.selectbox("Wybierz trening:", list(active_workouts.keys()))
    if selected_day == "Dzień C (Nogi)" and profile_type == "Mój Profil (info.md)": st.error("🚫 ZAKAZ BIEGANIA")
    for ex in active_workouts[selected_day]: st.checkbox(ex)
    
    # --- EXERCISE EVALUATOR (ONLY FOR CUSTOM) ---
    if profile_type == "Nowy Użytkownik (Custom)":
        st.divider()
        st.subheader("🤖 Mielarka Oceny Ćwiczeń")
        ex_query = st.text_input("Wprowadź ćwiczenie do oceny...", placeholder="Np. Bieganie 5km")
        if st.button("OCEŃ ĆWICZENIE"):
            opinion = evaluate_exercise(ex_query, current_weight, active_data["target_kcal"], total_p, active_data["protein_goal"])
            st.session_state.exercise_opinion = opinion
            
        if st.session_state.exercise_opinion:
            st.success(st.session_state.exercise_opinion)
            if st.button("WYCZYŚĆ OCENĘ"):
                st.session_state.exercise_opinion = None
                st.rerun()

st.divider()
if os.path.isfile(active_data["db"]):
    history_df = pd.read_csv(active_data["db"])
    st.line_chart(history_df.set_index("Data")["Waga"])
