#!/usr/bin/env python3
"""
Simple test for Google Vision service
"""

try:
    from app.services.google_vision_service import GoogleVisionService
    svc = GoogleVisionService()
    is_available = svc.is_available()
    print('✅ Google Vision available:', is_available)
    
    if is_available:
        print('🎉 Google Vision API is properly configured!')
    else:
        print('❌ Google Vision API is not available. Check credentials.')
        
except Exception as e:
    print('❌ Error testing Google Vision service:', str(e)) 