import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

class MLEngine:
    def __init__(self, csv_path="progress_me.csv", products_path="data/products.json"):
        self.csv_path = csv_path
        self.products_path = products_path
        try:
            self.df = pd.read_csv(csv_path)
            self.df['Data'] = pd.to_datetime(self.df['Data'])
        except:
            self.df = pd.DataFrame()
            
        try:
            with open(products_path, 'r', encoding='utf-8') as f:
                self.products = json.load(f)
        except:
            self.products = {}

    def predict_weight_trend(self, days_ahead=7):
        """Prosta regresja liniowa dla trendu wagi."""
        if len(self.df) < 3:
            return None
        
        # Konwersja daty na dni od początku pomiarów
        start_date = self.df['Data'].min()
        X = (self.df['Data'] - start_date).dt.days.values.reshape(-1, 1)
        y = self.df['Waga'].values
        
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        
        future_days = (datetime.now() - start_date).days + days_ahead
        prediction = model.predict([[future_days]])[0]
        
        # Obliczanie tempa zmiany (kg/tydzień)
        slope = model.coef_[0] * 7
        return {"target_weight": round(prediction, 2), "weekly_change": round(slope, 2)}

    def suggest_diet(self, target_kcal=1900, target_protein=180):
        """Optymalizacja doboru produktów pod makroskładniki (Heurystyka Greedy)."""
        if not self.products:
            return "Brak danych o produktach."
            
        # Sortowanie po g białka / kcal (najbardziej efektywne białko)
        sorted_products = sorted(
            self.products.items(), 
            key=lambda x: (x[1]['p'] / x[1]['kcal'] if x[1]['kcal'] > 0 else 0), 
            reverse=True
        )
        
        plan = []
        current_kcal = 0
        current_p = 0
        
        # Prosty algorytm zachłanny dla 100g porcji
        for name, macros in sorted_products:
            if current_kcal + macros['kcal'] <= target_kcal:
                plan.append({"product": name, "amount": 100})
                current_kcal += macros['kcal']
                current_p += macros['p']
                
        return {"plan": plan, "total_kcal": round(current_kcal), "total_p": round(current_p)}

    def recommend_workout_load(self, workout_name, last_rpe=None, last_weight=None):
        """Sugeruje zmianę obciążenia na bazie RPE."""
        if last_rpe is None:
            return "Zacznij logować RPE, aby uzyskać sugestie."
            
        if last_rpe <= 7:
            return f"Progresja: Dodaj 2.5kg lub 2 powtórzenia do {workout_name}."
        elif last_rpe >= 9:
            return f"Utrzymanie: Pozostań przy obecnym ciężarze w {workout_name}."
        else:
            return f"Stabilizacja: Skup się na tempie w {workout_name}."

# Test silnika (opcjonalny)
if __name__ == "__main__":
    engine = MLEngine()
    print(engine.predict_weight_trend())
