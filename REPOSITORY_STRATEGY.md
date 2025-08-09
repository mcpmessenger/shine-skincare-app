# 🏗️ Repository Strategy for AWS Deployment

## 📋 Overview
This document outlines the recommended repository structure for deploying the Shine Skincare App to AWS with proper backup and separation.

## 🎯 Recommended Approach: Separate Repositories

### **Why Separate Repositories?**
- ✅ **Independent deployments** - Frontend and backend can deploy separately
- ✅ **Better backup** - Each component has its own git history
- ✅ **Team collaboration** - Different teams can work on different repos
- ✅ **AWS integration** - Amplify and EB work better with focused repos
- ✅ **Security** - Backend credentials separate from frontend code

## 📁 Repository Structure

### **1. Frontend Repository: `shine-frontend`**
```
shine-frontend/
├── app/                    # Next.js app directory
├── components/             # React components
├── lib/                    # Utility functions
├── public/                 # Static assets
├── amplify.yml            # Amplify build config
├── package.json           # Dependencies
├── next.config.mjs        # Next.js config
├── tailwind.config.ts     # Styling
└── README.md              # Frontend documentation
```

### **2. Backend Repository: `shine-backend`**
```
shine-backend/
├── run_fixed_model_server.py    # Main Flask app
├── simple_fixed_integration.py  # ML integration
├── fixed_model_final.h5         # Trained model
├── requirements.txt             # Python dependencies
├── Procfile                    # Gunicorn config
├── .ebextensions/              # EB configuration
│   └── 01_flask.config
├── deploy.sh                   # Deployment script
└── README.md                   # Backend documentation
```

## 🚀 Migration Steps

### **Step 1: Create Backend Repository**
```bash
# Create new backend repository
mkdir shine-backend
cd shine-backend

# Initialize git
git init
git remote add origin https://github.com/your-username/shine-backend.git

# Copy backend files
cp -r ../shine-skincare-app/backend/* .
cp ../shine-skincare-app/DEPLOYMENT_GUIDE.md .
cp ../shine-skincare-app/DEPLOYMENT_CHECKLIST.md .
```

### **Step 2: Clean Frontend Repository**
```bash
# In shine-skincare-app (frontend repo)
# Remove backend files
rm -rf backend/
rm -rf ML-2folder/
rm -rf *.md (except frontend-specific docs)

# Keep only frontend files
# - app/
# - components/
# - lib/
# - public/
# - amplify.yml
# - package.json
# - etc.
```

### **Step 3: Update Environment Variables**
```bash
# Frontend (.env.local)
NEXT_PUBLIC_BACKEND_URL=https://your-eb-domain.elasticbeanstalk.com
NEXT_PUBLIC_APP_NAME=Shine Skin Collective
NEXT_PUBLIC_APP_VERSION=4.0.0

# Backend (EB Environment Variables)
FLASK_ENV=production
MODEL_PATH=/var/app/current/fixed_model_final.h5
```

## 🔄 Deployment Workflow

### **Frontend Deployment (Amplify)**
```bash
# In shine-frontend repository
git add .
git commit -m "Update frontend with new features"
git push origin main
# Amplify automatically deploys
```

### **Backend Deployment (Elastic Beanstalk)**
```bash
# In shine-backend repository
cd shine-backend
eb deploy
# Or use deploy.sh script
./deploy.sh
```

## 📊 Backup Strategy

### **GitHub Backup**
- ✅ **Frontend**: `shine-frontend` repository
- ✅ **Backend**: `shine-backend` repository
- ✅ **Documentation**: Both repos include README files
- ✅ **Deployment guides**: Included in each repo

### **AWS Backup**
- ✅ **Frontend**: Amplify automatically backs up builds
- ✅ **Backend**: EB creates snapshots
- ✅ **Database**: RDS snapshots (if using database)
- ✅ **Model files**: S3 backup for ML models

### **Local Backup**
```bash
# Create local backups
cp -r shine-frontend shine-frontend-backup-$(date +%Y%m%d)
cp -r shine-backend shine-backend-backup-$(date +%Y%m%d)
```

## 🔐 Security Considerations

### **Frontend Repository**
- ✅ No sensitive credentials
- ✅ Environment variables for backend URL
- ✅ Public repository safe

### **Backend Repository**
- ✅ Private repository recommended
- ✅ AWS credentials in environment variables
- ✅ Model files included (if < 100MB)
- ✅ No Kaggle credentials

## 🛠️ Alternative: Monorepo Approach

If you prefer to keep everything in one repository:

### **Structure**
```
shine-skincare-app/
├── frontend/              # Next.js app
│   ├── app/
│   ├── components/
│   ├── amplify.yml
│   └── package.json
├── backend/               # Flask API
│   ├── run_fixed_model_server.py
│   ├── requirements.txt
│   └── Procfile
├── docs/                  # Documentation
└── scripts/               # Deployment scripts
```

### **Pros**
- ✅ Single repository to manage
- ✅ Shared documentation
- ✅ Easier to coordinate changes

### **Cons**
- ❌ Mixed deployment concerns
- ❌ Larger repository size
- ❌ Harder to set different permissions

## 📋 Migration Checklist

### **For Separate Repositories**
- [ ] Create `shine-backend` repository
- [ ] Copy backend files to new repo
- [ ] Clean frontend repository
- [ ] Update environment variables
- [ ] Test both deployments
- [ ] Update documentation
- [ ] Set up CI/CD for both repos

### **For Monorepo**
- [ ] Reorganize current structure
- [ ] Update deployment scripts
- [ ] Configure Amplify for subdirectory
- [ ] Configure EB for subdirectory
- [ ] Test deployments

## 🎯 Recommendation

**Use Separate Repositories** because:
1. **Better AWS integration** - Amplify and EB work optimally
2. **Independent scaling** - Each component can scale separately
3. **Security** - Backend credentials isolated
4. **Team collaboration** - Different teams can work independently
5. **Backup** - Each component has its own git history

## 🚀 Next Steps

1. **Choose your approach** (separate repos or monorepo)
2. **Create the new repository structure**
3. **Migrate files accordingly**
4. **Update deployment configurations**
5. **Test both deployments**
6. **Update documentation**

Would you like me to help you implement either approach?
