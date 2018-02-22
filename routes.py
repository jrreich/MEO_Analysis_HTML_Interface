from werkzeug.utils import secure_filename
from flask import Flask, url_for, request, render_template, jsonify; 
#from app import app
import beacon_decode as bcn
from werkzeug.utils import secure_filename
import pypyodbc
import MEOInput_Analysis
import datetime
import csv
import sys
import os
#import sendsms as sms

UPLOAD_FOLDER = os.path.join('var','uploads')

approot = os.path.dirname(__file__)

OUTPUTFOLDER = os.path.join('static','output')
#OUTPUTFOLDER = r'C:/Users/reichj/Source/Repos/MEO_Analysis_HTML_Interface/static/output/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','db','zip'])

Deploy_on = 'other1' # for deploying on RYZEN7 2018-02-21
#Deploy_on = 'MCC'	
#Deploy_on = 'other2'

if Deploy_on == 'MCC':
    servername = 'localhost' #for deploying on MCC
    #oppsdatabase = 'mccoperationalRpt' #for deploying on operational MCC
    oppsdatabase = 'MccMeoLutMonitor' #for deploying on MCC - new db
    mcctestLGM = 'MccMeoLutMonitor' #for deploying on MCC - new db	
elif Deploy_on == 'other1':
    servername = r'.\SQLEXPRESS' #for deploying on REICHJ-PC - 2018 and on
    oppsdatabase = 'MccMeoLutMonitor' # for deploying on REICHJ-PC
    mcctestLGM = 'MccMeoLutMonitor' #should work for both MCC and REICHJ-PC
else: 
    servername = r'.\SQLEXPRESS' #for deploying on REICHJ-PC
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
            filesaved = os.path.join(approot, UPLOAD_FOLDER,secure_filename(f.filename))
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
        if result.get('RealPastTime',False) == 'RT_yes':
            EndTime = datetime.datetime.utcnow()
            StartTime = EndTime - datetime.timedelta(hours = float(result['realtimehours']))
        elif result.get('StartTime',False) <> '':
            StartTime = datetime.datetime.strptime(result['StartTime'],'%Y-%m-%dT%H:%M')
            EndTime = datetime.datetime.strptime(result['EndTime'],'%Y-%m-%dT%H:%M')
        else:
            EndTime = datetime.datetime.utcnow()
            StartTime = EndTime - datetime.timedelta(days = 7)
        if result['inputsource'] in ["excelfile", "zipfile", "sqldbfile"]:
            f = request.files['inputfile'] 
            filesaved = os.path.join(approot, UPLOAD_FOLDER,secure_filename(f.filename))
            f.save(filesaved)
            if result['inputsource'] == 'excelfile':
                MEOInput_Analysis.xlx_analysis(filesaved, OUTPUTFOLDER, MEOLUT, StartTime, EndTime, result) # need to add approot if this will be functional on apache
        elif result['inputsource'] == 'mccdb':
            csvoutfile, filelist = MEOInput_Analysis.MSSQL_analysis(result, StartTime, EndTime, OUTPUTFOLDER, approot, servername, oppsdatabase) 
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
        if request.args.get('sitenum') is not None:
            RCC_KML = False
            Input_KML = False
            KMLfile = False
            Mapfile = False
            sitenum = request.args.get('sitenum')
            if request.args.get('RCC_KML') is not None:
                RCC_KML = request.args.get('RCC_KML')        
            if request.args.get('Input_KML') is not None:
                Input_KML = request.args.get('Input_KML')  
            if request.args.get('Both_KML') is not None:
                KMLfile, Mapfile = MEOInput_Analysis.both_kml(sitenum,OUTPUTFOLDER,approot,servername,oppsdatabase)
            
            alertsitesum = MEOInput_Analysis.alertsitesum_query(sitenum,OUTPUTFOLDER,approot,servername,oppsdatabase)
            alertsitesols, Input_KMLfile = MEOInput_Analysis.alertsitesol_query(sitenum,OUTPUTFOLDER,approot,servername,oppsdatabase, makeKML = Input_KML)
            outsitesols, RCC_KMLfile = MEOInput_Analysis.outsol_query(sitenum,OUTPUTFOLDER,approot,servername,oppsdatabase, makeKML=RCC_KML)
            


            return render_template('SiteQuery.html',
                sitenum = sitenum,
                alertsitesum = alertsitesum,
                alertsitesols = alertsitesols, 
                outsitesols = outsitesols,
                RCC_KMLfile = RCC_KMLfile,
                Input_KMLfile = Input_KMLfile,
                KMLfile = KMLfile,
                Mapfile = Mapfile
                )
        else:
            open_site_list = MEOInput_Analysis.Open_Sites(servername,oppsdatabase)  # list of tuples
            return render_template('OpenSites.html',
                open_site_list = open_site_list,
                num_sites = len(open_site_list),
                ) 

