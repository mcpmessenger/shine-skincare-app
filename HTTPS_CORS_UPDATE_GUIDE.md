# HTTPS CORS Update Guide

## 🔄 **Update Backend CORS for HTTPS**

Once your HTTPS certificate is validated and working, update the CORS configuration:

### **File: `backend/simple_server_basic.py`**

**Current CORS (line 20):**
```python
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'], supports_credentials=True)
```

**Update to:**
```python
CORS(app, origins=[
    'http://localhost:3000', 
    'http://127.0.0.1:3000',
    'https://main.d3oid65kfbmqt4.amplifyapp.com',  # Your Amplify domain
    'https://your-custom-domain.com'  # If you have one
], supports_credentials=True)
```

### **Steps:**

1. **Update the CORS configuration** in your backend code
2. **Redeploy the backend** to Elastic Beanstalk
3. **Test the connection** with HTTPS

### **Deploy Backend:**

```bash
# Zip your backend files
cd backend
zip -r ../backend-deploy.zip .

# Deploy to Elastic Beanstalk
# (Use your existing deployment method)
```

### **Test HTTPS Connection:**

```bash
curl https://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com/api/health
```

## ✅ **Expected Result:**

- ✅ **HTTPS connection works**
- ✅ **Frontend can connect to backend**
- ✅ **No mixed content errors**
- ✅ **Secure data transmission**

## 🚨 **If HTTPS Still Doesn't Work:**

1. **Check certificate status** in AWS Certificate Manager
2. **Verify load balancer configuration** has HTTPS listener
3. **Check security groups** allow port 443
4. **Test with different browser** or incognito mode 