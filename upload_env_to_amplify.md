# 🚀 Upload Environment Variables to AWS Amplify

## 📋 **Step 1: Update Your Environment File**

1. **Open `env.amplify`** file
2. **Replace all placeholder values** with your actual credentials:

### **Supabase Credentials:**
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_actual_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_actual_service_role_key
```

### **Google Auth Credentials:**
```env
GOOGLE_CLIENT_ID=your_actual_google_client_id
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_actual_google_client_id
```

### **Update App URL:**
```env
NEXT_PUBLIC_APP_URL=https://your-actual-app-id.amplifyapp.com
```

## 🚀 **Step 2: Upload to AWS Amplify**

### **Method 1: AWS Amplify Console (Recommended)**

1. **Go to your AWS Amplify app**: https://console.aws.amazon.com/amplify/
2. **Click on your app** (ID: dt8p5usqdv9h5)
3. **Go to "Environment variables"** in the left sidebar
4. **Click "Import environment variables"**
5. **Upload your `env.amplify` file**

### **Method 2: Manual Entry (Alternative)**

If import doesn't work, manually add each variable:

1. **Go to "Environment variables"**
2. **Click "Add environment variable"** for each one
3. **Copy from `env.amplify`** file

## 🔗 **Step 3: Update Google OAuth Callback URLs**

### **For Google Cloud Console:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. **Find your OAuth 2.0 Client ID**
3. **Click "Edit"**
4. **Add these Authorized redirect URIs:**
   ```
   https://your-app-id.amplifyapp.com/auth/callback
   https://your-app-id.amplifyapp.com/api/auth/callback
   https://your-app-id.amplifyapp.com/auth/google/callback
   ```

### **For Supabase (if using Supabase Auth):**
1. Go to your Supabase project dashboard
2. **Settings** → **Auth** → **URL Configuration**
3. **Add Site URL:**
   ```
   https://your-app-id.amplifyapp.com
   ```
4. **Add Redirect URLs:**
   ```
   https://your-app-id.amplifyapp.com/auth/callback
   https://your-app-id.amplifyapp.com/auth/login
   https://your-app-id.amplifyapp.com/auth/signup
   ```

## 🚀 **Step 4: Redeploy**

After adding environment variables:

1. **Go to "Builds"** tab
2. **Click "Redeploy this version"**
3. **Wait for build to complete**

## 🧪 **Step 5: Test**

Test these features:
- ✅ **Guest access** (should work without sign-in)
- ✅ **Google sign-in** (should work with new callback URLs)
- ✅ **SCIN integration** (should access the dataset)
- ✅ **All app features** (should work with environment variables)

## 📋 **Required Credentials Checklist**

Make sure you have:
- ✅ **Supabase project URL and keys**
- ✅ **Google OAuth Client ID and Secret**
- ✅ **Your AWS Amplify app URL** (for callback URLs)
- ✅ **Any other API keys** (Stripe, Google Vision, etc.)

---

**Your app will be fully functional with authentication and SCIN integration!** 🎉 