# WSGI entry point for Elastic Beanstalk
# This file is required by the Procfile to run the Flask application

from application import app

# Elastic Beanstalk expects this variable name
application = app

if __name__ == "__main__":
    application.run()
