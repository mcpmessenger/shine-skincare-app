#!/usr/bin/env python3
"""
Start Flask server properly on Windows
"""

import threading
import time
from test_flask_simple import app

def run_server():
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("Starting Flask server in background...")
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    print("Server started in background thread")
    print("Testing server in 5 seconds...")
    time.sleep(5)
    
    try:
        import requests
        response = requests.get('http://127.0.0.1:5001/')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing server: {e}")
    
    print("Keeping server running...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped") 