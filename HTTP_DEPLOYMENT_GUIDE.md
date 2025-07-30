# 🚀 HTTP-Only Deployment Guide (Quick Fix)

## 🎯 **Goal:** Deploy working app without HTTPS complexity

Since HTTPS certificate creation is causing issues, let's deploy with HTTP first and add HTTPS later.

## 🔧 **Step 1: Remove HTTPS Listener (Fix Current Error)**

1. **Go to AWS Elastic Beanstalk Console**
2. **Select**: `Shine-backend-poc-env-new-env`
3. **Click**: "Configuration"
4. **Under "Load balancer", click**: "Edit"
5. **Remove the HTTPS listener** (port 443) that's causing the error
6. **Keep only HTTP listener** (port 80)
7. **Click**: "Apply"

## 🔧 **Step 2: Update Backend CORS for Amplify**

Update your backend CORS to allow your Amplify domain:

```python
# In backend/simple_server_basic.py
CORS(app, origins=[
    'http://localhost:3000',
    'https://main.d3oid65kfbmqt4.amplifyapp.com',  # Your Amplify domain
    'http://main.d3oid65kfbmqt4.amplifyapp.com'    # HTTP fallback
], supports_credentials=True)
```

## 🔧 **Step 3: Deploy Updated Backend**

1. **Create deployment package:**
   ```bash
   cd backend
   zip -r deployment.zip . -x "*.pyc" "__pycache__/*" ".git/*"
   ```

2. **Upload to Elastic Beanstalk:**
   - Go to Elastic Beanstalk Console
   - Select your environment
   - Click "Upload and Deploy"
   - Upload the deployment.zip file

## 🔧 **Step 4: Configure Amplify for HTTP**

### **Option A: Environment Variables**
1. **In Amplify Console, go to "App settings" → "Environment variables"**
2. **Add variable:**
   ```
   NEXT_PUBLIC_BACKEND_URL=http://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com
   ```

### **Option B: Update Code**
Update your frontend to use HTTP:

```javascript
// In lib/api.ts
this.baseUrl = 'http://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com';
```

## 🔧 **Step 5: Deploy Frontend to Amplify**

1. **Push your code to GitHub**
2. **Amplify will auto-deploy**
3. **Test the complete flow**

## 🎯 **Expected Result**

After completion:
- **Frontend**: `https://main.d3oid65kfbmqt4.amplifyapp.com` (HTTPS)
- **Backend**: `http://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com` (HTTP)
- **Mixed content warning** (acceptable for development)
- **All features working**

## 🚨 **Important Notes**

- **Mixed content warning**: Browser will show a warning about HTTP/HTTPS mix
- **Development acceptable**: This works for development and testing
- **Production upgrade**: Add HTTPS later when certificate issues are resolved

## 📋 **Testing Checklist**

- [ ] ✅ Backend HTTP endpoint works
- [ ] ✅ Frontend deployed to Amplify
- [ ] ✅ Skin analysis works (with mixed content warning)
- [ ] ✅ All features functional

## 🔄 **Next Steps (After HTTP Works)**

1. **Test everything works with HTTP**
2. **Create proper SSL certificate** (without protocol)
3. **Add HTTPS listener back**
4. **Update frontend to use HTTPS**

---

**Start with Step 1** - Remove the failed HTTPS listener to stop the deployment errors. 