# Repository Separation Guide

## Why Separate?
- ✅ Independent deployments (no unnecessary frontend builds)
- ✅ Better security isolation
- ✅ Cleaner access controls
- ✅ Separate CI/CD pipelines

## Steps to Separate:

### 1. Create New Backend Repository
```bash
# Create new repo on GitHub: shine-skincare-backend
git clone https://github.com/your-username/shine-skincare-backend.git
cd shine-skincare-backend

# Copy backend files
cp -r ../shine-skincare-app/backend/* .
cp ../shine-skincare-app/.gitignore .

# Initial commit
git add .
git commit -m "Initial backend setup"
git push origin main
```

### 2. Update Frontend Repository
```bash
# In original repo, remove backend
rm -rf backend/
git add .
git commit -m "Remove backend - moved to separate repo"
git push origin main
```

### 3. Update API Endpoints in Frontend
```typescript
// Update API base URL in frontend
const API_BASE_URL = 'https://your-backend.eba-bpcnncyq.us-east-1.elasticbeanstalk.com'
```

## Current Deployment Setup (Monorepo)
If keeping monorepo, configure:

### AWS EB Settings:
- Root Directory: `backend`
- Watch Paths: `backend/**`

### AWS Amplify Settings:
- Build Settings: Ignore `backend/` changes
- Or use build conditions to skip builds when only backend changes