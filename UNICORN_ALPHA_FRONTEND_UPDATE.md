# 🦄 UNICORN ALPHA FRONTEND UPDATE GUIDE

## 🎯 **FRONTEND UPDATE REQUIRED**

Your Unicorn Alpha backend is now live at:
```
http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com
```

But your frontend is still pointing to the old backend. Here's how to update it:

## 📋 **UPDATE OPTIONS:**

### **Option 1: Update Amplify Environment Variables (Recommended)**

**Via AWS Console:**
1. Go to **AWS Amplify Console**
2. Select your app: `shineskincareapp`
3. Go to **Environment variables**
4. Add/Update:
   ```
   NEXT_PUBLIC_BACKEND_URL=http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com
   ```
5. **Redeploy** your frontend

### **Option 2: Update Code and Deploy (Already Done)**

✅ **COMPLETED:** Updated `lib/api.ts` fallback URL to point to Unicorn Alpha

**Changes Made:**
```typescript
// OLD:
this.baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://api.shineskincollective.com';

// NEW:
this.baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com';
```

## 🚀 **DEPLOYMENT STEPS:**

### **Step 1: Commit and Push Changes**
```bash
git add .
git commit -m "Update backend URL to Unicorn Alpha deployment"
git push origin main
```

### **Step 2: Monitor Amplify Build**
- Go to AWS Amplify Console
- Watch the build process
- Ensure it completes successfully

### **Step 3: Test the Connection**
- Visit your frontend: `https://app.shineskincollective.com`
- Try the skin analysis feature
- Check browser console for API calls to the new backend

## 🔍 **VERIFICATION:**

### **Check API Calls in Browser Console:**
```javascript
// Should show calls to:
// http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest
```

### **Test Endpoints:**
1. **Health Check:** `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/health`
2. **Root Endpoint:** `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/`
3. **ML Analysis:** `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest`

## 🎉 **EXPECTED RESULTS:**

### **After Update:**
- ✅ Frontend connects to Unicorn Alpha backend
- ✅ ML analysis uses the new heavy ML stack
- ✅ All endpoints respond correctly
- ✅ CORS headers work properly
- ✅ File uploads work (up to 100MB)

### **Benefits of Unicorn Alpha:**
- 🦄 **Full ML Stack:** TensorFlow, OpenCV, scikit-learn
- 🚀 **Better Performance:** m5.2xlarge instance
- ⚡ **Enhanced Analysis:** More sophisticated skin analysis
- 🔧 **Production Ready:** Proper timeouts, CORS, file limits

## 🔧 **TROUBLESHOOTING:**

### **If Frontend Still Uses Old Backend:**
1. **Clear browser cache**
2. **Check Amplify environment variables**
3. **Verify build completed successfully**
4. **Check browser console for API calls**

### **If CORS Errors:**
- The Unicorn Alpha backend has CORS configured for `https://www.shineskincollective.com`
- Should work automatically

### **If Build Fails:**
- Check Amplify build logs
- Ensure all environment variables are set correctly
- Verify the backend URL is accessible

## 📊 **MONITORING:**

### **Backend Health:**
```bash
curl http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/health
```

### **Frontend Health:**
- Monitor Amplify build status
- Check frontend logs for API errors
- Test skin analysis functionality

---

## 🎯 **SUMMARY:**

**✅ Backend Updated:** Unicorn Alpha is live and operational  
**✅ Frontend Code Updated:** Fallback URL changed to new backend  
**🔄 Next Step:** Deploy frontend changes to Amplify  

**Your comprehensive ML-powered skincare app is ready to use the new Unicorn Alpha backend!** 