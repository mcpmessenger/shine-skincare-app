# 🚀 Quick AWS Amplify Deployment Guide

## ✅ **Bypass Git Issues - Direct AWS Amplify Deployment**

Since we're having git push issues, let's deploy directly to AWS Amplify using their web interface.

## 🎯 **Step 1: Manual GitHub Upload (Alternative)**

If git push fails, you can manually upload your files:

1. **Go to GitHub**: https://github.com/mcpmessenger/shine
2. **Upload Files**: Use GitHub's web interface to upload the new files
3. **Files to Upload**:
   - `amplify.yml`
   - `amplify-app.yml`
   - `backend/requirements-amplify.txt`
   - `AWS_AMPLIFY_DEPLOYMENT_GUIDE.md`

## 🚀 **Step 2: AWS Amplify Setup**

### **2.1 Access AWS Amplify**
1. Go to: https://console.aws.amazon.com/amplify/
2. Sign in with your AWS account
3. Click "New app" → "Host web app"

### **2.2 Connect Repository**
1. Choose "GitHub" as source
2. Authorize AWS Amplify
3. Select repository: `mcpmessenger/shine`
4. Select branch: `main`

### **2.3 Build Settings**
Use these build settings in the Amplify Console:

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
Add these in Amplify Console:

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
```

## 🚀 **Step 3: Deploy**

1. **Click "Save and deploy"**
2. **Monitor build logs**
3. **Wait for completion** (usually 5-10 minutes)

## 🧪 **Step 4: Test Deployment**

Once deployed, test these endpoints:

```bash
# Replace with your actual Amplify URL
curl https://your-app-id.amplifyapp.com/api/health
curl https://your-app-id.amplifyapp.com/api/scin/status
curl https://your-app-id.amplifyapp.com/api/scin/dataset-info
```

## 🎯 **Why AWS Amplify is Better**

- ✅ **Handles Python ML Libraries**: PyTorch, FAISS, etc.
- ✅ **No Dependency Issues**: Unlike Vercel
- ✅ **Full-Stack Support**: Frontend + Backend
- ✅ **Automatic Deployments**: From GitHub
- ✅ **Scalable**: AWS infrastructure
- ✅ **Free Tier**: Available

## 🎉 **Success Indicators**

Your deployment is successful when:
- ✅ Build completes without errors
- ✅ Frontend loads at your Amplify URL
- ✅ API endpoints respond correctly
- ✅ SCIN integration is functional

## 🚀 **Next Steps**

1. **Test all features**
2. **Set up custom domain** (optional)
3. **Configure monitoring**
4. **Scale as needed**

---

**Your SCIN integration will be live on AWS Amplify!** 🎉

*Platform: AWS Amplify*
*Features: Full SCIN Integration*
*Status: Ready for Deployment* 