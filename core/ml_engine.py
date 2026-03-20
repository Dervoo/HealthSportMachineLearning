import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

class MLEngine:
    def __init__(self, csv_path="progress_me.csv", products_path="data/products.json"):
        self.csv_path = csv_path
        self.products_path = products_path
        self.df = pd.DataFrame() # Initialize empty
        self.reload_data()
        try:
            with open(products_path, 'r', encoding='utf-8') as f:
                self.products = json.load(f)
        except:
            self.products = {}

    def set_data(self, df):
        """Ustawia dane bezpośrednio (np. z bazy SQL) i mapuje nazwy kolumn."""
        if df.empty:
            self.df = pd.DataFrame()
            return
            
        # Mapowanie nazw kolumn z bazy na format oczekiwany przez MLEngine/Dashboard
        mapping = {
            'date': 'Data',
            'weight': 'Waga',
            'water': 'Woda',
            'kcal': 'Kcal',
            'protein': 'Bialko',
            'carbs': 'Wegle',
            'fats': 'Tluszcze',
            'training_log': 'Trening',
            'rpe': 'RPE',
            'sleep_quality': 'Sen_Jakosc'
        }
        self.df = df.rename(columns=mapping)
        if 'Data' in self.df.columns:
            self.df['Data'] = pd.to_datetime(self.df['Data'])

    def reload_data(self):
        """Wczytuje najnowsze dane z pliku CSV (zachowanie wstecznej kompatybilności)."""
        try:
            if os.path.exists(self.csv_path):
                self.df = pd.read_csv(self.csv_path)
                if not self.df.empty and 'Data' in self.df.columns:
                    self.df['Data'] = pd.to_datetime(self.df['Data'])
        except:
            pass

    def calculate_water_requirement(self, weight, activity_level):
        """Oblicza zapotrzebowanie na wodę: 33ml na kg masy ciała + bonus za aktywność."""
        base_water = weight * 0.033
        activity_bonus = (activity_level - 1.2) * 1.5 # Dodatkowe 1.5L dla najwyższej aktywności
        return round(base_water + activity_bonus, 2)

    def predict_weight_trend(self, days_ahead=7):
        if len(self.df) < 3: return None
        start_date = self.df['Data'].min()
        X = (self.df['Data'] - start_date).dt.days.values.reshape(-1, 1)
        y = self.df['Waga'].values
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        future_days = (datetime.now() - start_date).days + days_ahead
        prediction = model.predict([[future_days]])[0]
        slope = model.coef_[0] * 7
        return {"target_weight": round(prediction, 2), "weekly_change": round(slope, 2)}

    def predict_plateau_prophet(self, days_ahead=14):
        if len(self.df) < 5:
            return {"msg": "Potrzeba min. 5 dni pomiarów.", "status": "wait"}
        try:
            from prophet import Prophet
            import logging
            logging.getLogger('prophet').setLevel(logging.WARNING)
            prophet_df = self.df[['Data', 'Waga']].rename(columns={'Data': 'ds', 'Waga': 'y'})
            model = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False)
            model.fit(prophet_df)
            future = model.make_future_dataframe(periods=days_ahead)
            forecast = model.predict(future)
            delta = forecast['yhat'].iloc[-1] - prophet_df['y'].iloc[-1]
            if abs(delta) < 0.2:
                return {"msg": "Plateau! Refeed Day sugerowany.", "delta": round(delta, 2), "status": "plateau"}
            return {"msg": f"Trend OK. Zmiana: {delta:+.2f} kg.", "delta": round(delta, 2), "status": "ok"}
        except: return {"msg": "Błąd modelu Prophet.", "status": "error"}

    def suggest_diet_lp(self, target_kcal, target_protein):
        from scipy.optimize import linprog
        if not self.products: return None
        product_names = list(self.products.keys())
        c = [self.products[name]['kcal'] for name in product_names]
        A_ub = [[-self.products[name]['p'] for name in product_names]]
        b_ub = [-target_protein]
        bounds = [(0, 5) for _ in product_names]
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        if res.success:
            plan = []
            for i, amount in enumerate(res.x):
                if amount > 0.05:
                    plan.append({"product": product_names[i], "amount": round(amount * 100), "p": round(self.products[product_names[i]]['p'] * amount, 1), "kcal": round(self.products[product_names[i]]['kcal'] * amount)})
            return {"plan": plan, "total_kcal": round(res.fun), "total_p": round(sum(p['p'] for p in plan))}
        return None

    def recommend_daily_activity(self, last_sleep=None, avg_rpe=None):
        if last_sleep is None: return {"type": "Standard", "msg": "Brak danych o śnie.", "color": "info"}
        if last_sleep <= 2: return {"type": "RECOVERY", "msg": "Niska regeneracja. Tylko spacer.", "color": "error"}
        if avg_rpe and avg_rpe >= 9 and last_sleep <= 3: return {"type": "DELOAD", "msg": "Zmęczenie. 50% objętości.", "color": "warning"}
        if last_sleep >= 4: return {"type": "HEAVY", "msg": "Forma peak! Bij rekordy.", "color": "success"}
        return {"type": "REGULAR", "msg": "Wykonaj plan.", "color": "primary"}

    def calculate_smart_goal(self, weight, height, age, gender, activity_level, goal):
        if gender.lower() == 'mężczyzna': bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else: bmr = 10 * weight + 6.25 * height - 5 * age - 161
        tdee = bmr * activity_level
        if goal == 'masa': target_kcal, target_p = tdee + 300, weight * 2.2
        elif goal == 'redukcja': target_kcal, target_p = tdee - 500, weight * 2.5
        else: target_kcal, target_p = tdee, weight * 2.0
        return {"tdee": round(tdee), "target_kcal": round(target_kcal), "target_p": round(target_p), "water": self.calculate_water_requirement(weight, activity_level)}

    def parse_volume(self):
        """Przetwarza tekstowe logi treningowe na liczbowy tonaż (Objętość)."""
        if self.df.empty or 'Trening' not in self.df.columns: return []
        
        volumes = []
        import re
        
        for index, row in self.df.iterrows():
            t_str = str(row['Trening'])
            if "Rest Day" in t_str or pd.isna(t_str):
                volumes.append(0)
                continue
                
            day_vol = 0
            # Szukamy wzorca: Nazwa(SxWkg x Reps) np. Pompki(3x15.0kg x 10) lub Pompki(3x15.0kg x 12,10,8)
            # Regex: (liczba)x(liczba)kg x (ciąg znaków)
            matches = re.findall(r"\((\d+)x([\d\.]+)kg x ([0-9,]+)\)", t_str)
            
            for sets, weight, reps_str in matches:
                try:
                    w = float(weight)
                    # Sumujemy powtórzenia (czy to "10" czy "12,10,8")
                    total_reps = sum([int(r) for r in reps_str.split(",") if r.isdigit()])
                    day_vol += w * total_reps
                except: pass
            
            volumes.append(day_vol)
        
        return volumes

    def analyze_training_insights(self):
        """Analizuje postępy w objętości i korelację ze snem."""
        volumes = self.parse_volume()
        if not volumes or len(volumes) < 3: return {"trend": "Zbieranie danych...", "corr": "Brak danych", "last_vol": 0}
        
        # 1. Trend Objętości (Średnia z 3 ostatnich vs 3 poprzednich)
        # Filtrujemy tylko dni treningowe (>0)
        train_vols = [v for v in volumes if v > 0]
        if len(train_vols) < 2: return {"trend": "Za mało treningów", "corr": "...", "last_vol": 0}
        
        last_vol = train_vols[-1]
        avg_vol = sum(train_vols) / len(train_vols)
        
        if last_vol > avg_vol * 1.05: trend_icon = "📈 Rosnąca (Progres)"
        elif last_vol < avg_vol * 0.95: trend_icon = "📉 Spadkowa (Regres)"
        else: trend_icon = "➡️ Stabilna"
        
        # 2. Korelacja Sen vs Objętość
        # Potrzebujemy połączyć volumes z df['Sen_Jakosc']
        sleeps = self.df['Sen_Jakosc'].tolist()
        
        # Pary (Sen, Volume) tylko dla dni treningowych
        pairs = [(s, v) for s, v in zip(sleeps, volumes) if v > 0 and not pd.isna(s)]
        
        if len(pairs) > 4:
            s_arr = np.array([p[0] for p in pairs])
            v_arr = np.array([p[1] for p in pairs])
            try:
                corr = np.corrcoef(s_arr, v_arr)[0, 1]
                if corr > 0.3: corr_msg = f"Dobry sen daje moc! (r={corr:.2f})"
                elif corr < -0.3: corr_msg = f"Brak związku (r={corr:.2f})"
                else: corr_msg = "Wpływ neutralny"
            except: corr_msg = "Błąd obliczeń"
        else:
            corr_msg = "Zbierz więcej danych"
            
        return {"trend": trend_icon, "corr": corr_msg, "last_vol": int(last_vol)}

    def get_volume_history(self):
        """Zwraca DataFrame z datą i obliczoną objętością do wykresów."""
        if self.df.empty: return pd.DataFrame()
        
        volumes = self.parse_volume()
        temp_df = self.df.copy()
        temp_df['Objetosc'] = volumes
        # Filtrujemy tylko dni treningowe
        return temp_df[temp_df['Objetosc'] > 0][['Data', 'Objetosc']]

    def analyze_sleep_impact(self):
        if len(self.df) < 5: return "Zbyt mało danych."
        data = self.df.dropna(subset=['RPE', 'Sen_Jakosc'])
        if len(data) < 3: return "Brak danych treningowych."
        correlation = data['Sen_Jakosc'].corr(data['RPE'])
        return f"Korelacja: {correlation:.2f}"
