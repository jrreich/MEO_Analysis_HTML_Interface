
import sys
import os
import logging


sys.stdout = sys.stderr

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename= os.path.dirname(os.path.realpath(__file__))+ "/MEOlog.txt",
                    filemode='w')

# Get app root, directory of .wsgi file
app_root = os.path.dirname(__file__)
logging.info('app root') 

activate_this = os.path.dirname(os.path.realpath(__file__))+r'\mcc_venv\Scripts\activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))


    
sys.path.insert(0, app_root)
#sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
logging.info('executed path insert') 

from app import app as application