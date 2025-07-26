# 🔐 Secure Deployment Guide

## Google Vision Key Security

### ✅ Current Security Status
- Google Vision key file is in `.gitignore` (not tracked by git)
- Service supports both file path and JSON content from environment variables
- No secrets will be committed to git

### 🚀 Deployment Options

## Option 1: Environment Variable (Recommended)

### For Local Development:
```bash
# Set the JSON content as environment variable
export GOOGLE_CREDENTIALS_JSON='{"type": "service_account", "project_id": "...", ...}'
```

### For Production Deployment:
1. **AWS ECS/Amplify**: Set `GOOGLE_CREDENTIALS_JSON` environment variable
2. **Vercel**: Add to environment variables in dashboard
3. **Netlify**: Add to environment variables in dashboard

## Option 2: File Path (Alternative)

### For Local Development:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="./backend/google-vision-key.json"
```

### For Production:
- Upload the key file to your deployment platform
- Set `GOOGLE_APPLICATION_CREDENTIALS` to the file path

## Option 3: Google Cloud Default Credentials

If running on Google Cloud Platform:
```bash
# No environment variables needed - uses default service account
gcloud auth application-default login
```

### 🔧 How to Get Your JSON Content

1. **Read your current key file:**
```bash
cat backend/google-vision-key.json
```

2. **Copy the entire JSON content** (including the `{}` brackets)

3. **Set as environment variable:**
```bash
export GOOGLE_CREDENTIALS_JSON='{"type": "service_account", "project_id": "your-project", ...}'
```

### 🛡️ Security Best Practices

1. **Never commit the key file to git** ✅ (already done)
2. **Use environment variables in production** ✅ (now supported)
3. **Rotate keys regularly**
4. **Use least privilege principle**
5. **Monitor API usage**

### 🚀 Quick Deployment Commands

#### For Vercel:
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy with environment variable
vercel --env GOOGLE_CREDENTIALS_JSON='{"type": "service_account", ...}'
```

#### For Netlify:
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod
# Then add environment variable in dashboard
```

#### For AWS Amplify:
```bash
# Add environment variable in Amplify Console
# Then deploy
amplify publish
```

### 🔍 Testing Your Setup

```bash
# Test if credentials work
python -c "
import os
from backend.app.services.google_vision_service import GoogleVisionService
service = GoogleVisionService()
print('✅ Google Vision available:', service.is_available())
"
```

### 📝 Environment Variables Summary

| Variable | Purpose | Required |
|----------|---------|----------|
| `GOOGLE_CREDENTIALS_JSON` | Google Vision credentials (JSON content) | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Vision credentials (file path) | Alternative |
| `SUPABASE_URL` | Supabase database URL | Yes |
| `SUPABASE_KEY` | Supabase service key | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes | 