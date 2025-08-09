# 🧪 Smoke Test Guide for Pre-Deployment

## 📋 Overview
This guide helps you test both frontend and backend locally before deploying to AWS to ensure everything works correctly.

## 🎯 Test Checklist

### **Pre-Test Setup**
- [ ] Backend server running locally
- [ ] Frontend development server running
- [ ] Test images ready
- [ ] Network connectivity verified

## 🔧 Step 1: Backend Smoke Test

### **1.1 Start Backend Server**
```bash
cd backend
pip install -r requirements.txt
python run_fixed_model_server.py
```

**Expected Output:**
```
🚀 Shine Backend Server Starting...
📊 Loading ML model: fixed_model_final.h5
✅ Model loaded successfully
🌐 Server running on http://localhost:5000
📋 Available endpoints:
   - /api/v5/skin/analyze-fixed
   - /api/v4/face/detect
   - /api/v5/skin/health
   - /api/v5/skin/model-status
```

### **1.2 Test Backend Health**
```bash
curl http://localhost:5000/api/v5/skin/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-01-XX...",
  "version": "fixed_v1.0"
}
```

### **1.3 Test Model Status**
```bash
curl http://localhost:5000/api/v5/skin/model-status
```

**Expected Response:**
```json
{
  "model_version": "fixed_v1.0",
  "accuracy": "62.50%",
  "conditions_supported": ["acne", "actinic_keratosis", "melanoma", "nevus", "seborrheic_keratosis"],
  "model_loaded": true
}
```

### **1.4 Test Face Detection**
```bash
# Using a test image
curl -X POST http://localhost:5000/api/v4/face/detect \
  -F "image=@test-image.jpg"
```

**Expected Response:**
```json
{
  "faces_detected": 1,
  "faces": [
    {
      "bounds": {"x": 100, "y": 100, "width": 200, "height": 200},
      "confidence": 0.95
    }
  ],
  "success": true
}
```

### **1.5 Test Skin Analysis**
```bash
# Using a test image
curl -X POST http://localhost:5000/api/v5/skin/analyze-fixed \
  -F "image=@test-image.jpg"
```

**Expected Response:**
```json
{
  "primary_condition": "acne",
  "percentage": 85.5,
  "severity": "moderate",
  "top_3_predictions": [...],
  "all_predictions": {...},
  "recommendations": {
    "immediate_actions": [...],
    "lifestyle_changes": [...],
    "professional_advice": [...]
  }
}
```

## 🎨 Step 2: Frontend Smoke Test

### **2.1 Start Frontend Server**
```bash
# In a new terminal
npm install
npm run dev
```

**Expected Output:**
```
✓ Ready in X ms
- Local:        http://localhost:3000
- Network:      http://192.168.X.X:3000
```

### **2.2 Test Frontend Pages**

#### **2.2.1 Home Page Test**
1. Navigate to `http://localhost:3000`
2. Verify elements load:
   - [ ] Logo displays correctly
   - [ ] Upload button works
   - [ ] Camera button works
   - [ ] File input accepts images

#### **2.2.2 Image Upload Test**
1. Upload a test image
2. Verify:
   - [ ] Image preview displays
   - [ ] Face detection works
   - [ ] Analysis starts
   - [ ] Progress indicator shows

#### **2.2.3 Results Page Test**
1. Complete an analysis
2. Navigate to `/suggestions`
3. Verify:
   - [ ] Analysis results display
   - [ ] Product recommendations show
   - [ ] Shopping cart buttons work
   - [ ] Add to cart functionality works

### **2.3 Test Shopping Cart**
1. Add products to cart
2. Verify:
   - [ ] Cart counter updates
   - [ ] Products show green border when added
   - [ ] "Added to Cart" button changes
   - [ ] Checkout button appears

## 🔄 Step 3: Integration Test

### **3.1 Full User Flow Test**
1. **Upload Image**: Upload a test image
2. **Face Detection**: Verify face is detected
3. **Analysis**: Wait for ML analysis
4. **Results**: Check results page loads
5. **Products**: Verify product recommendations
6. **Cart**: Test add to cart functionality

