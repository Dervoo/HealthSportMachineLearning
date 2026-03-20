import pandas as pd
import numpy as np
from db_manager import DBManager
from api_service import APIService

class AnalyticsEngine:
    def __init__(self):
        self.db = DBManager()
        self.api = APIService()
        self.ext_data_path = "external_fitness_data.csv"
        self._load_external_data()

    def _load_external_data(self):
        try:
            self.ext_df = pd.read_csv(self.ext_data_path)
        except:
            self.ext_df = pd.DataFrame()

    def get_user_status(self, user_id):
        user = self.db.get_all_users().query(f"id == {user_id}").iloc[0].to_dict()
        progress = self.db.get_user_progress(user_id)
        
        # 'Mielenie' danych lokalnych
        if not progress.empty:
            avg_kcal = progress['kcal'].tail(7).mean()
            avg_sleep = progress['sleep_quality'].tail(7).mean()
            
            # Strzał do API po interpretację
            api_response = self.api.send_progress_for_analysis(progress)
            benchmarks = self.api.fetch_market_benchmarks(user['goal'], user['age'])
            
            # Porównanie z populacją (Kaggle)
            pop_stats = self.get_population_benchmarks(user['goal'], user['age'])
            
            return {
                "user": user,
                "local_stats": {"avg_kcal": avg_kcal, "avg_sleep": avg_sleep},
                "api_insights": api_response['insights'],
                "opt_factor": api_response['optimization_factor'],
                "benchmarks": benchmarks,
                "population_benchmarks": pop_stats
            }
        return None

    def get_population_benchmarks(self, goal, age):
        """Pobiera średnie statystyki sukcesu z zewnętrznej bazy (Kaggle)."""
        if self.ext_df.empty: return None
        
        # Zgodnie z prośbą: bierze dane z CAŁEJ bazy (bez dodatkowych filtrów wieku i sukcesu)
        # Filtrujemy tylko po celu, aby autokorekta kaloryczna miała sens.
        filtered = self.ext_df[self.ext_df['goal'] == goal]
        
        if filtered.empty: return None
        
        return {
            "avg_kcal": round(filtered['avg_kcal'].mean()),
            "avg_p_kg": round(filtered['avg_p_kg'].mean(), 2),
            "avg_weekly_change": round(filtered['weight_change_weekly'].mean(), 2)
        }

    def refine_ml_parameters(self, user_id, current_kcal, source="api"):
        """Ulepsza zależności maszynek na podstawie 'mielenia' danych z API lub Populacji."""
        status = self.get_user_status(user_id)
        if not status: return current_kcal
        
        if source == "api":
            refined_kcal = current_kcal * status['opt_factor']
            # Jeśli sen jest słaby, API może sugerować obniżenie intensywności
            if status['local_stats']['avg_sleep'] < 3.5:
                refined_kcal *= 0.95
        else:
            # Optymalizacja na podstawie Sukcesu Populacji (Kaggle)
            pop = status.get('population_benchmarks')
            if pop:
                # Dążymy do średniej kaloryczności osób z sukcesem w tej samej grupie
                refined_kcal = (current_kcal + pop['avg_kcal']) / 2
            else:
                refined_kcal = current_kcal
            
        return round(refined_kcal)

if __name__ == "__main__":
    ae = AnalyticsEngine()
    print(ae.get_user_status(1))
