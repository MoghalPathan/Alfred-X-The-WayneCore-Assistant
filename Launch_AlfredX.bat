@echo off
title AlfredX — Waynecore Assistant Launcher
color 0B
cd /d "%~dp0"

echo ========================================================
echo   AlfredX: The Waynecore Assistant v2.1
echo   "I shall attend to it, Master."
echo ========================================================
echo.

:: Check if Python venv exists
if not exist "venv\Scripts\python.exe" (
    echo [!] Virtual environment not found in venv\
    echo Please create it first: python -m venv venv ^&^& venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

:: Check for ngrok to optionally launch mobile tunnel
set "NGROK_EXE=%LOCALAPPDATA%\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe"
if exist "%NGROK_EXE%" (
    echo [*] Starting mobile companion tunnel via Ngrok...
    start "AlfredX Mobile Tunnel" /min "%NGROK_EXE%" http 127.0.0.1:8000
    echo [OK] Mobile tunnel started in background.
) else (
    where ngrok >nul 2>nul
    if %errorlevel% equ 0 (
        echo [*] Starting mobile companion tunnel via Ngrok...
        start "AlfredX Mobile Tunnel" /min ngrok http 127.0.0.1:8000
        echo [OK] Mobile tunnel started in background.
    )
)

echo [*] Launching AlfredX Desktop HUD...
echo.
venv\Scripts\python.exe main.py

echo.
echo AlfredX has shut down.
exit /b 0
