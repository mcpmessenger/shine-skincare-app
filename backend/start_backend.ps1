# Start Enhanced Backend Script
Write-Host "🚀 Starting Enhanced Backend..." -ForegroundColor Green

# Kill any existing Python processes
Write-Host "🛑 Stopping existing Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Start the enhanced app
Write-Host "🔧 Starting enhanced_app.py..." -ForegroundColor Yellow
python enhanced_app.py 