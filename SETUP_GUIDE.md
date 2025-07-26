# 🚀 Shine Skincare App - Complete Setup Guide

## Overview

This guide will help you set up the complete Shine skincare application with both frontend (Next.js) and backend (Flask) components.

## Prerequisites

### Required Software
- **Node.js** (v18 or higher)
- **Python** (3.11 or higher)
- **PostgreSQL** (v12 or higher)
- **Git**

### Optional Software
- **Redis** (for caching and Celery tasks)
- **Docker** (for containerized deployment)

## 🗄️ Database Setup

### 1. Install PostgreSQL

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql
```

**macOS:**
```bash
# Using Homebrew:
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database User

```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create user and database
CREATE USER shine_user WITH PASSWORD 'shine_password';
CREATE DATABASE shine_dev OWNER shine_user;
GRANT ALL PRIVILEGES ON DATABASE shine_dev TO shine_user;
\q
```

## 🔧 Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:
```env
# Database Configuration
DATABASE_URL=postgresql://shine_user:shine_password@localhost:5432/shine_dev

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Google OAuth (Optional - for authentication)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Stripe (Optional - for payments)
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

# Redis (Optional - for caching)
REDIS_URL=redis://localhost:6379/0

# File Upload
UPLOAD_FOLDER=./uploads
```

### 5. Set Up Database
```bash
# Run the database setup script
python setup_database.py
```

### 6. Test Backend
```bash
# Start the backend server
python run.py

# In another terminal, test the API
python test_api.py
```

## 🎨 Frontend Setup

### 1. Navigate to Project Root
```bash
cd ..  # If you're in the backend directory
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env.local` file in the project root:
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000/api

# Google OAuth (Optional)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

### 4. Start Frontend Development Server
```bash
npm run dev
```

## 🧪 Testing the Application

### 1. Backend Tests
```bash
cd backend
python test_api.py
```

Expected output:
```
🧪 Testing Shine Backend API...
============================================================
Testing against: http://localhost:5000/api
Timestamp: 2024-01-15 10:30:00

✅ PASS Health Check
   Backend is running

✅ PASS Auth Login
   OAuth URL generated successfully

✅ PASS Trending Products
   Found 8 products

✅ PASS Products List
   Found 8 products

✅ PASS Image Upload (Auth Required)
   Correctly requires authentication

✅ PASS Payment Intent (Auth Required)
   Correctly requires authentication

✅ PASS MCP Discovery (Auth Required)
   Correctly requires authentication

============================================================
📊 Test Results: 7/7 tests passed
🎉 All tests passed! Backend is working correctly.
```

### 2. Frontend Tests
Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api/health

### 3. Manual Testing Checklist

#### Authentication Flow
- [ ] Click "Login" in the header
- [ ] Verify Google OAuth redirect works
- [ ] Test OAuth callback page
- [ ] Verify user profile displays after login
- [ ] Test logout functionality

#### Product Display
- [ ] Verify trending products load on homepage
- [ ] Check product cards display correctly
- [ ] Verify product images and details

#### API Integration
- [ ] Check browser network tab for API calls
- [ ] Verify no CORS errors
- [ ] Test error handling (disconnect backend)

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U shine_user -d shine_dev
```

#### 2. Port Already in Use
```bash
# Check what's using the port
lsof -i :5000  # Backend
lsof -i :3000  # Frontend

# Kill process if needed
kill -9 <PID>
```

#### 3. Python Dependencies
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt
pip install -r requirements.txt
```

#### 4. Node.js Dependencies
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Environment-Specific Issues

#### Windows
- Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- Ensure PostgreSQL service is running in Services
- Use Windows paths in configuration files

#### macOS
- Use Homebrew for PostgreSQL installation
- Ensure Xcode command line tools are installed
- Use `brew services start postgresql`

#### Linux
- Use `sudo systemctl` for PostgreSQL management
- Ensure proper file permissions for uploads directory
- Check firewall settings for port access

## 🚀 Production Deployment

### Backend Deployment
1. Set up production PostgreSQL database
2. Configure environment variables for production
3. Set up Redis for caching
4. Use Gunicorn for production server
5. Configure reverse proxy (Nginx)

### Frontend Deployment
1. Build production version: `npm run build`
2. Deploy to Vercel, Netlify, or similar
3. Configure environment variables
4. Set up custom domain

### Security Considerations
- Change all default passwords
- Use HTTPS in production
- Configure CORS properly
- Set up proper JWT expiration
- Enable rate limiting
- Use environment variables for secrets

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error logs in the terminal
3. Check the browser console for frontend errors
4. Verify all environment variables are set correctly
5. Ensure all services are running (PostgreSQL, Redis)

For additional support, check the project documentation or create an issue in the repository. 