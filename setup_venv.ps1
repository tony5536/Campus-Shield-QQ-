# CampusShield AI - Virtual Environment Setup Script for Windows
# This script creates a virtual environment and installs all dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CampusShield AI - Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .venv already exists
if (Test-Path ".venv") {
    Write-Host "Virtual environment (.venv) already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to remove it and create a new one? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force .venv
    } else {
        Write-Host "Using existing virtual environment." -ForegroundColor Green
        Write-Host "Activating virtual environment..." -ForegroundColor Cyan
        & .\.venv\Scripts\Activate.ps1
        Write-Host "Running dependency check..." -ForegroundColor Cyan
        python Backend\check_dependencies.py
        exit 0
    }
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv .venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create virtual environment!" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies from Backend\requirements.txt..." -ForegroundColor Cyan
python -m pip install -r Backend\requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Cyan
python Backend\check_dependencies.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Setup completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "To activate the virtual environment in the future, run:" -ForegroundColor Cyan
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "To start the server, run:" -ForegroundColor Cyan
    Write-Host "  cd Backend" -ForegroundColor White
    Write-Host "  uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Warning: Some dependencies may not be installed correctly." -ForegroundColor Yellow
    Write-Host "Please check the output above for details." -ForegroundColor Yellow
}

