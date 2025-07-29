# Custom Domain Setup Guide for shineskincollective.com

## 🎯 **Target Configuration**

```
Backend: https://api.shineskincollective.com → Elastic Beanstalk
Frontend: https://app.shineskincollective.com → AWS Amplify
```

## 🔧 **Step 1: Create SSL Certificate**

### **AWS Certificate Manager**
1. **Go to AWS Certificate Manager**
2. **Request certificate**
3. **Add domains:**
   ```
   api.shineskincollective.com
   app.shineskincollective.com
   *.shineskincollective.com
   ```
4. **Choose "DNS validation"**
5. **Add CNAME records** to your DNS provider

## 🌐 **Step 2: DNS Configuration**

### **Add these DNS records:**

#### **For Backend (Elastic Beanstalk):**
```
Type: CNAME
Name: api
Value: shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com
TTL: 300
```

#### **For Frontend (Amplify):**
```
Type: CNAME
Name: app
Value: [Your Amplify domain]
TTL: 300
```

#### **Certificate Validation CNAMEs:**
```
[Add the CNAME records provided by AWS Certificate Manager]
```

## 🚀 **Step 3: Configure Elastic Beanstalk**

### **Update Load Balancer:**
1. **Go to Elastic Beanstalk** → **Your Environment**
2. **Configuration** → **Load balancer** → **Edit**
3. **Add HTTPS listener:**
   - **Port:** `443`
   - **Protocol:** `HTTPS`
   - **SSL Certificate:** Select your new certificate
4. **Save changes**

## 📱 **Step 4: Configure AWS Amplify**

### **Add Custom Domain:**
1. **Go to AWS Amplify** → **Your App**
2. **Domain management** → **Add domain**
3. **Enter:** `app.shineskincollective.com`
4. **Configure SSL certificate**
5. **Update DNS records** as instructed

## 🔄 **Step 5: Deploy Updates**

### **Backend Deployment:**
```bash
# Your backend CORS is already updated
# Deploy to Elastic Beanstalk using your existing method
```

### **Frontend Deployment:**
```bash
# Deploy to Amplify
# The code is already updated to use custom domain
```

## ✅ **Step 6: Test Everything**

### **Test Commands:**
```bash
# Test backend
curl https://api.shineskincollective.com/api/health

# Test frontend
curl https://app.shineskincollective.com
```

## 🎉 **Expected Results:**

- ✅ **HTTPS working** on both frontend and backend
- ✅ **Custom domain** accessible
- ✅ **SSL certificate** valid
- ✅ **No mixed content errors**
- ✅ **Professional appearance**

## 🚨 **Troubleshooting:**

### **If DNS doesn't work:**
1. **Wait 24-48 hours** for DNS propagation
2. **Check DNS records** are correct
3. **Verify certificate** is validated

### **If HTTPS doesn't work:**
1. **Check load balancer** has HTTPS listener
2. **Verify certificate** is attached
3. **Check security groups** allow port 443

## 📞 **Next Steps:**

1. **Create the SSL certificate** in AWS Certificate Manager
2. **Add DNS records** to your domain provider
3. **Configure Elastic Beanstalk** with the certificate
4. **Deploy and test!** 