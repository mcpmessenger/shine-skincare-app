#!/bin/bash

# Shine Skincare App - Quick Start Script
# This script automates the setup process for development

set -e  # Exit on any error

echo "🚀 Shine Skincare App - Quick Start"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required software is installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION found"
    else
        print_error "npm is required but not installed"
        exit 1
    fi
    
    # Check PostgreSQL
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL found"
    else
        print_warning "PostgreSQL not found. Please install it manually."
        print_status "Installation instructions:"
        echo "  Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
        echo "  macOS: brew install postgresql"
        echo "  Windows: Download from https://www.postgresql.org/download/"
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://shine_user:shine_password@localhost:5432/shine_dev

# JWT Configuration
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production

# File Upload
UPLOAD_FOLDER=./uploads
EOF
        print_success "Created .env file"
    fi
    
    # Setup database
    print_status "Setting up database..."
    python setup_database.py
    
    cd ..
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    # Install Node.js dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    fi
    
    # Create .env.local file if it doesn't exist
    if [ ! -f ".env.local" ]; then
        print_status "Creating .env.local file..."
        cat > .env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000/api
EOF
        print_success "Created .env.local file"
    fi
}

# Test the application
test_application() {
    print_status "Testing application..."
    
    # Test backend
    cd backend
    source venv/bin/activate
    
    print_status "Testing backend API..."
    python test_api.py
    
    cd ..
}

# Start the application
start_application() {
    print_status "Starting application..."
    
    # Start backend in background
    cd backend
    source venv/bin/activate
    print_status "Starting backend server..."
    python run.py &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Start frontend
    print_status "Starting frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for both processes
    print_success "Application started!"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:5000"
    echo ""
    echo "Press Ctrl+C to stop both servers"
    
    # Wait for interrupt
    wait $BACKEND_PID $FRONTEND_PID
}

# Main execution
main() {
    check_requirements
    setup_backend
    setup_frontend
    test_application
    start_application
}

# Handle script interruption
trap 'echo ""; print_warning "Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

# Run main function
main 