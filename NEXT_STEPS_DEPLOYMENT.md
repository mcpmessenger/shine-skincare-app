# 🚀 Next Steps: AWS Deployment Guide

## 📋 Current Status
✅ **Repositories Created and Populated:**
- **Frontend**: [https://github.com/mcpmessenger/shine-frontend](https://github.com/mcpmessenger/shine-frontend)
- **Backend**: [https://github.com/mcpmessenger/shine-backend](https://github.com/mcpmessenger/shine-backend)

## 🎯 Deployment Order

### **Step 1: Deploy Backend First (Elastic Beanstalk)**
*Deploy backend first to get the API URL for frontend configuration*

#### **1.1 Clone Backend Repository**
```bash
cd ..
git clone https://github.com/mcpmessenger/shine-backend.git
cd shine-backend
```

#### **1.2 Install EB CLI**
```bash
pip install awsebcli
```

#### **1.3 Configure AWS Credentials**
```bash
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output format: json
```

#### **1.4 Initialize Elastic Beanstalk**
```bash
eb init shine-backend --platform python-3.11 --region us-east-1
```

#### **1.5 Create Environment**
```bash
eb create shine-backend-prod --instance-type t3.medium --single-instance
```

#### **1.6 Deploy**
```bash
eb deploy
```

#### **1.7 Get Backend URL**
```bash
eb status
# Note the CNAME URL (e.g., shine-backend-prod.us-east-1.elasticbeanstalk.com)
```

### **Step 2: Deploy Frontend (AWS Amplify)**
*Deploy frontend using the backend URL*

#### **2.1 Go to AWS Amplify Console**
1. Open [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click "New app" → "Host web app"
3. Choose "GitHub" as source

#### **2.2 Connect Repository**
1. Authorize GitHub access
2. Select repository: `mcpmessenger/shine-frontend`
3. Select branch: `main`

#### **2.3 Configure Build Settings**
1. Framework: **Next.js**
2. Build command: `npm run build`
3. Output directory: `.next`
4. Build specification: **Use amplify.yml**

#### **2.4 Set Environment Variables**
```
NEXT_PUBLIC_BACKEND_URL=https://your-eb-domain.elasticbeanstalk.com
NEXT_PUBLIC_APP_NAME=Shine Skin Collective
NEXT_PUBLIC_APP_VERSION=4.0.0
```
*Replace `your-eb-domain.elasticbeanstalk.com` with your actual backend URL*

#### **2.5 Deploy**
1. Click "Save and deploy"
2. Wait for build to complete (~5-10 minutes)
3. Note the Amplify app URL

## 🔍 Step 3: Verify Deployment

### **3.1 Test Backend**
```bash
# Health check
curl https://your-eb-domain.elasticbeanstalk.com/api/v5/skin/health

# Model status
curl https://your-eb-domain.elasticbeanstalk.com/api/v5/skin/model-status
```

### **3.2 Test Frontend**
1. Visit your Amplify app URL
2. Test image upload
3. Verify skin analysis works
4. Test shopping cart functionality

### **3.3 Test Integration**
1. Upload image on frontend
2. Verify it calls backend API
3. Check results display correctly
4. Test product recommendations

## 📊 Step 4: Monitor and Optimize

### **4.1 Backend Monitoring**
- **CloudWatch Logs**: Monitor for errors
- **Health Dashboard**: Check instance health
- **Performance**: Monitor response times

### **4.2 Frontend Monitoring**
- **Amplify Console**: Check build status
- **Performance**: Monitor page load times
- **Error Tracking**: Check for JavaScript errors

## 🔧 Step 5: Configuration Updates

### **5.1 Update Backend Environment Variables**
```bash
eb setenv FLASK_ENV=production MODEL_PATH=/var/app/current/fixed_model_final.h5
```

### **5.2 Update Frontend Environment Variables**
In Amplify Console → Environment Variables:
```
NEXT_PUBLIC_BACKEND_URL=https://your-actual-eb-domain.elasticbeanstalk.com
```

## 🚨 Troubleshooting Common Issues

### **Backend Issues**
1. **Deployment fails**: Check requirements.txt and Python version
2. **Model not loading**: Verify model file is in repository
3. **Health check fails**: Check CloudWatch logs

### **Frontend Issues**
1. **Build fails**: Check Node.js version and dependencies
2. **API calls fail**: Verify backend URL in environment variables
3. **CORS errors**: Check backend CORS configuration

### **Integration Issues**
1. **Connection refused**: Verify backend is running and accessible
2. **Environment variables**: Ensure frontend has correct backend URL
3. **SSL/HTTPS**: Ensure both use HTTPS in production

## ✅ Success Checklist

### **Backend Deployment**
- [ ] EB CLI installed
- [ ] AWS credentials configured
- [ ] Backend deployed successfully
- [ ] Health endpoint responding
- [ ] Model status endpoint working
- [ ] CloudWatch logs showing no errors

### **Frontend Deployment**
- [ ] Amplify app created
- [ ] Repository connected
- [ ] Environment variables set
- [ ] Build successful
- [ ] App accessible via URL
- [ ] No console errors

### **Integration Testing**
- [ ] Frontend can reach backend
- [ ] Image upload works
- [ ] Skin analysis completes
- [ ] Results display correctly
- [ ] Shopping cart functions
- [ ] No CORS errors

## 🎯 Expected Timeline

### **Backend Deployment**
- Setup: 5 minutes
- Initial deployment: 10-15 minutes
- Testing: 5 minutes
- **Total: ~25 minutes**

### **Frontend Deployment**
- Setup: 5 minutes
- Build and deployment: 5-10 minutes
- Testing: 5 minutes
- **Total: ~20 minutes**

### **Total Deployment Time: ~45 minutes**

## 📞 Support Resources

### **AWS Documentation**
- [Elastic Beanstalk Guide](https://docs.aws.amazon.com/elasticbeanstalk/)
- [Amplify Documentation](https://docs.amplify.aws/)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)

### **Troubleshooting**
- **EB Logs**: `eb logs`
- **Amplify Build Logs**: Check in Amplify Console
- **CloudWatch**: Monitor application logs

## 🚀 Post-Deployment Tasks

### **1. Performance Optimization**
- Monitor response times
- Optimize image sizes
- Configure CDN

### **2. Security**
- Enable HTTPS
- Configure security groups
- Set up monitoring alerts

### **3. Scaling**
- Configure auto-scaling
- Set up load balancing
- Monitor resource usage

## 🎉 Congratulations!

Once both deployments are successful, you'll have:
- ✅ **Scalable backend** on AWS Elastic Beanstalk
- ✅ **Fast frontend** on AWS Amplify with CDN
- ✅ **Independent deployments** for each component
- ✅ **Proper backup** with separate GitHub repositories
- ✅ **Production-ready** Shine Skincare App

Ready to start with the backend deployment? 🚀
