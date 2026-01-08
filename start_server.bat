@echo off
REM Start CampusShield AI Backend Server
REM Run this from the project root directory

cd /d %~dp0
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please create one first.
    pause
    exit /b 1
)

echo Starting CampusShield AI Backend Server...
echo.
echo Make sure you're in the project root: C:\Dev\CampusShield-AI
echo.
uvicorn Backend.app.main:app --reload --host 0.0.0.0 --port 8000

pause

