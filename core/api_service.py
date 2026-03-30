import time
import random
import pandas as pd

class APIService:
    """Mock API Service do 'mielenia' danych i interpretacji."""
    
    def __init__(self, api_url="https://api.health-ml-optimizer.mock"):
        self.api_url = api_url

    def fetch_market_benchmarks(self, user_goal, age):
        """Pobiera benchmarki rynkowe dla danej grupy wiekowej i celu."""
        # Symulacja opóźnienia sieci
        time.sleep(0.5)
        
        benchmarks = {
            "masa": {"avg_p_kg": 2.2, "avg_kcal_surplus": 300, "recovery_days": 1},
            "redukcja": {"avg_p_kg": 2.5, "avg_kcal_deficit": 500, "recovery_days": 2},
            "utrzymanie": {"avg_p_kg": 1.8, "avg_kcal_offset": 0, "recovery_days": 1.5}
        }
        return benchmarks.get(user_goal, benchmarks["utrzymanie"])

    def send_progress_for_analysis(self, progress_df):
        """Wysyła dane do API w celu głębokiej analizy (interpretacja trendów)."""
        if progress_df.empty:
            return {"status": "error", "msg": "Brak danych do analizy."}
            
        # Symulacja 'mielenia' danych przez zewnętrzny model
        time.sleep(1.0)
        
        # Prosta analiza na potrzeby mocka
        avg_sleep = progress_df['sleep_quality'].mean()
        avg_rpe = progress_df['rpe'].mean()
        
        insights = []
        if avg_sleep < 3:
            insights.append("Analiza API: Niska jakość snu drastycznie obniża Twoją wydolność (korelacja wykryta).")
        if avg_rpe > 8:
            insights.append("Analiza API: Twój RPE jest stale wysoki. Sugerowany tydzień deload.")
        
        return {
            "status": "success",
            "insights": insights if insights else ["Analiza API: Parametry w normie. Kontynuuj plan."],
            "optimization_factor": round(random.uniform(0.9, 1.1), 2)
        }

if __name__ == "__main__":
    api = APIService()
    print("API Service ready.")
