@echo off
REM CampusShield AI - Virtual Environment Setup Script for Windows (CMD)
REM This script creates a virtual environment and installs all dependencies

echo ========================================
echo CampusShield AI - Environment Setup
echo ========================================
echo.

REM Check if .venv already exists
if exist .venv (
    echo Virtual environment (.venv) already exists!
    set /p response="Do you want to remove it and create a new one? (y/N): "
    if /i "%response%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q .venv
    ) else (
        echo Using existing virtual environment.
        echo Activating virtual environment...
        call .venv\Scripts\activate.bat
        echo Running dependency check...
        python Backend\check_dependencies.py
        exit /b 0
    )
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv

if errorlevel 1 (
    echo Failed to create virtual environment!
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies from Backend\requirements.txt...
python -m pip install -r Backend\requirements.txt

if errorlevel 1 (
    echo Failed to install dependencies!
    exit /b 1
)

REM Verify installation
echo.
echo Verifying installation...
python Backend\check_dependencies.py

if errorlevel 1 (
    echo.
    echo Warning: Some dependencies may not be installed correctly.
    echo Please check the output above for details.
) else (
    echo.
    echo ========================================
    echo Setup completed successfully!
    echo ========================================
    echo.
    echo To activate the virtual environment in the future, run:
    echo   .venv\Scripts\activate.bat
    echo.
    echo To start the server, run:
    echo   cd Backend
    echo   uvicorn app.main:app --reload
    echo.
)

