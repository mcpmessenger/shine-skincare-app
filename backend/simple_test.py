#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""

from app import create_app, db
from app.models.products import Product

def test_backend():
    """Test basic backend functionality"""
    print("🧪 Testing Backend Functionality...")
    print("=" * 50)
    
    try:
        # Create app
        print("1. Creating Flask app...")
        app = create_app()
        print("✅ Flask app created successfully!")
        
        # Test database connection
        print("\n2. Testing database connection...")
        with app.app_context():
            # Count products
            product_count = Product.query.count()
            print(f"✅ Database connected! Found {product_count} products")
            
            # List some products
            products = Product.query.limit(3).all()
            print("\n3. Sample products:")
            for product in products:
                print(f"   - {product.name} by {product.brand} (${product.price})")
        
        print("\n" + "=" * 50)
        print("🎉 Backend is working correctly!")
        print("\nYou can now:")
        print("1. Start the server: python run.py")
        print("2. Test the API: python test_api.py")
        print("3. Start the frontend: npm run dev")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("1. Database setup: python setup_database.py")
        print("2. Dependencies: pip install -r requirements.txt")
        return False

if __name__ == '__main__':
    test_backend() 