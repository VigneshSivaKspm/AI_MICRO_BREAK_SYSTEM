@echo off
REM AI Micro Break System - Quick Start Script for Windows

echo.
echo ============================================
echo AI Micro Break System - Quick Start
echo ============================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Python found. Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/5] Installing dependencies...
pip install -r config\requirements.txt

echo [3/5] Creating logs directory...
if not exist logs mkdir logs

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo To start the application:
echo.
echo Terminal 1 - Start Backend:
echo   cd backend
echo   python app.py
echo.
echo Terminal 2 - Serve Frontend:
echo   cd frontend
echo   python -m http.server 9000
echo.
echo Then open your browser and go to: http://localhost:9000
echo.
echo Press any key to continue...
pause
