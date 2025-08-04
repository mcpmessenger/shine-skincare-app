#!/usr/bin/env python3
"""
Start backend on port 8000 to avoid conflicts
"""

import os
import sys

# Set environment variables
os.environ['PORT'] = '8000'
os.environ['FLASK_DEBUG'] = 'false'

print("Starting backend on port 8000...")
print("This should avoid any port conflicts")

try:
    from enhanced_app import app
    print("✅ Successfully imported enhanced_app")
    print("🚀 Starting Flask server on port 8000...")
    app.run(host='0.0.0.0', port=8000, debug=False)
except Exception as e:
    print(f"❌ Failed to start backend: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 