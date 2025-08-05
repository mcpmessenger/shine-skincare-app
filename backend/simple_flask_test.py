#!/usr/bin/env python3
"""
Simple Flask test to isolate the server startup issue
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/')
def home():
    return jsonify({'message': 'Flask server is working'})

if __name__ == '__main__':
    print("Starting simple Flask server...")
    print("This should work if Flask is configured correctly")
    try:
        app.run(debug=False, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Error starting Flask server: {e}")
        import traceback
        traceback.print_exc() 