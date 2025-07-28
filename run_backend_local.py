#!/usr/bin/env python3
"""
Run the backend locally for testing
"""
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'real_deploy'))

from real_working_backend import app

if __name__ == '__main__':
    print("🚀 Starting Shine Backend locally...")
    print("📡 Backend will be available at: http://localhost:5000")
    print("🔗 Frontend can connect to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 