#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick validation script for deployed Shine backend
    
.DESCRIPTION
    Tests key endpoints to ensure your ML backend is working after deployment
    
.EXAMPLE
    .\validate-deployment.ps1
#>

param(
    [string]$BaseUrl = "shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com"
)

Write-Host "🔍 Validating Shine ML Backend Deployment" -ForegroundColor Green
Write-Host "Testing: https://$BaseUrl" -ForegroundColor Yellow

$tests = @(
    @{ Name = "Basic Health"; Endpoint = "/api/health" },
    @{ Name = "Enhanced Health"; Endpoint = "/api/enhanced/health/enhanced" },
    @{ Name = "Service Config"; Endpoint = "/api/services/config" }
)

$passed = 0
$total = $tests.Count

foreach ($test in $tests) {
    $url = "https://$BaseUrl$($test.Endpoint)"
    Write-Host "`nTesting: $($test.Name)" -ForegroundColor Cyan
    Write-Host "URL: $url" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 30
        Write-Host "✅ PASS" -ForegroundColor Green
        
        # Show some response details
        if ($response.status) {
            Write-Host "   Status: $($response.status)" -ForegroundColor White
        }
        if ($response.message) {
            Write-Host "   Message: $($response.message)" -ForegroundColor White
        }
        
        $passed++
    } catch {
        Write-Host "❌ FAIL" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n📊 VALIDATION SUMMARY" -ForegroundColor Yellow
Write-Host "Passed: $passed/$total tests" -ForegroundColor White

if ($passed -eq $total) {
    Write-Host "🎉 All tests passed! Your ML backend is ready." -ForegroundColor Green
} elseif ($passed -gt 0) {
    Write-Host "⚠️ Some tests failed. Backend may still be starting up." -ForegroundColor Yellow
    Write-Host "Wait a few minutes and try again." -ForegroundColor Yellow
} else {
    Write-Host "❌ All tests failed. Check EB logs:" -ForegroundColor Red
    Write-Host "eb logs shine-backend-final --region us-east-1" -ForegroundColor White
}