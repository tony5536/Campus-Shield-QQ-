# Start CampusShield AI Backend Server
# Run this from the project root directory

$ErrorActionPreference = "Stop"

Write-Host "Starting CampusShield AI Backend Server..." -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "Backend\app\main.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "   Expected: C:\Dev\CampusShield-AI" -ForegroundColor Yellow
    Write-Host "   Current: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️  Warning: Virtual environment not found at .venv" -ForegroundColor Yellow
    Write-Host "   Continuing anyway..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting server on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Start uvicorn
uvicorn Backend.app.main:app --reload --host 0.0.0.0 --port 8000

