# Health & Sport Machine Learning Optimizer 🚀

Dashboard Streamlit do monitorowania postępów sportowych, diety oraz optymalizacji procesów przy użyciu zaawansowanych modeli matematycznych i ML.

## 📱 System Architecture

Projekt ewoluował w ekosystem **Web + Mobile + API**:

1.  **Web Dashboard (Streamlit)**: Zaawansowane centrum dowodzenia z pełną analityką ML i optymalizacją diety (`dashboard.py`).
2.  **Backend API (FastAPI)**: Produkcyjne API obsługujące autoryzację, synchronizację danych i logikę ML dla aplikacji mobilnej (`backend/main.py`).
3.  **Mobile App (Flutter)**: Nowoczesna aplikacja na systemy iOS/Android z logowaniem i szybkim podglądem postępów (`frontend_mobile/`).

---

## 🚀 Uruchomienie

### 1. Web Dashboard (Analityka ML)
Wymagane biblioteki: `streamlit`, `pandas`, `scipy`, `scikit-learn`, `prophet`.
```powershell
# Rekomendowana metoda na Windows
py -m pip install -r requirements.txt
py -m streamlit run dashboard.py
```

### 2. Backend API (Dla Mobile)
Umożliwia synchronizację danych i logowanie użytkowników.
```powershell
# Uruchomienie serwera na porcie 8000
py backend/main.py
```

### 3. Aplikacja Mobilna (Flutter)
Wymaga zainstalowanego SDK Flutter.
```powershell
cd frontend_mobile
flutter pub get
# Upewnij się, że Backend API działa przed uruchomieniem aplikacji
flutter run
```

---

## 🌟 Funkcje
*   **AI SMART GOAL**: Automatyczne wyliczanie zapotrzebowania kcal i białka (Mifflin-St Jeor).
*   **Diet Optimizer (LP)**: Precyzyjne dobieranie posiłków przy użyciu programowania liniowego (`scipy.optimize`).
*   **Weight Trend (Prophet)**: Zaawansowane prognozowanie wagi i wykrywanie zastojów (**Plateau Detection**).
*   **Training Analytics (Volume)**: Automatyczne parsowanie logów treningowych i obliczanie tonażu (objętości).
*   **AI Recommendation**: Sugestie treningowe na bazie regeneracji i korelacji sen-siła.
*   **Mielarka Sugestii**: Integracja z API Edamam i lokalną bazą produktów.

## 🧠 Dokumentacja Modeli i Wzorów

### 1. Obliczanie Zapotrzebowania (AI SMART GOAL)
System wykorzystuje wzór **Mifflin-St Jeor** oraz współczynnik **PAL**.
*   **Nowość ML:** System automatycznie wylicza cel nawodnienia: $\text{waga} \times 0.033 + \text{bonus aktywności}$.

### 2. Optymalizacja Diety (Linear Programming)
Wykorzystuje solver `highs` z biblioteki `scipy.optimize.linprog` do minimalizacji nadmiaru kcal przy zachowaniu minimum białkowego.

### 3. Prognozowanie Trendu i Plateau (Facebook Prophet)
Model analizuje szeregi czasowe, wykrywając sezonowość i punkty krytyczne wagi. Sugeruje **Refeed Day**, gdy zmiana wagi < 0.2kg/14 dni.

### 4. Analiza Objętości i Korelacji (Workout ML)
*   **Parser:** Wykorzystuje wyrażenia regularne (Regex) do wyciągania tonażu z tekstu.
*   **Korelacja Pearsona:** Bada statystyczny wpływ jakości snu na łączną objętość sesji.

### 5. Multi-User Vault & API Analytics (New!)
*   **Baza SQL (SQLite)**: Przejście z prostych plików CSV na relacyjną bazę danych `health_vault.db` dla wielu użytkowników.
*   **API Connector**: Integracja z zewnętrznym API do 'mielenia' danych i pobierania rynkowych benchmarków.
*   **Cross-User Analytics**: Moduł `AnalyticsEngine` analizujący korelacje między snem, celem a objętością treningową w celu optymalizacji parametrów modelu.
*   **Refine ML**: System automatycznej korekty `target_kcal` na podstawie współczynnika optymalizacji z API.

### 6. Skala RPE (Rate of Perceived Exertion)
Jak wybierać trudność treningu?
*   **10**: Max wysiłek, brak możliwości wykonania kolejnego powtórzenia.
*   **9**: Bardzo ciężko, 1 powtórzenie w zapasie (RIR 1).
*   **8**: Ciężko, 2 powtórzenia w zapasie (RIR 2).
*   **7**: Solidny trening, kontrolowany ciężar, 3-4 powtórzenia w zapasie.
*   **1-5**: Rozgrzewka, cardio o niskiej intensywności lub regeneracja.

---

## 🛠️ Poprawki User-Centric (Human-Driven Improvements)
Dzisiejsze kluczowe zmiany wprowadzone na prośbę użytkownika:

*   **Multi-User Vault**: Nowy tryb "Vault" w sidebarze pozwala na tworzenie wielu profili i bezpieczne przechowywanie ich danych w bazie SQL.
*   **Kaggle Population Analytics**: Integracja 1000 rekordów syntetycznych (docelowo MyFitnessPal) do porównywania Twoich wyników z globalnymi trendami.
*   **Dynamic Cardio Forms**: Inteligentny formularz, który dla "Biegania" pyta o spalone kcal zamiast serii, a dla "Dnia Wolnego" oferuje szybki zapis "Rest Day".
*   **ML Hybrid Optimization**: Możliwość wyboru źródła autokorekty parametrów: API (lokalne) lub Kaggle (populacyjne).
*   <u>**Persistence Settings**</u>: Wszystkie dane w panelu AI (wiek, wzrost, cele) są teraz zapisywane w lokalnym pliku JSON.
*   <u>**Fitatu UI Order**</u>: Przebudowano formularz dodawania makroskładników (Białko -> Tłuszcz -> Węgle) dla płynnej obsługi klawiszem `Tab`.
*   <u>**Mixed Reps Logging**</u>: Możliwość logowania serii o różnej ilości powtórzeń (np. `12,10,8`) zamiast stałych wartości.
*   <u>**Load Last Workout**</u>: Funkcja "Wczytaj ostatni trening" – system przeszukuje historię i jednym kliknięciem kopiuje ostatnią udaną sesję do obecnego logu.
*   <u>**Smart Backpack Weights**</u>: System rozpoznaje bazowe obciążenia (np. plecak 15kg) i pozwala na dodawanie do nich wartości "Extra".
*   <u>**Retro-Logging**</u>: Możliwość wyboru daty wpisu (dzisiaj/wczoraj/dowolna data), co pozwala na uzupełnianie danych z opóźnieniem.
*   <u>**Advanced Hydration**</u>: Dodanie logowania ziół (liczone jako 90% wody) oraz wody z posiłków (zupy, koktajle).
*   <u>**UI Visibility Fix**</u>: Całkowita poprawka stylów CSS – białe czcionki na ciemnych kafelkach dla maksymalnej czytelności.
