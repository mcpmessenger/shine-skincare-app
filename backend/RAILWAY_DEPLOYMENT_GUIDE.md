# Complete Railway Deployment Guide

## 🚀 Railway Backend Environment Variables

### **Required Railway Environment Variables**

Set these in your Railway project dashboard under "Variables" tab:

#### **Core Flask Configuration**
```
FLASK_ENV=production
PORT=5000
SECRET_KEY=X5lx34nDqkidpmJBfPMwvSOyVGetLQIWhRNagY61bZ0jUurT7ozKAF8EcCsH92
LOG_LEVEL=INFO
```

#### **Service Configuration**
```
USE_MOCK_SERVICES=false
USE_PRODUCTION_FAISS=true
GOOGLE_VISION_ENABLED=true
FAISS_PERSISTENCE_ENABLED=true
```

#### **Google Cloud Vision API** 
```
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"shine-466907",...paste your complete JSON here...}

GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_CLOUD_PROJECT_ID=shine-466907
```

#### **Supabase Database**
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-service-role-key-here
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-service-role-key-here
```

#### **FAISS Configuration**
```
FAISS_DIMENSION=2048
FAISS_INDEX_PATH=/app/faiss_index
```

#### **AI Service Weights**
```
DEMOGRAPHIC_WEIGHT=0.3
ETHNICITY_WEIGHT=0.6
SKIN_TYPE_WEIGHT=0.3
AGE_GROUP_WEIGHT=0.1
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7
```

---

## 🌐 Frontend Amplify Environment Variables

### **Current Frontend Environment Variables**

The frontend (Amplify deployment) needs to know where the Railway backend is deployed:

#### **Required Frontend Environment Variables**
```
NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

#### **Current Frontend Variables (from .env.vercel)**
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
GOOGLE_CLIENT_ID=your-google-client-id-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

---

## 🔄 Deployment Steps

### **Step 1: Deploy Backend to Railway**

1. **Create Railway Project**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and create project
   railway login
   cd backend
   railway init
   ```

2. **Set Environment Variables**:
   - Go to Railway dashboard → Your Project → Variables
   - Add all the Railway environment variables listed above
   - **Important**: Copy the `GOOGLE_CREDENTIALS_JSON` as a single line

3. **Deploy**:
   ```bash
   railway up
   ```

4. **Get Railway URL**:
   - After deployment, Railway will provide a URL like: `https://your-app.railway.app`

### **Step 2: Update Frontend to Point to Railway**

1. **Update Amplify Environment Variables**:
   - Go to AWS Amplify Console → Your App → Environment Variables
   - Update or add:
     ```
     NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app
     NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
     ```

2. **Update Local Development**:
   ```bash
   # Update .env.local
   echo "NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.railway.app" >> .env.local
   ```

3. **Redeploy Frontend**:
   - Trigger a new Amplify build to pick up the new environment variables

---

## 🧪 Testing the Connection

### **Test Railway Backend**:
```bash
# Test health endpoint
curl https://your-railway-app.railway.app/api/health

# Test with our script
python test_railway_deployment.py https://your-railway-app.railway.app
```

### **Test Frontend → Backend Connection**:
1. Open your Amplify frontend URL
2. Try the skin analysis feature
3. Check browser network tab to confirm API calls go to Railway URL

---

## 📋 Environment Variables Summary

### **Railway Backend Needs:**
- ✅ Google Cloud Vision API credentials
- ✅ Supabase database connection
- ✅ FAISS configuration
- ✅ AI service weights
- ✅ Flask configuration

### **Amplify Frontend Needs:**
- ✅ Railway backend URL
- ✅ Supabase URL (for direct frontend access)
- ✅ Google OAuth credentials (for user auth)

### **Key Connection Point:**
The frontend's `NEXT_PUBLIC_BACKEND_URL` must point to your Railway deployment URL for the skin analysis API calls to work.