# Face Detection Troubleshooting Guide

## Overview
This guide covers common face detection issues and their solutions for the Shine Skincare app.

## Quick Status Check

### ✅ Face Detection Working
- Green oval appears around detected faces
- Console shows: "Face detected with confidence: 0.95"
- Face bounds are calculated correctly

### ❌ Face Detection Failing
- No green oval appears
- Console shows errors
- Face detection requests fail

## Common Issues & Solutions

### 1. CORS Policy Blocked
**Symptoms:**
```
Access to fetch at 'http://localhost:8000/api/v4/face/detect' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solutions:**
- Ensure backend has CORS enabled: `CORS(app, origins=['http://localhost:3000'])`
- Check backend is running on correct port
- Verify frontend environment variables

### 2. Backend Endpoint Not Found (404)
**Symptoms:**
```
POST http://localhost:8000/api/v4/face/detect 404 (Not Found)
```

**Solutions:**
- Restart backend after code changes
- Verify endpoint exists: `@app.route('/api/v4/face/detect', methods=['POST'])`
- Check backend logs for startup errors

### 3. Port Mismatch
**Symptoms:**
- Frontend tries to connect to wrong port
- Connection refused errors

**Solutions:**
- Backend should run on port 8000
- Frontend should use `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000`
- Check `.env.local` file exists in project root

### 4. Backend Not Running
**Symptoms:**
- All requests fail
- Connection refused errors

**Solutions:**
- Start backend: `python application_hare_run_v6.py`
- Look for: "Running on http://0.0.0.0:8000"
- Check for Python import errors

## Debugging Steps

### Step 1: Check Backend Status
```bash
curl http://localhost:8000/
```
Should show all available endpoints including `/api/v4/face/detect`

### Step 2: Test Face Detection Endpoint
```bash
curl -X POST http://localhost:8000/api/v4/face/detect \
  -H "Content-Type: application/json" \
  -d '{"image": "test"}'
```

### Step 3: Check Frontend Configuration
```javascript
// In browser console
console.log('Backend URL:', process.env.NEXT_PUBLIC_BACKEND_URL);
console.log('API Config:', API_CONFIG.BACKEND_URL);
```

### Step 4: Verify Environment File
Ensure `.env.local` exists in project root:
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Environment Setup

### Backend (Port 8000)
```bash
cd backend
python application_hare_run_v6.py
```

### Frontend (Port 3000)
```bash
cd project_root
npm run dev
```

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_DEBUG_MODE=true
NEXT_PUBLIC_ENVIRONMENT=development
```

## Expected Flow

1. **Camera Access**: User grants camera permissions
2. **Face Detection**: Frontend captures video frame
3. **API Call**: POST to `/api/v4/face/detect` with image data
4. **Backend Processing**: OpenCV face detection
5. **Response**: Face coordinates and confidence
6. **Visual Feedback**: Green oval overlay on detected face

## Success Indicators

- ✅ Green oval appears around faces
- ✅ Console shows successful face detection
- ✅ Face bounds are reasonable values
- ✅ No CORS or network errors

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| CORS policy blocked | Backend CORS not configured | Enable CORS in Flask app |
| 404 Not Found | Endpoint missing | Restart backend, check route |
| Connection refused | Backend not running | Start backend server |
| Port mismatch | Wrong backend URL | Check .env.local file |

## Testing Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] .env.local file exists with correct backend URL
- [ ] Camera permissions granted
- [ ] Face detection endpoint responds (not 404)
- [ ] Green oval appears around detected faces
- [ ] Console shows successful face detection logs

## Next Steps After Face Detection Works

Once face detection is working, the next step is usually:
- ML model loading for skin analysis
- Model file availability
- Enhanced analysis endpoints

## Support

If face detection issues persist:
1. Check this troubleshooting guide
2. Review backend startup logs
3. Verify environment configuration
4. Test endpoints individually
5. Check browser console for specific errors

---
*Last Updated: December 2024*
*Version: 1.0*
