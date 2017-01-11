from werkzeug.utils import secure_filename
from flask import Flask, url_for, request, render_template; 
from app import app
import beacon_decode as bcn
from werkzeug.utils import secure_filename
import pypyodbc
import MEOInput_Analysis
import datetime
import csv

UPLOAD_FOLDER = 'var/uploads/'
OUTPUTFOLDER = 'static/output/'
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
        if 'MEOLUT' in result: 
            MEOLUTList = [int(x) for x in result.getlist('MEOLUT')]
            
            #MEOLUT_list = [x.strip() for x in MEOLUT_in.split(',')] 
        else:
            MEOLUTList = ['%']
        print 'MEOLUTList - ' 
        print MEOLUTList 
        if result['StartTime']:
            StartTime = datetime.datetime.strptime(result['StartTime'],'%Y-%m-%dT%H:%M')
        else:
            StartTime = datetime.datetime(2015,1,1,0,0,0)
        if result['EndTime']:
            EndTime = datetime.datetime.strptime(result['EndTime'],'%Y-%m-%dT%H:%M')
        else:
            EndTime = datetime.datetime.utcnow()
        if result['inputsource'] in ["excelfile", "zipfile", "sqldbfile"]:
            f = request.files['inputfile'] 
            filesaved = UPLOAD_FOLDER + secure_filename(f.filename)    
            f.save(filesaved)
            #if result['inputsource'] == 'excelfile':
                #MEOInput_Analysis.xlx_analysis(UPLOAD_FOLDER, secure_filename(f.filename), MEOLUT, StartTime, EndTime, result)
        elif result['inputsource'] == 'mccdb':
            filelist = MEOInput_Analysis.MSSQL_burst(result, MEOLUTList, StartTime, EndTime, OUTPUTFOLDER, databasename='MccTestLGM')
            return render_template('BurstAnalysisReturn.html', filelist=filelist )



    else: 
        return '<h2> Invalid Request </h2>'
@app.route('/MEOInputAnalysis', methods=['GET','POST'])
def MEOInputAnalysis():
    if request.method == 'GET':
        # Send the user the form
        return render_template('MEOInputAnalysisForm.html')
    elif request.method == 'POST':
        # read input
        result = request.form
        #print result['StartTime']
        MEOLUT = int(result['MEOLUT'])
        if result['StartTime']:
            StartTime = datetime.datetime.strptime(result['StartTime'],'%Y-%m-%dT%H:%M')
        else:
            StartTime = datetime.datetime(2015,1,1,0,0,0)
        if result['EndTime']:
            EndTime = datetime.datetime.strptime(result['EndTime'],'%Y-%m-%dT%H:%M')
        else:
            EndTime = datetime.datetime.utcnow()
        if result['inputsource'] in ["excelfile", "zipfile", "sqldbfile"]:
            f = request.files['inputfile'] 
            filesaved = UPLOAD_FOLDER + '/' + secure_filename(f.filename)    
            f.save(filesaved)
            print result['KMLgen']
            if result['EncLocGen']: print 'true'
            if result['inputsource'] == 'excelfile':
                MEOInput_Analysis.xlx_analysis(UPLOAD_FOLDER, OUTPUTFOLDER, secure_filename(f.filename), MEOLUT, StartTime, EndTime, result)
        elif result['inputsource'] == 'mccdb':
            csvfile = MEOInput_Analysis.MSSQL_analysis(result, MEOLUT, StartTime, EndTime, UPLOAD_FOLDER)
            rdr= csv.reader( open(csvfile, "r" ) )
            csv_data = [ row for row in rdr ]
            return render_template('MEOInputAnalysisReturn.html', data=csv_data )
            
            
        #print result
        #print result['StartTime']
        #print result.getlist('MEOLUT')  #.encode('ascii','ignore') - need to do it to each element not list
        #return render_template('MEOInputAnalysisReturn.html', \
        #    result = result)
            #StartTime = result['StartTime'], \
            #file_name = secure_filename(f.filename))


    else: 
        return '<h2> Invalid Request </h2>'
@app.route('/create')
def create():
    return ' create page'