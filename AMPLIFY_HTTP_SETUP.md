# 🔧 Amplify HTTP Configuration (Temporary Fix)

## 🚨 **Quick Solution for Mixed Content Error**

Since your Elastic Beanstalk environment doesn't have HTTPS configured, you can temporarily configure Amplify to serve over HTTP.

## 📋 **Steps to Configure Amplify for HTTP:**

### **Option 1: Amplify Console Configuration**

1. **Go to AWS Amplify Console**
2. **Select your app**: `shine-skincare-app`
3. **Go to "App settings" → "General"**
4. **Under "Domain management":**
   - Look for "Custom domains" section
   - If you have a custom domain, you can configure it for HTTP
   - Or use the default Amplify domain with HTTP

### **Option 2: Environment Variables**

1. **In Amplify Console, go to "App settings" → "Environment variables"**
2. **Add environment variable:**
   - Key: `NEXT_PUBLIC_FORCE_HTTP`
   - Value: `true`
3. **Redeploy your app**

### **Option 3: Update Next.js Configuration**

Add this to your `next.config.mjs`:

```javascript
const nextConfig = {
  // ... existing config
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "upgrade-insecure-requests 'none'"
          }
        ]
      }
    ]
  }
}
```

## 🎯 **Expected Result**

After configuration:
- Frontend: `http://main.d3oid65kfbmqt4.amplifyapp.com` (HTTP)
- Backend: `http://shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com` (HTTP)
- No more mixed content errors
- Both frontend and backend use HTTP

## ⚠️ **Important Notes**

- **This is a temporary solution** for development/testing
- **Not recommended for production** as it removes HTTPS security
- **Consider enabling HTTPS on backend** for production use

## 🔄 **Next Steps**

1. **Test with HTTP configuration**
2. **If it works, consider upgrading to Load Balancer + HTTPS**
3. **For production, definitely enable HTTPS on backend** 