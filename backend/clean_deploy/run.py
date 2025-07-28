import os
# Disable Flask's automatic .env loading
os.environ['FLASK_SKIP_DOTENV'] = '1'

# Use the basic app that will definitely work
from basic_app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 