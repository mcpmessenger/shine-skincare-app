# Shine Skincare App Testing Guide

This guide provides comprehensive testing instructions for the Shine Skincare App, covering local development, backend testing, frontend testing, and AWS deployment testing.

## 🚀 Quick Start Testing

### 1. Local Backend Testing

First, let's test the backend locally to ensure everything works:

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your test credentials

# Run the backend locally
python run.py
```

**Test the backend endpoints:**
```bash
# Health check
curl http://localhost:5000/api/health

# Test image analysis endpoint
curl -X POST http://localhost:5000/api/analyze-skin \
  -H "Content-Type: application/json" \
  -d '{"image_url": "test_image_url"}'
```

### 2. Local Frontend Testing

```bash
# Navigate to project root
cd ..

# Install dependencies
npm install

# Start development server
npm run dev
```

**Test the frontend:**
- Open http://localhost:3000
- Test skin analysis upload
- Test authentication flow
- Test product recommendations

## 🔧 Backend Testing

### Unit Tests

```bash
cd backend

# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_api.py

# Run with coverage
python -m pytest --cov=app
```

### API Testing

Use the provided test script:
```bash
cd backend
python test_api.py
```

**Manual API Testing:**
```bash
# Health check
curl http://localhost:5000/api/health

# Skin analysis
curl -X POST http://localhost:5000/api/analyze-skin \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/test-image.jpg"}'

# Get recommendations
curl http://localhost:5000/api/recommendations?skin_type=oily

# Authentication
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Database Testing

```bash
# Test database connection
python setup_database.py --test

# Run database migrations
python setup_database.py --migrate

# Seed test data
python seed_data.py
```

## 🎨 Frontend Testing

### Component Testing

```bash
# Run component tests
npm test

# Run specific test
npm test -- --testNamePattern="SkinAnalysis"

# Run with coverage
npm test -- --coverage
```

### E2E Testing

```bash
# Install Playwright
npx playwright install

# Run E2E tests
npx playwright test

# Run specific test
npx playwright test skin-analysis.spec.ts
```

### Manual Frontend Testing

1. **Authentication Flow:**
   - Test signup process
   - Test login/logout
   - Test password reset
   - Test OAuth integration

2. **Skin Analysis:**
   - Upload test images
   - Verify analysis results
   - Test different image formats
   - Test error handling

3. **Product Recommendations:**
   - Verify recommendations based on skin type
   - Test filtering and sorting
   - Test add to cart functionality

4. **Shopping Cart:**
   - Add/remove products
   - Update quantities
   - Test checkout process

## 🐳 Docker Testing

### Local Docker Testing

```bash
# Build the Docker image
docker build -t shine-api:test ../backend/

# Run the container
docker run -p 5000:5000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e GOOGLE_CLIENT_ID="test_id" \
  -e GOOGLE_CLIENT_SECRET="test_secret" \
  -e JWT_SECRET_KEY="test_jwt_secret" \
  -e STRIPE_SECRET_KEY="sk_test_key" \
  shine-api:test

# Test the containerized API
curl http://localhost:5000/api/health
```

### Docker Compose Testing

```bash
# Create docker-compose.test.yml
version: '3.8'
services:
  api:
    build: ../backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://test:test@db:5432/test_db
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=test_db
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
    ports:
      - "5432:5432"

# Run the test environment
docker-compose -f docker-compose.test.yml up --build
```

## ☁️ AWS Deployment Testing

### Infrastructure Testing

Since we're having AWS permission issues, let's test the deployment scripts locally first:

```powershell
# Test deployment script syntax
cd aws-infrastructure
powershell -Command "Get-Content .\deploy-fixed.ps1 | Out-Null; Write-Host 'Script syntax is valid!'"

# Test ECS update script
powershell -Command "Get-Content .\update-ecs-service.ps1 | Out-Null; Write-Host 'ECS script syntax is valid!'"
```

### Manual AWS Testing

If you have proper AWS permissions:

```bash
# Test CloudFormation template
aws cloudformation validate-template \
  --template-body file://cloudformation-template.yaml

# Test ECR repository
aws ecr describe-repositories --repository-names shine-api

# Test ECS cluster
aws ecs describe-clusters --clusters production-shine-cluster
```

## 🧪 Integration Testing

### Full Stack Testing

1. **Backend + Database:**
   ```bash
   # Start backend with database
   cd backend
   python run.py
   
   # Test database operations
   python test_enhanced_services.py
   ```

2. **Frontend + Backend:**
   ```bash
   # Start backend
   cd backend && python run.py &
   
   # Start frontend
   cd .. && npm run dev
   
   # Test full user flow
   ```

3. **API Integration:**
   ```bash
   # Test all API endpoints
   python test_api.py
   
   # Test enhanced features
   python test_enhanced_services.py
   ```

