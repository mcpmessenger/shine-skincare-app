# 🚀 AWS Amplify Deployment Guide for SCIN Integration

## ✅ **Deployment Strategy: AWS Amplify + GitHub**

This guide will help you deploy your SCIN integration using AWS Amplify, which handles Python dependencies much better than Vercel and integrates seamlessly with GitHub.

## 🎯 **Why AWS Amplify?**

- ✅ **Better Python Support**: Handles ML libraries like PyTorch, FAISS, etc.
- ✅ **GitHub Integration**: Automatic deployments from GitHub
- ✅ **Full-Stack Support**: Both frontend and backend in one platform
- ✅ **Scalable**: AWS infrastructure
- ✅ **Cost-Effective**: Free tier available

## 📋 **Prerequisites**

1. **AWS Account**: Create an AWS account if you don't have one
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **AWS CLI** (optional): For advanced configuration

## 🚀 **Step 1: Push to GitHub**

First, let's push your code to GitHub:

```bash
# Add all changes
git add .

# Commit changes
git commit -m "feat: Complete SCIN integration ready for AWS Amplify deployment"

# Push to GitHub
git push origin main
```

## 🚀 **Step 2: Set Up AWS Amplify**

### **2.1 Access AWS Amplify Console**
1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Sign in with your AWS account
3. Click "New app" → "Host web app"

### **2.2 Connect to GitHub**
1. Choose "GitHub" as your repository source
2. Authorize AWS Amplify to access your GitHub account
3. Select your repository: `mcpmessenger/shine`
4. Select the branch: `main`

### **2.3 Configure Build Settings**
AWS Amplify will auto-detect your build settings, but you can customize:

**Build Settings:**
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
      - .next/cache/**/*

backend:
  phases:
    preBuild:
      commands:
        - cd backend
        - python -m pip install --upgrade pip
        - pip install -r requirements-amplify.txt
    build:
      commands:
        - echo "Backend build completed"
  artifacts:
    baseDirectory: backend
    files:
      - '**/*'
  cache:
    paths:
      - backend/venv/**/*
      - backend/__pycache__/**/*
```

### **2.4 Environment Variables**
Add these environment variables in the Amplify Console:

```env
# SCIN Configuration
SCIN_BUCKET_PATH=gs://dx-scin-public-data/dataset/
SCIN_CACHE_DIR=scin_cache
SCIN_VECTOR_CACHE_DIR=vector_cache
SCIN_BATCH_SIZE=100
SCIN_MAX_IMAGES=1000
SCIN_FEATURE_DIMENSION=2048
SCIN_VECTORIZATION_MODEL=resnet50
SCIN_VECTORIZATION_DEVICE=cpu

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Database Configuration (if using)
DATABASE_URL=your-database-url
```

## 🚀 **Step 3: Deploy**

### **3.1 Start Deployment**
1. Click "Save and deploy"
2. AWS Amplify will start building your application
3. Monitor the build logs for any issues

### **3.2 Build Process**
The build process will:
1. **Frontend**: Install Node.js dependencies and build Next.js app
2. **Backend**: Install Python dependencies and prepare Flask app
3. **Testing**: Run basic import tests
4. **Deployment**: Deploy to AWS infrastructure

## 🧪 **Step 4: Testing Your Deployment**

### **4.1 Check Build Status**
- Monitor the build logs in AWS Amplify Console
- Look for any errors in the build process

### **4.2 Test Endpoints**
Once deployed, test these endpoints:

```bash
# Health check
curl https://your-app-id.amplifyapp.com/api/health

# SCIN integration status
curl https://your-app-id.amplifyapp.com/api/scin/status

# Dataset information
curl https://your-app-id.amplifyapp.com/api/scin/dataset-info
```

### **4.3 Frontend Testing**
- Visit your Amplify app URL
- Test all frontend functionality
- Verify SCIN integration features

## 🔧 **Step 5: Custom Domain (Optional)**

### **5.1 Add Custom Domain**
1. In Amplify Console, go to "Domain management"
2. Click "Add domain"
3. Enter your domain name
4. Follow the DNS configuration instructions

### **5.2 SSL Certificate**
- AWS Amplify automatically provides SSL certificates
- Your app will be accessible via HTTPS

## 📊 **Step 6: Monitoring and Maintenance**

### **6.1 Build Monitoring**
- AWS Amplify provides build logs and status
- Set up notifications for build failures
- Monitor deployment success rates

### **6.2 Performance Monitoring**
- Use AWS CloudWatch for performance metrics
- Monitor API response times
- Track user engagement

### **6.3 Updates and Deployments**
- Every push to `main` branch triggers automatic deployment
- Review build logs before deployment
- Test changes locally before pushing

## 🎯 **Troubleshooting**

### **Common Issues:**

**1. Python Dependencies**
```bash
# If you see import errors, check requirements-amplify.txt
# Make sure all dependencies are listed
```

**2. Build Failures**
```bash
# Check build logs in Amplify Console
# Verify all files are committed to GitHub
```

**3. Environment Variables**
```bash
# Ensure all required environment variables are set
# Check for typos in variable names
```

**4. API Endpoints**
```bash
# Test endpoints individually
# Check CORS configuration
# Verify Flask app is running
```

## 🎉 **Success Indicators**

Your deployment is successful when:
- ✅ Build completes without errors
- ✅ Frontend loads correctly
- ✅ API endpoints respond
- ✅ SCIN integration is functional
- ✅ All features work as expected

## 🚀 **Next Steps After Deployment**

### **1. Production Optimization**
- Set up monitoring and alerting
- Configure auto-scaling
- Implement caching strategies

### **2. Feature Enhancement**
- Add more SCIN dataset features
- Implement advanced ML models
- Add user authentication

### **3. Performance Tuning**
- Optimize database queries
- Implement CDN for static assets
- Add API rate limiting

## 📞 **Support**

If you encounter issues:
1. Check AWS Amplify documentation
2. Review build logs for specific errors
3. Test locally to isolate issues
4. Contact AWS support if needed

---

**Your SCIN integration will be live and fully functional on AWS Amplify!** 🎉

*Status: Ready for AWS Amplify Deployment*
*Platform: AWS Amplify + GitHub*
*Features: Full SCIN Integration*
*Scalability: Production Ready* 