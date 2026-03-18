import streamlit as st
import pandas as pd
import datetime
import os
import json
import requests
from ml_engine import MLEngine
from db_manager import DBManager
from analytics_engine import AnalyticsEngine

# --- CONFIG & STYLES ---
st.set_page_config(page_title="Health-ML Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- DB & ANALYTICS ---
if "db" not in st.session_state:
    st.session_state.db = DBManager()
if "ae" not in st.session_state:
    st.session_state.ae = AnalyticsEngine()

# --- ML ENGINE ---
if "ml" not in st.session_state or not hasattr(st.session_state.ml, "calculate_water_requirement"):
    st.session_state.ml = MLEngine()

# --- PERSISTENT SETTINGS ---
SETTINGS_FILE = "ai_settings.json"
def load_ai_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f: return json.load(f)
    return {"weight": 78.1, "height": 180.0, "age": 25, "gender": "Mężczyzna", "activity": 1.55, "goal": "utrzymanie", "target_kcal": 1900, "protein_goal": 180, "water_goal": 2.5}

def save_ai_settings(data):
    with open(SETTINGS_FILE, "w") as f: json.dump(data, f, indent=4)

if "ai_cfg" not in st.session_state: st.session_state.ai_cfg = load_ai_settings()

# --- SESSION STATE ---
if "extra_meals" not in st.session_state: st.session_state.extra_meals = []
if "meal_water" not in st.session_state: st.session_state.meal_water = 0.0
if "workout_session" not in st.session_state: st.session_state.workout_session = []
if "api_results" not in st.session_state: st.session_state.api_results = []
if "target_kcal" not in st.session_state: st.session_state.target_kcal = st.session_state.ai_cfg["target_kcal"]
if "protein_goal" not in st.session_state: st.session_state.protein_goal = st.session_state.ai_cfg["protein_goal"]
if "water_goal" not in st.session_state: st.session_state.water_goal = st.session_state.ai_cfg.get("water_goal", 2.5)

# --- CONSTANTS ---
MY_MEALS = [{"name": "High Protein Milk", "kcal": 130, "p": 20.0, "c": 12.0, "f": 0.6}, {"name": "Soy Protein (30g)", "kcal": 109, "p": 25.8, "c": 1.2, "f": 0.1}, {"name": "Twaróg Chudy (230g)", "kcal": 202, "p": 41.4, "c": 8.1, "f": 0.5}]
MY_WORKOUTS = {"Dzień A (Push)": ["Pompki z plecakiem 15kg", "Floor Press 24kg", "Barki OHP 24kg", "Pompki nogi wyżej", "Pompki z wąskimi rękoma", "Wyprosty za głowę"], "Dzień B (Pull)": ["Podciąganie", "Wiosłowanie 24kg+15kg", "Wiosłowanie hantlami 7kg", "Biceps hantle", "Plank z plecakiem 15kg"], "Dzień C (Nogi)": ["Bułgarskie przysiady", "RDL 24kg+15kg", "Hip Thrust 24kg", "Wykroki 7kg", "Wznosy nóg"], "Bieganie": ["Bieganie 35-40 min"], "Dzień Wolny": ["Rest Day"]}

# --- EDAMAM CONFIG ---
try:
    EDAMAM_APP_ID = st.secrets["EDAMAM_APP_ID"]
    EDAMAM_APP_KEY = st.secrets["EDAMAM_APP_KEY"]
except:
    EDAMAM_APP_ID = ""
    EDAMAM_APP_KEY = ""

def search_edamam_products(query):
    if not EDAMAM_APP_ID or not EDAMAM_APP_KEY:
        return []
    url = f"https://api.edamam.com/api/food-database/v2/parser?app_id={EDAMAM_APP_ID}&app_key={EDAMAM_APP_KEY}&ingr={query}&nutrition-type=logging"
    try:
        res = requests.get(url).json()
        results = []
        for item in res.get("hints", []):
            food = item["food"]
            nutrients = food.get("nutrients", {})
            results.append({
                "display_name": f"🌐 {food['label']} ({food.get('category', 'Food')})",
                "full_name": food['label'],
                "kcal": round(nutrients.get("ENERC_KCAL", 0)),
                "p": round(nutrients.get("PROCNT", 0), 1),
                "c": round(nutrients.get("CHOCDF", 0), 1),
                "f": round(nutrients.get("FAT", 0), 1)
            })
        return results
    except: return []

def load_products():
    try:
        with open("data/products.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

# --- SIDEBAR ---
st.sidebar.title("👤 PROFIL")
profile_type = st.sidebar.radio("Użytkownik:", ["Mój Profil", "Vault (Baza DB)"])

if profile_type == "Mój Profil":
    db_file = "progress_me.csv"
    st.session_state.ml.reload_data()
    current_user_id = None
else:
    all_users = st.session_state.db.get_all_users()
    if all_users.empty:
        st.sidebar.warning("Baza pusta. Dodaj użytkownika.")
        if st.sidebar.button("➕ DODAJ TESTOWEGO"):
            st.session_state.db.add_user("Tester", 30, 185, "Mężczyzna", 1.55, "masa", 3000, 180, 3.5)
            st.rerun()
    selected_user = st.sidebar.selectbox("Wybierz profil:", all_users['name'].tolist())
    user_data = st.session_state.db.get_user_by_name(selected_user)
    current_user_id = user_data['id']
    # Sync settings with DB user
    st.session_state.ai_cfg["weight"] = 80.0 # Default if no progress
    progress = st.session_state.db.get_user_progress(current_user_id)
    if not progress.empty:
        st.session_state.ai_cfg["weight"] = progress['weight'].iloc[-1]
    
    st.session_state.ml.set_data(progress)
    st.session_state.target_kcal = user_data['target_kcal']
    st.session_state.protein_goal = user_data['target_protein']
    st.session_state.water_goal = user_data['water_goal']

st.sidebar.divider()
log_date = st.sidebar.date_input("📅 Data wpisu:", datetime.date.today())
daily_rpe = st.sidebar.select_slider("🧠 RPE (Trudność)", options=list(range(1, 11)), value=7)
daily_sleep = st.sidebar.select_slider("😴 Sen (Jakość)", options=list(range(1, 6)), value=4)

st.sidebar.divider()
water_val = st.sidebar.slider("💧 Woda (L)", 0.0, 5.0, 1.5, step=0.1)
herbs_val = st.sidebar.number_input("🌿 Ziółka (L)", 0.0, 2.0, 0.0, step=0.1)
total_hydration = round(water_val + (herbs_val * 0.9) + st.session_state.meal_water, 2)

with st.sidebar.expander("🤖 AI SMART GOAL"):
    s_w = st.number_input("Waga", value=float(st.session_state.ai_cfg["weight"]))
    s_act = st.select_slider("Aktywność", options=[1.2, 1.375, 1.55, 1.725, 1.9], value=st.session_state.ai_cfg["activity"])
    goal_list = ["redukcja", "utrzymanie", "masa"]
    s_goal = st.selectbox("Cel", goal_list, index=goal_list.index(st.session_state.ai_cfg.get("goal", "utrzymanie")))
    if st.button("🚀 OBLICZ I ZAPISZ"):
        smart = st.session_state.ml.calculate_smart_goal(s_w, 180, 25, "Mężczyzna", s_act, s_goal)
        st.session_state.target_kcal, st.session_state.protein_goal, st.session_state.water_goal = smart["target_kcal"], smart["target_p"], smart["water"]
        save_ai_settings({"weight": s_w, "height": 180, "age": 25, "gender": "Mężczyzna", "activity": s_act, "goal": s_goal, "target_kcal": smart["target_kcal"], "protein_goal": smart["target_p"], "water_goal": smart["water"]})
        st.rerun()

# --- STYLES ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .main-title { color: #00d4ff; font-size: 3rem; font-weight: 800; text-shadow: 2px 2px 10px rgba(0,212,255,0.3); margin-bottom: 20px; }
    [data-testid="stMetric"] { background-color: #1e2130 !important; padding: 20px !important; border-radius: 12px !important; border: 1px solid #00d4ff !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 800 !important; font-size: 2.2rem !important; }
    [data-testid="stMetricLabel"] { color: #00d4ff !important; font-weight: bold !important; font-size: 1.1rem !important; }
    </style>
    <h1 class='main-title'>🚀 Health-ML Optimizer</h1>
    """, unsafe_allow_html=True)

# --- TOP METRICS ---
total_p = sum(m["p"] for m in st.session_state.extra_meals)
total_kcal = sum(m["kcal"] for m in st.session_state.extra_meals)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Energia", f"{total_kcal:.0f} kcal", f"{st.session_state.target_kcal - total_kcal:.0f} left")
m2.metric("Białko", f"{total_p:.1f}g", f"Cel: {st.session_state.protein_goal}")
m3.metric("Nawodnienie", f"{total_hydration} L", f"Cel AI: {st.session_state.water_goal}L")
m4.metric("Waga", f"{st.session_state.ai_cfg['weight']} kg")

# --- LOGS PREVIEW ---
c_log1, c_log2 = st.columns(2)
with c_log1:
    with st.expander("🍱 DZISIEJSZE JEDZENIE", expanded=True):
        if st.session_state.extra_meals:
            st.table(pd.DataFrame(st.session_state.extra_meals))
            if st.button("🗑️ WYCZYŚĆ JEDZENIE"): st.session_state.extra_meals = []; st.session_state.meal_water = 0.0; st.rerun()
with c_log2:
    with st.expander("🏋️ SESJA TRENINGOWA", expanded=True):
        if st.session_state.workout_session:
            for ex in st.session_state.workout_session: st.write(f"✅ {ex}")
            if st.button("🗑️ WYCZYŚĆ TRENING"): st.session_state.workout_session = []; st.rerun()

st.sidebar.divider()
if st.sidebar.button("💾 ZAPISZ CAŁY DZIEŃ"):
    workout_str = ", ".join(st.session_state.workout_session) if st.session_state.workout_session else "Rest Day"
    if profile_type == "Mój Profil":
        new_data = pd.DataFrame([{"Data": str(log_date), "Waga": st.session_state.ai_cfg["weight"], "Woda": total_hydration, "Kcal": total_kcal, "Bialko": total_p, "Wegle": 0, "Tluszcze": 0, "Trening": workout_str, "Skladniki": "Logged", "RPE": daily_rpe, "Sen_Jakosc": daily_sleep, "Cel_Kcal": st.session_state.target_kcal, "Cel_Bialko": st.session_state.protein_goal}])
        if not os.path.isfile(db_file): new_data.to_csv(db_file, index=False)
        else: new_data.to_csv(db_file, mode='a', header=False, index=False)
    else:
        st.session_state.db.add_progress(current_user_id, str(log_date), st.session_state.ai_cfg["weight"], total_hydration, total_kcal, total_p, 0, 0, workout_str, daily_rpe, daily_sleep)
    
    st.session_state.ml.reload_data()
    st.session_state.extra_meals = []; st.session_state.workout_session = []; st.session_state.meal_water = 0.0; st.rerun()

st.divider()

# --- VAULT & API INSIGHTS ---
if profile_type != "Mój Profil" and current_user_id:
    st.header("🧠 Vault Insights (Mielenie Danych)")
    v1, v2, v3 = st.columns(3)
    status = st.session_state.ae.get_user_status(current_user_id)
    if status:
        with v1:
            st.subheader("🌐 Global Benchmarks")
            st.write(f"Cel: **{status['user']['goal']}**")
            st.write(f"Sugerowane Białko: {status['benchmarks']['avg_p_kg']} g/kg")
            st.write(f"Recovery Days: {status['benchmarks']['recovery_days']}")
        with v2:
            st.subheader("🧪 API Interpretacja")
            for insight in status['api_insights']:
                st.info(insight)
        with v3:
            st.subheader("⚙️ Optymalizacja ML")
            opt_source = st.radio("Źródło korekty:", ["API Insights", "Population (Kaggle)"], horizontal=True)
            source_key = "api" if opt_source == "API Insights" else "kaggle"
            
            refined_kcal = st.session_state.ae.refine_ml_parameters(current_user_id, st.session_state.target_kcal, source=source_key)
            
            if status.get('population_benchmarks'):
                st.caption(f"Średnia Kaggle: {status['population_benchmarks']['avg_kcal']} kcal")
            
            if refined_kcal != st.session_state.target_kcal:
                st.warning(f"Sugerowana korekta: {st.session_state.target_kcal} -> {refined_kcal}")
                if st.button("✅ ZASTOSUJ KOREKTĘ", key="apply_refine_btn"):
                    st.session_state.target_kcal = refined_kcal
                    st.rerun()
            else:
                st.success("Parametry optymalne.")
    st.divider()

ai1, ai2, ai3, ai4 = st.columns(4)
with ai1:
    st.subheader("📉 Trend Wagi")
    p_info = st.session_state.ml.predict_plateau_prophet()
    st.info(p_info["msg"])
with ai2:
    st.subheader("🍗 Diet (LP)")
    n_p = st.session_state.protein_goal - total_p
    if n_p > 0:
        diet = st.session_state.ml.suggest_diet_lp(st.session_state.target_kcal - total_kcal, n_p)
        if diet: 
            for i in diet['plan']: st.success(f"✔️ {i['product']} - {i['amount']}g")
    else: st.write("Makro OK! ✨")
with ai3:
    st.subheader("🧘 AI Rec")
    avg_rpe = st.session_state.ml.df['RPE'].tail(3).mean() if not st.session_state.ml.df.empty else None
    rec = st.session_state.ml.recommend_daily_activity(daily_sleep, avg_rpe)
    st.warning(f"{rec['type']}: {rec['msg']}")
with ai4:
    st.subheader("🏋️ Objętość & Sen")
    insights = st.session_state.ml.analyze_training_insights()
    st.write(f"Trend: {insights['trend']}")
    st.caption(f"Ostatnia: {insights['last_vol']} kg")
    st.info(insights['corr'])

st.divider()
col_left, col_mid, col_right = st.columns([1, 1, 1.2])

with col_left:
    st.header("🍱 Baza")
    sq = st.text_input("Szukaj:")
    if sq:
        # Local Matches
        local_matches = [{"display_name": f"🏠 {n}", "full_name": n, "kcal": i["kcal"], "p": i["p"], "c": i.get("c",0), "f": i.get("f",0)} 
                         for n, i in st.session_state.ml.products.items() if sq.lower() in n.lower()]
        
        # Edamam Trigger
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("🌐 SZUKAJ GLOBALNIE"):
            with st.spinner("Mielę dane z Edamam..."):
                st.session_state.api_results = search_edamam_products(sq)
        if col_btn2.button("🧹 CZYŚĆ"):
            st.session_state.api_results = []
            st.rerun()

        all_results = local_matches + st.session_state.api_results
        
        if all_results:
            sel_name = st.selectbox("Wynik:", [x["display_name"] for x in all_results])
            sel_prod = next(x for x in all_results if x["display_name"] == sel_name)
            
            gr = st.number_input("Gramy", value=100, step=10)
            mult = gr / 100.0
            
            st.info(f"📊 {sel_prod['full_name']} ({gr}g)\n\n**{round(sel_prod['kcal']*mult)} kcal** | B: {round(sel_prod['p']*mult,1)} | W: {round(sel_prod['c']*mult,1)} | T: {round(sel_prod['f']*mult,1)}")
            
            if st.button("✅ DODAJ PRODUKT"):
                # Add to session
                st.session_state.extra_meals.append({
                    "name": f"{sel_prod['full_name']} ({gr}g)", 
                    "kcal": round(sel_prod['kcal']*mult), 
                    "p": round(sel_prod['p']*mult,1), 
                    "c": round(sel_prod['c']*mult,1), 
                    "f": round(sel_prod['f']*mult,1)
                })
                
                # Auto-save global to local
                if "🌐" in sel_name:
                    current_db = load_products()
                    if sel_prod["full_name"] not in current_db:
                        current_db[sel_prod["full_name"]] = {"kcal": sel_prod["kcal"], "p": sel_prod["p"], "c": sel_prod["c"], "f": sel_prod["f"]}
                        with open("data/products.json", "w", encoding="utf-8") as f:
                            json.dump(current_db, f, indent=4, ensure_ascii=False)
                        st.session_state.ml.reload_data() # Refresh ML engine products
                st.rerun()

with col_mid:
    st.header("🥗 Ręcznie")
    if profile_type == "Mój Profil":
        with st.expander("⚡ QUICK ADD"):
            for m in MY_MEALS:
                if st.button(f"➕ {m['name']}", key=f"q_{m['name']}"): st.session_state.extra_meals.append(m); st.rerun()
    with st.form("manual_form", clear_on_submit=True):
        m_n = st.text_input("Nazwa")
        col_k, col_w = st.columns(2)
        m_k = col_k.number_input("Kcal", value=None)
        m_water = col_w.number_input("Woda (ml)", value=0, step=50)
        c1, c2, c3 = st.columns(3)
        m_p, m_f, m_c = c1.number_input("Białko", value=None), c2.number_input("Tłuszcz", value=None), c3.number_input("Węgle", value=None)
        if st.form_submit_button("➕ DODAJ"):
            kcal = m_k if m_k else int((m_p or 0)*4 + (m_c or 0)*4 + (m_f or 0)*9)
            st.session_state.extra_meals.append({"name": m_n or "Ręczny", "kcal": kcal, "p": m_p or 0.0, "c": m_c or 0.0, "f": m_f or 0.0})
            st.session_state.meal_water += (m_water / 1000.0)
            st.rerun()

with col_right:
    st.header("🏋️ Trening")
    if st.button("📋 WCZYTAJ OSTATNI"):
        if os.path.exists(db_file):
            df = pd.read_csv(db_file)
            last = df[df['Trening'] != "Rest Day"]
            if not last.empty: st.session_state.workout_session = [e.strip() for e in last['Trening'].iloc[-1].split(",")]
            st.rerun()
    day = st.selectbox("Dzień:", list(MY_WORKOUTS.keys()))
    ex_name = st.selectbox("Ćwiczenie:", MY_WORKOUTS[day])
    
    is_running = "Bieganie" in day
    is_rest = "Dzień Wolny" in day
    base_w = 15.0 if "15kg" in ex_name else 24.0 if "24kg" in ex_name else 0.0
    
    if is_rest:
        if st.button("➕ DODAJ DZIEŃ WOLNY"):
            st.session_state.workout_session.append("Rest Day")
            st.rerun()
    elif not is_running:
        is_var = st.checkbox("Różne powtórzenia?", key="is_var_check")
        with st.form("workout_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([1, 1, 2])
            extra_w = c1.number_input("Extra kg", value=0.0, step=0.5)
            if is_var:
                reps_str = c3.text_input("Powtórzenia (np. 12,10,8)")
                sets_count = 0
            else:
                sets_count = c2.number_input("Serie", value=3, min_value=1)
                reps_val = c3.number_input("Powtórzenia", value=10, min_value=1)
                reps_str = str(reps_val)
            if st.form_submit_button("➕ DODAJ ĆWICZENIE"):
                if is_var and reps_str:
                    count = len(reps_str.split(","))
                    st.session_state.workout_session.append(f"{ex_name}({count}x{base_w + extra_w}kg x {reps_str})")
                elif not is_var:
                    st.session_state.workout_session.append(f"{ex_name}({sets_count}x{base_w + extra_w}kg x {reps_str})")
                st.rerun()
    else:
        with st.form("running_form", clear_on_submit=True):
            run_kcal = st.number_input("Spalone kcal", value=300, step=10)
            if st.form_submit_button("➕ DODAJ BIEGANIE"):
                st.session_state.workout_session.append(f"Bieganie ({run_kcal} kcal)")
                st.rerun()

if not st.session_state.ml.df.empty:
    st.divider()
    st.header("📈 Analiza Historyczna")
    c_hist1, c_hist2 = st.columns(2)
    
    with c_hist1:
        st.subheader("Waga w czasie")
        st.line_chart(st.session_state.ml.df.set_index("Data")["Waga"])
        
    with c_hist2:
        st.subheader("Objętość Treningowa (Tonaż)")
        vol_df = st.session_state.ml.get_volume_history()
        if not vol_df.empty:
            st.line_chart(vol_df.set_index("Data")["Objetosc"])
        else:
            st.info("Loguj treningi z ciężarem, aby zobaczyć wykres objętości.")
