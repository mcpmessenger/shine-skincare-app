# 🚀 Deployment Checklist

## ✅ Pre-Deployment Checklist

### 🔒 Security
- [ ] Kaggle credentials removed from repository
- [ ] No sensitive data in committed files
- [ ] Environment variables configured
- [ ] CORS settings updated for production

### 📁 File Structure
- [ ] Large dataset files excluded from git
- [ ] ML model files properly included
- [ ] Backend deployment files created
- [ ] Frontend build configuration ready

### 🔧 Backend (Elastic Beanstalk)
- [ ] `requirements.txt` updated with all dependencies
- [ ] `Procfile` configured for Gunicorn
- [ ] `.ebextensions/01_flask.config` created
- [ ] `deploy.sh` script ready
- [ ] Model file `fixed_model_final.h5` in backend directory
- [ ] Flask app `run_fixed_model_server.py` ready

### 🎨 Frontend (Amplify)
- [ ] `amplify.yml` build configuration created
- [ ] `package.json` dependencies up to date
- [ ] Environment variables configured
- [ ] API routes point to backend URL
- [ ] Build commands working locally

### 📊 ML Model
- [ ] Model file size < 100MB (GitHub limit)
- [ ] Model loads successfully in Flask
- [ ] All dependencies in requirements.txt
- [ ] Model accuracy documented (62.50%)

## 🚀 Deployment Steps

### Step 1: Backend Deployment
```bash
cd backend
pip install awsebcli
eb init shine-backend --platform python-3.11 --region us-east-1
eb create shine-backend-prod --instance-type t3.medium --single-instance
eb deploy
```

### Step 2: Frontend Deployment
```bash
# In AWS Amplify Console
1. Connect GitHub repository
2. Configure build settings (amplify.yml)
3. Set environment variables
4. Deploy
```

### Step 3: Environment Variables
```
NEXT_PUBLIC_BACKEND_URL=https://your-eb-domain.elasticbeanstalk.com
NEXT_PUBLIC_APP_NAME=Shine Skin Collective
NEXT_PUBLIC_APP_VERSION=4.0.0
```

## 🔍 Post-Deployment Verification

### Backend Health Check
```bash
curl https://your-eb-domain.elasticbeanstalk.com/api/v5/skin/health
```

### Frontend Health Check
```bash
curl https://your-amplify-domain.amplifyapp.com
```

### ML Model Test
```bash
# Test skin analysis endpoint
curl -X POST https://your-eb-domain.elasticbeanstalk.com/api/v5/skin/analyze-fixed \
  -F "image=@test-image.jpg"
```

## 📊 Monitoring Setup

### Backend Monitoring
- [ ] CloudWatch logs enabled
- [ ] Health checks configured
- [ ] Auto-scaling rules set
- [ ] Error alerts configured

### Frontend Monitoring
- [ ] Amplify console monitoring
- [ ] Build status tracking
- [ ] Performance insights enabled

## 🔄 CI/CD Pipeline

### Frontend (Amplify)
- [ ] Automatic builds on git push
- [ ] Preview deployments for PRs
- [ ] Production deployment on main branch

### Backend (EB)
- [ ] Manual deployment via EB CLI
- [ ] Blue-green deployments available
- [ ] Rollback capability

## 🛠️ Troubleshooting

### Common Issues
1. **Backend Connection Failed**
   - Check environment variables
   - Verify EB domain is correct
   - Test backend health endpoint

2. **ML Model Not Loading**
   - Ensure model file is in backend directory
   - Check file permissions
   - Verify model path in environment

3. **Frontend Build Fails**
   - Check Node.js version compatibility
   - Verify all dependencies in package.json
   - Check build logs in Amplify console

## 📈 Performance Optimization

### Backend
- [ ] Gunicorn workers configured (2 workers)
- [ ] Timeout settings optimized (120s)
- [ ] Auto-scaling configured (1-4 instances)

### Frontend
- [ ] Next.js build optimized
- [ ] Static assets compressed
- [ ] CDN distribution enabled

## 🔒 Security Checklist

### Environment Variables
- [ ] No sensitive data in code
- [ ] AWS Systems Manager for secrets
- [ ] Credentials rotated regularly

### CORS Configuration
- [ ] Allowed origins configured
- [ ] API access limited
- [ ] HTTPS only enforced

### Model Security
- [ ] Model file secured
- [ ] Rate limiting implemented
- [ ] API usage monitored

## ✅ Final Verification

### Functional Tests
- [ ] Skin analysis works
- [ ] Product recommendations display
- [ ] Cart functionality works
- [ ] Face detection works
- [ ] All API endpoints respond

### Performance Tests
- [ ] Page load times < 3s
- [ ] API response times < 10s
- [ ] Model inference < 30s
- [ ] Concurrent users supported

### Security Tests
- [ ] HTTPS enforced
- [ ] CORS properly configured
- [ ] No sensitive data exposed
- [ ] Rate limiting active

## 📞 Support Contacts

- **AWS Support**: For infrastructure issues
- **Amplify Console**: For frontend deployment issues
- **EB Console**: For backend deployment issues
- **CloudWatch**: For monitoring and logs
