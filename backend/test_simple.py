import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from load_env import load_env_file
    load_env_file()
except ImportError:
    print("Warning: Could not load environment variables")

def test_basic():
    print("Testing basic functionality...")
    
    # Test environment variables
    required_vars = ['SECRET_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"[OK] {var}: Set")
        else:
            print(f"[ERROR] {var}: Not set")
    
    # Test Flask app
    try:
        from simple_app import app
        print("[OK] Flask app created successfully")
        
        routes = [rule.rule for rule in app.url_map.iter_rules() if rule.rule.startswith('/api/')]
        print(f"[OK] API routes registered: {len(routes)}")
        for route in routes:
            print(f"  {route}")
            
    except Exception as e:
        print(f"[ERROR] Flask app test failed: {e}")

if __name__ == "__main__":
    test_basic()