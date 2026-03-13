# Health & Sport Machine Learning Optimizer 🚀

Dashboard Streamlit do monitorowania postępów sportowych, diety oraz optymalizacji procesów przy użyciu Reinforcement Learning.

## 🌟 Funkcje
*   **Mielarka Sugestii**: Analiza produktów spożywczych.
*   **Dodawanie Ręczne**: Precyzyjne wprowadzanie Kcal i makroskładników.
*   **Dzienny Log**: Podgląd produktów wprowadzonych w danym dniu przed zapisem.
*   **Historia i Szczegóły**: Wykresy wagi oraz dokładny wgląd w historyczne dni.
*   **Ewaluaator Ćwiczeń**: Ocena treningu pod kątem Twojego profilu (tylko dla profilu Custom).

## 🛠️ Technologie
*   **Python / Streamlit**
*   **Pandas**
*   **Git (Conventional Commits)**

## 📋 Instrukcja Obsługi Agenta (Gemini CLI)
Agent operuje zgodnie z zasadami zawartymi w `info.md`. Główne zasady to:
1.  **Conventional Commits**: Każda zmiana musi być commitowana zgodnie ze standardem v1.0.0.
2.  **Pull Requests**: Każdy update musi być wdrażany przez Pull Request.
3.  **Ton i Format**: Senior Developer - chłodny, profesjonalny, techniczny.
4.  **Human Control & Verification**: Każda akcja agenta (szczególnie modyfikacje plików instrukcyjnych, `info.md` czy struktury projektu) **musi być bezwzględnie weryfikowana przez człowieka**. Agent może popełniać błędy w logice nadpisywania plików lub proponować nieoptymalne rozwiązania, dlatego ostateczna kontrola i akceptacja zmian leży po stronie użytkownika.

## 🚀 Uruchomienie
```bash
streamlit run dashboard.py
```
