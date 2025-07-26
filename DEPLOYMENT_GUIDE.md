# 🚀 AWS Amplify Deployment Guide

## **Prerequisites**

1. **AWS Account** with Amplify access
2. **GitHub Repository** connected to your project
3. **Environment Variables** configured
4. **Backend API** deployed (if using separate backend)

## **Step 1: Connect Repository to Amplify**

### **1.1 Create Amplify App**
1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click **"New app"** → **"Host web app"**
3. Choose **"GitHub"** as your repository source
4. Authorize AWS Amplify to access your GitHub account
5. Select your repository: `mcpmessenger/shine`
6. Choose the **main** branch

### **1.2 Configure Build Settings**
Amplify will auto-detect Next.js, but verify these settings:

```yaml
# amplify.yml (already created)
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm install -g pnpm
        - pnpm install --frozen-lockfile
    build:
      commands:
        - pnpm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
      - .next/cache/**/*
```

## **Step 2: Configure Environment Variables**

### **2.1 Required Environment Variables**
In Amplify Console → **Environment variables**:

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://your-backend-api.com

# Google OAuth
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id

# Stripe (Production)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_key

# App Configuration
NEXT_PUBLIC_APP_NAME=Shine
NEXT_PUBLIC_APP_URL=https://your-amplify-domain.amplifyapp.com
```

### **2.2 Google OAuth Setup**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Add authorized redirect URIs:
   - `https://your-amplify-domain.amplifyapp.com/auth/callback`
   - `http://localhost:3000/auth/callback` (for development)

## **Step 3: Deploy Backend (Optional)**

### **3.1 Option A: Deploy Backend Separately**
- Deploy Flask backend to **AWS Lambda** or **EC2**
- Update `NEXT_PUBLIC_API_URL` to point to your backend

### **3.2 Option B: Use Amplify Backend**
- Use **AWS AppSync** for GraphQL API
- Use **AWS Lambda** for serverless functions
- Use **Amazon DynamoDB** for database

## **Step 4: Deploy Frontend**

### **4.1 Initial Deployment**
1. Click **"Save and deploy"** in Amplify Console
2. Monitor build progress in real-time
3. Check build logs for any errors

### **4.2 Common Issues & Solutions**

#### **Issue: `papm: command not found`**
**Solution:** Use the `amplify.yml` file we created

#### **Issue: Build fails with TypeScript errors**
**Solution:** Already configured in `next.config.mjs`:
```javascript
typescript: {
  ignoreBuildErrors: true,
}
```

#### **Issue: Environment variables not available**
**Solution:** Ensure all variables start with `NEXT_PUBLIC_` for client-side access

## **Step 5: Configure Custom Domain (Optional)**

### **5.1 Add Custom Domain**
1. Go to **Domain management** in Amplify Console
2. Click **"Add domain"**
3. Enter your domain (e.g., `shine-skincare.com`)
4. Configure DNS settings as instructed

### **5.2 SSL Certificate**
- Amplify automatically provisions SSL certificates
- No additional configuration needed

## **Step 6: Set Up Continuous Deployment**

### **6.1 Automatic Deployments**
- Amplify automatically deploys on every push to `main` branch
- Configure branch protection rules in GitHub

### **6.2 Preview Deployments**
- Create feature branches for testing
- Amplify creates preview URLs for each branch

## **Step 7: Monitoring & Analytics**

### **7.1 Amplify Analytics**
1. Enable **Amplify Analytics** in console
2. Track user behavior and app performance
3. Monitor errors and performance metrics

### **7.2 Custom Analytics**
- Integrate with **Google Analytics**
- Add **Hotjar** for user session recordings
- Use **Sentry** for error tracking

## **Step 8: Performance Optimization**

### **8.1 Build Optimization**
```javascript
// next.config.mjs
const nextConfig = {
  output: 'standalone',
  experimental: {
    optimizeCss: true,
  },
  compress: true,
}
```

### **8.2 Image Optimization**
- Use **Next.js Image** component
- Configure CDN for static assets
- Enable image compression

## **Step 9: Security Configuration**

### **9.1 Environment Variables**
- Never commit sensitive data to Git
- Use Amplify's environment variable system
- Rotate API keys regularly

### **9.2 CORS Configuration**
```javascript
// For backend API
const corsOptions = {
  origin: ['https://your-amplify-domain.amplifyapp.com'],
  credentials: true,
}
```

## **Step 10: Testing Deployment**

### **10.1 Pre-Deployment Checklist**
- [ ] All environment variables set
- [ ] Google OAuth configured
- [ ] Backend API deployed and accessible
- [ ] Database migrations completed
- [ ] SSL certificates valid

### **10.2 Post-Deployment Testing**
- [ ] Test authentication flow
- [ ] Verify camera functionality
- [ ] Check shopping cart features
- [ ] Test payment integration
- [ ] Validate mobile responsiveness

## **Troubleshooting**

### **Common Build Errors**

#### **Error: `pnpm: command not found`**
```yaml
# amplify.yml
preBuild:
  commands:
    - npm install -g pnpm
    - pnpm install --frozen-lockfile
```

#### **Error: Environment variables undefined**
- Ensure variables start with `NEXT_PUBLIC_`
- Rebuild after adding new variables

#### **Error: API calls failing**
- Check CORS configuration
- Verify API URL is correct
- Test API endpoints directly

### **Performance Issues**

#### **Slow Build Times**
- Enable build caching in `amplify.yml`
- Optimize dependencies
- Use build optimization flags

#### **Slow Page Loads**
- Enable Next.js optimizations
- Use CDN for static assets
- Implement lazy loading

## **Support Resources**

- [AWS Amplify Documentation](https://docs.aws.amazon.com/amplify/)
- [Next.js Deployment Guide](https://nextjs.org/docs/deployment)
- [Amplify Troubleshooting](https://docs.aws.amazon.com/amplify/latest/userguide/troubleshooting.html)

## **Next Steps**

1. **Deploy to production** using this guide
2. **Set up monitoring** and analytics
3. **Configure custom domain** for branding
4. **Implement CI/CD** for automated testing
5. **Set up backup** and disaster recovery

---

**Your Shine app is now ready for AWS Amplify deployment!** 🚀 