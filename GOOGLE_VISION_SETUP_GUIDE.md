# Google Vision AI Setup Guide

## 🎯 **Objective**
Connect your Shine app to real Google Cloud Vision AI for accurate skin analysis.

## 📋 **Prerequisites**
- Google Cloud account (free tier available)
- Basic understanding of Google Cloud Console
- 5-10 minutes setup time

---

## 🚀 **Step-by-Step Setup**

### **Step 1: Create Google Cloud Project**

1. **Go to Google Cloud Console**
   ```
   https://console.cloud.google.com/
   ```

2. **Create New Project**
   - Click "Select a project" → "New Project"
   - Name: `shine-skincare-app` (or your preferred name)
   - Click "Create"

3. **Set as Active Project**
   - Select your new project from the dropdown

### **Step 2: Enable Cloud Vision API**

1. **Navigate to APIs**
   - Go to "APIs & Services" → "Library"

2. **Search for Vision API**
   - Search: "Cloud Vision API"
   - Click on "Cloud Vision API"

3. **Enable the API**
   - Click "Enable"

### **Step 3: Create Service Account**

1. **Go to Service Accounts**
   - Navigate to "APIs & Services" → "Credentials"

2. **Create Service Account**
   - Click "Create Credentials" → "Service Account"
   - Name: `shine-vision-api`
   - Description: `Service account for Shine skin analysis`
   - Click "Create and Continue"

3. **Grant Access**
   - Role: "Cloud Vision API User"
   - Click "Continue" → "Done"

### **Step 4: Generate API Key**

1. **Create Key**
   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON"
   - Click "Create"

2. **Download Key File**
   - The JSON file will download automatically
   - Save it as `google-vision-key.json` in your project

### **Step 5: Configure Environment**

1. **Copy Environment Template**
   ```bash
   cd backend
   cp env.enhanced.example .env
   ```

2. **Update .env File**
   ```env
   # Google Cloud Vision AI Configuration
   GOOGLE_CLOUD_PROJECT_ID=your-project-id-here
   GOOGLE_APPLICATION_CREDENTIALS=./google-vision-key.json
   ```

3. **Place Key File**
   - Put `google-vision-key.json` in your `backend/` folder

### **Step 6: Test the Integration**

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run Test Script**
   ```bash
   python test_enhanced_services.py
   ```

3. **Check Output**
   - Look for "Google Vision service: ✅ Available"
   - If successful, you'll see real analysis results

---

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. "Service not available" Error**
```bash
# Check if credentials file exists
ls -la backend/google-vision-key.json

# Verify environment variable
echo $GOOGLE_APPLICATION_CREDENTIALS
```

#### **2. "Permission denied" Error**
- Ensure the service account has "Cloud Vision API User" role
- Check that the API is enabled in your project

#### **3. "Invalid project ID" Error**
- Verify your project ID in Google Cloud Console
- Make sure it matches exactly in your .env file

#### **4. "Quota exceeded" Error**
- Check your Google Cloud billing
- Free tier includes 1000 requests/month

### **Debug Commands:**
```bash
# Test Google Vision directly
cd backend
python -c "
from app.services.google_vision_service import GoogleVisionService
service = GoogleVisionService()
print(f'Service available: {service.is_available()}')
"
```

---

## 📊 **What You Get with Real Google Vision AI**

### **Enhanced Analysis Features:**
- **Face Detection**: Precise facial feature analysis
- **Image Properties**: Color analysis and image quality
- **Label Detection**: Automatic skin condition identification
- **Safe Search**: Content moderation
- **Text Detection**: Extract text from images (if any)

### **Real vs Mock Data:**
```json
// Mock Data (Current)
{
  "skinType": "Combination",
  "conditions": ["Acne", "Hyperpigmentation"]
}

// Real Google Vision Data
{
  "face_detection": {
    "faces": [{
      "confidence": 0.98,
      "bounding_poly": {...},
      "landmarks": [...],
      "properties": {
        "skin_tone": "medium",
        "age_range": "25-35"
      }
    }]
  },
  "label_detection": {
    "labels": [
      {"description": "person", "confidence": 0.99},
      {"description": "face", "confidence": 0.98},
      {"description": "skin", "confidence": 0.95}
    ]
  }
}
```

---

## 💰 **Costs & Limits**

### **Free Tier (First 1000 requests/month):**
- Face Detection: 1000 requests
- Label Detection: 1000 requests
- Image Properties: 1000 requests

### **Paid Tier:**
- $1.50 per 1000 requests after free tier
- Very cost-effective for MVP testing

### **Monitoring Usage:**
1. Go to Google Cloud Console
2. Navigate to "APIs & Services" → "Dashboard"
3. Select "Cloud Vision API"
4. View usage metrics

---

## 🎯 **Next Steps After Setup**

1. **Test with Real Images**
   ```bash
   # Use the MVP page
   npm run dev
   # Visit: http://localhost:3000/skin-analysis-mvp
   ```

2. **Monitor API Calls**
   - Check Google Cloud Console for usage
   - Verify analysis quality

3. **Optimize for Production**
   - Add error handling
   - Implement caching
   - Set up monitoring

---

## 🆘 **Need Help?**

### **Quick Fixes:**
- **API not working**: Check if Vision API is enabled
- **Credentials error**: Verify JSON key file path
- **Permission issues**: Ensure service account has correct role

### **Support Resources:**
- [Google Cloud Vision Documentation](https://cloud.google.com/vision/docs)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Vision API Pricing](https://cloud.google.com/vision/pricing)

---

## ✅ **Success Checklist**

- [ ] Google Cloud project created
- [ ] Cloud Vision API enabled
- [ ] Service account created with API key
- [ ] JSON key file downloaded and placed in backend/
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Test script runs successfully
- [ ] MVP page shows real analysis results

**🎉 Once completed, your Shine app will have real AI-powered skin analysis!** 