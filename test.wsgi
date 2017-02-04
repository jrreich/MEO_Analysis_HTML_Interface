import sys
 
#Expand Python classes path with your app's path
sys.path.insert(0, "C:/Users/reichj/Source/Repos/MEO_Analysis_HTML_Interface/")
 
from test import app
 
#Put logging code (and imports) here ...
 
#Initialize WSGI app object
application = app