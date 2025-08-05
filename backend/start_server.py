#!/usr/bin/env python3
"""
Script to start Flask server in background thread
"""

import threading
import time
import sys

try:
    from enhanced_analysis_api import app
    
    def run_server():
        app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
    
    print("Starting Flask server in background thread...")
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    print("✅ Server started! Waiting 5 seconds for startup...")
    time.sleep(5)
    print("✅ Server should be ready at http://127.0.0.1:5000")
    print("Press Ctrl+C to stop...")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        sys.exit(0)
        
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 