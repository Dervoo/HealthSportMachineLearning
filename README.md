# Health & Sport Machine Learning Optimizer 🚀

Dashboard Streamlit do monitorowania postępów sportowych, diety oraz optymalizacji procesów przy użyciu Reinforcement Learning.

## 🌟 Funkcje
*   **Mielarka Sugestii (Baza Produktów)**: Pozwala na wybór produktów z bazy JSON (`data/products.json`). Po wybraniu produktu i podaniu wagi, system automatycznie przelicza kalorie oraz makroskładniki.
*   **Domyślne Posiłki**: W profilu `info.md` system automatycznie dolicza 441 kcal (Milk Product, Soy Protein, Twaróg). Można to wyłączyć w pasku bocznym (checkbox "Pomiń posiłki domyślne").
*   **Dodawanie Ręczne**: Precyzyjne wprowadzanie Kcal i makroskładników dla produktów spoza bazy.
*   **Dzienny Log**: Podgląd produktów wprowadzonych w danym dniu przed zapisem.
*   **Historia i Szczegóły**: Wykresy wagi oraz dokładny wgląd w historyczne dni.
*   **Ewaluaator Ćwiczeń**: Ocena treningu pod kątem Twojego profilu (tylko dla profilu Custom).

## 🛠️ Technologie
*   **Python / Streamlit**
*   **Pandas / JSON**
*   **Git (Conventional Commits)**

## 📋 Instrukcja Obsługi Bazy Produktów
1.  **Dodawanie**: Aby dodać nowy produkt do bazy, edytuj plik `data/products.json` dodając wpis w formacie: `"Nazwa": {"kcal": X, "p": X, "c": X, "f": X}` (wartości na 100g).
2.  **Użycie**: W sekcji "Mielarka Sugestii" wybierz produkt z listy, wpisz wagę w gramach i kliknij "DODAJ (AUTO-CALC)".

## 📋 Instrukcja Obsługi Agenta (Gemini CLI)
Agent operuje zgodnie z zasadami zawartymi w `info.md`. Główne zasady to:
1.  **Conventional Commits**: Każda zmiana musi być commitowana zgodnie ze standardem v1.0.0.
2.  **Pull Requests**: Każdy update musi być wdrażany przez Pull Request.
3.  **Ton i Format**: Senior Developer - chłodny, profesjonalny, techniczny.
4.  **Human Control & Verification**: Każda akcja agenta (szczególnie modyfikacje plików instrukcyjnych, `info.md` czy struktury projektu) **musi być bezwzględnie weryfikowana przez człowieka**. Agent może popełniać błędy w logice nadpisywania plików lub proponować nieoptymalne rozwiązania, dlatego ostateczna kontrola i akceptacja zmian leży po stronie użytkownika.

## 🧠 Machine Learning Engine & AI Insights
System wykorzystuje `ml_engine.py` do analizy Twoich postępów. Aby algorytmy działały poprawnie, musisz rzetelnie uzupełniać dane subiektywne.

### 1. Skala RPE (Rate of Perceived Exertion) - Jak oceniać?
Oceniasz **najcięższą serię** w danym treningu. Bądź uczciwy - oszukiwanie tutaj sprawi, że model błędnie dobierze obciążenie.

| Ocena (1-10) | Opis (Reps In Reserve - RIR) | Interpretacja dla ML |
| :--- | :--- | :--- |
| **10** | **Upadek (0 RIR)** | Nie byłeś w stanie wykonać ani jednego powtórzenia więcej. |
| **9** | **1 RIR** | Zostało siły na dokładnie 1 ruch. |
| **8** | **2 RIR** | Zostało siły na 2 ruchy (optymalne do budowania siły). |
| **7** | **3 RIR** | Trening dynamiczny/szybkościowy. |
| **5-6** | **Rozgrzewka** | Ciężar był za lekki. |
| **1-4** | **Regeneracja** | Aktywny wypoczynek / Cardio. |

### 2. Skala Jakości Snu - Jak oceniać?
Oceniasz sen z nocy **poprzedzającej** wpis.

| Ocena (1-5) | Opis |
| :--- | :--- |
| **5** | **Idealny** - Wstałeś bez budzika, pełna regeneracja, brak wybudzeń. |
| **4** | **Dobry** - Standardowa noc, lekkie zmęczenie rano, ale szybko mija. |
| **3** | **Przeciętny** - Wybudzenia w nocy, trudności ze wstaniem, potrzeba kofeiny. |
| **2** | **Słaby** - Krótki sen (<6h), stres, "zombie mode" rano. |
| **1** | **Tragiczny** - Bezsenność, impreza, choroba. Trening odradzany. |

### 3. Jak działają modele?
*   **Weight Trend Predictor:** Regresja liniowa (Linear Regression) analizuje historię wagi i rysuje linię trendu na 7 dni w przód. Wymaga min. 3 dni pomiarów.
*   **Sleep-Performance Correlation:** Korelacja Pearsona sprawdza, czy Twoje RPE jest wyższe po słabo przespanej nocy. Jeśli korelacja jest silna (< -0.5), system zasugeruje priorytetyzację snu.
*   **Diet Optimizer:** Algorytm zachłanny (Greedy) dobiera produkty z `products.json`, które mają najlepszy stosunek białka do kalorii, aby dobić do celu 180g.

## 🚀 Uruchomienie
```bash
py -m streamlit run dashboard.py
```
