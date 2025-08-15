#!/usr/bin/env python3
"""
Test script to analyze the Kris image with updated acne detection thresholds
"""

import requests
import base64
import json

def test_image_analysis(image_path):
    """Test the image analysis with the updated acne detection"""
    
    # Read and encode the image
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Prepare the request payload
    payload = {
        'image': f'data:image/jpeg;base64,{image_data}'
    }
    
    # Test the latest v6 endpoint
    url = 'http://localhost:8000/api/v6/skin/analyze-hare-run'
    
    try:
        print(f"🧪 Testing image: {image_path}")
        print(f"🌐 Endpoint: {url}")
        print("⏳ Sending request...")
        
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis successful!")
            print("\n📊 Results:")
            print(json.dumps(result, indent=2))
            
            # Extract acne-specific results
            if 'skin_condition_analysis' in result:
                skin_analysis = result['skin_condition_analysis']
                if 'conditions' in skin_analysis and 'acne' in skin_analysis['conditions']:
                    acne = skin_analysis['conditions']['acne']
                    print(f"\n🩹 Acne Analysis (Updated Thresholds):")
                    print(f"   Detected: {acne.get('detected', False)}")
                    print(f"   Percentage: {acne.get('percentage', 0):.4f}")
                    print(f"   Spot Count: {acne.get('spot_count', 0)}")
                    print(f"   Severity: {acne.get('severity', 'none')}")
                    print(f"   Confidence: {acne.get('confidence', 0):.3f}")
                    
                    # Check if our thresholds are working
                    if acne.get('detected', False):
                        if acne.get('severity') == 'severe':
                            print("   ⚠️  SEVERE - This should be rare with new thresholds")
                        elif acne.get('severity') == 'moderate':
                            print("   🔶 MODERATE - Moderate detection")
                        else:
                            print("   🟢 MILD - Conservative detection working")
                    else:
                        print("   🟢 NO ACNE DETECTED - Very conservative thresholds")
            
        else:
            print(f"❌ Analysis failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    # Test with the Kris image
    image_path = "Kris/Snapchat-1544972475.jpg"
    test_image_analysis(image_path)
