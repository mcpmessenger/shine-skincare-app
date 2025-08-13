# Test Backend Endpoints
Write-Host "🧪 Testing Backend Endpoints..." -ForegroundColor Green
Write-Host ""

# Test health endpoint
Write-Host "🔍 Testing /health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
    Write-Host "✅ Health endpoint: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Health endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test face detection endpoint
Write-Host "🔍 Testing /api/v4/face/detect endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v4/face/detect" -Method GET
    Write-Host "✅ Face detection endpoint: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Face detection endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test skin analysis endpoint
Write-Host "🔍 Testing /api/v5/skin/analyze-fixed endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v5/skin/analyze-fixed" -Method GET
    Write-Host "✅ Skin analysis endpoint: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Skin analysis endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Endpoint testing complete!" -ForegroundColor Green
