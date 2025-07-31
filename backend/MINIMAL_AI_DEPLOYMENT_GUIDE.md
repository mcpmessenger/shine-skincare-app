# 🔬 Minimal AI Deployment Guide

## 🎯 **PURPOSE**
Deploy with **minimal AI services** within **t3.micro environment constraints** while building on the proven stable approach. This addresses the **version mismatch** and **web service not running** issues.

## 🚀 **FEATURES INCLUDED**

### **🔬 Minimal AI Services:**
- **Core AI Libraries**: NumPy, Pillow (minimal memory usage)
- **Optional OpenCV**: Lightweight image processing
- **Memory Optimized**: 64x64 image processing (vs 224x224)
- **Gradual Loading**: AI models loaded with fallbacks
- **Conservative Configuration**: Single worker, minimal timeouts

### **🔧 Minimal Configuration:**
- **Instance Type**: `t3.micro` (1GB RAM, 2 vCPUs) - current environment
- **Workers**: 1 (minimal for stability)
- **Timeout**: 60 seconds (conservative)
- **Memory**: Optimized for 1GB RAM constraint

## 📦 **DEPLOYMENT PACKAGE**
- **File**: `MINIMAL_AI_DEPLOYMENT_20250731_052856.zip`
- **Size**: 0.00 MB (minimal, dependencies downloaded)
- **Strategy**: Minimal AI services within t3.micro constraints

## 🎯 **STRATEGY: ADDRESS THE VERSION MISMATCH**

### **✅ WHAT'S THE SAME (Proven to Work):**
- **Self-contained `application.py`** (no imports from `app` module)
- **Simple CORS configuration** (no duplication)
- **Valid Elastic Beanstalk configuration** (no invalid options)
- **Stable deployment pattern** (proven approach)

### **🔬 WHAT'S NEW (Minimal AI):**
- **Minimal AI libraries** (NumPy, Pillow, OpenCV only)
- **Memory optimization** (64x64 images, minimal processing)
- **Single worker** (reduces memory usage)
- **Conservative timeouts** (60 seconds)
- **Gradual loading** (with fallbacks)

## 🚀 **DEPLOYMENT INSTRUCTIONS**

### **Step 1: Upload to Elastic Beanstalk**
1. **Go to AWS Elastic Beanstalk Console**
2. **Select environment**: SHINE-env
3. **Upload and Deploy** → **Upload your file**
4. **Select**: `MINIMAL_AI_DEPLOYMENT_20250731_052856.zip`
5. **Deploy**

### **Step 2: Monitor Deployment**
- **Watch for**: Successful deployment completion
- **Check**: Environment health remains "Ok"
- **Verify**: Core AI libraries load successfully
- **Monitor**: Memory usage stays under 1GB

### **Step 3: Test Minimal AI Services**
1. **Test core AI** (`/api/v2/analyze/guest`)
2. **Check model status** (`/health` endpoint)
3. **Verify memory usage** (should stay under 1GB)
4. **Test minimal search** (`/api/minimal/search`)

## ✅ **SUCCESS CRITERIA**

### **✅ Deployment Success:**
- [ ] Environment deploys without errors
- [ ] No version mismatch errors
- [ ] Web service starts successfully
- [ ] Health checks pass
- [ ] No engine execution errors

### **✅ Minimal AI Success:**
- [ ] Core AI (NumPy, Pillow) working
- [ ] OpenCV loads with fallback
- [ ] Memory usage under 1GB
- [ ] Minimal analysis completing
- [ ] Detailed model status reporting

### **✅ Stability Success:**
- [ ] No version mismatch from previous deployment
- [ ] Web service running properly
- [ ] Conservative resource usage
- [ ] Graceful error handling

## 🔍 **TROUBLESHOOTING**

### **If version mismatch persists:**
1. **Check deployment ID** (should be new version)
2. **Verify application.py** (self-contained)
3. **Monitor startup logs** (for AI library issues)
4. **Check memory usage** (should stay under 1GB)

### **If web service not running:**
1. **Check AI library imports** (gradual loading)
2. **Verify memory constraints** (1GB limit)
3. **Monitor startup time** (60 second timeout)
4. **Check fallback mechanisms** (mock services)

### **If deployment fails:**
1. **Rollback to simple CORS fix** (proven stable)
2. **Check minimal dependencies** (lighter than conservative)
3. **Verify t3.micro constraints** (1GB RAM limit)
4. **Monitor resource usage** (minimal approach)

## 📊 **EXPECTED RESULTS**

### **Before Minimal AI Deployment:**
- ❌ Version mismatch errors
- ❌ Web service not running
- ❌ 100% HTTP 5xx errors
- ❌ Environment in "Severe" status

### **After Minimal AI Deployment:**
- ✅ Core AI libraries working
- ✅ Minimal memory usage (< 1GB)
- ✅ Web service running properly
- ✅ Conservative resource usage
- ✅ Detailed model status reporting

## 🎯 **NEXT STEPS**

### **Immediate (After Deployment):**
1. **Test minimal AI functionality**
2. **Verify memory constraints**
3. **Monitor model status**
4. **Check conservative performance**

### **Future:**
1. **Gradually increase AI capabilities**
2. **Optimize minimal approach**
3. **Consider environment upgrade**
4. **Add more AI models gradually**

---

**🔬 This deployment addresses the version mismatch with minimal AI services within t3.micro constraints!**

**The strategy: Build on proven stable approach, use minimal AI libraries with memory optimization, single worker for stability, and gradual loading with fallbacks.** 