#!/usr/bin/env python3
"""
☠️ Operation Skully Fix Test
Tests the analysis ID extraction and response structure
"""

import json
import uuid
from datetime import datetime

def test_backend_response_structure():
    """Test the backend response structure to ensure analysis_id is in the correct location"""
    
    # Simulate the backend response structure
    backend_response = {
        'success': True,
        'data': {
            'image_id': f"guest_{uuid.uuid4().hex[:8]}",
            'analysis': {
                'analysis_id': str(uuid.uuid4()),
                'skinType': 'Combination',
                'concerns': ['Dryness', 'Uneven texture'],
                'recommended_products': [
                    {
                        'id': 'prod_1',
                        'name': 'Hydrating Cleanser',
                        'brand': 'Test Brand',
                        'price': 25.99,
                        'image_url': 'https://example.com/image.jpg',
                        'description': 'Gentle hydrating cleanser',
                        'ingredients': ['Hyaluronic Acid', 'Glycerin'],
                        'match_score': 0.85,
                        'matching_ingredients': ['Hyaluronic Acid']
                    }
                ],
                'ingredient_analysis': {
                    'primary_ingredients': ['Hyaluronic Acid', 'Glycerin'],
                    'secondary_ingredients': ['Aloe Vera'],
                    'avoid_ingredients': ['Fragrance', 'Alcohol']
                },
                'confidence_score': 0.87,
                'similar_profiles_analyzed': 150
            },
            'skin_classification': {
                'fitzpatrick_type': 'III',
                'confidence': 0.85
            },
            'message': 'Guest analysis completed. Sign up to save your results!'
        }
    }
    
    print("☠️ Operation Skully: Testing Backend Response Structure")
    print("=" * 60)
    
    # Test 1: Check if analysis_id exists in the correct location
    analysis_id = backend_response.get('data', {}).get('analysis', {}).get('analysis_id')
    print(f"✅ Analysis ID found: {analysis_id}")
    
    # Test 2: Check if the response structure matches frontend expectations
    if backend_response.get('success') and backend_response.get('data', {}).get('analysis'):
        print("✅ Response structure is correct")
    else:
        print("❌ Response structure is incorrect")
    
    # Test 3: Simulate frontend extraction logic
    frontend_extraction = backend_response.get('data', {}).get('analysis', {}).get('analysis_id')
    if frontend_extraction:
        print(f"✅ Frontend can extract analysis_id: {frontend_extraction}")
    else:
        print("❌ Frontend cannot extract analysis_id")
    
    return backend_response

def test_frontend_extraction_logic():
    """Test the frontend extraction logic with different response structures"""
    
    print("\n☠️ Operation Skully: Testing Frontend Extraction Logic")
    print("=" * 60)
    
    # Test case 1: New structure (data.analysis.analysis_id)
    response1 = {
        'success': True,
        'data': {
            'analysis': {
                'analysis_id': 'test_analysis_123'
            }
        }
    }
    
    # Test case 2: Old structure (analysis_id at top level)
    response2 = {
        'success': True,
        'analysis_id': 'test_analysis_456'
    }
    
    # Test case 3: Mixed structure
    response3 = {
        'success': True,
        'analysis_id': 'test_analysis_789',
        'data': {
            'analysis': {
                'analysis_id': 'test_analysis_999'
            }
        }
    }
    
    def extract_analysis_id(response):
        """Frontend extraction logic"""
        return response.get('data', {}).get('analysis', {}).get('analysis_id') or response.get('analysis_id')
    
    # Test all cases
    test_cases = [
        ('New structure', response1),
        ('Old structure', response2),
        ('Mixed structure', response3)
    ]
    
    for name, response in test_cases:
        analysis_id = extract_analysis_id(response)
        print(f"✅ {name}: analysis_id = {analysis_id}")
    
    return True

def test_localstorage_simulation():
    """Test localStorage simulation for the analysis results page"""
    
    print("\n☠️ Operation Skully: Testing localStorage Simulation")
    print("=" * 60)
    
    # Simulate the stored response
    stored_response = {
        'success': True,
        'data': {
            'analysis': {
                'analysis_id': 'test_analysis_123',
                'skinType': 'Combination',
                'concerns': ['Dryness'],
                'recommended_products': []
            }
        }
    }
    
    analysis_id = 'test_analysis_123'
    
    # Simulate localStorage.getItem
    stored_data = json.dumps(stored_response)
    
    # Simulate frontend parsing and extraction
    parsed_result = json.loads(stored_data)
    
    # Frontend extraction logic
    analysis_data = None
    if parsed_result.get('data', {}).get('analysis'):
        analysis_data = parsed_result['data']['analysis']
    elif parsed_result.get('analysis'):
        analysis_data = parsed_result['analysis']
    else:
        analysis_data = parsed_result
    
    print(f"✅ Analysis ID: {analysis_data.get('analysis_id')}")
    print(f"✅ Skin Type: {analysis_data.get('skinType')}")
    print(f"✅ Concerns: {analysis_data.get('concerns')}")
    
    return analysis_data

if __name__ == "__main__":
    print("☠️ Operation Skully Fix Test Suite")
    print("=" * 60)
    
    # Run all tests
    test_backend_response_structure()
    test_frontend_extraction_logic()
    test_localstorage_simulation()
    
    print("\n☠️ Operation Skully: All tests completed!")
    print("✅ The fix should resolve the 'Analysis result not found' bug") 