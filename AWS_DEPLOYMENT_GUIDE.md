# 🚀 AWS Deployment Guide - Fix HTTPS & Load Balancer

## 🎯 **Current Status:**
- ✅ **Local Development**: Working perfectly (`http://localhost:3000`)
- ✅ **Backend**: Deployed on AWS Elastic Beanstalk (HTTP working)
- ❌ **HTTPS**: Certificate validation failed
- ❌ **Load Balancer**: Configuration needs fixing

## 🔧 **Step 1: Fix the SSL Certificate Issue**

### **Problem:** Certificate doesn't have fully-qualified domain name

### **Solution A: Create New Certificate (Recommended)**

1. **Go to AWS Certificate Manager (ACM)**
   - AWS Console → Certificate Manager
   - Click "Request certificate"

2. **Request certificate for your domain:**
   ```
   shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com
   ```

3. **Choose validation method:**
   - **DNS validation** (recommended)
   - **Email validation** (alternative)

4. **Wait for certificate issuance** (5-10 minutes)

### **Solution B: Use Wildcard Certificate**

1. **Request certificate for:**
   ```
   *.elasticbeanstalk.com
   ```

2. **This covers all Elastic Beanstalk domains**

## 🔧 **Step 2: Fix Load Balancer Configuration**

### **Current Issue:** HTTPS listener failed due to certificate

### **Temporary Fix: Remove HTTPS Listener**

1. **Go to Elastic Beanstalk Console**
2. **Select environment**: `Shine-backend-poc-env-new-env`
3. **Click "Configuration"**
4. **Under "Load balancer", click "Edit"**
5. **Remove HTTPS listener:**
   - Delete the port 443 listener
   - Keep only HTTP listener (port 80)
6. **Save changes**

### **After Certificate is Ready: Re-add HTTPS**

1. **Go back to Load balancer configuration**
2. **Add listener:**
   - **Port**: 443
   - **Protocol**: HTTPS
   - **SSL Certificate**: Select your new certificate
3. **Save changes**

## 🔧 **Step 3: Update Frontend for Production**

### **Option A: Deploy Frontend to Amplify (Recommended)**

1. **Push your code to GitHub** (if not already done)
2. **Go to AWS Amplify Console**
3. **Connect your repository**
4. **Configure build settings:**
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
   ```

### **Option B: Environment Variables for HTTPS**

1. **In Amplify Console, go to "App settings" → "Environment variables"**
2. **Add variables:**
   ```
   NEXT_PUBLIC_BACKEND_URL=https://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com
   ```

## 🔧 **Step 4: Update Backend CORS for Production**

### **Current Issue:** CORS only allows localhost

Update your backend CORS configuration:

```python
# In your Flask app
CORS(app, origins=[
    'http://localhost:3000',
    'https://main.d3oid65kfbmqt4.amplifyapp.com',  # Your Amplify domain
    'https://your-custom-domain.com'  # If you have one
], supports_credentials=True)
```

## 🔧 **Step 5: Test the Complete Flow**

### **Local Testing (Current - Working)**
```bash
# Frontend
npm run dev
# Access: http://localhost:3000

# Backend (if needed locally)
cd backend
python simple_server_basic.py
# Access: http://localhost:5000
```

### **Production Testing**
1. **Deploy frontend to Amplify**
2. **Test HTTPS backend**: `https://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com`
3. **Test complete flow** from Amplify frontend

## 📋 **Deployment Checklist**

### **Backend (Elastic Beanstalk)**
- [ ] ✅ Environment is load balanced
- [ ] ✅ HTTP listener working (port 80)
- [ ] ✅ Create new SSL certificate
- [ ] ✅ Add HTTPS listener (port 443)
- [ ] ✅ Update CORS for production domains
- [ ] ✅ Test all API endpoints

### **Frontend (Amplify)**
- [ ] ✅ Code pushed to GitHub
- [ ] ✅ Amplify app connected to repository
- [ ] ✅ Build configuration set up
- [ ] ✅ Environment variables configured
- [ ] ✅ Deployed and accessible
- [ ] ✅ Test skin analysis feature

### **Integration**
- [ ] ✅ Frontend can reach backend
- [ ] ✅ No mixed content errors
- [ ] ✅ All features working
- [ ] ✅ Performance acceptable

## 🎯 **Expected Result**

After completion:
- **Frontend**: `https://main.d3oid65kfbmqt4.amplifyapp.com`
- **Backend**: `https://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com`
- **No mixed content errors**
- **Secure HTTPS communication**
- **All features working**

## 🚨 **Troubleshooting**

### **If HTTPS still doesn't work:**
1. **Check certificate status** in ACM
2. **Verify domain name** matches exactly
3. **Wait for certificate propagation** (up to 30 minutes)
4. **Check load balancer health** in EC2 console

### **If frontend can't reach backend:**
1. **Check CORS configuration**
2. **Verify environment variables**
3. **Test backend directly** with curl
4. **Check security groups** allow traffic

### **If deployment fails:**
1. **Check CloudFormation logs**
2. **Verify instance capacity** (t3.xlarge)
3. **Check application logs** in Elastic Beanstalk
4. **Rollback to previous version** if needed

---

**Next Steps:** Start with Step 1 (fix the certificate) and work through each step systematically. 