# 🔒 HTTPS ENABLEMENT GUIDE - MANUAL STEPS

## 🚨 **URGENT: MIXED CONTENT ERROR BLOCKING REQUESTS**

**Current Error**: Browser blocking HTTP requests from HTTPS frontend
**Solution**: Enable HTTPS on Elastic Beanstalk environment

## 📋 **STEP-BY-STEP MANUAL SETUP**

### **Step 1: Create SSL Certificate**

1. **AWS Certificate Manager Console**
   - URL: https://console.aws.amazon.com/acm/
   - Region: **us-east-1** (IMPORTANT!)

2. **Request Certificate**
   - Click "Request certificate"
   - Domain name: `shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com`
   - Validation method: **DNS**
   - Click "Request certificate"

3. **Validate Certificate**
   - Copy the DNS records provided
   - Add them to your domain's DNS settings
   - Wait for validation (5-10 minutes)
   - Status should change to "Issued"

### **Step 2: Enable HTTPS on Elastic Beanstalk**

1. **Elastic Beanstalk Console**
   - URL: https://console.aws.amazon.com/elasticbeanstalk/
   - Select environment: **SHINE-env**

2. **Configure Load Balancer**
   - Click "Configuration" tab
   - Under "Load balancer", click "Edit"
   - **Enable HTTPS:**
     - ✅ Check "Enable HTTPS"
     - Port: **443**
     - Protocol: **HTTPS**
     - SSL Certificate: **Select your certificate**
   - **Save changes**

3. **Wait for Update**
   - Environment will update (5-10 minutes)
   - Status should remain "Ready"

### **Step 3: Test HTTPS**

Once enabled, test:
```bash
curl -I https://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/health
```

Expected response:
```
HTTP/2 200
```

### **Step 4: Update Frontend (After HTTPS is Working)**

Once HTTPS is confirmed working, I'll update:
- `app/page.tsx`
- `app/test/page.tsx`
- `lib/api.ts`

## 🦄 **UNICORN ALPHA BACKEND STATUS**

**Current URL**: `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com`
**Status**: ✅ **LIVE AND OPERATIONAL**
**Response**: `{"message":"🦄 UNICORN ALPHA FIXED is running!","ml_available":true}`

## 🎯 **EXPECTED RESULTS**

After HTTPS is enabled:
- ✅ **No Mixed Content errors**
- ✅ **No CORS errors**
- ✅ **File uploads work** (up to 100MB)
- ✅ **ML analysis works**
- ✅ **All API calls succeed**

## 📞 **IMMEDIATE ACTION REQUIRED**

**Please complete Steps 1-2 above in the AWS Console, then let me know when HTTPS is working so I can update the frontend!**

---

**🚨 URGENT**: The Mixed Content error is blocking all API calls. HTTPS must be enabled on the EB environment. 