@app.route('/MEOBeaconAnalysis', methods=['GET','POST'])
def MEOBeaconAnalysis():
    if request.method == 'GET':
        return render_template('MEOBeaconAnalysisForm.html')
    elif request.method == 'POST':
        # read input
        result = request.form
        print result
        if result.get('RealPastTime',False) == 'RT_yes':
            print 'should be here'
            EndTime = datetime.datetime.utcnow()
            StartTime = EndTime - datetime.timedelta(hours = float(168))
            print 'check again'
        else:
            StartTime = datetime.datetime.strptime(result['StartTime'],'%Y-%m-%dT%H:%M')
            EndTime = datetime.datetime.strptime(result['EndTime'],'%Y-%m-%dT%H:%M')	
        filesaved = False
        print 'still here?'
        if result['GTSource'] == 'GTFile':
            print 'using file'
            f = request.files['gt_inputfile'] 
            filesaved = os.path.join(approot, UPLOAD_FOLDER,secure_filename(f.filename))
            f.save(filesaved)
        print filesaved
        csvoutfile, imglist, filelist = MEOInput_Analysis.MSSQL_beacon_analysis(result, StartTime, EndTime, OUTPUTFOLDER, approot, servername, oppsdatabase, filesaved) 
        if csvoutfile == None:
            print 'csvoutfile was None'
            return render_template('MEOBeaconAnalysisReturnNoData.html', result = result, StartTime = StartTime, EndTime = EndTime)
        rdr= csv.reader( open(os.path.join(approot,csvoutfile), "r" ))
        csv_data = [ row for row in rdr ]
        return render_template('MEOBeaconAnalysisReturn.html', data=csv_data, imglist = imglist, linklist = filelist)

    else: 
        return '<h2> Invalid Request </h2>'
@app.route('/MapTest', methods=['GET','POST'])
def MapTest():
    if request.method == 'GET':
        if request.args.get('KML') is not None:
            return render_template('MapTest_v3.html', KMLFILE = request.args.get('KML'))
        else: 
            return render_template('MapTest_v3.html')


@app.route('/api/sitesum/<int:sitenum>', methods=['GET','POST'])
def sitereturn(sitenum):
    print sitenum
    if request.method == 'GET':
        SiteData = MEOInput_Analysis.api_site_sum_query(sitenum,servername, oppsdatabase)
        try: 
            data = SiteData
            print 'got data'
            print data
        except IndexError:
            abort(404)
        print jsonify(data)
        return jsonify(data)

@app.route("/stream")
def stream():
    AllSiteData = MEOInput_Analysis.czml_all_sites_sum_query(servername, oppsdatabase)
    return jsonify(AllSiteData)
    def eventStream():
        while True:
            # Poll data from the database
            # and see if there's a new message
            if len(messages) > len(previous_messages):
                yield "data: {}\n\n".format(messages[len(messages)-1])
    
    return Response(eventStream(), mimetype="text/event-stream")

@app.route("/api/czml/meo/per/<int:sourceid>")
def czml_meolut_ant_per(sourceid):
    currentDateTime = datetime.datetime.utcnow()
    bcnid = 'ADDC00202020201'
    MeoPercent = MEOInput_Analysis.czml_meolut_ant_per(currentDateTime, bcnid, sourceid, servername, mcctestLGM)
    return MeoPercent 

@app.route("/api/czml/site/<int:sitenum>")
def czml_meo_input_by_site(sitenum):
    MeoInput = MEOInput_Analysis.czml_site_meo_input(sitenum, servername, oppsdatabase)
    return jsonify(MeoInput)

@app.route("/api/czml/orbit/meo")
def czml_meo_sat_orbit():
    #starttime = datetime.datetime(2017,8,21)
    #endtime = datetime.datetime(2017,8, 22)
    endtime = datetime.datetime.utcnow() + datetime.timedelta(days = 1)
    starttime = endtime - datetime.timedelta(days = 2)
    OrbitData = MEOInput_Analysis.czml_meo_orbit_all(starttime, endtime, servername, oppsdatabase ) #, satnum)
    return jsonify(OrbitData)

@app.route("/api/czml/orbit/leo")
def czml_leo_sat_orbit():
    #starttime = datetime.datetime(2017,8,19)
    #endtime = datetime.datetime(2017,8, 22)
    endtime = datetime.datetime.utcnow() + datetime.timedelta(days = 1)
    starttime = endtime - datetime.timedelta(days = 1)
    OrbitData = MEOInput_Analysis.czml_leo_orbit_all(starttime, endtime, servername, oppsdatabase ) #, satnum)
    return jsonify(OrbitData)

@app.route("/api/czml/sched/meo")
def czml_meo_schedule_all():
    starttime = datetime.datetime(2017,8,19)
    endtime = datetime.datetime(2017,8, 22)
    #endtime = datetime.datetime.utcnow() + datetime.timedelta(days = 1)
    #starttime = endtime - datetime.timedelta(days = 1)
    MeoSchedData = MEOInput_Analysis.czml_meo_sched_all(starttime, endtime, servername, oppsdatabase ) #, antenna)
    return jsonify(MeoSchedData)

@app.route('/messager', methods=['GET','POST'])
def messager():
    if request.method == 'GET':
        # Send the user the form
        return render_template('messager.html')
    elif request.method == 'POST':
        # read beacon ID and save it
        phonenumber = request.form['phonenumber']        
        messagetext = request.form['messagetext']
        #decode and return it
        #return results
        sms.send_sms(phonenumber, messagetext)
        return render_template('messagesent.html', \
            phonenumber = phonenumber, \
            messagetext = messagetext)
    else: 
        return '<h2> Invalid Request </h2>'