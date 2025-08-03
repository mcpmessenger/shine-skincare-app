# Start Flask Server for Windows
# This script properly starts the Flask server on Windows

Write-Host "🚀 Starting Flask Server for Windows..." -ForegroundColor Green

# Kill any existing Python processes (optional)
Write-Host "Checking for existing Python processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait a moment
Start-Sleep -Seconds 2

# Start the Flask server
Write-Host "Starting Flask server on port 5001..." -ForegroundColor Cyan
Write-Host "Server will be available at: http://127.0.0.1:5001" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red

# Start the server in the current directory
python working_flask_server.py 