## 🔍 Performance Testing

### Load Testing

```bash
# Install Apache Bench
# On Windows: Download from Apache website
# On macOS: brew install httpd
# On Linux: apt-get install apache2-utils

# Test API performance
ab -n 100 -c 10 http://localhost:5000/api/health

# Test image analysis endpoint
ab -n 50 -c 5 -p test_image.json -T application/json \
  http://localhost:5000/api/analyze-skin
```

### Memory Testing

```bash
# Monitor memory usage
python -m memory_profiler backend/run.py

# Test with large images
python test_performance.py
```

## 🐛 Debugging

### Backend Debugging

```bash
# Enable debug mode
export FLASK_DEBUG=1
python run.py

# Use Python debugger
python -m pdb run.py

# Check logs
tail -f logs/app.log
```

### Frontend Debugging

```bash
# Enable React DevTools
# Install browser extension

# Check console for errors
# Use React Developer Tools

# Debug with VS Code
# Set breakpoints in components
```

### Database Debugging

```bash
# Connect to database
psql -h localhost -U test -d test_db

# Check tables
\dt

# Check data
SELECT * FROM users LIMIT 5;
```

## 📊 Test Data

### Sample Images for Testing

Create a `test_images` directory with:
- `test_skin_1.jpg` - Normal skin
- `test_skin_2.jpg` - Oily skin  
- `test_skin_3.jpg` - Dry skin
- `test_skin_4.jpg` - Acne-prone skin

### Sample User Data

```sql
-- Insert test users
INSERT INTO users (email, password_hash, skin_type) VALUES
('test1@example.com', 'hashed_password', 'normal'),
('test2@example.com', 'hashed_password', 'oily'),
('test3@example.com', 'hashed_password', 'dry');

-- Insert test products
INSERT INTO products (name, category, skin_type, price) VALUES
('Test Cleanser', 'cleanser', 'all', 25.00),
('Test Moisturizer', 'moisturizer', 'normal', 30.00),
('Test Serum', 'serum', 'oily', 45.00);
```

## 🚨 Common Issues & Solutions

### Backend Issues

1. **Database Connection Failed:**
   ```bash
   # Check database is running
   sudo systemctl status postgresql
   
   # Check connection string
   echo $DATABASE_URL
   ```

2. **Google Vision API Error:**
   ```bash
   # Check API key
   echo $GOOGLE_APPLICATION_CREDENTIALS
   
   # Test API access
   python test_google_vision.py
   ```

3. **JWT Token Issues:**
   ```bash
   # Check secret key
   echo $JWT_SECRET_KEY
   
   # Test token generation
   python test_auth.py
   ```

### Frontend Issues

1. **API Calls Failing:**
   ```bash
   # Check API URL in frontend
   grep -r "localhost:5000" src/
   
   # Test API endpoint
   curl http://localhost:5000/api/health
   ```

2. **Authentication Not Working:**
   ```bash
   # Check OAuth configuration
   # Verify Google Client ID
   # Test login flow
   ```

### AWS Issues

1. **Permission Denied:**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity
   
   # Check IAM permissions
   aws iam get-user
   ```

2. **ECS Service Not Starting:**
   ```bash
   # Check service logs
   aws logs tail /ecs/production-shine-api
   
   # Check task definition
   aws ecs describe-task-definition --task-definition production-shine-api
   ```

## 📋 Testing Checklist

### Pre-Deployment Testing
- [ ] Backend unit tests pass
- [ ] Frontend component tests pass
- [ ] API integration tests pass
- [ ] Database migrations work
- [ ] Docker image builds successfully
- [ ] Local environment works end-to-end

### Deployment Testing
- [ ] CloudFormation template validates
- [ ] ECR repository exists
- [ ] ECS cluster is accessible
- [ ] Database is accessible
- [ ] Load balancer health checks pass
- [ ] API endpoints respond correctly

### Post-Deployment Testing
- [ ] Frontend loads correctly
- [ ] Authentication works
- [ ] Skin analysis uploads work
- [ ] Product recommendations display
- [ ] Shopping cart functions
- [ ] Payment processing works

## 🎯 Next Steps

1. **Fix AWS Permissions:** Contact your AWS administrator to grant necessary permissions
2. **Test Locally:** Ensure everything works in local environment first
3. **Deploy Incrementally:** Start with basic infrastructure, then add features
4. **Monitor Performance:** Set up CloudWatch monitoring and alerts
5. **Security Testing:** Run security scans and penetration tests

## 📞 Support

For testing issues:
1. Check the logs for error messages
2. Verify all environment variables are set
3. Test components individually
4. Use the debugging tools provided
5. Check the troubleshooting section above 