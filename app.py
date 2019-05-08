"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.debug import DebuggedApplication
#from flask_cors import CORS


app = Flask(__name__)

#enable CORS - need to install flask_cors first
#CORS(app)

#app.wsgi_app = ProxyFix(app.wsgi_app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
#wsgi_app = app.wsgi_app




#import all of our routes
from routes import *

# Launching server
if __name__ == '__main__':
    print('running on localhost port 8081 huh')
    #import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    print(HOST)
    #try:
    #    PORT = int(os.environ.get('SERVER_PORT', '8000'))
    #except ValueError:
    PORT = 8081
    app.debug = True
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True, pin_security=False)
    #print PORT
    app.run(HOST, PORT, threaded = True)
    #app.run(port = 8081, threaded = True, debug = True)
    #app.run(host='127.0.0.1',port=8000)

