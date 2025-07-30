# 🔧 CORS FIX GUIDE

## 🚨 **CURRENT ISSUE: CORS PREFLIGHT FAILURE**

**Error**: "Response to preflight request doesn't pass access control check: It does not have HTTP ok status"
**Cause**: Backend not properly handling OPTIONS requests for CORS preflight

## 🔍 **DIAGNOSIS:**

### **CORS Configuration Issue:**
The backend needs to properly handle OPTIONS requests and return correct CORS headers for:
- **Origin**: `https://www.shineskincollective.com`
- **Methods**: GET, POST, OPTIONS
- **Headers**: Content-Type, Authorization

## 🎯 **SOLUTION: UPDATE BACKEND CORS CONFIG**

### **Step 1: Check Current CORS Configuration**

The backend needs to be updated to handle OPTIONS requests properly. The current configuration may be missing proper OPTIONS handling.

### **Step 2: Update Backend CORS Settings**

**Option A: Update via EB Console**
1. **Go to Elastic Beanstalk Console**
2. **Select environment**: SHINE-env
3. **Configuration** → **Software**
4. **Add environment variable**:
   ```
   CORS_ORIGINS=https://www.shineskincollective.com
   ```

**Option B: Update Backend Code**
The Flask app needs to properly handle OPTIONS requests:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://www.shineskincollective.com'], 
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

@app.route('/api/v2/analyze/guest', methods=['OPTIONS'])
def handle_options():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', 'https://www.shineskincollective.com')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
```

### **Step 3: Deploy Updated Backend**

1. **Update backend code** with proper CORS handling
2. **Deploy to EB** environment
3. **Test CORS** with browser requests

## 🦄 **UNICORN ALPHA BACKEND:**

**URL**: `https://api.shineskincollective.com`
**Status**: ✅ **LIVE AND OPERATIONAL**
**Issue**: ⚠️ **CORS configuration needs update**

## 📋 **IMMEDIATE ACTION:**

**Please update the backend CORS configuration to properly handle OPTIONS requests for `https://www.shineskincollective.com`**

**Then test with:**
```bash
curl -I https://api.shineskincollective.com/api/v2/analyze/guest
```

---

**🎯 Status**: Frontend working, backend needs CORS fix!
**⏰ Next**: Update backend CORS configuration. 