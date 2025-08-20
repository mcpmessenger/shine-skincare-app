# HARE Run 4 Local Deployment Startup Script
# This script starts the HARE Run 4 backend locally for testing

Write-Host "🚀 Starting HARE Run 4 Local Deployment..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if required files exist
$backendFile = "application_hare_run_v4.py"
if (Test-Path $backendFile) {
    Write-Host "✅ Backend file found: $backendFile" -ForegroundColor Green
} else {
    Write-Host "❌ Backend file not found: $backendFile" -ForegroundColor Red
    exit 1
}

# Install requirements if needed
Write-Host "📦 Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Start the backend
Write-Host ""
Write-Host "🚀 Starting HARE Run 4 backend on localhost:8000..." -ForegroundColor Green
Write-Host "📱 Frontend should be running on localhost:3000" -ForegroundColor Cyan
Write-Host "🔗 API endpoints available at http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python application_hare_run_v4.py
