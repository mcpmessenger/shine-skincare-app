#!/usr/bin/env python3
"""
Minimal Flask test to see if basic server works
"""

from flask import Flask

app = Flask(__name__)

@app.route('/test')
def test():
    return {'status': 'ok', 'message': 'Server is running'}

if __name__ == '__main__':
    print("Starting minimal Flask server...")
    app.run(debug=False, host='127.0.0.1', port=5000) 