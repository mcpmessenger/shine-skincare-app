# Simple Test Script - Test if the 504 Gateway Timeout is fixed
Write-Host "🧪 Testing if 504 Gateway Timeout is Fixed..." -ForegroundColor Green

$ALB_DNS = "production-shine-skincare-alb-1879927784.us-east-1.elb.amazonaws.com"

Write-Host "`n📡 Testing API Gateway (port 8080):" -ForegroundColor Cyan
Write-Host "Testing: http://$ALB_DNS`:8080/" -ForegroundColor White

try {
    $response = Invoke-WebRequest -Uri "http://$ALB_DNS`:8080/" -Method GET -TimeoutSec 10
    Write-Host "✅ SUCCESS! Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "🎉 The 504 Gateway Timeout is FIXED!" -ForegroundColor Green
} catch {
    Write-Host "❌ Still getting error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "The service may still be starting up..." -ForegroundColor Yellow
}

Write-Host "`n📡 Testing ML Service (port 5000):" -ForegroundColor Cyan
Write-Host "Testing: http://$ALB_DNS`:5000/" -ForegroundColor White

try {
    $response = Invoke-WebRequest -Uri "http://$ALB_DNS`:5000/" -Method GET -TimeoutSec 10
    Write-Host "✅ SUCCESS! Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 Test Summary:" -ForegroundColor Cyan
Write-Host "If you see SUCCESS above, your deployment is 100% complete!" -ForegroundColor White
Write-Host "If you still see errors, the service may need a few more minutes to fully start." -ForegroundColor White
