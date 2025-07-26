@echo off
REM Shine Skincare App - Quick Start Script for Windows
REM This script automates the setup process for development

echo 🚀 Shine Skincare App - Quick Start
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is required but not installed
    echo Please install Python from https://python.org
    pause
    exit /b 1
) else (
    echo [SUCCESS] Python found
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is required but not installed
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
) else (
    echo [SUCCESS] Node.js found
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is required but not installed
    pause
    exit /b 1
) else (
    echo [SUCCESS] npm found
)

echo [INFO] Setting up backend...

REM Navigate to backend directory
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env file...
    (
        echo # Database Configuration
        echo DATABASE_URL=postgresql://shine_user:shine_password@localhost:5432/shine_dev
        echo.
        echo # JWT Configuration
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo JWT_SECRET_KEY=jwt-secret-key-change-in-production
        echo.
        echo # File Upload
        echo UPLOAD_FOLDER=./uploads
    ) > .env
    echo [SUCCESS] Created .env file
)

REM Setup database
echo [INFO] Setting up database...
python setup_database.py

REM Go back to root directory
cd ..

echo [INFO] Setting up frontend...

REM Install Node.js dependencies
if not exist "node_modules" (
    echo [INFO] Installing Node.js dependencies...
    npm install
)

REM Create .env.local file if it doesn't exist
if not exist ".env.local" (
    echo [INFO] Creating .env.local file...
    (
        echo # API Configuration
        echo NEXT_PUBLIC_API_URL=http://localhost:5000/api
    ) > .env.local
    echo [SUCCESS] Created .env.local file
)

echo [INFO] Testing application...

REM Test backend
cd backend
call venv\Scripts\activate.bat
echo [INFO] Testing backend API...
python test_api.py
cd ..

echo [INFO] Starting application...

REM Start backend in background
cd backend
call venv\Scripts\activate.bat
echo [INFO] Starting backend server...
start "Backend Server" python run.py
cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo [INFO] Starting frontend server...
start "Frontend Server" npm run dev

echo [SUCCESS] Application started!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:5000
echo.
echo Press any key to stop the servers...
pause

REM Stop the servers
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo [INFO] Servers stopped.
pause 