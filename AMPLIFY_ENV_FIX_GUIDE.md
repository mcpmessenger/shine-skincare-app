# 🔧 AMPLIFY ENVIRONMENT VARIABLES FIX

## 🚨 **URGENT: FRONTEND STILL USING OLD BACKEND**

**Current Issue**: Frontend is calling `https://api.shineskincollective.com` instead of Unicorn Alpha

**Error Messages**:
- CORS policy blocked
- 413 (Content Too Large)
- Failed to fetch

## 🎯 **IMMEDIATE FIX REQUIRED:**

### **Step 1: Update Amplify Environment Variables**

**Via AWS Console:**
1. Go to **AWS Amplify Console**
2. Select your app: `shineskincollectiveapp`
3. Go to **Environment variables**
4. **Add/Update** this variable:

```
NEXT_PUBLIC_BACKEND_URL=http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com
```

### **Step 2: Trigger Rebuild**

**Option A: Via Amplify Console**
1. Go to your app in Amplify Console
2. Click **Redeploy this version**
3. Monitor the build process

**Option B: Via Git Push**
```bash
# Make a small change to trigger rebuild
echo "# Trigger rebuild for Unicorn Alpha" >> README.md
git add README.md
git commit -m "Trigger rebuild for Unicorn Alpha backend integration"
git push origin main
```

## 🔍 **VERIFICATION STEPS:**

### **1. Check Current Backend URL**
Visit: `https://app.shineskincollective.com`
Open browser console and check:
```javascript
// Should show Unicorn Alpha URL
console.log(process.env.NEXT_PUBLIC_BACKEND_URL)
```

### **2. Test Backend Connection**
```bash
# Test Unicorn Alpha backend
curl http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/health

# Test CORS headers
curl -H "Origin: https://www.shineskincollective.com" \
     -I http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/health
```

### **3. Expected Results**
- **✅ No CORS errors**
- **✅ File uploads work (up to 100MB)**
- **✅ ML analysis responds correctly**
- **✅ No 413 errors**

## 🦄 **UNICORN ALPHA BACKEND STATUS:**

**URL**: `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com`
**Status**: ✅ **LIVE AND OPERATIONAL**
**Response**: 
```json
{
  "message": "🦄 UNICORN ALPHA FIXED is running!",
  "ml_available": true,
  "timestamp": "2025-07-30T06:01:54.054612",
  "version": "unicorn-alpha-fixed-py39"
}
```

## 📋 **TROUBLESHOOTING:**

### **If Environment Variables Don't Work:**
1. **Clear browser cache** - Hard refresh (Ctrl+F5)
2. **Check Amplify build logs** - Ensure build completed successfully
3. **Verify environment variable** - Check Amplify Console
4. **Test directly** - Try the Unicorn Alpha URL directly

### **If Still Getting CORS Errors:**
1. **Check backend CORS configuration** - Should allow `https://www.shineskincollective.com`
2. **Verify frontend domain** - Ensure it matches CORS allowed origins
3. **Test with curl** - Verify CORS headers are present

## 🎯 **SUCCESS CRITERIA:**

After the fix:
- ✅ **No CORS errors** in browser console
- ✅ **File uploads work** (up to 100MB)
- ✅ **ML analysis responds** with Unicorn Alpha data
- ✅ **No 413 errors** (Content Too Large)
- ✅ **Frontend connects** to Unicorn Alpha backend

---

**🚨 URGENT**: Update Amplify environment variables immediately to fix the CORS and file size issues! 