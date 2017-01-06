from werkzeug.utils import secure_filename
from flask import Flask, url_for, request, render_template; 
from app import app
import beacon_decode as bcn
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'var/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','db','zip'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#server/Main
@app.route('/')
def index():
    """Renders a sample page."""
    createLink = "<a href = '" + url_for('beacon') + "'>Beacon Decoder</a>"; # url_for usings the function name to point to URL
    return render_template('index3.html')

@app.route('/beacon', methods=['GET','POST'])
def beacon():
    if request.method == 'GET':
        # Send the user the form
        return render_template('BeaconDecoder3.html')
    elif request.method == 'POST':
        # read beacon ID and save it
        beaconID = request.form['beaconID']        

        #decode and return it
        bcn1 = bcn.beacon(beaconID)
        #return results
        return render_template('BeaconDecoded.html', \
            beaconID = beaconID, \
            beaconID15 = bcn1.bcnID15, \
            countrycode = int(bcn1.country_code,2), \
            protocolcode = bcn1.protocol)
    else: 
        return '<h2> Invalid Request </h2>'

@app.route('/rawburst', methods=['GET','POST'])
def rawburst():
    if request.method == 'GET':
        # Send the user the form
        return render_template('BurstAnalysisForm.html')
    elif request.method == 'POST':
        # read input
        result = request.form
        f = request.files['inputfile']
        print f        
        f.save(UPLOAD_FOLDER + '/' + secure_filename(f.filename))
        print result
        print result['StartTime']
        print result.getlist('MEOLUT')  #.encode('ascii','ignore') - need to do it to each element not list
        return render_template('BurstAnalysisReturn.html', \
            MEOLUT = result['MEOLUT'], \
            StartTime = result['StartTime'], \
            file_name = secure_filename(f.filename))


    else: 
        return '<h2> Invalid Request </h2>'
@app.route('/create')
def create():
    return ' create page'