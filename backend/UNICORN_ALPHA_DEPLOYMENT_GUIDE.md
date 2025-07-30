# 🦄 UNICORN ALPHA Deployment Guide

## 🚨 **CRITICAL ISSUE RESOLVED: Windows/Linux Path Separators**

The Unicorn Alpha package deployment was failing due to **Windows backslashes vs Linux forward slashes** in the ZIP file structure. This has been **FIXED** in the new deployment script.

## 📋 **What is UNICORN ALPHA?**

**UNICORN ALPHA** is a comprehensive ML deployment package that includes:

### **Heavy ML Dependencies:**
- ✅ **TensorFlow 2.13.0** - Deep learning framework
- ✅ **OpenCV 4.8.0.76** - Computer vision library
- ✅ **scikit-learn 1.3.0** - Machine learning library
- ✅ **NumPy 1.24.3** - Numerical computing
- ✅ **Pandas 2.0.3** - Data manipulation
- ✅ **Matplotlib 3.7.2** - Data visualization
- ✅ **Seaborn 0.12.2** - Statistical visualization

### **Infrastructure Requirements:**
- 🎯 **Target**: XL Elastic Beanstalk Environment
- 🖥️ **Instance Type**: m5.2xlarge (8 vCPU, 32 GB RAM)
- ⏱️ **Timeout**: 900 seconds for ML processing
- 📁 **File Upload**: 100MB limit
- 🔧 **Workers**: 6 Gunicorn workers

## 🚀 **Deployment Steps**

### **Step 1: Create the Fixed Deployment Package**

```powershell
# Navigate to backend directory
cd backend

# Create UNICORN ALPHA FIXED package
.\create-unicorn-alpha-fixed.ps1
```

**This will create:** `UNICORN_ALPHA_FIXED-YYYYMMDD-HHMMSS.zip`

### **Step 2: Verify Package Structure**

```powershell
# Verify the deployment package
.\verify-unicorn-deployment.ps1
```

**Expected Output:**
```
✅ Found: app.py
✅ Found: requirements.txt
✅ Found: Procfile
✅ Found: .ebextensions directory
✅ Forward slash: app.py
✅ All critical files present!
```

### **Step 3: Deploy to XL Elastic Beanstalk**

1. **Open AWS Console** → Elastic Beanstalk
2. **Select your XL environment** (SHINE-env or similar)
3. **Upload and Deploy** the `UNICORN_ALPHA_FIXED-*.zip`
4. **Monitor deployment logs** for success

### **Step 4: Verify Deployment**

```powershell
# Test the deployment
.\verify-unicorn-deployment.ps1
```

## 🔧 **What Was Fixed**

### **❌ Previous Issue:**
```python
# Windows created ZIP with backslashes
arcname = "app\\app.py"  # ❌ Linux can't find this
```

### **✅ Fixed Solution:**
```python
# Python script converts to forward slashes
arcname = os.path.relpath(file_path, source_dir).replace('\\', '/')
# Result: "app/app.py"  # ✅ Linux can find this
```

## 📊 **Deployment Verification**

### **Health Check:**
```bash
curl -I https://api.shineskincollective.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "ml_available": true,
  "version": "unicorn-alpha-fixed-py39"
}
```

### **ML Analysis Test:**
```bash
curl -X POST https://api.shineskincollective.com/api/v2/analyze/guest \
  -F "image=@test-image.jpg"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "🦄 UNICORN ALPHA FIXED analysis completed!",
  "data": {
    "skin_tone": "medium",
    "undertone": "warm",
    "concerns": ["hyperpigmentation", "sensitivity"],
    "recommendations": [
      "🦄 Use gentle cleanser",
      "🦄 Apply vitamin C serum",
      "🦄 Wear SPF daily"
    ],
    "confidence": 0.95,
    "unicorn_power": true,
    "deployment_fixed": true
  }
}
```

## 🚨 **Troubleshooting**

### **If Deployment Fails:**

1. **Check Logs:**
   ```bash
   # View Elastic Beanstalk logs
   eb logs
   ```

2. **Common Issues:**
   - ❌ `No dependency file found` → Path separator issue (FIXED)
   - ❌ `creating default Procfile` → Procfile not found (FIXED)
   - ❌ `MemoryError` → Increase instance size to m5.2xlarge
   - ❌ `TimeoutError` → Increase timeout to 900s

3. **Force Restart:**
   ```bash
   # Restart the environment
   eb restart
   ```

### **If ML Dependencies Fail:**

1. **Check Python Version:** Ensure Python 3.9 compatibility
2. **Memory Issues:** Verify m5.2xlarge instance type
3. **Timeout Issues:** Check 900s timeout configuration

## 📈 **Performance Expectations**

### **Deployment Time:**
- ⏱️ **Package Creation**: ~30 seconds
- ⏱️ **Upload**: ~2-5 minutes (100MB+ package)
- ⏱️ **Installation**: ~10-15 minutes (heavy ML dependencies)
- ⏱️ **Total**: ~15-20 minutes

### **Runtime Performance:**
- 🚀 **Cold Start**: ~30-60 seconds (ML model loading)
- 🚀 **Warm Start**: ~1-5 seconds
- 🚀 **Concurrent Requests**: 6 workers × 15 threads = 90 concurrent

## 🎯 **Success Criteria**

### **✅ Deployment Success:**
- [ ] Package uploads without errors
- [ ] `requirements.txt` found and installed
- [ ] `Procfile` recognized and used
- [ ] Gunicorn starts on port 8000
- [ ] Health endpoint responds
- [ ] ML analysis endpoint works

### **✅ Performance Success:**
- [ ] 100MB file uploads work
- [ ] ML analysis completes within 900s
- [ ] CORS headers configured correctly
- [ ] No memory errors on m5.2xlarge

## 🦄 **UNICORN ALPHA Features**

### **Advanced ML Capabilities:**
- 🧠 **TensorFlow**: Deep learning models
- 👁️ **OpenCV**: Computer vision processing
- 📊 **scikit-learn**: Machine learning algorithms
- 📈 **Pandas/NumPy**: Data processing
- 📊 **Matplotlib/Seaborn**: Data visualization

### **Production Ready:**
- 🔒 **CORS Security**: Proper cross-origin handling
- ⏱️ **Timeout Management**: 900s for ML processing
- 📁 **File Upload**: 100MB limit for high-res images
- 🔄 **Worker Management**: 6 Gunicorn workers
- 🖥️ **Resource Allocation**: m5.2xlarge instance

---

**🎯 Ready to deploy UNICORN ALPHA to your XL Elastic Beanstalk environment!**

**Next Step:** Run `.\create-unicorn-alpha-fixed.ps1` to create the deployment package. 