# 🔧 Custom Domain Setup for Backend

## 🎯 **Goal**: Use `api.shineskincollective.com` for backend

### **Step 1: Check Your Certificate**
1. Go to: https://console.aws.amazon.com/acm/
2. Find your certificate for `shineskincollective.com`
3. Ensure it's **ISSUED** status

### **Step 2: Create Subdomain**
1. Go to **Route 53**: https://console.aws.amazon.com/route53/
2. Select your hosted zone: `shineskincollective.com`
3. **Create A record**:
   - **Name**: `api`
   - **Type**: A - Routes traffic to an IPv4 address
   - **Alias**: Yes
   - **Route traffic to**: Application and Classic Load Balancer
   - **Region**: US East (N. Virginia)
   - **Load balancer**: Your Elastic Beanstalk load balancer

### **Step 3: Update Backend Configuration**
Once the subdomain is created, update the backend to use it.

### **Step 4: Update Frontend**
Change backend URL to: `https://api.shineskincollective.com`

## 🔍 **Current Status**:
- ✅ Domain: `shineskincollective.com`
- ✅ Certificate: (Check ACM console)
- ⏳ Subdomain: `api.shineskincollective.com` (needs setup)
- ⏳ Backend URL: (will be updated)

## 🚀 **Benefits**:
- ✅ No Mixed Content errors
- ✅ Professional domain
- ✅ SSL certificate already covers subdomain
- ✅ Better for production 