### **3.2 API Communication Test**
```bash
# Test frontend-backend communication
curl -X POST http://localhost:3000/api/v4/skin/analyze-enhanced \
  -H "Content-Type: application/json" \
  -d '{"image_data": "base64_encoded_image_data"}'
```

## 🐛 Step 4: Error Handling Test

### **4.1 Backend Error Tests**
```bash
# Test with no image
curl -X POST http://localhost:5000/api/v5/skin/analyze-fixed

# Test with invalid image
curl -X POST http://localhost:5000/api/v5/skin/analyze-fixed \
  -F "image=@invalid.txt"

# Test with no face
curl -X POST http://localhost:5000/api/v4/face/detect \
  -F "image=@no-face-image.jpg"
```

### **4.2 Frontend Error Tests**
1. **Network Error**: Disconnect backend, test frontend
2. **Invalid Image**: Upload non-image file
3. **No Face**: Upload image without face
4. **Large Image**: Test with very large image

## 📊 Step 5: Performance Test

### **5.1 Response Time Tests**
```bash
# Test backend response times
time curl http://localhost:5000/api/v5/skin/health
time curl -X POST http://localhost:5000/api/v5/skin/analyze-fixed \
  -F "image=@test-image.jpg"
```

**Expected Performance:**
- Health check: < 100ms
- Face detection: < 2s
- Skin analysis: < 30s

### **5.2 Frontend Performance**
1. **Page Load**: < 3 seconds
2. **Image Upload**: < 5 seconds
3. **Analysis**: < 30 seconds
4. **Results Display**: < 2 seconds

## 🔍 Step 6: Browser Compatibility Test

### **6.1 Test Different Browsers**
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### **6.2 Test Mobile Responsiveness**
- [ ] iPhone Safari
- [ ] Android Chrome
- [ ] Tablet browsers

## 🎯 Step 7: Pre-Deployment Checklist

### **Backend Tests**
- [ ] Server starts without errors
- [ ] All endpoints respond correctly
- [ ] ML model loads successfully
- [ ] Error handling works
- [ ] Performance meets requirements

### **Frontend Tests**
- [ ] All pages load correctly
- [ ] Shopping cart works
- [ ] Image upload works
- [ ] API communication works
- [ ] Error messages display properly

### **Integration Tests**
- [ ] Full user flow works
- [ ] Frontend-backend communication works
- [ ] Environment variables configured
- [ ] No console errors

## 🚨 Common Issues & Solutions

### **Backend Issues**
1. **Model not loading**: Check file path and permissions
2. **Port already in use**: Change port or kill existing process
3. **Missing dependencies**: Run `pip install -r requirements.txt`

### **Frontend Issues**
1. **Build errors**: Check Node.js version and dependencies
2. **API connection failed**: Verify backend URL in environment
3. **Image upload fails**: Check file size and format

### **Integration Issues**
1. **CORS errors**: Check backend CORS configuration
2. **Environment variables**: Verify `.env.local` setup
3. **Network issues**: Check firewall and network settings

## ✅ Success Criteria

### **All Tests Pass**
- [ ] Backend health check: ✅
- [ ] Model status: ✅
- [ ] Face detection: ✅
- [ ] Skin analysis: ✅
- [ ] Frontend pages: ✅
- [ ] Shopping cart: ✅
- [ ] Error handling: ✅
- [ ] Performance: ✅

### **Ready for Deployment**
- [ ] All smoke tests pass
- [ ] No critical errors
- [ ] Performance acceptable
- [ ] Error handling robust
- [ ] Documentation complete

## 🚀 Next Steps After Smoke Test

1. **If all tests pass**: Proceed with AWS deployment
2. **If issues found**: Fix issues and re-test
3. **Document results**: Update deployment checklist
4. **Prepare deployment**: Follow migration steps

## 📞 Troubleshooting

If you encounter issues during smoke testing:
1. Check console logs for errors
2. Verify all dependencies installed
3. Test endpoints individually
4. Check environment variables
5. Review error messages carefully
