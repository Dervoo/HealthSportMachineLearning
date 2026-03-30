import subprocess
import time
import sys
import os

def run_command(command, name):
    print(f"🚀 Uruchamiam {name}...")
    return subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    print("=== Health-ML Optimizer: System Startup ===\n")

    # Pobieramy ścieżkę do bieżącego interpretera (np. py lub python)
    python_exe = sys.executable

    # 1. Backend API (FastAPI) - uruchamiamy przez moduł uvicorn
    backend = run_command(f'"{python_exe}" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000', "Backend API")

    # 2. Frontend Web (Streamlit) - uruchamiamy przez moduł streamlit
    time.sleep(2) # Czekaj na start API
    frontend = run_command(f'"{python_exe}" -m streamlit run frontend_web/app.py --server.port 8501', "Frontend Dashboard")

    print("\n✅ Systemy działają!")
    print("🔗 API: http://localhost:8000/docs (Swagger)")
    print("🔗 Dashboard: http://localhost:8501")
    print("\n📱 Aplikacja Mobilna (Development):")
    print("   cd frontend_mobile")
    print("   flutter run")
    print("\nUżyj: py run_project.py (jeśli python nie działa)")
    print("Naciśnij Ctrl+C, aby zatrzymać wszystko.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Zatrzymywanie systemów...")
        backend.terminate()
        frontend.terminate()
        print("Done.")
