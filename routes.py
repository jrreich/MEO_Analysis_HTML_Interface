from werkzeug.utils import secure_filename
from flask import Flask, url_for, request, render_template; 
#from app import app
import beacon_decode as bcn
from werkzeug.utils import secure_filename
import pypyodbc
import MEOInput_Analysis
import datetime
import csv
import sys
import os

UPLOAD_FOLDER = os.path.join('var','uploads')
approot = os.path.dirname(__file__)
OUTPUTFOLDER = os.path.join('static','output')
#OUTPUTFOLDER = r'C:/Users/reichj/Source/Repos/MEO_Analysis_HTML_Interface/static/output/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','db','zip'])

#servername = 'localhost' #for deploying on MCC
servername = r'.\SQLEXPRESS' #for deploying on REICHJ-PC
#oppsdatabase = 'mccoperationalRpt' #for deploying on MCC
oppsdatabase = 'mccoperational' # for deploying on REICHJ-PC

mcctestLGM = 'MccTestLGM' #should work for both MCC and REICHJ-PC

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#server/Main
@app.route('/')
def index():
    """Renders a sample page."""
    #createLink = "<a href = '" + url_for('beacon') + "'>Beacon Decoder</a>"; # url_for usings the function name to point to URL
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
            protocolcode = bcn1.protocol,
            bcn = bcn1)
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
        #print 'MEOLUTList - ' 
        #print MEOLUTList 
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
            filelist = MEOInput_Analysis.MSSQL_burst(result, MEOLUTList, StartTime, EndTime, OUTPUTFOLDER, approot, servername, mcctestLGM) #,sql_login = 'yes') # sql_login uses FreeTDS and sql login rather than windows auth - used for linux
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
                MEOInput_Analysis.xlx_analysis(UPLOAD_FOLDER, OUTPUTFOLDER, secure_filename(f.filename), MEOLUT, StartTime, EndTime, result) # need to add approot if this will be functional on apache
        elif result['inputsource'] == 'mccdb':
            csvoutfile, filelist = MEOInput_Analysis.MSSQL_analysis(result, MEOLUT, StartTime, EndTime, OUTPUTFOLDER, approot, servername, oppsdatabase) 
            if csvoutfile == None:
                return render_template('MEOInputAnalysisReturnNone.html', data = filelist)
            rdr= csv.reader( open(os.path.join(approot,csvoutfile), "r" ))
            csv_data = [ row for row in rdr ]
            return render_template('MEOInputAnalysisReturn.html', data=csv_data, linklist = filelist)

    else: 
        return '<h2> Invalid Request </h2>'

@app.route('/RealTimeMonitor')
def realtimemonitor():
    if request.method == 'GET':
        if request.args.get('days') <> None:
            days = request.args.get('days')
        else:
            days = 4
        if request.args.get('refreshtimer') <> None:
            refreshtimer = float(request.args.get('refreshtimer'))
        else:
            refreshtimer = 30
        if request.args.get('burstwindow') <> None:
            burstwindow = float(request.args.get('burstwindow'))
        else:
            burstwindow = 60
        #StartTime = datetime.datetime(2017,1,9,14,0)
        EndTime = datetime.datetime.utcnow() #.strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]
        #print EndTime
        #s = t.strftime('%Y-%m-%d %H:%M:%S.%f')
        #return s[:-3]
        #EndTime = datetime.datetime(2017,1,9,16,0)
        StartTime = EndTime - datetime.timedelta(days=float(days)) 
        BurstStartTime = EndTime - datetime.timedelta(minutes=burstwindow)
        alarmlist, closedalarms, numalarms = MEOInput_Analysis.MEOLUT_alarms(StartTime,EndTime, servername,oppsdatabase) #, sql_login = 'yes')
        statusHI, statusFL = MEOInput_Analysis.MEOLUT_status(StartTime,EndTime, servername,oppsdatabase)  #, sql_login = 'yes')
        packetpercent = MEOInput_Analysis.MEOLUT_percent(BurstStartTime, EndTime, servername,mcctestLGM)  #, sql_login = 'yes')
        open_site_list = MEOInput_Analysis.Open_Sites(servername,oppsdatabase)  # list of tuples
        return render_template('RealTimeMonitor.html', 
            alarmlist=alarmlist, 
            closedalarms = closedalarms, 
            open_site_list = open_site_list,
            numalarms = numalarms,
            statusHI = statusHI, 
            statusFL = statusFL,
            packetpercent = packetpercent,
            StartTime = StartTime,
            EndTime = EndTime,
            BurstStartTime = BurstStartTime,
            refreshtimer = refreshtimer,
            burstwindow = burstwindow,
            )

@app.route('/SiteQuery')
def opensites():
    if request.method == 'GET':
        if request.args.get('sitenum') <> None:
            KML = False
            if request.args.get('KML') <> None:
                KML = request.args.get('KML')            
            sitenum = request.args.get('sitenum')
            alertsitesum = MEOInput_Analysis.alertsitesum_query(sitenum,OUTPUTFOLDER,approot,servername,oppsdatabase)
            alertsitesols = MEOInput_Analysis.alertsitesol_query(sitenum,OUTPUTFOLDER,approot,servername,oppsdatabase)
            outsitesols, KMLfile = MEOInput_Analysis.outsol_query(sitenum,OUTPUTFOLDER,approot,servername,oppsdatabase, makeKML=KML)

            return render_template('SiteQuery.html',
                sitenum = sitenum,
                alertsitesum = alertsitesum,
                alertsitesols = alertsitesols, 
                outsitesols = outsitesols,
                KMLfile = KMLfile,
                )
        else:
            open_site_list = MEOInput_Analysis.Open_Sites(servername,oppsdatabase)  # list of tuples
            return render_template('OpenSites.html',
                open_site_list = open_site_list,
                num_sites = len(open_site_list),
                ) 