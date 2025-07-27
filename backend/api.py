"""
Main API entry point - redirects to Railway app for deployment
"""
import os
import sys

# For Railway deployment, redirect to railway_app.py
if __name__ == "__main__":
    # Import and run the railway app
    from railway_app import app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # For other imports, try to import the full app
    try:
        from app import create_app
        app = create_app('production')
    except ImportError:
        # If full app fails, import railway app
        from railway_app import app