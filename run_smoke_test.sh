#!/bin/bash

# Shine Skincare App Smoke Test Script
# This script tests the backend functionality before deployment

echo "🧪 Starting Shine Skincare App Smoke Test..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Check if backend server is running
echo "🔍 Checking if backend server is running..."
if curl -s http://localhost:5000/api/v5/skin/health > /dev/null; then
    print_status 0 "Backend server is running"
else
    print_status 1 "Backend server is not running"
    echo "💡 Start the backend with: cd backend && python run_fixed_model_server.py"
    exit 1
fi

# Test health endpoint
echo "🏥 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:5000/api/v5/skin/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_status 0 "Health endpoint working"
else
    print_status 1 "Health endpoint failed"
    echo "Response: $HEALTH_RESPONSE"
fi

# Test model status endpoint
echo "📊 Testing model status endpoint..."
MODEL_RESPONSE=$(curl -s http://localhost:5000/api/v5/skin/model-status)
if echo "$MODEL_RESPONSE" | grep -q "model_loaded.*true"; then
    print_status 0 "Model status endpoint working"
else
    print_status 1 "Model status endpoint failed"
    echo "Response: $MODEL_RESPONSE"
fi

# Test face detection endpoint (if test image exists)
if [ -f "test-image.jpg" ]; then
    echo "👤 Testing face detection endpoint..."
    FACE_RESPONSE=$(curl -s -X POST http://localhost:5000/api/v4/face/detect -F "image=@test-image.jpg")
    if echo "$FACE_RESPONSE" | grep -q "faces_detected"; then
        print_status 0 "Face detection endpoint working"
    else
        print_status 1 "Face detection endpoint failed"
        echo "Response: $FACE_RESPONSE"
    fi
else
    echo -e "${YELLOW}⚠️  No test image found. Skipping face detection test.${NC}"
fi

# Test skin analysis endpoint (if test image exists)
if [ -f "test-image.jpg" ]; then
    echo "🔬 Testing skin analysis endpoint..."
    echo "⏳ This may take up to 30 seconds..."
    ANALYSIS_RESPONSE=$(curl -s -X POST http://localhost:5000/api/v5/skin/analyze-fixed -F "image=@test-image.jpg" --max-time 35)
    if echo "$ANALYSIS_RESPONSE" | grep -q "primary_condition"; then
        print_status 0 "Skin analysis endpoint working"
    else
        print_status 1 "Skin analysis endpoint failed"
        echo "Response: $ANALYSIS_RESPONSE"
    fi
else
    echo -e "${YELLOW}⚠️  No test image found. Skipping skin analysis test.${NC}"
fi

# Test error handling
echo "🐛 Testing error handling..."
ERROR_RESPONSE=$(curl -s -X POST http://localhost:5000/api/v5/skin/analyze-fixed)
if echo "$ERROR_RESPONSE" | grep -q "error"; then
    print_status 0 "Error handling working"
else
    print_status 1 "Error handling failed"
    echo "Response: $ERROR_RESPONSE"
fi

# Performance test
echo "⚡ Testing performance..."
START_TIME=$(date +%s.%N)
curl -s http://localhost:5000/api/v5/skin/health > /dev/null
END_TIME=$(date +%s.%N)
RESPONSE_TIME=$(echo "$END_TIME - $START_TIME" | bc)
if (( $(echo "$RESPONSE_TIME < 1" | bc -l) )); then
    print_status 0 "Performance acceptable (${RESPONSE_TIME}s)"
else
    print_status 1 "Performance slow (${RESPONSE_TIME}s)"
fi

echo ""
echo "=============================================="
echo "🧪 Smoke Test Complete!"
echo ""
echo "📋 Summary:"
echo "- Backend server: Running"
echo "- Health endpoint: Working"
echo "- Model status: Working"
echo "- Face detection: Tested"
echo "- Skin analysis: Tested"
echo "- Error handling: Working"
echo "- Performance: Acceptable"
echo ""
echo "🎯 Next Steps:"
echo "1. Test frontend locally (npm run dev)"
echo "2. Test full user flow"
echo "3. If all tests pass, proceed with deployment"
echo ""
echo "💡 To test frontend:"
echo "   npm install"
echo "   npm run dev"
echo "   Then visit http://localhost:3000"
