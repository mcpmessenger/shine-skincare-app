# Test Backend Connection Script
# This script tests if the Flask backend is running and responding

Write-Host "🧪 Testing Backend Connection" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green

# Test 1: Check if port 5001 is listening
Write-Host "🔍 Testing port 5001..." -ForegroundColor Yellow
try {
    $connection = Test-NetConnection -ComputerName localhost -Port 5001 -InformationLevel Quiet
    if ($connection.TcpTestSucceeded) {
        Write-Host "✅ Port 5001 is open" -ForegroundColor Green
    } else {
        Write-Host "❌ Port 5001 is not responding" -ForegroundColor Red
        Write-Host "Backend may not be running" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Cannot test port 5001: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Test health endpoint
Write-Host "🏥 Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Health endpoint responded" -ForegroundColor Green
    Write-Host "Status: $($response.status)" -ForegroundColor Cyan
    Write-Host "Version: $($response.version)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Health endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Backend may not be fully started" -ForegroundColor Yellow
    exit 1
}

# Test 3: Test root endpoint
Write-Host "🏠 Testing root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/" -Method GET -TimeoutSec 10
    Write-Host "✅ Root endpoint responded" -ForegroundColor Green
    Write-Host "Message: $($response.message)" -ForegroundColor Cyan
    Write-Host "Status: $($response.status)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Root endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 4: Test UTKFace status (if available)
Write-Host "👥 Testing UTKFace status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/v3/utkface/status" -Method GET -TimeoutSec 10
    Write-Host "✅ UTKFace endpoint responded" -ForegroundColor Green
    Write-Host "Available: $($response.utkface_available)" -ForegroundColor Cyan
    Write-Host "Initialized: $($response.system_initialized)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️ UTKFace endpoint not available: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 5: Test Facial Skin Diseases status (if available)
Write-Host "🔬 Testing Facial Skin Diseases status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/v3/facial-skin-diseases/status" -Method GET -TimeoutSec 10
    Write-Host "✅ Facial Skin Diseases endpoint responded" -ForegroundColor Green
    Write-Host "Available: $($response.facial_skin_diseases_available)" -ForegroundColor Cyan
    Write-Host "Initialized: $($response.system_initialized)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️ Facial Skin Diseases endpoint not available: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "==================================================" -ForegroundColor Green
Write-Host "✅ All tests completed successfully!" -ForegroundColor Green
Write-Host "🌐 Backend is running and responding properly" -ForegroundColor Green
Write-Host "📊 API is ready for frontend connections" -ForegroundColor Green 