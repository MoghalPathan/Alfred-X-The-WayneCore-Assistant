@echo off
title AlfredX - Waynecore Assistant Launcher
color 0B
cd /d "%~dp0"

echo ========================================================
echo   AlfredX: The Waynecore Assistant v2.1
echo   "I shall attend to it, Master."
echo ========================================================
echo.

set "NGROK_EXE=%LOCALAPPDATA%\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe"
if exist "%NGROK_EXE%" goto :CHECK_NGROK

where ngrok >nul 2>nul
if errorlevel 1 goto :RUN_APP
set "NGROK_EXE=ngrok"

:CHECK_NGROK
tasklist /fi "imagename eq ngrok.exe" 2>nul | find /i "ngrok.exe" >nul
if not errorlevel 1 goto :NGROK_RUNNING

echo [*] Starting mobile companion tunnel via Ngrok...
start "AlfredX Mobile Tunnel" /min "%NGROK_EXE%" http 127.0.0.1:8000
ping -n 3 127.0.0.1 >nul
goto :RUN_APP

:NGROK_RUNNING
echo [OK] Ngrok tunnel is already running.

:RUN_APP
if exist "venv\Scripts\python.exe" goto :RUN_VENV
if exist "AlfredX.exe" goto :RUN_EXE
if exist "dist\AlfredX\AlfredX.exe" goto :RUN_DIST_EXE

echo [!] Virtual environment not found in venv\ and AlfredX.exe not found.
echo Please run:
echo   python -m venv venv
echo   venv\Scripts\pip install -r requirements.txt
pause
exit /b 1

:RUN_VENV
echo [*] Launching AlfredX Desktop HUD...
echo.
venv\Scripts\python.exe main.py
if errorlevel 1 goto :ERR_EXIT
goto :END

:RUN_EXE
echo [*] Launching AlfredX.exe...
echo.
start "" "AlfredX.exe"
goto :END

:RUN_DIST_EXE
echo [*] Launching dist\AlfredX\AlfredX.exe...
echo.
start "" "dist\AlfredX\AlfredX.exe"
goto :END

:ERR_EXIT
echo.
echo [!] AlfredX exited with an error.
pause
exit /b 1

:END
echo.
echo AlfredX has shut down.
exit /b 0
