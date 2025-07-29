# 🚨 Immediate Fixes - Step by Step

## 🎯 **Priority 1: Fix the Certificate Issue**

### **Step 1: Remove Failed HTTPS Listener**
1. **Go to AWS Elastic Beanstalk Console**
2. **Select**: `Shine-backend-poc-env-new-env`
3. **Click**: "Configuration"
4. **Under "Load balancer", click**: "Edit"
5. **Remove the HTTPS listener** (port 443) that's causing the error
6. **Keep only HTTP listener** (port 80)
7. **Click**: "Apply"

### **Step 2: Create New SSL Certificate**
1. **Go to AWS Certificate Manager**
2. **Click**: "Request certificate"
3. **Domain name**: `shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com`
4. **Validation**: Choose DNS validation
5. **Click**: "Request"
6. **Wait**: 5-10 minutes for issuance

### **Step 3: Re-add HTTPS Listener**
1. **Go back to Elastic Beanstalk Configuration**
2. **Load balancer → Edit**
3. **Add listener**:
   - **Port**: 443
   - **Protocol**: HTTPS
   - **SSL Certificate**: Select your new certificate
4. **Click**: "Apply"

## 🎯 **Priority 2: Update Backend CORS**

### **Step 1: Update CORS Configuration**
In your backend code, update the CORS origins:

```python
# In backend/simple_server_basic.py or your Flask app
CORS(app, origins=[
    'http://localhost:3000',
    'https://main.d3oid65kfbmqt4.amplifyapp.com',  # Your Amplify domain
    'http://main.d3oid65kfbmqt4.amplifyapp.com'    # HTTP fallback
], supports_credentials=True)
```

### **Step 2: Redeploy Backend**
1. **Create new deployment package**
2. **Upload to Elastic Beanstalk**
3. **Wait for deployment to complete**

## 🎯 **Priority 3: Update Frontend for HTTPS**

### **Step 1: Update API Configuration**
Once HTTPS is working, update your frontend:

```javascript
// In lib/api.ts
this.baseUrl = 'https://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com';
```

### **Step 2: Deploy to Amplify**
1. **Push code to GitHub**
2. **Amplify will auto-deploy**
3. **Test the complete flow**

## 🎯 **Testing Checklist**

### **Local Testing (Current - Working)**
- [ ] ✅ `http://localhost:3000` works
- [ ] ✅ Skin analysis works
- [ ] ✅ No mixed content errors

### **Backend Testing**
- [ ] ✅ HTTP endpoint works: `http://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com/api/health`
- [ ] ✅ HTTPS endpoint works: `https://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com/api/health`
- [ ] ✅ CORS allows Amplify domain

### **Production Testing**
- [ ] ✅ Amplify frontend deployed
- [ ] ✅ Can reach HTTPS backend
- [ ] ✅ Skin analysis works in production
- [ ] ✅ No mixed content errors

## 🚨 **If Something Goes Wrong**

### **Rollback Plan**
1. **Keep HTTP listener only** (remove HTTPS)
2. **Use local development** for testing
3. **Fix certificate issues** before re-adding HTTPS

### **Alternative: HTTP-Only Production**
If HTTPS continues to fail:
1. **Keep HTTP backend**
2. **Configure Amplify for HTTP**
3. **Accept mixed content** (not recommended for production)

---

**Start with Step 1** - Remove the failed HTTPS listener first, then create a new certificate. 