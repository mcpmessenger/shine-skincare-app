# 🧪 Local Testing Guide

## 📋 Overview
Test the Shine Skincare App locally before AWS deployment to ensure everything works correctly.

## 🔧 Step 1: Test Backend Server

### **1.1 Start Backend Server**
Open a terminal and run:
```bash
cd backend
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

### **1.2 Test Backend Endpoints**
Open a **new terminal** and test each endpoint:

#### **Health Check**
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

#### **Model Status**
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

#### **Face Detection Test** (if you have test-image.jpg)
```bash
curl -X POST http://localhost:5000/api/v4/face/detect -F "image=@test-image.jpg"
```

#### **Skin Analysis Test** (if you have test-image.jpg)
```bash
curl -X POST http://localhost:5000/api/v5/skin/analyze-fixed -F "image=@test-image.jpg"
```

## 🎨 Step 2: Test Frontend

### **2.1 Start Frontend Server**
Open a **new terminal** and run:
```bash
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
1. Open browser to `http://localhost:3000`
2. Check if these elements load correctly:
   - [ ] Shine logo displays
   - [ ] Upload button is visible
   - [ ] Camera button is visible
   - [ ] File input accepts images

#### **2.2.2 Image Upload Test**
1. Upload a test image (face photo)
2. Verify:
   - [ ] Image preview displays
   - [ ] Face detection message appears
   - [ ] Analysis starts automatically
   - [ ] Progress indicator shows

#### **2.2.3 Results Page Test**
1. Wait for analysis to complete
2. Navigate to `/suggestions` page
3. Verify:
   - [ ] Analysis results display
   - [ ] Primary condition shows
   - [ ] Confidence percentage shows
   - [ ] Product recommendations appear
   - [ ] Shopping cart buttons are visible

### **2.3 Test Shopping Cart Functionality**
1. On results page, find product recommendations
2. Test cart functionality:
   - [ ] Click "Add to Cart" button
   - [ ] Button changes to "Added to Cart" with checkmark
   - [ ] Product card shows green border
   - [ ] Cart counter updates at top
   - [ ] Click button again to remove from cart
   - [ ] Checkout button appears when items in cart

## 🔄 Step 3: Integration Test

### **3.1 Full User Flow Test**
Complete this entire flow:

1. **Start both servers** (backend and frontend)
2. **Upload image** on home page
3. **Wait for face detection** (should see "Face detected" message)
4. **Wait for analysis** (may take 10-30 seconds)
5. **Check results page** - should show:
   - Primary skin condition
   - Confidence percentage
   - Severity level
   - Top 3 predictions
   - Recommendations (immediate actions, lifestyle, professional advice)
   - Product recommendations with images
6. **Test shopping cart**:
   - Add products to cart
   - Verify visual feedback
   - Test checkout button

### **3.2 Browser Console Check**
1. Open browser developer tools (F12)
2. Check Console tab for errors
3. Should see minimal errors, mainly:
   - ✅ API calls to backend
   - ✅ Successful responses
   - ❌ No critical errors

## 🐛 Step 4: Error Testing

### **4.1 Test Error Handling**
1. **Stop backend server** (Ctrl+C)
2. **Try uploading image** on frontend
3. **Expected behavior**:
   - Should show error message
   - Should not crash
   - Should handle gracefully

### **4.2 Test Invalid Inputs**
1. **Upload non-image file** (e.g., .txt file)
2. **Upload image without face**
3. **Expected behavior**:
   - Should show appropriate error messages
   - Should not crash

## ✅ Success Checklist

### **Backend Tests**
- [ ] Server starts without errors
- [ ] Health endpoint returns "healthy"
- [ ] Model status shows "model_loaded": true
- [ ] Face detection endpoint works
- [ ] Skin analysis endpoint works
- [ ] All endpoints respond within reasonable time

### **Frontend Tests**
- [ ] Home page loads correctly
- [ ] Image upload works
- [ ] Results page displays properly
- [ ] Shopping cart functions correctly
- [ ] No critical console errors
- [ ] Responsive design works

### **Integration Tests**
- [ ] Frontend can communicate with backend
- [ ] Full user flow works end-to-end
- [ ] Error handling works properly
- [ ] Performance is acceptable (analysis < 30s)

## 🚨 Common Issues & Solutions

### **Backend Issues**
1. **"Model not found"**: Check if `fixed_model_final.h5` exists in backend directory
2. **"Port already in use"**: Kill existing process or use different port
3. **"Module not found"**: Run `pip install -r requirements.txt`

### **Frontend Issues**
1. **"Module not found"**: Run `npm install`
2. **"Connection refused"**: Make sure backend is running on port 5000
3. **Build errors**: Check Node.js version compatibility

### **Integration Issues**
1. **CORS errors**: Check backend CORS settings
2. **API calls fail**: Verify backend URL in environment variables
3. **Images not uploading**: Check file size and format

## 🎯 Performance Expectations

### **Response Times**
- Health check: < 100ms
- Face detection: < 2s
- Skin analysis: < 30s
- Page loads: < 3s

### **Accuracy**
- Model accuracy: 62.50% (improved from 60.2%)
- Face detection: Should detect faces in clear photos
- Product recommendations: Should show relevant products

## 🚀 Next Steps

### **If All Tests Pass ✅**
- Proceed with AWS deployment
- Backend first (Elastic Beanstalk)
- Then frontend (Amplify)

### **If Issues Found ❌**
- Fix issues locally first
- Re-test until all pass
- Document any changes needed
- Then proceed with deployment

## 📞 Need Help?

If you encounter issues:
1. Check the terminal/console for error messages
2. Verify all dependencies are installed
3. Check file paths and permissions
4. Test endpoints individually
5. Review error logs carefully

Ready to test? Start with Step 1! 🧪
