---
noteId: "70d85dd01dff11f1a62ac95b651edd41"
tags: []

---

# Health-ML Optimizer Dashboard 🚀

System zarządzania sylwetką, dietą i treningiem oparty na analityce i zalążkach Machine Learning.

## 🛠 Kluczowe Funkcje (Wdrożone dzisiaj)

### 1. Inteligentna "Mielarka Sugestii" (Active ML Logger)
- **Dynamiczne Skalowanie:** System rozpoznaje gramaturę w zapytaniu (np. "300g kurczak") i automatycznie przelicza makroskładniki.
- **Detekcja Produktów i Sklepów:** Baza wiedzy o produktach z popularnych sklepów (Biedronka, Lidl, Żabka) z uwzględnieniem ekonomii wyboru.
- **Interaktywne Logowanie:** Możliwość edycji sugerowanych wartości przed dodaniem ich do dziennego bilansu.

### 2. Zaawansowane Śledzenie Nutrie-Analityczne
- **Pełne Makro (B, W, T):** Śledzenie nie tylko kalorii, ale precyzyjnego rozkładu składników odżywczych.
- **Super-Ingredients Detection:** System wykrywa składniki pro-zdrowotne (imbir, kurkuma, cynamon, ostropest, koperek) i wyświetla ich bonusy metaboliczne/regeneracyjne.
- **Batch Logging:** Możliwość dodawania wielu posiłków w ciągu dnia przed końcowym zapisem.

### 3. System Trwałej Pamięci (Persistence Layer)
- **Lokalna Baza CSV:** Wszystkie dane (waga, woda, kcal, treningi, składniki) zapisywane są w pliku `progress.csv`.
- **Analityka Trendów:** Automatyczne generowanie wykresów wagi i historii postępów bezpośrednio w dashboardzie.
- **Prywatność:** Wszystkie obliczenia i dane pozostają na localhost (`127.0.0.1`).

### 4. Inteligentny Plan Treningowy
- **Logika Bezpieczeństwa:** System blokuje możliwość biegania (Cardio) w dni treningu nóg (Dzień C) oraz dzień po nim, chroniąc regenerację.
- **Check-lista Dni A/B/C:** Interaktywne śledzenie serii do upadku zgodnie z wytycznymi `info.md`.
- **PRO TIPS:** Dynamiczne porady dotyczące techniki (Rest-Pause, Drop-sety) wyświetlane w zależności od wybranego treningu.

### 5. Nowoczesny High-Visibility UI
- **Wysoki Kontrast:** Etykiety w kolorze jaskrawego błękitu (`#00d4ff`) i białe wartości dla maksymalnej czytelności podczas treningu.
- **Centrum Dowodzenia:** Pasek metryk: **Energia | Białko | Waga | Hydracja**.

## 🚀 Jak uruchomić?

1. Upewnij się, że masz zainstalowanego Pythona 3.13+.
2. Zainstaluj wymagane biblioteki:
   ```bash
   py -m pip install streamlit pandas matplotlib
   ```
3. Uruchom aplikację:
   ```bash
   py -m streamlit run dashboard.py
   ```

---
*Dane bazują na Twoim indywidualnym profilu z pliku `info.md` (Cel: 1900 kcal, redukcja tkanki tłuszczowej i luźnej skóry).*
