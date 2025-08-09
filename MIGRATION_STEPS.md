# 🚀 Migration Steps for New GitHub Repositories

## 📋 Overview
This guide will help you migrate your Shine Skincare App to the new separate repositories:
- **Frontend**: [https://github.com/mcpmessenger/shine-frontend](https://github.com/mcpmessenger/shine-frontend)
- **Backend**: [https://github.com/mcpmessenger/shine-backend](https://github.com/mcpmessenger/shine-backend)

## 🔧 Step 1: Set Up Backend Repository

### **1.1 Clone the Backend Repository**
```bash
cd ..
git clone https://github.com/mcpmessenger/shine-backend.git
cd shine-backend
```

### **1.2 Copy Backend Files**
```bash
# Copy all backend files from current project
cp -r ../shine-skincare-app/backend/* .
cp ../shine-skincare-app/backend/requirements.txt .
cp ../shine-skincare-app/backend/Procfile .
cp ../shine-skincare-app/backend/deploy.sh .
cp -r ../shine-skincare-app/backend/.ebextensions .

# Copy deployment documentation
cp ../shine-skincare-app/DEPLOYMENT_GUIDE.md .
cp ../shine-skincare-app/DEPLOYMENT_CHECKLIST.md .
cp ../shine-skincare-app/REPOSITORY_STRATEGY.md .
```

### **1.3 Create Backend README**
```bash
cat > README.md << 'EOF'
# Shine Skincare Backend

Flask API server for the Shine Skincare App with ML model integration.

## Features
- Skin condition analysis with ML model (62.50% accuracy)
- Face detection
- Product recommendations
- RESTful API endpoints

## Deployment
- AWS Elastic Beanstalk
- Python 3.11
- Gunicorn server

## Environment Variables
- FLASK_ENV=production
- MODEL_PATH=/var/app/current/fixed_model_final.h5

## Quick Start
```bash
pip install -r requirements.txt
python run_fixed_model_server.py
```

## Deployment
```bash
eb deploy
```

## API Endpoints
- `/api/v5/skin/analyze-fixed` - Skin analysis
- `/api/v4/face/detect` - Face detection
- `/api/v5/skin/health` - Health check
EOF
```

### **1.4 Push Backend to GitHub**
```bash
git add .
git commit -m "Initial backend setup with Flask API and ML model"
git push origin main
```

## 🎨 Step 2: Set Up Frontend Repository

### **2.1 Clone the Frontend Repository**
```bash
cd ..
git clone https://github.com/mcpmessenger/shine-frontend.git
cd shine-frontend
```

### **2.2 Copy Frontend Files**
```bash
# Copy frontend files from current project
cp -r ../shine-skincare-app/app .
cp -r ../shine-skincare-app/components .
cp -r ../shine-skincare-app/lib .
cp -r ../shine-skincare-app/public .
cp -r ../shine-skincare-app/hooks .
cp -r ../shine-skincare-app/types .

# Copy configuration files
cp ../shine-skincare-app/package.json .
cp ../shine-skincare-app/package-lock.json .
cp ../shine-skincare-app/next.config.mjs .
cp ../shine-skincare-app/tailwind.config.ts .
cp ../shine-skincare-app/tsconfig.json .
cp ../shine-skincare-app/postcss.config.mjs .
cp ../shine-skincare-app/.eslintrc.json .
cp ../shine-skincare-app/next-env.d.ts .

# Copy Amplify configuration
cp ../shine-skincare-app/amplify.yml .
```

### **2.3 Create Frontend README**
```bash
cat > README.md << 'EOF'
# Shine Frontend

Next.js frontend for the Shine Skincare App with shopping cart functionality.

## Features
- Skin analysis interface
- Product recommendations with images
- Shopping cart functionality
- Responsive design

## Deployment
- AWS Amplify
- Next.js 14
- TypeScript

## Environment Variables
- NEXT_PUBLIC_BACKEND_URL=https://your-eb-domain.elasticbeanstalk.com
- NEXT_PUBLIC_APP_NAME=Shine Skin Collective
- NEXT_PUBLIC_APP_VERSION=4.0.0

## Quick Start
```bash
npm install
npm run dev
```

## Build
```bash
npm run build
```

## Pages
- `/` - Main skin analysis page
- `/suggestions` - Results and product recommendations
EOF
```

### **2.4 Push Frontend to GitHub**
```bash
git add .
git commit -m "Initial frontend setup with Next.js and shopping cart"
git push origin main
```

## 🔄 Step 3: Update Environment Variables

### **3.1 Frontend Environment**
Create `.env.local` in the frontend repository:
```bash
# In shine-frontend directory
cat > .env.local << 'EOF'
NEXT_PUBLIC_BACKEND_URL=https://your-eb-domain.elasticbeanstalk.com
NEXT_PUBLIC_APP_NAME=Shine Skin Collective
NEXT_PUBLIC_APP_VERSION=4.0.0
EOF
```

### **3.2 Backend Environment**
Set these in AWS Elastic Beanstalk environment variables:
```
FLASK_ENV=production
MODEL_PATH=/var/app/current/fixed_model_final.h5
```

## 🚀 Step 4: Deploy to AWS

### **4.1 Deploy Backend (Elastic Beanstalk)**
```bash
cd shine-backend
pip install awsebcli
eb init shine-backend --platform python-3.11 --region us-east-1
eb create shine-backend-prod --instance-type t3.medium --single-instance
eb deploy
```

### **4.2 Deploy Frontend (Amplify)**
1. Go to AWS Amplify Console
2. Connect to `shine-frontend` repository
3. Configure build settings (use `amplify.yml`)
4. Set environment variables
5. Deploy

## 🔍 Step 5: Verify Deployment

### **5.1 Test Backend**
```bash
curl https://your-eb-domain.elasticbeanstalk.com/api/v5/skin/health
```

### **5.2 Test Frontend**
```bash
curl https://your-amplify-domain.amplifyapp.com
```

## 📊 Backup Strategy

### **GitHub Backup**
- ✅ **Frontend**: [shine-frontend](https://github.com/mcpmessenger/shine-frontend)
- ✅ **Backend**: [shine-backend](https://github.com/mcpmessenger/shine-backend)
- ✅ **Documentation**: Both repos include README files

### **Local Backup**
```bash
# Create local backups
cp -r shine-frontend shine-frontend-backup-$(date +%Y%m%d)
cp -r shine-backend shine-backend-backup-$(date +%Y%m%d)
```

## 🎯 Success Checklist

- [ ] Backend repository populated and pushed
- [ ] Frontend repository populated and pushed
- [ ] Environment variables configured
- [ ] Backend deployed to Elastic Beanstalk
- [ ] Frontend deployed to Amplify
- [ ] Health checks passing
- [ ] Shopping cart functionality working
- [ ] ML model responding correctly

## 🔐 Security Notes

- ✅ **Frontend repo**: Public, no sensitive data
- ✅ **Backend repo**: Private recommended, AWS credentials in environment variables
- ✅ **Model files**: Included in backend repo (if < 100MB)
- ✅ **No Kaggle credentials**: Removed from all repositories

## 📞 Support

If you encounter issues:
1. Check CloudWatch logs for backend
2. Check Amplify build logs for frontend
3. Verify environment variables
4. Test endpoints manually
