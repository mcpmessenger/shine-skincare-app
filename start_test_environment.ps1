# Start Test Environment Script
# This script starts both backend and frontend for testing

Write-Host "🚀 Starting Shine Skincare App Test Environment..." -ForegroundColor Green

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Check if ports are available
Write-Host "🔍 Checking port availability..." -ForegroundColor Yellow
if (Test-Port 5001) {
    Write-Host "⚠️  Port 5001 (Backend) is already in use" -ForegroundColor Yellow
} else {
    Write-Host "✅ Port 5001 (Backend) is available" -ForegroundColor Green
}

if (Test-Port 3000) {
    Write-Host "⚠️  Port 3000 (Frontend) is already in use" -ForegroundColor Yellow
} else {
    Write-Host "✅ Port 3000 (Frontend) is available" -ForegroundColor Green
}

# Start Backend
Write-Host "🔧 Starting Backend (Flask)..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory "backend" -WindowStyle Minimized

# Wait for backend to start
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if backend is running
if (Test-Port 5001) {
    Write-Host "✅ Backend is running on http://localhost:5001" -ForegroundColor Green
} else {
    Write-Host "❌ Backend failed to start" -ForegroundColor Red
}

# Start Frontend
Write-Host "🎨 Starting Frontend (Next.js)..." -ForegroundColor Cyan
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "." -WindowStyle Minimized

# Wait for frontend to start
Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if frontend is running
if (Test-Port 3000) {
    Write-Host "✅ Frontend is running on http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend failed to start" -ForegroundColor Red
}

# Display test information
Write-Host ""
Write-Host "🎯 Test Environment Ready!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "Backend:  http://localhost:5001" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "📋 Test Commands:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:3000 in browser" -ForegroundColor White
Write-Host "2. Test camera/upload functionality" -ForegroundColor White
Write-Host "3. Run: python backend/test_full_pipeline.py" -ForegroundColor White
Write-Host "4. Check analysis results" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop: Close the terminal windows or use Ctrl+C" -ForegroundColor Red
Write-Host ""

# Keep script running
Write-Host "Press any key to run the pipeline test..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Run the pipeline test
Write-Host "🧪 Running Pipeline Test..." -ForegroundColor Green
Set-Location "backend"
python test_full_pipeline.py

Write-Host ""
Write-Host "✅ Test complete! Check the results above." -ForegroundColor Green 