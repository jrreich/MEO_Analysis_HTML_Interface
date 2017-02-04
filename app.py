"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)

#app.wsgi_app = ProxyFix(app.wsgi_app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
#wsgi_app = app.wsgi_app



#import all of our routes
from routes import *


# Launching server
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '8000'))
    except ValueError:
        PORT = 8000
    app.run(HOST, PORT)
    #app.run(host='127.0.0.1',port=8000)

