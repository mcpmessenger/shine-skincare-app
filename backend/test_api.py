#!/usr/bin/env python3
"""
API Testing Script for Shine Backend
This script tests all API endpoints to ensure they're working correctly
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def print_test(self, test_name, success=True, details=""):
        """Print test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        print()
    
    def test_health_check(self):
        """Test basic health check"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.print_test("Health Check", True, "Backend is running")
                return True
            else:
                self.print_test("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_auth_login(self):
        """Test authentication login endpoint"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "client_type": "web"
            })
            
            if response.status_code == 200:
                data = response.json()
                if "authorization_url" in data:
                    self.print_test("Auth Login", True, "OAuth URL generated successfully")
                    return True
                else:
                    self.print_test("Auth Login", False, "No authorization URL in response")
                    return False
            else:
                self.print_test("Auth Login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Auth Login", False, f"Error: {str(e)}")
            return False
    
    def test_trending_products(self):
        """Test trending products endpoint (public)"""
        try:
            response = self.session.get(f"{BASE_URL}/recommendations/trending")
            
            if response.status_code == 200:
                data = response.json()
                if "trending_products" in data:
                    product_count = len(data["trending_products"])
                    self.print_test("Trending Products", True, f"Found {product_count} products")
                    return True
                else:
                    self.print_test("Trending Products", False, "No trending_products in response")
                    return False
            else:
                self.print_test("Trending Products", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Trending Products", False, f"Error: {str(e)}")
            return False
    
    def test_products_endpoint(self):
        """Test products endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/recommendations/products")
            
            if response.status_code == 200:
                data = response.json()
                if "products" in data:
                    product_count = len(data["products"])
                    self.print_test("Products List", True, f"Found {product_count} products")
                    return True
                else:
                    self.print_test("Products List", False, "No products in response")
                    return False
            else:
                self.print_test("Products List", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Products List", False, f"Error: {str(e)}")
            return False
    
    def test_image_analysis_upload(self):
        """Test image analysis upload (requires authentication)"""
        try:
            # Create a simple test image (1x1 pixel PNG)
            test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\xd7\xd4\xc7\x00\x00\x00\x00IEND\xaeB`\x82'
            
            files = {'image': ('test.png', test_image_data, 'image/png')}
            data = {
                'analysis_type': 'skin_analysis',
                'privacy_level': 'private'
            }
            
            response = self.session.post(f"{BASE_URL}/analysis/upload", files=files, data=data)
            
            if response.status_code == 401:
                self.print_test("Image Upload (Auth Required)", True, "Correctly requires authentication")
                return True
            elif response.status_code == 200:
                data = response.json()
                if "upload_id" in data:
                    self.print_test("Image Upload", True, f"Upload ID: {data['upload_id']}")
                    return True
                else:
                    self.print_test("Image Upload", False, "No upload_id in response")
                    return False
            else:
                self.print_test("Image Upload", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Image Upload", False, f"Error: {str(e)}")
            return False
    
    def test_payment_intent_creation(self):
        """Test payment intent creation (requires authentication)"""
        try:
            response = self.session.post(f"{BASE_URL}/payments/create-intent", json={
                "amount": 1000,  # $10.00 in cents
                "currency": "usd",
                "order_items": [
                    {
                        "product_id": "test-product-id",
                        "quantity": 1
                    }
                ]
            })
            
            if response.status_code == 401:
                self.print_test("Payment Intent (Auth Required)", True, "Correctly requires authentication")
                return True
            elif response.status_code == 200:
                data = response.json()
                if "payment_intent_id" in data:
                    self.print_test("Payment Intent Creation", True, f"Intent ID: {data['payment_intent_id']}")
                    return True
                else:
                    self.print_test("Payment Intent Creation", False, "No payment_intent_id in response")
                    return False
            else:
                self.print_test("Payment Intent Creation", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Payment Intent Creation", False, f"Error: {str(e)}")
            return False
    
    def test_mcp_discovery(self):
        """Test MCP discovery endpoint (requires authentication)"""
        try:
            response = self.session.post(f"{BASE_URL}/mcp/discover-similar", json={
                "analysis_id": "test-analysis-id",
                "search_parameters": {},
                "result_limit": 10,
                "quality_threshold": 0.5
            })
            
            if response.status_code == 401:
                self.print_test("MCP Discovery (Auth Required)", True, "Correctly requires authentication")
                return True
            elif response.status_code == 200:
                data = response.json()
                if "discovery_id" in data:
                    self.print_test("MCP Discovery", True, f"Discovery ID: {data['discovery_id']}")
                    return True
                else:
                    self.print_test("MCP Discovery", False, "No discovery_id in response")
                    return False
            else:
                self.print_test("MCP Discovery", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("MCP Discovery", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Testing Shine Backend API...")
        print("=" * 60)
        print(f"Testing against: {BASE_URL}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Auth Login", self.test_auth_login),
            ("Trending Products", self.test_trending_products),
            ("Products List", self.test_products_endpoint),
            ("Image Upload", self.test_image_analysis_upload),
            ("Payment Intent", self.test_payment_intent_creation),
            ("MCP Discovery", self.test_mcp_discovery),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.print_test(test_name, False, f"Exception: {str(e)}")
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the backend configuration.")
        
        return passed == total

def main():
    """Main testing function"""
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Backend is ready for frontend integration!")
        print("\nNext steps:")
        print("1. Start the frontend: npm run dev")
        print("2. Test the full application at http://localhost:3000")
    else:
        print("\n❌ Backend needs attention before frontend integration.")
        print("\nPlease check:")
        print("1. Backend server is running: python run.py")
        print("2. Database is properly configured")
        print("3. All dependencies are installed")

if __name__ == '__main__':
    main() 