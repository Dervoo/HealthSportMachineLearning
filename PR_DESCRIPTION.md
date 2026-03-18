---
noteId: "94b1f56021f911f1b07dcb892cc276f3"
tags: []

---

# PR: Advanced ML Integration & Human-Centric UX Overhaul 🚀

## 📝 Summary
Ten Pull Request przekształca prosty dashboard w zaawansowane narzędzie analityczne typu **Health-Intelligence**. Zmiany obejmują wdrożenie czterech nowych modeli matematycznych/ML oraz całkowitą przebudowę interfejsu użytkownika (UX) pod kątem wydajności wprowadzania danych (tzw. "Fitatu-speed flow").

---

## 🧠 Machine Learning & Data Science (The "Engine")

### 1. Diet Optimization (Linear Programming)
Zastąpiono algorytm zachłanny (Greedy) modelem **Programowania Liniowego** przy użyciu `scipy.optimize.linprog`. 
*   **Solver:** `highs`.
*   **Logika:** Minimalizacja nadmiaru kalorii przy twardym ograniczeniu osiągnięcia celu białkowego. System precyzyjnie wylicza wagę produktów (np. 143g), aby idealnie domknąć makro.

### 2. Time-Series Forecasting (Facebook Prophet)
Wdrożono bibliotekę `prophet` do analizy trendów wagi.
*   **Funkcja:** Model analizuje sezonowość tygodniową i wykrywa punkty zmiany trendu.
*   **Plateau Detection:** Jeśli prognozowana zmiana wagi na 14 dni wynosi < 0.2 kg, system automatycznie generuje alert o zastoju i sugeruje **Refeed Day**.

### 3. Workout Volume Analytics (Regex Parsing)
Zaimplementowano autorski parser danych treningowych.
*   **Technologia:** Wyrażenia regularne (Regex) wyciągają dane z nieustrukturyzowanego tekstu (np. `Pompki(3x15.0kg x 12,10,8)`).
*   **Wynik:** Obliczanie całkowitego tonażu sesji (kg) i wizualizacja postępów na wykresie liniowym.

### 4. Correlation & Recovery Model
*   **Pearson Correlation:** Statystyczna analiza wpływu jakości snu na objętość treningową.
*   **Activity Recommender:** Heurystyczny system klasyfikacji formy (HEAVY/DELOAD/RECOVERY) na bazie RPE z ostatnich 3 sesji i jakości snu.

---

## 🛠️ Human-Driven Improvements (UX/UI)

*   **Persistence (ai_settings.json):** Wprowadzono trwały zapis parametrów fizycznych. Aplikacja pamięta dane po restarcie.
*   **Fitatu Order & Tab-Flow:** Zmieniono kolejność makroskładników na **Białko -> Tłuszcz -> Węgle**. Formularz obsługuje `Enter` do zapisu i płynny `Tab` bez przeładowywania strony.
*   **Mixed Reps Support:** Umożliwiono logowanie serii o różnej długości (np. `12,10,10,8`).
*   **Training Template Loading:** Funkcja **"Wczytaj ostatni trening"**, która odtwarza poprzednią sesję.
*   **Smart Weights Logic:** System rozpoznaje obciążenie bazowe sprzętu (np. plecak 15kg).
*   **Retro-Logging:** Kalendarz pozwalający na wybór daty wpisu.
*   **UI Visibility Fix:** Biała czcionka na ciemnym tle (`#1e2130`) z błękitnym obramowaniem.

---

## 🔍 Code Review / Technical Highlights
*   **Anti-Data-Loss:** Przeniesiono wprowadzanie danych treningowych do `st.form`.
*   **Dynamic Data Reload:** Dodano metodę `reload_data()` do `MLEngine`.
*   **Advanced Hydration Model:** Nowy wzór na wodę uwzględniający ziółka (90%) oraz wodę z posiłków.

---

## 🚀 Libraries Added
`prophet`, `scipy`, `scikit-learn`