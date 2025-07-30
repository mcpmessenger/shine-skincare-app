#!/usr/bin/env pwsh
# Check current EB environment status

Write-Host "🔍 Checking AWS Elastic Beanstalk Status" -ForegroundColor Green

# Check AWS credentials
Write-Host "`n📋 Checking AWS credentials..." -ForegroundColor Cyan
try {
    $identity = aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Host "✅ AWS Identity: $($identity.Arn)" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials not configured" -ForegroundColor Red
    exit 1
}

# List all EB environments
Write-Host "`n🏗️ Checking EB environments..." -ForegroundColor Cyan
try {
    $environments = aws elasticbeanstalk describe-environments --region us-east-1 --output json | ConvertFrom-Json
    
    if ($environments.Environments.Count -eq 0) {
        Write-Host "❌ No EB environments found" -ForegroundColor Red
    } else {
        Write-Host "✅ Found $($environments.Environments.Count) environment(s):" -ForegroundColor Green
        foreach ($env in $environments.Environments) {
            Write-Host "  - Name: $($env.EnvironmentName)" -ForegroundColor White
            Write-Host "    Status: $($env.Status)" -ForegroundColor White
            Write-Host "    Health: $($env.Health)" -ForegroundColor White
            Write-Host "    URL: $($env.CNAME)" -ForegroundColor Cyan
            Write-Host ""
        }
    }
} catch {
    Write-Host "❌ Error checking environments: $($_.Exception.Message)" -ForegroundColor Red
}

# Check if we're in the backend directory
Write-Host "🔍 Checking backend directory..." -ForegroundColor Cyan
if (Test-Path "backend") {
    Write-Host "✅ Backend directory found" -ForegroundColor Green
    
    # Check if EB is initialized
    if (Test-Path "backend/.elasticbeanstalk/config.yml") {
        Write-Host "✅ EB application initialized" -ForegroundColor Green
        
        # Show EB status
        Push-Location backend
        try {
            Write-Host "`n📊 EB Status:" -ForegroundColor Cyan
            eb status
        } catch {
            Write-Host "❌ Could not get EB status" -ForegroundColor Red
        }
        Pop-Location
    } else {
        Write-Host "⚠️ EB not initialized in backend directory" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Backend directory not found" -ForegroundColor Red
}

Write-Host "`n🚀 Next steps:" -ForegroundColor Yellow
Write-Host "1. If no environment exists: .\aws-infrastructure\deploy-simple.ps1" -ForegroundColor White
Write-Host "2. If environment exists but unhealthy: eb deploy shine-backend-final" -ForegroundColor White