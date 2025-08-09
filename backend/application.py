# Minimal EB application - guaranteed to work
from flask import Flask, jsonify

# Create Flask app
application = Flask(__name__)

@application.route('/')
def root():
    return jsonify({
        "message": "Shine Backend is running!",
        "status": "ok"
    })

@application.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "version": "minimal"
    })

@application.route('/api/health')
def api_health():
    return jsonify({
        "status": "ok",
        "version": "minimal"
    })

if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=8000)