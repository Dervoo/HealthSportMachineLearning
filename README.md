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

## 🚀 Uruchomienie
```bash
py -m streamlit run dashboard.py
```
