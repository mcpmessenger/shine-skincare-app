#!/usr/bin/env pwsh
# Simple deployment test

$BaseUrl = "shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com"

Write-Host "Testing Shine Backend: https://$BaseUrl" -ForegroundColor Green

# Test basic health endpoint
Write-Host "`nTesting /api/health..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "https://$BaseUrl/api/health" -Method Get -TimeoutSec 30
    Write-Host "✅ SUCCESS" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor White
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test enhanced health
Write-Host "`nTesting /api/enhanced/health/enhanced..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "https://$BaseUrl/api/enhanced/health/enhanced" -Method Get -TimeoutSec 30
    Write-Host "✅ SUCCESS" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor White
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nDone!" -ForegroundColor Green