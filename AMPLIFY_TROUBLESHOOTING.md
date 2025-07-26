# 🔧 AWS Amplify Troubleshooting Guide

## **Current Issue: Cache Writing Error**

### **Error Message:**
```
[WARNING] ! Unable to write cache: {"code":"ERR_BAD_REQUEST", "message": "Request failed with status code 404"}
```

## **Solutions to Try:**

### **Solution 1: Clear Amplify Cache (Recommended)**

#### **In AWS Amplify Console:**
1. Go to your app in AWS Amplify Console
2. Navigate to **Build settings**
3. Click **Edit** on the build settings
4. Scroll down to **Build cache**
5. Click **Clear cache**
6. Save and redeploy

#### **Alternative: Disable Cache Temporarily**
1. In build settings, set **Build cache** to **Disabled**
2. Save and redeploy
3. Once successful, re-enable cache

### **Solution 2: Use Simple Build Configuration**

If the cache issue persists, temporarily rename `amplify.yml` to `amplify-backup.yml` and use the simpler configuration:

```bash
# Rename current config
mv amplify.yml amplify-backup.yml

# Use simple config
mv amplify-simple.yml amplify.yml
```

### **Solution 3: Manual Build Test**

Test the build locally to ensure it works:

```bash
# Clear local cache
rm -rf .next
rm -rf node_modules
rm -rf .pnpm-store

# Install dependencies
npm install

# Test build
npm run build
```

### **Solution 4: Update Amplify App Settings**

#### **In Amplify Console:**
1. Go to **App settings** → **General**
2. Check **Repository** settings
3. Verify **Branch** settings
4. Update **Build settings** if needed

### **Solution 5: Check Environment Variables**

Ensure all required environment variables are set in Amplify Console:

1. Go to **Environment variables**
2. Add these variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-url.com
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key
   ```

### **Solution 6: Force Redeploy**

#### **Option A: Via Console**
1. Go to **All builds**
2. Click **Redeploy this version** on the failed build
3. Or trigger a new build by pushing a small change

#### **Option B: Via Git**
```bash
# Make a small change and push
echo "# Amplify fix" >> README.md
git add README.md
git commit -m "Fix Amplify deployment"
git push origin main
```

## **Common Amplify Issues and Fixes:**

### **Issue 1: Build Timeout**
**Solution:** Increase build timeout in build settings

### **Issue 2: Memory Issues**
**Solution:** Use the simple build configuration without pnpm

### **Issue 3: Node Version Conflicts**
**Solution:** Specify Node.js version in build settings

### **Issue 4: Environment Variable Issues**
**Solution:** Check all environment variables are properly set

## **Build Configuration Options:**

### **Option 1: Standard (Current)**
```yaml
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
```

### **Option 2: Simple (Fallback)**
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm install
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
```

### **Option 3: With Cache Disabled**
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm install
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths: []
```

## **Debugging Steps:**

### **1. Check Build Logs**
- Look for specific error messages
- Check if dependencies are installing correctly
- Verify build commands are executing

### **2. Test Locally**
```bash
# Test the exact build process
npm install
npm run build
```

### **3. Check Dependencies**
```bash
# Verify package.json is valid
npm run lint
```

### **4. Monitor Resource Usage**
- Check if build is hitting memory limits
- Monitor build duration

## **Prevention Tips:**

### **1. Keep Builds Light**
- Minimize dependencies
- Use efficient build tools
- Optimize build scripts

### **2. Use Proper Caching**
- Cache node_modules
- Cache build artifacts
- Avoid caching unnecessary files

### **3. Monitor Build Performance**
- Track build times
- Monitor resource usage
- Set up alerts for failures

## **Next Steps:**

1. **Try Solution 1** (Clear cache) first
2. If that fails, **try Solution 2** (Simple config)
3. **Test locally** to ensure builds work
4. **Monitor** the next deployment
5. **Document** what works for future reference

---

**If none of these solutions work, consider using the AWS CLI deployment approach instead of Amplify for more control over the deployment process.** 