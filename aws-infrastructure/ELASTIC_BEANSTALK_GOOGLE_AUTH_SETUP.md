# Google Auth Setup for Elastic Beanstalk Deployment

This guide helps you configure Google OAuth credentials for your Shine Skincare App running on AWS Elastic Beanstalk.

## 🎯 **Your Current Setup**

- **Elastic Beanstalk URL**: `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/`
- **Google Service Account**: `shine-466907-994eb9c6926a.json`
- **Deployment Status**: ✅ Running successfully

## 🔗 **Required Authorized Redirect URIs**

Add these **exact URLs** to your Google OAuth 2.0 Client ID:

### **Production (Elastic Beanstalk):**
```
http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/auth/callback
```

### **Local Development:**
```
http://localhost:3000/auth/callback
```

### **If you add a custom domain later:**
```
https://your-custom-domain.com/auth/callback
```

## 📋 **Step-by-Step Google Cloud Console Setup**

### **Step 1: Access Google Cloud Console**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `shine-466907`

### **Step 2: Enable Required APIs**
1. Go to **APIs & Services** > **Library**
2. Search for and enable these APIs:
   - **Google+ API**
   - **Google OAuth2 API**
   - **Google Cloud Vision API**

### **Step 3: Configure OAuth 2.0 Client**
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Set **Application Type** to **Web application**
4. Add these **Authorized redirect URIs**:
   ```
   http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/auth/callback
   http://localhost:3000/auth/callback
   ```
5. Click **Create**
6. **Copy the Client ID and Client Secret**

### **Step 4: Configure Service Account (for Google Vision API)**
1. Go to **APIs & Services** > **Credentials**
2. Find your service account: `shine-466907-994eb9c6926a`
3. Download the JSON key file (you already have this)
4. Ensure it has the **Cloud Vision API User** role

## 🔧 **Environment Variables Setup**

### **For Elastic Beanstalk Environment:**

You need to set these environment variables in your Elastic Beanstalk environment:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-oauth-client-id
GOOGLE_CLIENT_SECRET=your-oauth-client-secret

# Google Vision API (Service Account)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/shine-466907-994eb9c6926a.json

# OpenAI (for enhanced analysis)
OPENAI_API_KEY=your-openai-api-key

# Other required variables
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=your-database-url
```

## 🚀 **Quick Setup Commands**

### **Option 1: Use the Automated Script**
```powershell
# Navigate to aws-infrastructure
cd aws-infrastructure

# Run the update script with your credentials
.\update-google-auth.ps1 -GoogleClientId "your-client-id" -GoogleClientSecret "your-client-secret" -Interactive:$false
```

### **Option 2: Manual Elastic Beanstalk Update**
```bash
# Set environment variables in Elastic Beanstalk
aws elasticbeanstalk update-environment \
  --environment-name shine-env \
  --option-settings \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=GOOGLE_CLIENT_ID,Value=your-client-id \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=GOOGLE_CLIENT_SECRET,Value=your-client-secret \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=OPENAI_API_KEY,Value=your-openai-key
```

## 🔍 **Verification Steps**

### **1. Test OAuth Flow**
1. Visit your app: `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/`
2. Try to log in with Google
3. Verify the callback works correctly

### **2. Test Google Vision API**
1. Try the enhanced skin analysis feature
2. Check that face detection works
3. Verify image processing completes

### **3. Check Environment Variables**
```bash
# SSH into your Elastic Beanstalk instance
eb ssh

# Check environment variables
echo $GOOGLE_CLIENT_ID
echo $GOOGLE_CLIENT_SECRET
echo $OPENAI_API_KEY
```

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **1. "Invalid redirect_uri" Error**
- Double-check the exact URL in Google Cloud Console
- Ensure no trailing slashes
- Verify protocol (http vs https)

#### **2. Google Vision API Not Working**
- Verify service account JSON is uploaded to Elastic Beanstalk
- Check `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- Ensure service account has proper permissions

#### **3. OAuth Callback Fails**
- Check Elastic Beanstalk logs
- Verify environment variables are set correctly
- Test with local development first

### **Useful Commands:**
```bash
# Check Elastic Beanstalk environment
aws elasticbeanstalk describe-environments --environment-names shine-env

# View application logs
eb logs

# SSH into instance
eb ssh
```

## 📁 **File Locations**

### **Service Account JSON**
- **Local**: `C:\Users\senti\OneDrive\Desktop\Shine\shine-skincare-app\shine-466907-994eb9c6926a.json`
- **Elastic Beanstalk**: Upload via environment variables or S3

### **Environment Configuration**
- **Elastic Beanstalk**: Configure via AWS Console or CLI
- **Local Development**: Use `.env.local` file

## 🔐 **Security Best Practices**

1. **Never commit credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate credentials** regularly
4. **Monitor access** in Google Cloud Console
5. **Use least privilege** for service accounts

## 📞 **Next Steps**

1. **Add the redirect URIs** to Google Cloud Console
2. **Get your OAuth Client ID and Secret**
3. **Update your Elastic Beanstalk environment** with the credentials
4. **Test the authentication flow**
5. **Verify enhanced analysis features work**

## 🎯 **Quick Reference**

### **Your URLs:**
- **Production**: `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/`
- **Callback**: `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/auth/callback`
- **Local**: `http://localhost:3000/auth/callback`

### **Required Environment Variables:**
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `OPENAI_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS`

### **Service Account:**
- File: `shine-466907-994eb9c6926a.json`
- Project: `shine-466907` 