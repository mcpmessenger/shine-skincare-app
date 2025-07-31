# Dual Skin Analysis Deployment Manifest
# Created: 2025-07-31T14:15:18.749556

## 🎯 PURPOSE
Deploy dual skin analysis with two workflows: 1) Selfie analysis with Google Vision face isolation, 2) General skin analysis
Both tools query the SCIN dataset for skin condition detection

## 🔧 FEATURES
- Core AI: NumPy, Pillow, OpenCV (proven working)
- SCIN Dataset Integration: Google Cloud Storage, SCIN dataset (proven working)
- Google Vision API: Face isolation for selfie analysis
- Selfie Analysis: Google Vision face isolation + skin condition detection + SCIN queries
- General Skin Analysis: Any skin photo + skin condition detection + SCIN queries
- Optimized for m5.2xlarge (32GB RAM, 8 vCPUs)
- Production-ready AI platform

## 📦 CONTENTS
- application.py: Dual skin analysis capabilities with SCIN dataset integration
- requirements.txt: SCIN dataset dependencies enabled
- Procfile: Gunicorn configuration (1 worker, 120s timeout)
- .ebextensions: m5.2xlarge configuration

## 🚀 DEPLOYMENT
1. Upload zip file to Elastic Beanstalk
2. Configure Google Vision API credentials
3. Configure SCIN dataset access
4. Monitor for successful deployment
5. Test both selfie and general skin analysis
6. Verify SCIN dataset queries

## ✅ SUCCESS CRITERIA
- Environment deploys successfully
- Google Vision API working for face isolation
- SCIN dataset queries completing
- Both selfie and general skin analysis working
- Memory usage within 32GB limits

## 🎯 STRATEGY
Build on proven SCIN dataset foundation
Add Google Vision API for face isolation
Support two distinct analysis workflows
Use fallback approach for stability
Monitor performance carefully
