import sys
import os
import logging
import sys 

sys.stdout = sys.stderr

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename= os.path.dirname(os.path.realpath(__file__))+ "/MEOlog.txt",
                    filemode='w')

# Get app root, directory of .wsgi file
app_root = os.path.dirname(__file__)
logging.info('app root') 
#print 'ap root'
#print app_root
# Activate the virtualenv
activate_file = os.path.dirname(os.path.realpath(__file__))+r'\env\Scripts\activate_this.py'
#activate_file = os.path.join(app_root, 'env/Scripts/activate_this.py')
#print 'act file'
#print activate_file

execfile(activate_file, dict(__file__=activate_file))
logging.info('executed activate virtualenv') 
#print 'activated virtualenv'
# Add app root to path for imports

#sys.path.insert(0, app_root)
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
logging.info('executed path insert') 

#test import
import beacon_decode
logging.info('beacon decode as a test') 
# Import the app
from werkzeug.utils import secure_filename

from flask import Flask, url_for, request, render_template; 
#from app import app
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=os.path.dirname(os.path.realpath(__file__))+"/MEOimportlog.txt",
                    filemode='w')

from app import app
logging.info('imported app') 
application = app
logging.info('imported application as app') 
#from routes import app
#application = app