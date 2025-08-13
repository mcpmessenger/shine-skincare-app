# 🚀 Shine Skincare App - Deployment Pipeline & Workflow

## Overview
This document outlines the complete deployment pipeline from local development to production, ensuring smooth rollouts and minimal downtime.

## 🔄 Pipeline Stages

### 1. Local Development & Testing
```bash
# Start local development server
npm run dev

# Start local backend (if needed)
cd backend
python app.py
# or
python -m flask run --host=0.0.0.0 --port=5000
```

**Local Environment Variables** (`.env.local`):
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
NEXT_PUBLIC_AMPLIFY_APP_ID=your_amplify_app_id
NEXT_PUBLIC_AMPLIFY_REGION=us-east-1
```

**Testing Checklist**:
- [ ] Frontend loads without errors
- [ ] Backend API endpoints respond
- [ ] Face detection works locally
- [ ] Skin analysis works locally
- [ ] Cart functionality works
- [ ] Authentication flows work
- [ ] Responsive design on different screen sizes

### 2. Pre-Deployment Validation
```bash
# Build the application locally
npm run build

# Run linting and type checking
npm run lint
npm run type-check

# Run tests (if available)
npm test

# Check for build errors
npm run build:analyze
```

**Validation Checklist**:
- [ ] Build completes without errors
- [ ] No TypeScript errors
- [ ] No linting violations
- [ ] All tests pass
- [ ] Bundle size is acceptable
- [ ] No security vulnerabilities detected

### 3. Staging Deployment
**Create a staging branch**:
```bash
git checkout -b staging
git push origin staging
```

**Staging Environment Variables** (Amplify Console):
```env
NEXT_PUBLIC_BACKEND_URL=https://staging-backend-url
NEXT_PUBLIC_AMPLIFY_APP_ID=staging_app_id
NEXT_PUBLIC_AMPLIFY_REGION=us-east-1
```

**Staging Testing**:
- [ ] Deploy to staging environment
- [ ] Test all functionality in staging
- [ ] Verify backend connectivity
- [ ] Test face detection and skin analysis
- [ ] Validate responsive design
- [ ] Performance testing
- [ ] Security testing

### 4. Production Deployment
**Merge to main branch**:
```bash
git checkout main
git merge staging
git push origin main
```

**Production Environment Variables** (Amplify Console):
```env
NEXT_PUBLIC_BACKEND_URL=https://awseb--AWSEB-ydAUJ3jj2fwA-1083929952.us-east-1.elb.amazonaws.com
NEXT_PUBLIC_AMPLIFY_APP_ID=production_app_id
NEXT_PUBLIC_AMPLIFY_REGION=us-east-1
```

## 🛠️ Deployment Scripts

### Local Development Script
```bash
# scripts/dev-local.ps1
Write-Host "🚀 Starting Local Development Environment..." -ForegroundColor Green

# Check if backend is running
$backendProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($backendProcess) {
    Write-Host "✅ Backend is already running" -ForegroundColor Green
} else {
    Write-Host "🔄 Starting backend..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory "backend" -WindowStyle Minimized
    Start-Sleep -Seconds 3
}

# Start frontend
Write-Host "🔄 Starting frontend..." -ForegroundColor Yellow
npm run dev
```

### Staging Deployment Script
```bash
# scripts/deploy-staging.ps1
Write-Host "🚀 Deploying to Staging..." -ForegroundColor Green

# Create staging branch
git checkout -b staging
git add .
git commit -m "Deploy to staging - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git push origin staging

Write-Host "✅ Staging deployment initiated" -ForegroundColor Green
Write-Host "🔗 Check Amplify Console for build status" -ForegroundColor Blue
```

### Production Deployment Script
```bash
# scripts/deploy-production.ps1
Write-Host "🚀 Deploying to Production..." -ForegroundColor Green

# Merge staging to main
git checkout main
git merge staging
git push origin main

Write-Host "✅ Production deployment initiated" -ForegroundColor Green
Write-Host "🔗 Check Amplify Console for build status" -ForegroundColor Blue
```

## 🔍 Health Check Scripts

### Backend Health Check
```bash
# scripts/health-check.ps1
$backendUrl = "https://awseb--AWSEB-ydAUJ3jj2fwA-1083929952.us-east-1.elb.amazonaws.com/api/health"

Write-Host "🔍 Checking backend health..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $backendUrl -Method Get -TimeoutSec 10
    Write-Host "✅ Backend is healthy: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}
```

### Frontend Health Check
```bash
# scripts/frontend-health.ps1
$frontendUrl = "https://main.d2ej0h04rafihr.amplifyapp.com"

Write-Host "🔍 Checking frontend health..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri $frontendUrl -Method Get -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is healthy: Status $($response.StatusCode)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Frontend returned status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Frontend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests pass locally
- [ ] Code review completed
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Database migrations ready (if applicable)

### During Deployment
- [ ] Monitor build logs
- [ ] Check for deployment errors
- [ ] Verify environment variables
- [ ] Test critical functionality
- [ ] Monitor error rates
- [ ] Check performance metrics

### Post-Deployment
- [ ] Verify all features work
- [ ] Check error monitoring
- [ ] Monitor user experience
- [ ] Validate analytics
- [ ] Update deployment documentation
- [ ] Schedule post-deployment review

## 🚨 Rollback Procedures

### Quick Rollback
```bash
# Revert to previous commit
git revert HEAD
git push origin main
```

### Emergency Rollback
```bash
# Force push to previous working version
git reset --hard HEAD~1
git push --force origin main
```

## 🔧 Environment Management

### Environment-Specific Configs
```typescript
// lib/config.ts
const config = {
  development: {
    backendUrl: 'http://localhost:5000',
    apiTimeout: 10000,
    debugMode: true
  },
  staging: {
    backendUrl: 'https://staging-backend-url',
    apiTimeout: 15000,
    debugMode: true
  },
  production: {
    backendUrl: 'https://awseb--AWSEB-ydAUJ3jj2fwA-1083929952.us-east-1.elb.amazonaws.com',
    apiTimeout: 20000,
    debugMode: false
  }
};

export const getConfig = () => {
  const env = process.env.NODE_ENV || 'development';
  return config[env] || config.development;
};
```

## 📊 Monitoring & Alerts

### Key Metrics to Monitor
- [ ] API response times
- [ ] Error rates
- [ ] User session duration
- [ ] Feature usage rates
- [ ] Performance metrics
- [ ] Security events

### Alert Thresholds
- [ ] API errors > 5%
- [ ] Response time > 3 seconds
- [ ] Failed authentication > 10%
- [ ] Face detection failures > 15%

## 🎯 Best Practices

1. **Always test locally first**
2. **Use feature flags for risky changes**
3. **Deploy during low-traffic periods**
4. **Have a rollback plan ready**
5. **Monitor closely after deployment**
6. **Document all changes**
7. **Train team on deployment procedures**
8. **Regular backup and recovery testing**

## 🔗 Useful Commands

```bash
# Check current environment
echo $NODE_ENV

# View build logs
npm run build --verbose

# Check bundle size
npm run build:analyze

# Run security audit
npm audit

# Update dependencies
npm update

# Clean install
rm -rf node_modules package-lock.json
npm install
```

## 📞 Emergency Contacts

- **DevOps Lead**: [Your Name]
- **Backend Engineer**: [Backend Team]
- **Frontend Engineer**: [Frontend Team]
- **System Administrator**: [SysAdmin]

---

*Last Updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')*
*Version: 1.0*
