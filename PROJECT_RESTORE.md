---
noteId: "d91b3fd0243e11f1b30b89b95243d2ca"
tags: []

---

# 🚀 Health-ML Optimizer: Punkt Przywracania Systemu

Ten plik zawiera wszystkie kluczowe informacje o stanie projektu i instrukcje "po restarcie".

## 1. Stan Projektu (Gdzie skończyliśmy)
- **Backend (FastAPI)**: Gotowy pod adres `http://localhost:8000`. Obsługuje JWT, rejestrację, postępy i wysyłanie zdjęć (`/upload-photo/`).
- **Web/PWA (Streamlit)**: Gotowy pod adres `http://localhost:8501`. Dodano meta-tagi PWA i Service Worker (można instalować na telefonie).
- **Mobile (Flutter)**: Stworzono fundament w `frontend_mobile/lib/main.dart` (Logowanie + Dashboard).

## 2. Jak uruchomić system po restarcie?
Otwórz terminal w głównym folderze projektu i wpisz:
```powershell
py run_project.py
```
(Ten skrypt automatycznie odpali Backend i Dashboard naraz).

## 3. Naprawa FLUTTERA (Zrób to zaraz po restarcie!)
Jeśli `flutter doctor` dalej nie działa, wykonaj te 3 kroki:

**KROK A: Sprawdzenie ścieżki**
Upewnij się, że pliki są tutaj: `C:\src\flutter\bin\flutter.bat`.

**KROK B: Ręczne dodanie do Windows (100% pewności)**
1. Wyszukaj w Windows: **"Zmienne środowiskowe"** -> "Edytuj zmienne środowiskowe dla Twojego konta".
2. W górnej tabelce edytuj zmienną **`Path`**.
3. Dodaj nową linię: `C:\src\flutter\bin`.
4. Kliknij OK, OK, OK.

**KROK C: Test w nowym terminalu**
Wpisz:
```powershell
flutter doctor
```

## 4. Inicjalizacja Aplikacji Mobilnej (Gdy Flutter już działa)
Gdy `flutter doctor` przejdzie pomyślnie, wykonaj te komendy, aby stworzyć brakujące pliki projektu:
```powershell
cd frontend_mobile
flutter create .
flutter run
```

## 5. Kluczowe Endpointy API dla Twojej Apki:
- `POST /auth/register` - Rejestracja użytkownika.
- `POST /auth/token` - Logowanie (zwraca token JWT).
- `GET /ml/insights` - Twoje analizy AI (trend, plateau).
- `POST /upload-photo/` - Wysyłanie zdjęć posiłków.

---
**Data zapisu:** 20 marca 2026
**Autor:** Twoje AI (Gemini CLI)
