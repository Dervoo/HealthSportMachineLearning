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

    def analyze_sleep_impact(self):
        """Analizuje korelację między jakością snu a trudnością treningu (RPE)."""
        if len(self.df) < 5:
            return "Zbyt mało danych (wymagane 5 dni z treningiem)."
        
        # Filtrujemy dni, gdzie był trening i jest ocena snu
        data = self.df.dropna(subset=['RPE', 'Sen_Jakosc'])
        if len(data) < 3:
            return "Brak wystarczających danych treningowych."

        # Korelacja ujemna jest dobra (Więcej Snu = Mniejsze RPE/Lżej)
        correlation = data['Sen_Jakosc'].corr(data['RPE'])
        
        if np.isnan(correlation):
            return "Brak korelacji (stałe wartości)."
            
        if correlation < -0.5:
            return f"Silna zależność ({correlation:.2f}): Lepszy sen wyraźnie ułatwia treningi!"
        elif correlation > 0.5:
            return f"Anomalia ({correlation:.2f}): Mimo dobrego snu, treningi są ciężkie (sprawdź objętość)."
        else:
            return f"Brak wyraźnego wpływu snu na RPE ({correlation:.2f})."

# Test silnika (opcjonalny)
if __name__ == "__main__":
    engine = MLEngine()
    print(engine.predict_weight_trend())
