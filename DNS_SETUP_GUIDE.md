# 🌐 DNS Setup for api.shineskincollective.com

## 🎯 **Goal**: Point `api.shineskincollective.com` to your Elastic Beanstalk backend

### **Step 1: Go to Route 53**
1. **Open**: https://console.aws.amazon.com/route53/
2. **Click**: "Hosted zones"
3. **Find**: `shineskincollective.com`
4. **Click**: On your domain name

### **Step 2: Create A Record**
1. **Click**: "Create record"
2. **Fill in**:
   - **Record name**: `api`
   - **Record type**: `A - Routes traffic to an IPv4 address`
   - **Alias**: ✅ **Yes**
   - **Route traffic to**: `Application and Classic Load Balancer`
   - **Region**: `US East (N. Virginia)`
   - **Load balancer**: `shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com`
3. **Click**: "Create records"

### **Step 3: Wait for DNS Propagation**
- **Time**: 5-15 minutes
- **Test**: `nslookup api.shineskincollective.com`

### **Step 4: Update Frontend**
Once DNS is working, we'll update the frontend to use:
```
https://api.shineskincollective.com
```

## ✅ **What You Have**:
- ✅ Certificate: `api.shineskincollective.com` (ISSUED)
- ✅ Certificate: In use
- ⏳ DNS Record: Needs to be created
- ⏳ Frontend: Will be updated

## 🚀 **Benefits**:
- ✅ No more Mixed Content errors
- ✅ Professional API domain
- ✅ SSL certificate already working
- ✅ Production-ready setup 