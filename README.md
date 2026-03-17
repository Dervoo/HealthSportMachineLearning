# Health & Sport Machine Learning Optimizer 🚀

Dashboard Streamlit do monitorowania postępów sportowych, diety oraz optymalizacji procesów przy użyciu zaawansowanych modeli matematycznych i ML.

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

---

## 🛠️ Poprawki User-Centric (Human-Driven Improvements)
Dzisiejsze kluczowe zmiany wprowadzone na prośbę użytkownika:

*   <u>**Persistence Settings**</u>: Wszystkie dane w panelu AI (wiek, wzrost, cele) są teraz zapisywane w lokalnym pliku JSON – koniec z wpisywaniem danych po każdym restarcie!
*   <u>**Fitatu UI Order**</u>: Przebudowano formularz dodawania makroskładników (Białko -> Tłuszcz -> Węgle) dla płynnej obsługi klawiszem `Tab`.
*   <u>**Mixed Reps Logging**</u>: Możliwość logowania serii o różnej ilości powtórzeń (np. `12,10,8`) zamiast stałych wartości.
*   <u>**Load Last Workout**</u>: Funkcja "Wczytaj ostatni trening" – system przeszukuje historię i jednym kliknięciem kopiuje ostatnią udaną sesję do obecnego logu.
*   <u>**Smart Backpack Weights**</u>: System rozpoznaje bazowe obciążenia (np. plecak 15kg) i pozwala na dodawanie do nich wartości "Extra".
*   <u>**Retro-Logging**</u>: Możliwość wyboru daty wpisu (dzisiaj/wczoraj/dowolna data), co pozwala na uzupełnianie danych z opóźnieniem.
*   <u>**Advanced Hydration**</u>: Dodanie logowania ziół (liczone jako 90% wody) oraz wody z posiłków (zupy, koktajle).
*   <u>**UI Visibility Fix**</u>: Całkowita poprawka stylów CSS – białe czcionki na ciemnych kafelkach dla maksymalnej czytelności.

## 🚀 Uruchomienie
Wymagane biblioteki: `streamlit`, `pandas`, `scipy`, `scikit-learn`, `prophet`.

```bash
py -m pip install streamlit pandas scipy scikit-learn prophet
py -m streamlit run dashboard.py
```
