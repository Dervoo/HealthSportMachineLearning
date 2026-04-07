# 📱 Mobile Release Guide: Firebase App Distribution

**Kompletna instrukcja wydawania wersji testowych aplikacji Health-ML.**

---

## 🚀 Szybka Aktualizacja (Reset & Push)

Jeśli chcesz mieć pewność, że powiadomienie e-mail dotrze do testerów, użyj pełnej procedury resetu:

### 1. Budowa APK
```powershell
# Uruchom w głównym folderze projektu (skrypt wykryje frontend_mobile)
flutter build apk --release
```

### 2. Dystrybucja przez Firebase
Uruchom poniższy zestaw komend w folderze `frontend_mobile`:

```powershell
# 1. Odświeżenie sesji testera
firebase appdistribution:testers:remove contact.dervoo@gmail.com --project health-ml-app
firebase appdistribution:testers:add contact.dervoo@gmail.com --project health-ml-app

# 2. Wysyłka pliku
firebase appdistribution:distribute build/app/outputs/flutter-apk/app-release.apk `
    --app 1:450035263910:android:eb5cf1a8debbc929a60767 `
    --testers contact.dervoo@gmail.com `
    --release-notes "🚀 WERSJA STABILNA: AI Calorie Goals + Workout Weight Field"
```

---

## 👥 Zarządzanie Testerami

### Dodawanie nowych osób:
```powershell
firebase appdistribution:testers:add EMAIL_TESTERA --project health-ml-app
```

---

## 🛠️ Troubleshooting (Najczęstsze Problemy)

| Problem | Rozwiązanie |
| :--- | :--- |
| **"Firebase not recognized"** | Zainstaluj Firebase CLI lub zaloguj się: `firebase login`. |
| **"Flutter not recognized"** | Upewnij się, że jesteś w folderze `frontend_mobile` i masz Flutter w PATH. |
| **Brak maila u testera** | Zastosuj procedurę resetu (Krok 2 powyżej) – usuń i dodaj testera ponownie. |
| **Błąd App ID** | Stałe ID: `1:450035263910:android:eb5cf1a8debbc929a60767`. |

---

*Wskazówka: Każda nowa wersja automatycznie pojawia się w aplikacji Firebase App Tester na telefonie.*
