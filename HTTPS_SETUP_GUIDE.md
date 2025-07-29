# 🔒 HTTPS Setup Guide for Elastic Beanstalk

## 🚨 **Current Issue: Mixed Content Error**

Your frontend is served over HTTPS (AWS Amplify), but your backend uses HTTP, causing browsers to block requests for security reasons.

**Error:** `Mixed Content: The page at 'https://main.d3oid65kfbmqt4.amplifyapp.com/skin-analysis' was loaded over HTTPS, but requested an insecure resource 'http://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest'`

## 🎯 **Solution: Enable HTTPS on Elastic Beanstalk**

### **Option 1: Configure HTTPS in Elastic Beanstalk Console (Recommended)**

1. **Go to AWS Elastic Beanstalk Console**
2. **Select your environment**: `Shine-backend-poc-env-new-env`
3. **Click "Configuration"**
4. **Under "Load balancer" section, click "Edit"**
5. **Enable HTTPS:**
   - Check "Enable HTTPS"
   - Choose "Application Load Balancer" if not already selected
   - Select a certificate (or create one in ACM)
   - Set port 443 for HTTPS
6. **Save changes**

### **Option 2: Use AWS Certificate Manager (ACM)**

1. **Create SSL Certificate:**
   - Go to AWS Certificate Manager
   - Request a certificate for your domain
   - Validate the certificate
2. **Configure Load Balancer:**
   - In Elastic Beanstalk configuration
   - Add HTTPS listener on port 443
   - Attach your SSL certificate

### **Option 3: Quick Fix - Use HTTP for Frontend (Temporary)**

If you need a quick fix while setting up HTTPS:

1. **Deploy frontend to use HTTP instead of HTTPS**
2. **Update Amplify settings to serve over HTTP**
3. **This will allow mixed content (not recommended for production)**

## 🔧 **Immediate Workaround**

For now, you can test your application by:

1. **Using local development server** (which uses HTTP):
   ```bash
   npm run dev
   ```
   Then access: `http://localhost:3000`

2. **Or temporarily disable HTTPS enforcement** in your browser (for testing only)

## 📋 **Next Steps**

1. **Choose Option 1** (recommended) to enable HTTPS on your backend
2. **Update the frontend URLs** to use HTTPS once backend is configured
3. **Test the complete flow** with HTTPS

## 🎯 **Expected Result**

After enabling HTTPS on your backend:
- Frontend: `https://main.d3oid65kfbmqt4.amplifyapp.com`
- Backend: `https://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com`
- No more mixed content errors
- Secure communication between frontend and backend

---

**Note:** The current configuration uses HTTP for the backend, which works for local development but causes mixed content errors when the frontend is served over HTTPS. 