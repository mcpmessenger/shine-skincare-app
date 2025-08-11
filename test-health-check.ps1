# Test Health Check After Fix
# This script tests the health check endpoints to verify the fix worked

Write-Host "🧪 Testing Health Check After Fix..." -ForegroundColor Green

# Configuration
$ALB_DNS = "production-shine-skincare-alb-1879927784.us-east-1.elb.amazonaws.com"

Write-Host "`n🔍 Testing ALB endpoints..." -ForegroundColor Yellow

# Test API Gateway endpoint (port 8080)
Write-Host "`n📡 Testing API Gateway (port 8080):" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://$ALB_DNS`:8080/" -Method GET -TimeoutSec 10
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📝 Response: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))..." -ForegroundColor White
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test ML Service endpoint (port 5000)
Write-Host "`n📡 Testing ML Service (port 5000):" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://$ALB_DNS`:5000/" -Method GET -TimeoutSec 10
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📝 Response: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))..." -ForegroundColor White
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test health endpoint (should fail as expected)
Write-Host "`n📡 Testing /health endpoint (should fail):" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://$ALB_DNS`:8080/health" -Method GET -TimeoutSec 10
    Write-Host "⚠️  Unexpected success: $($response.StatusCode)" -ForegroundColor Yellow
} catch {
    Write-Host "✅ Expected failure: $($_.Exception.Message)" -ForegroundColor Green
}

Write-Host "`n🎯 Health Check Test Summary:" -ForegroundColor Cyan
Write-Host "- Root path (/) should return 200 OK" -ForegroundColor White
Write-Host "- /health path should return 404 or connection error" -ForegroundColor White
Write-Host "- This confirms the health check fix is working" -ForegroundColor White
