# Development Environment Setup Script for Shine Skincare Backend
# This script sets up the development environment with all necessary dependencies

Write-Host "🚀 Setting up Shine Skincare Backend Development Environment..." -ForegroundColor Green

# Check if Python is installed
Write-Host "📋 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+ first." -ForegroundColor Red
    exit 1
}

# Check if pip is available
Write-Host "📦 Checking pip availability..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found. Please install pip first." -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "📥 Installing Python dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create development configuration file
Write-Host "⚙️ Creating development configuration..." -ForegroundColor Yellow
$devConfig = @"
# Development Environment Configuration
FLASK_ENV=development
FLASK_DEBUG=1
PORT=8000
MODEL_PATH=./models
S3_BUCKET=shine-skincare-models-dev
LOG_LEVEL=DEBUG
"@

$devConfig | Out-File -FilePath ".env.dev" -Encoding UTF8
Write-Host "✅ Development configuration created (.env.dev)" -ForegroundColor Green

# Create models directory if it doesn't exist
Write-Host "📁 Setting up models directory..." -ForegroundColor Yellow
if (!(Test-Path "models")) {
    New-Item -ItemType Directory -Path "models" | Out-Null
    Write-Host "✅ Models directory created" -ForegroundColor Green
} else {
    Write-Host "✅ Models directory already exists" -ForegroundColor Green
}

# Check for model files
Write-Host "🔍 Checking for model files..." -ForegroundColor Yellow
$modelFiles = Get-ChildItem "models" -Filter "*.h5" -ErrorAction SilentlyContinue
if ($modelFiles.Count -gt 0) {
    Write-Host "✅ Found $($modelFiles.Count) model file(s):" -ForegroundColor Green
    foreach ($file in $modelFiles) {
        Write-Host "   - $($file.Name) ($([math]::Round($file.Length / 1MB, 2)) MB)" -ForegroundColor Cyan
    }
} else {
    Write-Host "⚠️ No model files found in models directory" -ForegroundColor Yellow
    Write-Host "   You may need to download models or copy them from production" -ForegroundColor Yellow
}

# Create development startup script
Write-Host "📝 Creating development startup script..." -ForegroundColor Yellow
$startupScript = @"
# Development Startup Script
Write-Host "Starting Shine Skincare Backend in development mode..." -ForegroundColor Green
Write-Host "Environment: Development" -ForegroundColor Cyan
Write-Host "Port: 8000" -ForegroundColor Cyan
Write-Host "Debug: Enabled" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Set development environment variables
`$env:FLASK_ENV = "development"
`$env:FLASK_DEBUG = "1"
`$env:PORT = "8000"

# Start the application
python wsgi.py
"@

$startupScript | Out-File -FilePath "start-dev.ps1" -Encoding UTF8
Write-Host "✅ Development startup script created (start-dev.ps1)" -ForegroundColor Green

# Create health check script
Write-Host "🔍 Creating health check script..." -ForegroundColor Yellow
$healthScript = @"
# Health Check Script for Development
Write-Host "Checking backend health..." -ForegroundColor Yellow

try {
    # Check if server is running
    `$response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Health endpoint: OK" -ForegroundColor Green
    
    # Check API health
    `$apiHealth = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method GET -TimeoutSec 5
    Write-Host "✅ API Health: `$(`$apiHealth.status)" -ForegroundColor Green
    Write-Host "   Models loaded: `$(`$apiHealth.models_loaded)" -ForegroundColor Cyan
    
    # Check model status
    `$modelStatus = Invoke-RestMethod -Uri "http://localhost:8000/api/v5/skin/model-status" -Method GET -TimeoutSec 5
    Write-Host "✅ Model Status: `$(`$modelStatus.status)" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Health check failed: `$(`$_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure the backend is running on port 8000" -ForegroundColor Yellow
}
"@

$healthScript | Out-File -FilePath "check-health.ps1" -Encoding UTF8
Write-Host "✅ Health check script created (check-health.ps1)" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Development environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: .\start-dev.ps1" -ForegroundColor White
Write-Host "2. In another terminal, test with: .\check-health.ps1" -ForegroundColor White
Write-Host "3. Access your API at: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
