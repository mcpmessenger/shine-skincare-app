# Simple Backend Startup Script
# This script starts the Flask backend reliably

Write-Host "Starting Shine Skincare Backend..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Step 1: Clean up any existing processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
try {
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 3
    Write-Host "Existing processes cleaned up" -ForegroundColor Green
} catch {
    Write-Host "No existing processes to clean" -ForegroundColor Blue
}

# Step 2: Check Python and dependencies
Write-Host "Checking Python environment..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
    
    # Check if we're in the right directory
    if (Test-Path "enhanced_app.py") {
        Write-Host "Found enhanced_app.py" -ForegroundColor Green
    } else {
        Write-Host "enhanced_app.py not found in current directory" -ForegroundColor Red
        Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "Python not found or not accessible" -ForegroundColor Red
    exit 1
}

# Step 3: Check required packages
Write-Host "Checking required packages..." -ForegroundColor Yellow
$requiredPackages = @("flask", "opencv-python", "numpy", "pillow")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        python -c "import $package" 2>$null
        Write-Host "OK: $package" -ForegroundColor Green
    } catch {
        Write-Host "Missing: $package" -ForegroundColor Red
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "Warning: Missing packages: $($missingPackages -join ', ')" -ForegroundColor Yellow
    Write-Host "Run: pip install $($missingPackages -join ' ')" -ForegroundColor Yellow
    Write-Host "Continuing anyway..." -ForegroundColor Yellow
}

# Step 4: Set environment variables
Write-Host "Setting environment variables..." -ForegroundColor Yellow
$env:FLASK_DEBUG = "false"
$env:PORT = "5001"
Write-Host "Environment configured" -ForegroundColor Green

# Step 5: Start the backend
Write-Host "Starting Flask backend..." -ForegroundColor Green
Write-Host "Port: 5001" -ForegroundColor Cyan
Write-Host "Debug: false" -ForegroundColor Cyan
Write-Host "Host: 0.0.0.0" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Green

try {
    # Start the Flask app
    python enhanced_app.py
    
} catch {
    Write-Host "Failed to start backend: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Check if port 5001 is already in use" -ForegroundColor White
    Write-Host "2. Ensure all dependencies are installed" -ForegroundColor White
    Write-Host "3. Check the enhanced_app.py file for syntax errors" -ForegroundColor White
    Write-Host "4. Try running: python -c 'import enhanced_app'" -ForegroundColor White
    exit 1
}

Write-Host "Backend started successfully!" -ForegroundColor Green
Write-Host "Access the API at: http://localhost:5001" -ForegroundColor Cyan
Write-Host "Health check: http://localhost:5001/api/health" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow 