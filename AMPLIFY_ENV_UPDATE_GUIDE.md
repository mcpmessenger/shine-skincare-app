# 🔄 AMPLIFY ENVIRONMENT VARIABLES UPDATE GUIDE

## 🎯 **UPDATE REQUIRED FOR UNICORN ALPHA DEPLOYMENT**

### **Current Configuration:**
- **Frontend URL:** `https://app.shineskincollective.com`
- **Current Backend:** `https://api.shineskincollective.com`
- **New Backend:** `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com`

## 📋 **STEP-BY-STEP UPDATE PROCESS:**

### **Step 1: Update Amplify Environment Variables**

**Via AWS Console:**
1. Go to **AWS Amplify Console**
2. Select your app: `shineskincareapp`
3. Go to **Environment variables**
4. Add/Update the following variable:

```bash
NEXT_PUBLIC_BACKEND_URL=http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com
```

### **Step 2: Trigger Frontend Rebuild**

**Via AWS Console:**
1. Go to your Amplify app
2. Click **Redeploy this version** or make a small commit to trigger rebuild
3. Monitor the build process

**Via Git (Recommended):**
```bash
# Make a small change to trigger rebuild
git add .
git commit -m "Update backend URL to Unicorn Alpha deployment"
git push origin main
```

### **Step 3: Verify the Update**

**Check the updated configuration:**
```typescript
// In lib/api.ts - should now use the new URL
this.baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://api.shineskincollective.com';
```

## 🔧 **ALTERNATIVE: Update Frontend Code Directly**

If you prefer to update the code directly:

### **Option A: Update the fallback URL**
 