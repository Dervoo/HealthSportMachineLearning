@echo off
TITLE Health-ML Auto-Starter
echo ==================================================
echo   🚀 Health-ML: AUTOMATYCZNY START SYSTEMU
echo ==================================================

:: Ustawienie folderu roboczego na ten, w ktorym jest plik .bat
cd /d "%~dp0"

:: 1. Sprawdzenie czy Python istnieje
where py >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] Nie znaleziono launchera 'py'. Sprawdzam 'python'...
    where python >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python nie jest zainstalowany! Pobierz z python.org
        pause
        exit /b
    ) else (
        set PY_CMD=python
    )
) else (
    set PY_CMD=py
)

echo [+] Wykryto: %PY_CMD%

:: 2. Instalacja zaleznosci (tylko brakujacych)
echo [+] Sprawdzam biblioteki...
%PY_CMD% -m pip install -r requirements.txt --quiet

:: 3. Uruchomienie projektu
echo [+] Odpalam run_project.py...
%PY_CMD% run_project.py

echo.
echo [!] Jesli okno zamknelo sie za szybko, sprawdz bledy powyzej.
pause
