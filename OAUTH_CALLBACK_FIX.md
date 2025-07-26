# 🔧 Fix OAuth Callback URLs for Vercel Deployment

## 🚨 Current Issue
Your OAuth login is failing because the callback URLs in Google Cloud Console don't match your new Vercel domain.

## 🎯 Your Vercel URL
**`https://shine-skincare-34e1qjma6-williamtflynn-2750s-projects.vercel.app`**

## 📋 Step-by-Step Fix

### Step 1: Update Google Cloud Console

1. **Go to Google Cloud Console:** https://console.cloud.google.com/
2. **Select your project:** `shine-466907`
3. **Navigate to:** APIs & Services → Credentials
4. **Click on your OAuth 2.0 Client ID**

### Step 2: Update Authorized Redirect URIs

**Add these URLs to "Authorized redirect URIs":**

```
https://shine-skincare-34e1qjma6-williamtflynn-2750s-projects.vercel.app/auth/callback
https://shine-skincare-34e1qjma6-williamtflynn-2750s-projects.vercel.app/api/auth/callback/google
```

**Keep any existing localhost URLs for development:**
```
http://localhost:3000/auth/callback
http://localhost:3000/api/auth/callback/google
```

### Step 3: Update Authorized JavaScript Origins

**Add this to "Authorized JavaScript origins":**

```
https://shine-skincare-34e1qjma6-williamtflynn-2750s-projects.vercel.app
```

**Keep any existing localhost origins:**
```
http://localhost:3000
```

### Step 4: Save Changes

1. **Click "Save"** at the bottom of the page
2. **Wait a few minutes** for changes to propagate

### Step 5: Test the Fix

1. **Go to your Vercel app:** https://shine-skincare-34e1qjma6-williamtflynn-2750s-projects.vercel.app
2. **Click "Login"**
3. **Try Google OAuth login**
4. **Should now work!** ✅

## 🔍 Alternative: Check Current Configuration

If you want to see your current OAuth configuration:

1. **Go to:** https://console.cloud.google.com/apis/credentials
2. **Click on your OAuth 2.0 Client ID**
3. **Check the "Authorized redirect URIs" section**

## 🚀 Expected Result

After updating the callback URLs:
- ✅ Google OAuth login will work
- ✅ Users can sign in with Google
- ✅ Callback will redirect properly
- ✅ Authentication will complete successfully

## 🆘 If Still Not Working

1. **Wait 5-10 minutes** for Google's changes to propagate
2. **Clear browser cache** and try again
3. **Check browser console** for any errors
4. **Verify the exact URL** matches your Vercel deployment

## 📝 Summary

The issue was that Google OAuth was configured for localhost but your app is now running on Vercel. By adding the Vercel domain to the authorized redirect URIs, Google will now allow the OAuth callback to work properly.

---

**After making these changes, your Shine skincare app will have fully functional Google OAuth login!** 🎉 