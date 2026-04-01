---
noteId: "28d9d7702dbd11f1ae54db68b00e2af6"
tags: []

---

# 📋 Instrukcja: Czyste Code Review na GitHub

## 🚫 Problem: Wstrzykiwanie metadanych
Podczas dodawania komentarzy przez `gh CLI` przy użyciu plików tymczasowych (`--body-file`), systemy automatyzacji mogą wstrzykiwać niepożądane metadane, takie jak:
- `noteId: "..."`
- `tags: []`

Dla dewelopera-człowieka jest to sygnał "wygenerowano przez AI", co narusza zasady profesjonalnego Code Review.

## ✅ Rozwiązanie: Raw API Injection
Aby zapewnić 100% czystości komentarzy, należy używać bezpośredniego wywołania **GitHub REST API**. Ta metoda omija procesory tekstu CLI i przesyła treść jako surowy ciąg znaków.

### Komenda wzorcowa:
```powershell
gh api repos/:owner/:repo/issues/:number/comments -f body="TWOJA TREŚĆ PL / EN"
```

### Zasady konstrukcji komentarza:
1.  **Brak plików tymczasowych**: Nie używaj `write_file` do tworzenia treści komentarza, jeśli zamierzasz go wysłać przez `--body-file`.
2.  **Surowy String**: Przekazuj treść bezpośrednio w komendzie `gh api` przy użyciu flagi `-f body`.
3.  **Bilingwalność**: Zawsze zachowuj format PL (góra) / EN (dół).
4.  **Zero metadanych**: Przed wysłaniem upewnij się, że w stringu nie ma żadnych znaczników systemowych.

## 🛠️ Procedura naprawcza (jeśli błąd wystąpi):
1.  Pobierz ID wszystkich komentarzy:
    ```powershell
    gh api repos/:owner/:repo/issues/:number/comments --jq ".[] | .id"
    ```
2.  Usuń wadliwe komentarze:
    ```powershell
    gh api -X DELETE "repos/:owner/:repo/issues/comments/:comment_id"
    ```
3.  Wyślij ponownie używając metody **Raw API Injection**.
