@echo off
setlocal
cd /d "%~dp0"
title HVAC Design Studio

if not exist ".venv\Scripts\streamlit.exe" (
    echo.
    echo The project virtual environment was not found.
    echo Create it from this folder with:
    echo.
    echo   py -m venv .venv
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo Starting the HVAC Design Studio...
echo The browser will open at http://localhost:8501
echo Close this window or press Ctrl+C to stop the server.
echo.

".venv\Scripts\streamlit.exe" run main.py

echo.
echo The HVAC Design Studio server has stopped.
pause
