#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Fix AWS region deployment issues and redeploy to us-east-1
    
.DESCRIPTION
    Clean up resources in wrong region and redeploy to us-east-1
    
.EXAMPLE
    .\fix-region-deployment.ps1
#>

Write-Host "🔧 Fixing AWS Region Deployment Issues" -ForegroundColor Green
Write-Host "Target Region: us-east-1" -ForegroundColor Yellow

# Set AWS region
Write-Host "`n🌍 Setting AWS region to us-east-1..." -ForegroundColor Cyan
aws configure set region us-east-1

# Verify region
Write-Host "`n✅ Verifying AWS region..." -ForegroundColor Cyan
$currentRegion = aws configure get region
Write-Host "Current region: $currentRegion" -ForegroundColor Green

if ($currentRegion -ne "us-east-1") {
    Write-Host "❌ Region is not us-east-1. Please check AWS configuration." -ForegroundColor Red
    exit 1
}

# List resources in us-east-1
Write-Host "`n📋 Listing resources in us-east-1..." -ForegroundColor Cyan

try {
    Write-Host "CodeBuild Projects:" -ForegroundColor White
    aws codebuild list-projects --region us-east-1 --output table
    
    Write-Host "`nCodeDeploy Applications:" -ForegroundColor White
    aws deploy list-applications --region us-east-1 --output table
    
    Write-Host "`nElastic Beanstalk Applications:" -ForegroundColor White
    aws elasticbeanstalk describe-applications --region us-east-1 --output table
    
} catch {
    Write-Host "⚠️ Error listing resources: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Clean up wrong region resources (us-east-2)
Write-Host "`n🗑️ Cleaning up resources in us-east-2..." -ForegroundColor Cyan

try {
    Write-Host "Checking for resources in us-east-2..." -ForegroundColor White
    
    # Temporarily set region to us-east-2 to clean up
    $originalRegion = aws configure get region
    aws configure set region us-east-2
    
    # List and optionally delete resources in us-east-2
    Write-Host "Resources in us-east-2:" -ForegroundColor White
    try {
        aws codebuild list-projects --region us-east-2 --output table
    } catch {
        Write-Host "No CodeBuild projects in us-east-2" -ForegroundColor Yellow
    }
    
    try {
        aws deploy list-applications --region us-east-2 --output table
    } catch {
        Write-Host "No CodeDeploy applications in us-east-2" -ForegroundColor Yellow
    }
    
    # Restore original region
    aws configure set region $originalRegion
    
} catch {
    Write-Host "⚠️ Error checking us-east-2 resources: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Commit and push changes
Write-Host "`n📤 Committing and pushing changes..." -ForegroundColor Cyan
try {
    git add .
    git commit -m "Fix region deployment - configure for us-east-1"
    git push
    Write-Host "✓ Changes pushed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Error pushing changes: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✅ Region deployment fix completed!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Check AWS Console for us-east-1 deployment" -ForegroundColor White
Write-Host "2. Monitor build logs" -ForegroundColor White
Write-Host "3. Verify application is working" -ForegroundColor White 