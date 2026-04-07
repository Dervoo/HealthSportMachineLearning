---
noteId: "40f348802f5411f1a3b2419e1a333938"
tags: []

---

# 📱 Instrukcja: Wydawanie Wersji Mobilnej (Firebase App Distribution)

Ten dokument opisuje, jak w 2 minuty wysłać nową wersję aplikacji Health-ML na Twój telefon i telefony testerów.

## 🚀 Szybka Aktualizacja (Po zmianach w kodzie)

Jeśli chcesz mieć pewność, że powiadomienie e-mail dotrze do testerów, użyj pełnej procedury resetu:

1.  **Zbuduj aplikację:**
    ```powershell
    flutter build apk --release
    ```

2.  **Wymuś odświeżenie testera i wyślij:**
    ```powershell
    cd frontend_mobile
    firebase appdistribution:testers:remove contact.dervoo@gmail.com --project health-ml-app
    firebase appdistribution:testers:add contact.dervoo@gmail.com --project health-ml-app
    firebase appdistribution:distribute build/app/outputs/flutter-apk/app-release.apk --app 1:450035263910:android:eb5cf1a8debbc929a60767 --testers contact.dervoo@gmail.com --release-notes "OPIS ZMIAN"
    ```

*Wskazówka: Usunięcie i ponowne dodanie testera przed komendą distribute gwarantuje wysłanie nowego powiadomienia e-mail.*

---

## 👥 Dodawanie Nowych Testerów

Jeśli chcesz dodać kogoś nowego, wpisz:
```powershell
firebase appdistribution:testers:add EMAIL_TESTERA --project health-ml-app
```

---

## 🛠️ Rozwiązywanie problemów

1.  **"Firebase not recognized":**
    Upewnij się, że jesteś zalogowany: `firebase login`
2.  **"Flutter not recognized":**
    Sprawdź, czy jesteś w folderze `frontend_mobile`.
3.  **Błąd App ID:**
    Twoje stałe ID aplikacji to: `1:450035263910:android:eb5cf1a8debbc929a60767`
