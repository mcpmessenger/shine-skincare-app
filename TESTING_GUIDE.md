# 🧪 **Testing Guide - Enhanced Skin Analysis App**

## 🚀 **How to Start and Test the Application**

### **1. Starting the Application**

#### **Option A: Start Enhanced Analysis API (Recommended)**
```bash
cd backend
python enhanced_analysis_api.py
```
- **Port**: 5000
- **URL**: http://localhost:5000
- **Status**: ✅ Running and tested

#### **Option B: Start Main Flask App**
```bash
cd backend
python enhanced_app.py
```
- **Port**: 8000
- **URL**: http://localhost:8000

#### **Option C: Start Basic Flask App**
```bash
cd backend
python application.py
```
- **Port**: 5000
- **URL**: http://localhost:5000

### **2. Testing the API Endpoints**

#### **✅ Health Check**
```bash
# PowerShell
Invoke-WebRequest -Uri "http://localhost:5000/api/v3/system/health" -Method GET

# curl (if available)
curl -X GET http://localhost:5000/api/v3/system/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-04T...",
  "service": "Enhanced Skin Analysis API",
  "version": "3.0.0"
}
```

#### **✅ System Status**
```bash
Invoke-WebRequest -Uri "http://localhost:5000/api/v3/system/status" -Method GET
```

**Expected Response:**
```json
{
  "system_status": "operational",
  "components": {
    "enhanced_analyzer": "loaded",
    "embedding_system": "loaded",
    "utkface_integration": "loaded",
    "db_integration": "loaded"
  },
  "data_loaded": {
    "condition_embeddings": 6,
    "demographic_baselines": 103,
    "embedding_dimensions": 2304
  }
}
```

#### **✅ System Capabilities**
```bash
Invoke-WebRequest -Uri "http://localhost:5000/api/v3/system/capabilities" -Method GET
```

### **3. Testing Skin Analysis**

#### **🔬 Basic Analysis Test**
```bash
# Create test image data (base64 encoded)
$testImage = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

# Test basic analysis
$body = @{
    image = $testImage
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/v3/skin/analyze-basic" -Method POST -Body $body -ContentType "application/json"
```

#### **🔬 Comprehensive Analysis Test**
```bash
# Test comprehensive analysis with demographics
$body = @{
    image = $testImage
    demographics = @{
        age = 25
        gender = 0
        ethnicity = 0
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/v3/skin/analyze-comprehensive" -Method POST -Body $body -ContentType "application/json"
```

#### **🔬 Normalized Analysis Test**
```bash
# Test normalized analysis (requires demographics)
$body = @{
    image = $testImage
    demographics = @{
        age = 30
        gender = 1
        ethnicity = 2
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/v3/skin/analyze-normalized" -Method POST -Body $body -ContentType "application/json"
```

### **4. Python Testing Scripts**

#### **✅ Test Integrated System**
```bash
cd backend
python test_integrated_system.py
```

**Expected Output:**
```
🔄 Integrated Skin Analysis System Test
==================================================
✅ All tests passed! Integrated system is working correctly.
```

#### **✅ Test Condition Embeddings**
```bash
cd backend
python check_embeddings.py
```

**Expected Output:**
```
🔍 Checking existing embeddings and baselines...
✅ Condition embeddings found: 6 conditions
✅ Demographic baselines found: 103 groups
✅ UTKFace metadata found: 23705 images
```

#### **✅ Test UTKFace Baselines**
```bash
cd backend
python setup_utkface_baselines.py
```

### **5. Frontend Testing**

#### **🌐 Start Frontend (if available)**
```bash
cd ..  # Go to root directory
npm run dev
```
- **URL**: http://localhost:3000

#### **🌐 Test Frontend Integration**
1. Open browser to http://localhost:3000
2. Navigate to skin analysis section
3. Upload a test image
4. Check analysis results

### **6. Advanced Testing**

#### **🔧 Test with Real Images**
```python
# Create test_image.py
import cv2
import numpy as np
import base64

# Create a realistic test image
img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
img[:, :, 0] = np.random.randint(150, 200, (224, 224))  # Blue
img[:, :, 1] = np.random.randint(120, 180, (224, 224))  # Green  
img[:, :, 2] = np.random.randint(180, 220, (224, 224))  # Red

# Convert to base64
_, buffer = cv2.imencode('.jpg', img)
image_base64 = base64.b64encode(buffer).decode('utf-8')

print(f"Test image base64: {image_base64[:100]}...")
```

#### **🔧 Load Testing**
```bash
# Test multiple concurrent requests
for ($i=1; $i -le 10; $i++) {
    Invoke-WebRequest -Uri "http://localhost:5000/api/v3/system/health" -Method GET
    Start-Sleep -Milliseconds 100
}
```

### **7. Troubleshooting**

#### **❌ API Not Starting**
```bash
# Check if port is in use
netstat -an | findstr :5000

# Kill process if needed
taskkill /F /PID <PID>
```

#### **❌ Import Errors**
```bash
# Install missing dependencies
pip install -r requirements.txt
pip install flask flask-cors opencv-python numpy scikit-learn
```

#### **❌ Memory Issues**
```bash
# Check memory usage
Get-Process python | Select-Object ProcessName, WorkingSet

# Restart with more memory
python -X maxsize=2GB enhanced_analysis_api.py
```

### **8. Expected Test Results**

#### **✅ Successful Analysis Response**
```json
{
  "timestamp": "2025-08-04T...",
  "basic_analysis": {
    "acne_severity": 0.15,
    "redness_severity": 0.08,
    "dark_spots_severity": 0.12
  },
  "baseline_comparison": {
    "status": "baseline_comparison",
    "demographics": {"age": 25, "gender": 0, "ethnicity": 0},
    "similarity_to_healthy": 0.75,
    "health_score": 75.0,
    "interpretation": "Good skin health - generally similar to healthy baseline"
  },
  "condition_analysis": {
    "status": "condition_analysis_complete",
    "top_matches": [
      {"condition": "acne", "similarity": 0.86, "confidence": 86.0}
    ]
  },
  "analysis_summary": {
    "overall_health_score": 75,
    "primary_concerns": ["acne"],
    "recommendations": ["Use gentle, non-comedogenic skincare products"]
  }
}
```

### **9. Performance Benchmarks**

#### **⏱️ Expected Response Times**
- **Health Check**: < 100ms
- **System Status**: < 200ms
- **Basic Analysis**: < 2s
- **Comprehensive Analysis**: < 5s
- **Normalized Analysis**: < 5s

#### **📊 System Resources**
- **Memory Usage**: ~2-4GB
- **CPU Usage**: 10-30% during analysis
- **Disk Space**: ~5GB for datasets

### **🎯 Quick Start Summary**

1. **Start API**: `cd backend && python enhanced_analysis_api.py`
2. **Test Health**: `Invoke-WebRequest -Uri "http://localhost:5000/api/v3/system/health"`
3. **Test Analysis**: Use the comprehensive analysis endpoint with test image
4. **Check Results**: Verify health score, condition matching, and recommendations

The enhanced skin analysis system is now **fully operational and ready for testing**! 🚀 