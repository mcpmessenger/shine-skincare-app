from backend.app.services.google_vision_service import GoogleVisionService

def test_vision_service():
    try:
        svc = GoogleVisionService()
        is_available = svc.is_available()
        print('✅ Google Vision available:', is_available)
        
        if is_available:
            print('🎉 Google Vision API is properly configured!')
        else:
            print('❌ Google Vision API is not available. Check credentials.')
            
    except Exception as e:
        print('❌ Error testing Google Vision service:', str(e))

if __name__ == "__main__":
    test_vision_service() 