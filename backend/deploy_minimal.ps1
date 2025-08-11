# Shine Skincare App - Minimal Requirements Deployment Script (PowerShell)
# Updated: 2025-08-10 - Deploy minimal ML capabilities for stability

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "SHINE SKINCARE APP - MINIMAL REQUIREMENTS DEPLOYMENT" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "Instance: t3.large (8GB RAM, 2 vCPU)" -ForegroundColor Yellow
Write-Host "Goal: Deploy stable minimal ML capabilities first" -ForegroundColor Yellow
Write-Host "Strategy: Build foundation, then gradually add advanced features" -ForegroundColor Yellow
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "application_minimal.py")) {
    Write-Host "ERROR: Must run from backend directory with minimal app" -ForegroundColor Red
    exit 1
}

# Verify Elastic Beanstalk CLI is available
try {
    $ebVersion = eb --version 2>$null
    if (-not $ebVersion) {
        throw "EB CLI not found"
    }
    Write-Host "SUCCESS: Elastic Beanstalk CLI found: $ebVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Elastic Beanstalk CLI not found" -ForegroundColor Red
    Write-Host "Install with: pip install awsebcli" -ForegroundColor Yellow
    exit 1
}

# Check current environment status
Write-Host "Checking current environment status..." -ForegroundColor Cyan
eb status

Write-Host ""
Write-Host "Deploying minimal requirements to t3.large (8GB RAM)..." -ForegroundColor Yellow
Write-Host "This approach prioritizes stability over advanced features:" -ForegroundColor Yellow
Write-Host "SUCCESS: Basic face detection (OpenCV)" -ForegroundColor Green
Write-Host "SUCCESS: Basic skin analysis (numpy + OpenCV)" -ForegroundColor Green
Write-Host "SUCCESS: S3 model integration" -ForegroundColor Green
Write-Host "SUCCESS: Health monitoring" -ForegroundColor Green
Write-Host "DISABLED: Advanced ML frameworks (TensorFlow, PyTorch, etc.)" -ForegroundColor Red
Write-Host "DISABLED: Enhanced embeddings and analysis" -ForegroundColor Red
Write-Host "DISABLED: Advanced recommendation engine" -ForegroundColor Red
Write-Host ""

# Confirm deployment (unless -Force is used)
if (-not $Force) {
    $confirmation = Read-Host "Proceed with minimal requirements deployment? (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Host "Deployment cancelled" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Starting minimal deployment..." -ForegroundColor Green

# Backup current application.py
Write-Host "Backing up current application.py..." -ForegroundColor Cyan
Copy-Item "application.py" "application_comprehensive_backup.py"

# Replace with minimal version
Write-Host "Switching to minimal application..." -ForegroundColor Cyan
Copy-Item "application_minimal.py" "application.py"

# Deploy with standard timeout
Write-Host "Deploying to Elastic Beanstalk..." -ForegroundColor Green
eb deploy --timeout 30

Write-Host ""
Write-Host "Deployment initiated. This should complete within 10-15 minutes for minimal workloads..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Monitor deployment in AWS Console" -ForegroundColor White
Write-Host "2. Check environment health status" -ForegroundColor White
Write-Host "3. Test endpoints once healthy" -ForegroundColor White
Write-Host "4. Restore comprehensive app when ready" -ForegroundColor White
Write-Host ""

# Restore comprehensive app for future use
Write-Host "Restoring comprehensive application for future use..." -ForegroundColor Cyan
Copy-Item "application_comprehensive_backup.py" "application.py"

Write-Host ""
Write-Host "Script completed successfully!" -ForegroundColor Green
Write-Host "Check your Elastic Beanstalk environment for deployment status" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ready to deploy minimal requirements!" -ForegroundColor Green
