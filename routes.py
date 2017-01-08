from werkzeug.utils import secure_filename
from flask import Flask, url_for, request, render_template; 
from app import app
import beacon_decode as bcn
from werkzeug.utils import secure_filename
import pypyodbc
import MEOInput_Analysis
import datetime

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
        StartTime = datetime.datetime.strptime(result['StartTime'],'%Y-%m-%dT%H:%M')
        EndTime = datetime.datetime.strptime(result['EndTime'],'%Y-%m-%dT%H:%M')
        print StartTime
        if result['inputsource'] in ["excelfile", "zipfile", "sqldbfile"]:
            f = request.files['inputfile'] 
            filesaved = UPLOAD_FOLDER + '/' + secure_filename(f.filename)    
            f.save(filesaved)
            if result['inputsource'] == 'excelfile':
                MEOInput_Analysis.xlx_analysis(UPLOAD_FOLDER, secure_filename(f.filename), MEOLUT, StartTime, EndTime, result['beaconID'])
        else:
            conn = pypyodbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database=mccoperational;Trusted_Connection=yes;')
            cursor = conn.cursor()
            print result['MEOLUT'], result['StartTime'][:10], result['EndTime'][:10]
            cursor.execute("Select * from MEOInputSolution where SourceId = ? and TimeSolutionGenerated BETWEEN ? AND ?", [result['MEOLUT'],result['StartTime'][:10], result['EndTime'][:10]])
            for dataRow in cursor.fetchall():
                print(dataRow)
            #    crsr.execute(sql, dataRow)
            cursor.close()
            conn.close()
            
        print result
        print result['StartTime']
        print result.getlist('MEOLUT')  #.encode('ascii','ignore') - need to do it to each element not list
        return render_template('MEOInputAnalysisReturn.html', \
            result = result)
            #StartTime = result['StartTime'], \
            #file_name = secure_filename(f.filename))


    else: 
        return '<h2> Invalid Request </h2>'
@app.route('/create')
def create():
    return ' create page'