# Minimal Lesion Detection Deployment Manifest
# Created: 2025-07-31T14:03:13.436346

## 🎯 PURPOSE
Deploy minimal lesion detection with Google Vision API for facial features overlay
Focus on core functionality without heavy AI dependencies

## 🔧 FEATURES
- Core AI: NumPy, Pillow (proven working - minimal set)
- Google Vision API: Facial features overlay
- Lesion/Mole Detection: Focused on specific skin features
- Lesion Matching: Find similar cases
- Optimized for m5.large (8GB RAM, 2 vCPUs)
- Minimal dependencies for fast deployment

## 📦 CONTENTS
- application.py: Minimal lesion detection capabilities
- requirements.txt: Minimal dependencies (no heavy AI libraries)
- Procfile: Gunicorn configuration (1 worker, 120s timeout)
- .ebextensions: m5.large configuration

## 🚀 DEPLOYMENT
1. Upload zip file to Elastic Beanstalk
2. Configure Google Vision API credentials
3. Monitor for successful deployment
4. Test lesion detection and matching
5. Verify facial features overlay

## ✅ SUCCESS CRITERIA
- Environment deploys successfully (no hanging)
- Google Vision API working
- Lesion detection completing
- Memory usage within 8GB limits
- Fast deployment (minimal dependencies)

## 🎯 STRATEGY
Focus on core functionality only
Use minimal dependencies to avoid timeouts
Add Google Vision API for facial features
Add lesion/mole detection and matching
Use fallback approach for stability
Monitor performance carefully
