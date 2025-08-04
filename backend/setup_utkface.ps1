#!/usr/bin/env pwsh

# UTKFace Integration Setup Script
Write-Host "🧠 UTKFace Integration Setup for Shine Skincare App" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ and try again." -ForegroundColor Red
    exit 1
}

# Check if required packages are installed
Write-Host "📦 Checking required packages..." -ForegroundColor Yellow

$requiredPackages = @("tensorflow", "opencv-python", "pillow", "pandas", "numpy", "scipy")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        python -c "import $package" 2>$null
        Write-Host "  ✅ $package" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $package" -ForegroundColor Red
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "📦 Installing missing packages..." -ForegroundColor Yellow
    foreach ($package in $missingPackages) {
        Write-Host "  Installing $package..." -ForegroundColor Yellow
        pip install $package
    }
}

# Create data directory structure
$dataDir = "data/utkface"
$rawImagesDir = "$dataDir/raw_images"

Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
New-Item -ItemType Directory -Force -Path $rawImagesDir | Out-Null

# Check if dataset exists
if (-not (Test-Path "$rawImagesDir/*.jpg")) {
    Write-Host "❌ UTKFace dataset not found in $rawImagesDir" -ForegroundColor Red
    Write-Host "Please download the dataset manually:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://susanqq.github.io/UTKFace/" -ForegroundColor Cyan
    Write-Host "  2. Download UTKFace.tar.gz" -ForegroundColor Cyan
    Write-Host "  3. Extract to: $rawImagesDir" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Dataset found in $rawImagesDir" -ForegroundColor Green

# Run UTKFace integration setup
Write-Host "🧠 Setting up UTKFace integration..." -ForegroundColor Yellow

try {
    python setup_utkface_setup.py
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "✅ UTKFace integration setup completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ UTKFace integration setup failed" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "❌ Error during setup: $_" -ForegroundColor Red
    exit 1
}

# Test the integration
Write-Host "🧪 Testing UTKFace integration..." -ForegroundColor Yellow

try {
    python setup_utkface_test.py
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "✅ UTKFace integration test passed!" -ForegroundColor Green
    } else {
        Write-Host "❌ UTKFace integration test failed" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "❌ Error during testing: $_" -ForegroundColor Red
    exit 1
}

# Create a simple summary
Write-Host "📊 Creating setup summary..." -ForegroundColor Yellow

$summary = "UTKFace Integration Setup Complete`n"
$summary += "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
$summary += "Dataset Location: $rawImagesDir`n"
$summary += "API Endpoints:`n"
$summary += "  - GET /api/v3/utkface/status`n"
$summary += "  - POST /api/v3/skin/analyze-demographic`n"
$summary += "`nNext steps:`n"
$summary += "1. Start the backend: python enhanced_app.py`n"
$summary += "2. Test the endpoints using the provided examples`n"

$summary | Out-File -FilePath "$dataDir/setup_summary.txt" -Encoding UTF8
Write-Host "✅ Setup summary saved to: $dataDir/setup_summary.txt" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 UTKFace Integration Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start the backend: python enhanced_app.py" -ForegroundColor Cyan
Write-Host "2. Test the endpoints:" -ForegroundColor Cyan
Write-Host "   - GET /api/v3/utkface/status" -ForegroundColor Cyan
Write-Host "   - POST /api/v3/skin/analyze-demographic" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more information, see: $dataDir/setup_summary.txt" -ForegroundColor Cyan 