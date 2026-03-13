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
profile_type = st.sidebar.radio("Wybierz użytkownika:", ["Mój Profil (info.md)", "Nowy Użytkownik (Custom)"])

# Option to toggle default meals
skip_defaults = st.sidebar.checkbox("Pomiń posiłki domyślne (441 kcal)", value=False)

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
def load_products():
    try:
        with open("data/products.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

PRODUCTS_DB = load_products()

def save_progress(w, water, cals, p, c, f, workout, items, db_file):
    ingredients = ", ".join([i["name"] for i in items]) if items else "Logged"
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

# --- UI LOGIC ---
st.sidebar.divider()
current_weight = st.sidebar.number_input("Pomiar wagi (kg)", value=float(active_data["weight"]), step=0.1)
water_drank = st.sidebar.slider("Woda (L)", 0.0, 5.0, 1.5)

# --- AGGREGATION ---
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

# --- DAILY LOG (STAGED) ---
with st.expander("📝 DZIENNY LOG (Wprowadzone produkty)", expanded=True):
    if st.session_state.extra_meals:
        df_meals = pd.DataFrame(st.session_state.extra_meals)
        st.table(df_meals)
        if st.button("🗑️ WYCZYŚĆ DZISIEJSZY LOG"):
            st.session_state.extra_meals = []
            st.rerun()
    else:
        st.info("Brak wpisanych produktów. Dodaj coś za pomocą mielarki lub ręcznie.")

# --- WORKOUT STATE ---
if "workout_status" not in st.session_state: st.session_state.workout_status = []

if st.sidebar.button("💾 ZAPISZ DZIEŃ"):
    workout_log = st.session_state.workout_status if st.session_state.workout_status else "Rest Day"
    save_progress(current_weight, water_drank, total_kcal, total_p, total_c, total_f, workout_log, st.session_state.extra_meals, active_data["db"])
    st.sidebar.success("Zapisano!")
    st.session_state.extra_meals = []

st.divider()
col_left, col_mid, col_right = st.columns([1, 1, 1])

with col_left:
    st.header("🍱 Mielarka Sugestii")
    st.caption("Baza Wiedzy (Machine Learning Dataset)")
    
    if PRODUCTS_DB:
        selected_product = st.selectbox("Wybierz produkt:", list(PRODUCTS_DB.keys()))
        input_grams = st.number_input("Ile gram?", value=100, step=10, min_value=1)
        
        # Calculate
        p_info = PRODUCTS_DB[selected_product]
        multiplier = input_grams / 100.0
        
        calc_kcal = round(p_info["kcal"] * multiplier, 1)
        calc_p = round(p_info["p"] * multiplier, 1)
        calc_c = round(p_info["c"] * multiplier, 1)
        calc_f = round(p_info["f"] * multiplier, 1)
        
        st.info(f"📊 {selected_product} ({input_grams}g)\n\n**{calc_kcal} kcal** | B: {calc_p} | W: {calc_c} | T: {calc_f}")
        
        if st.button("✅ DODAJ (AUTO-CALC)"):
            st.session_state.extra_meals.append({
                "name": f"{selected_product} ({input_grams}g)",
                "kcal": calc_kcal, "p": calc_p, "c": calc_c, "f": calc_f
            })
            st.rerun()
    else:
        st.error("Brak pliku data/products.json! Stwórz go, aby korzystać z bazy.")
with col_mid:
    st.header("🥗 Dodaj Ręcznie")
    m_name = st.text_input("Nazwa produktu", key="m_name")
    m_kcal = st.number_input("Kcal", min_value=0, step=1, key="m_kcal")
    m_p = st.number_input("Białko (g)", min_value=0.0, step=0.1, key="m_p")
    m_c = st.number_input("Węglowodany (g)", min_value=0.0, step=0.1, key="m_c")
    m_f = st.number_input("Tłuszcze (g)", min_value=0.0, step=0.1, key="m_f")
    if st.button("➕ DODAJ DO DNIA"):
        if m_name:
            st.session_state.extra_meals.append({
                "name": m_name, "kcal": m_kcal, "p": m_p, "c": m_c, "f": m_f
            })
            st.success(f"Dodano: {m_name}")
            st.rerun()
        else: st.error("Podaj nazwę produktu!")

with col_right:
    st.header("🏋️ Plan Treningowy")
    selected_day = st.selectbox("Wybierz trening:", list(active_workouts.keys()))
    if selected_day == "Dzień C (Nogi)" and profile_type == "Mój Profil (info.md)": st.error("🚫 ZAKAZ BIEGANIA")
    
    # Capture state
    checked_exercises = []
    for ex in active_workouts[selected_day]:
        # Unique key for every exercise to avoid conflicts
        if st.checkbox(ex, key=f"chk_{ex}"):
            checked_exercises.append(ex)
            
    # Update session state for the Save button (which is in Sidebar)
    if checked_exercises:
        st.session_state.workout_status = f"{selected_day}: " + ", ".join(checked_exercises)
    else:
        st.session_state.workout_status = selected_day # Default to just day name if no specific exercise checked yet
    
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
    st.header("📈 Historia i Szczegóły")
    history_df = pd.read_csv(active_data["db"])
    
    col_hist1, col_hist2 = st.columns([1, 2])
    with col_hist1:
        st.subheader("Waga")
        st.line_chart(history_df.set_index("Data")["Waga"])
    
    with col_hist2:
        st.subheader("Podgląd Dnia")
        available_dates = history_df["Data"].unique()
        selected_date = st.selectbox("Wybierz datę do podglądu:", available_dates[::-1])
        day_details = history_df[history_df["Data"] == selected_date].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Kcal", day_details["Kcal"])
        c2.metric("Białko", day_details["Bialko"])
        c3.metric("Woda", day_details["Woda"])
        
        st.write(f"**Produkty:** {day_details['Skladniki']}")
        st.write(f"**Trening:** {day_details['Trening']}")
