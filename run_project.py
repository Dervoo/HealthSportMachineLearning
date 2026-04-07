import subprocess
import time
import sys
import os

def run_command(command, name):
    print(f"🚀 Uruchamiam {name}...")
    # Używamy subprocess.Popen z powłoką, ale bez blokowania
    return subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    print("=== Health-ML Optimizer: System Startup ===\n")
    
    # Ustalenie katalogu roboczego (root projektu)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)

    # Pobieramy ścieżkę do bieżącego interpretera
    python_exe = sys.executable
    if not python_exe or "python.exe" not in python_exe.lower():
        # Fallback na systemowy 'py' jeśli sys.executable zawiedzie
        python_exe = "py"

    # 1. Backend API (FastAPI)
    # Dodajemy PYTHONPATH oraz flagę --reload dla automatycznego odświeżania po zmianach w kodzie
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(root_dir, "core")
    
    # Dodanie --reload pozwala na edycję kodu bez restartu .bat
    backend_cmd = f'"{python_exe}" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload'
    backend = subprocess.Popen(backend_cmd, shell=True, env=env)

    # 2. Frontend Web (Streamlit)
    time.sleep(3) # Trochę więcej czasu na start API
    frontend_cmd = f'"{python_exe}" -m streamlit run frontend_web/app.py --server.port 8501'
    frontend = subprocess.Popen(frontend_cmd, shell=True)

    print("\n✅ Systemy działają!")
    print("🔗 API: http://localhost:8000/docs")
    print("🔗 Dashboard: http://localhost:8501")
    
    # OPCJA STARTU FLUTTERA
    time.sleep(2) # Dajmy logom uvicorn/streamlit spokojnie się wyświetlić
    print("\n" + "="*50)
    print("📱 OPCJA: Czy chcesz uruchomić aplikację mobilną (Flutter)?")
    print("Wpisz 'y' i naciśnij Enter, aby odpalić.")
    print("Naciśnij sam Enter, aby pominąć.")
    print("="*50)
    
    choice = input("Wybór [y/N]: ").strip().lower()
    if choice == 'y':
        import json
        print("🔍 Szukam urządzeń Flutter...")
        try:
            # Sprawdzamy listę urządzeń w formacie JSON
            res = subprocess.check_output('flutter devices --machine', shell=True).decode('utf-8')
            devices = json.loads(res)
            
            target_device = "windows" # Domyślny fallback
            found_android = False
            
            for d in devices:
                # Priorytet dla emulatora lub fizycznego Androida
                if d['targetPlatform'].startswith('android'):
                    target_device = d['id']
                    device_type = "Emulator" if d['emulator'] else "Urządzenie"
                    print(f"✅ Wykryto {device_type}: {d['name']} ({target_device})")
                    found_android = True
                    break
            
            if not found_android:
                print("ℹ️ Nie znaleziono emulatora Androida, używam Windows Desktop.")
            
            print(f"🚀 Uruchamiam Flutter na: {target_device}...")
            # Używamy start, żeby Flutter otworzył się w nowym oknie i nie blokował tego skryptu
            flutter_cmd = f'cd frontend_mobile && flutter run -d {target_device}'
            subprocess.Popen(f'start cmd /k "{flutter_cmd}"', shell=True)
            print("✨ Flutter startuje w nowym oknie!")
            
        except Exception as e:
            print(f"⚠️ Błąd detekcji urządzeń: {e}")
            print("Próbuję domyślnego startu...")
            subprocess.Popen('start cmd /k "cd frontend_mobile && flutter run"', shell=True)
    else:
        print("⏭️ Pominięto start Fluttera.")

    print("\nUżywaj 'Ctrl+C' aby zamknąć wszystko naraz.")

    try:
        while True:
            # Sprawdzamy czy procesy żyją
            if backend.poll() is not None:
                print("⚠️ Backend przestał działać!")
                break
            if frontend.poll() is not None:
                print("⚠️ Frontend przestał działać!")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Zatrzymywanie systemów...")
        backend.terminate()
        frontend.terminate()
        print("Gotowe.")
