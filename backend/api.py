"""
Main API entry point for AWS Elastic Beanstalk deployment
"""
import os
import sys

# For AWS EB deployment, import the main Flask app
if __name__ == "__main__":
    # Import and run the main app
    from app import create_app
    app = create_app('production')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # For other imports, import the full app
    from app import create_app
    app = create_app('production')