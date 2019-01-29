from werkzeug.utils import secure_filename
from werkzeug.routing import BaseConverter, ValidationError
from flask import Flask, url_for, request, render_template, jsonify
#from app import app
import beacon_decode as bcn
import pypyodbc
import MEOInput_Analysis
import datetime
import csv
import sys
import os
import json
import requests 
from requests import get
#import sendsms as sms

#os.environ['NO_PROXY'] = 'localhost'

UPLOAD_FOLDER = os.path.join('var','uploads')
computer_name = os.environ['COMPUTERNAME']
approot = os.path.dirname(__file__)



OUTPUTFOLDER = os.path.join('static','output')
#OUTPUTFOLDER = r'C:/Users/reichj/Source/Repos/MEO_Analysis_HTML_Interface/static/output/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','db','zip'])

if computer_name == 'RYZEN7':
    Deploy_on = 'other1' # for deploying on RYZEN7 2018-02-21
else: Deploy_on = 'MCC'	
#Deploy_on = 'other2'

TimeLog = True

if Deploy_on == 'MCC':
    servername = 'localhost' #for deploying on MCC
    #oppsdatabase = 'mccoperationalRpt' #for deploying on operational MCC
    oppsdatabase = 'MccMeoLutMonitor' #for deploying on MCC - new db
    mcctestLGM = 'MccMeoLutMonitor' #for deploying on MCC - new db
    #urlbase = 'https://sar-reportsrv'
elif Deploy_on == 'other1':
    servername = r'.\SQLEXPRESS' #for deploying on REICHJ-PC - 2018 and on
    oppsdatabase = 'MccMeoLutMonitor' # for deploying on REICHJ-PC
    mcctestLGM = 'MccMeoLutMonitor' #should work for both MCC and REICHJ-PC
    #urlbase = "http://jrreich.myftp.org/"
else: 
    servername = r'.\SQLEXPRESS' #for deploying on REICHJ-PC
    oppsdatabase = 'mccoperational' # for deploying on REICHJ-PC
    mcctestLGM = 'MccTestLGM' #should work for both MCC and REICHJ-PC

config_dict = {"UPLOAD_FOLDER": UPLOAD_FOLDER, 
          "approot": approot,
          "OUTPUTFOLDER": OUTPUTFOLDER,
          "servername": servername,
          "oppsdatabase": oppsdatabase,
          "mcctestLGM": mcctestLGM}
												
app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class DateConverter(BaseConverter):
    """Extracts a ISO8601 date from the path and validates it."""
    regex = r'\d{4}-\d{2}-\d{2}'
    def to_python(self, value):
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValidationError()
    def to_url(self, value):
        return value.strftime('%Y-%m-%d')
app.url_map.converters['date'] = DateConverter

#Function and route to get list of all routes:
def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/site-map")
def getRoutes():
    routes = {}
    for r in app.url_map._rules:
        routes[r.rule] = {}
        routes[r.rule]["functionName"] = r.endpoint
        routes[r.rule]["methods"] = list(r.methods)

    routes.pop("/static/<path:filename>")

    return jsonify(routes)



#server/Main
@app.route('/', methods =['GET'])
def index():
    """Renders home page."""
    #createLink = "<a href = '" + url_for('beacon') + "'>Beacon Decoder</a>"; # url_for usings the function name to point to URL
    return render_template('index.html')

@app.route("/vue")
def vue_test_page():
    return render_template('vue_test_page.html')

@app.route("/api")
def api():
    urlbase = url_for('index', _external = True)
    url = urlbase + "site-map"
    data = requests.get(url,verify=False).json()
    return render_template('api.html', api_dict = data)

@app.route("/UTCtime")
def UTCtime():
    return jsonify(CurrentTime = datetime.datetime.utcnow())

@app.route("/layout")
def layout():
    return render_template("layout.html")

@app.route('/beacon', methods=['GET','POST'])
def beacon():
    if request.method == 'GET':
        # Send the user the form
        return render_template('BeaconDecode1.html')
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
        return render_template('BurstAnalysisForm1.html')
    elif request.method == 'POST':
        # read input
        result = request.form
        if 'MEOLUT' in result: 
            MEOLUTList = [int(x) for x in result.getlist('MEOLUT')]
            #MEOLUT_list = [x.strip() for x in MEOLUT_in.split(',')] 
        else:
            MEOLUTList = ['%']
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
            return render_template('BurstAnalysisReturn1.html', filelist=filelist, MEOLUTList=MEOLUTList, StartTime=StartTime, EndTime=EndTime )
    else: 
        return '<h2> Invalid Request </h2>'
@app.route('/MEOInputAnalysis', methods=['GET','POST'])
def MEOInputAnalysis():
    if request.method == 'GET':
        result = request.args
        print 'in get of MEOInputAnalysis'
        
        if len(result)==0: return render_template('MEOInputAnalysisForm1.html')
    elif request.method == 'POST':
        # read input
        result = request.form
        print 'in post of MEOInputAnalysis'
    else: 
        return '<h2> Invalid Request </h2>'
    print 'length of result = '     
    print len(result)
    print result
    if 'MEOLUT' in result: 
        MEOLUTList = [int(x) for x in result.getlist('MEOLUT')]
    else:
        MEOLUTList = [None]
    print MEOLUTList
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
        csvoutfile, filelist = MEOInput_Analysis.MSSQL_analysis(result, MEOLUTList, StartTime, EndTime, config_dict) 
        if csvoutfile == None:
            return render_template('MEOInputAnalysisReturnNone.html', data = filelist)
        rdr= csv.reader( open(os.path.join(approot,csvoutfile), "r" ))
        csv_data = [ row for row in rdr ]
        return render_template('MEOInputAnalysisForm1.html', data=csv_data, linklist = filelist)

@app.route('/MEOBeaconAnalysis', methods=['GET','POST'])
def MEOBeaconAnalysis():
    if request.method == 'GET':
        result = request.args
        if len(result)==0: return render_template('MEOBeaconAnalysisForm1.html')
    elif request.method == 'POST':
        # read input
        print "in get of MEOBeaconAnalysis" 
        result = request.form
    else: 
        return '<h2> Invalid Request </h2>'
        
        
    print result
    print 'length of result = ' 
    print len(result) 
    ### get inputs for MSSQL_beacon_analysis
    if 'MEOLUT' in result: 
        MEOLUTList = [int(x) for x in result.getlist('MEOLUT')]
    else:
        MEOLUTList = [None]
    print MEOLUTList
    if result.get('RealPastTime',False) == 'RT_yes':
        EndTime = datetime.datetime.utcnow()
        StartTime = EndTime - datetime.timedelta(hours = float(168))
    else:
        StartTime = datetime.datetime.strptime(result['StartTime'],'%Y-%m-%dT%H:%M')
        if result.get('EndTime',False):
            EndTime = datetime.datetime.strptime(result['EndTime'],'%Y-%m-%dT%H:%M')
        else: 
            EndTime = datetime.datetime.utcnow()
    filesaved = False
    filesaved_zip = False
    if result.get('zipFile',False):
        f = request.files['zip_inputfile'] 
        filesaved_zip = os.path.join(approot, UPLOAD_FOLDER, secure_filename(f.filename))
        f.save(filesaved_zip)
    if result['GTSource'] == 'GTFile':
        f = request.files['gt_inputfile'] 
        filesaved = os.path.join(approot, UPLOAD_FOLDER,secure_filename(f.filename))
        f.save(filesaved)
    
    #Calling appropriate functions
    if TimeLog: print 'start of MEOInput_Analysis calls - ' + str(datetime.datetime.utcnow()) 
    filelist1_dict = MEOInput_Analysis.MeoDataCollection(result, MEOLUTList, StartTime, EndTime, config_dict, filesaved_zip) 
    if TimeLog: print 'after of MEOInput_Analysis.MeoDataCollection - ' + str(datetime.datetime.utcnow()) 
    csvoutfile, imglist, filelist_dict = MEOInput_Analysis.MSSQL_beacon_analysis(result, MEOLUTList, StartTime, EndTime, config_dict, filesaved) 
    if TimeLog: print 'after of MEOBeaconInput_Analysis.MSSQL_beacon_analysis - ' + str(datetime.datetime.utcnow()) 
    
    #Rendering Templates
    if csvoutfile == None:
        print 'csvoutfile was None'
        return render_template('MEOBeaconAnalysisReturnNoData1.html', result = result, StartTime = StartTime, EndTime = EndTime)
    if filelist_dict is not None:
        filelist_dict.update(filelist1_dict)
    rdr= csv.reader( open(os.path.join(approot,csvoutfile), "r" ))
    csv_data = [ row for row in rdr ]
    return render_template('MEOBeaconAnalysisReturn1.html', data=csv_data, imglist = imglist, linklist = filelist_dict)


@app.route('/RealTimeMonitor')
def realtimemonitor():
    startofscript = datetime.datetime.utcnow()
    if request.method == 'GET':
        if request.args.get('days') <> None:
            days = request.args.get('days')
        else:
            days = 4
        if request.args.get('refreshtimer', None):
            print request.args.get('refreshtimer')
            print type(request.args.get('refreshtimer'))
            refreshtimer = float(request.args.get('refreshtimer'))
        else:
            refreshtimer = 300
        if request.args.get('burstwindow') <> None:
            burstwindow = float(request.args.get('burstwindow'))
        else:
            burstwindow = 60
        EndTime = datetime.datetime.utcnow()
        EndTime_str = EndTime.strftime('%Y-%m-%d %H:%M:%S')
        StartTime = EndTime - datetime.timedelta(days=float(days)) 
        StartTime_str = StartTime.strftime('%Y-%m-%d %H:%M:%S')
        BurstStartTime = EndTime - datetime.timedelta(minutes=burstwindow)
        BurstStartTime_str = BurstStartTime.strftime('%Y-%m-%d %H:%M:%S')
        alarmlist, closedalarms, numalarms = MEOInput_Analysis.MEOLUT_alarms(StartTime,EndTime, servername,oppsdatabase) #, sql_login = 'yes')
        if TimeLog:
            print '1 - MEO Alarms'
            print datetime.datetime.utcnow() - startofscript 
        statusHI, statusFL = MEOInput_Analysis.MEOLUT_status(StartTime,EndTime, servername,oppsdatabase)  #, sql_login = 'yes')
        if TimeLog:
            print '2 - MEO Status'
            print datetime.datetime.utcnow() - startofscript 
        HI_location_accuracy = MEOInput_Analysis.api_meo_location_accuracy(3385, BurstStartTime, EndTime, config_dict)[3385]
        #HI_location_accuracy = json.loads(get(url_for('meolut_location_accuracy', MEOLUT_ID = 3385, _external = True, 
        #                                              StartTime = BurstStartTime_str, EndTime = EndTime_str),verify = False).content)
        if TimeLog:
            print '3 - HI loc accuracy'
            print datetime.datetime.utcnow() - startofscript         
        HI_packet_percent = MEOInput_Analysis.api_meo_packet_throughput(3385, BurstStartTime, EndTime, config_dict, 
                                                          beaconId = 'AA5FC0000000001', rep_rate = 50, minutes = burstwindow)
        #HI_packet_percent = json.loads(get(url_for('meolut_packet_throughput', MEOLUT_ID = 3385, rep_rate = 50, 
        #                                           StartTime = BurstStartTime_str, EndTime = EndTime_str, beaconId = 'AA5FC0000000001', 
        #                                           _external = True),verify = False).content)
        if TimeLog:
            print '4 - HI packet percent'
            print datetime.datetime.utcnow() - startofscript      
        FL_location_accuracy = MEOInput_Analysis.api_meo_location_accuracy(3669, BurstStartTime, EndTime, config_dict)[3669]
        #FL_location_accuracy = json.loads(get(url_for('meolut_location_accuracy', MEOLUT_ID = 3669, _external = True,
        #                                              StartTime = BurstStartTime_str, EndTime = EndTime_str), verify = False).content)
        if TimeLog:
            print '5 - FL loc accuracy '
            print datetime.datetime.utcnow() - startofscript
        FL_packet_percent = MEOInput_Analysis.api_meo_packet_throughput(3669, BurstStartTime, EndTime, config_dict, 
                                                          beaconId = 'ADDC00202020201', rep_rate = 50, minutes = burstwindow)
        #FL_url = url_for('meolut_packet_throughput', MEOLUT_ID = 3669, rep_rate = 50, 
        #                                           beaconId = 'ADDC00202020201', _external = True, 
        #                                           StartTime = BurstStartTime_str, EndTime = EndTime_str)
        #FL_packet_percent = json.loads(get(FL_url, verify = False).content)
        if TimeLog:
            print '6 - FL packet percent'
            print datetime.datetime.utcnow() - startofscript  
        open_site_list = MEOInput_Analysis.Open_Sites(servername,oppsdatabase)
        # list of tuples
        return render_template('RealTimeMonitor1.html', 
            alarmlist=alarmlist, 
            closedalarms = closedalarms, 
            open_site_list = open_site_list,
            numalarms = numalarms,
            statusHI = statusHI, 
            statusFL = statusFL,
            HI_packet_percent = HI_packet_percent,
            HI_location_accuracy = HI_location_accuracy,
            FL_packet_percent = FL_packet_percent,
            FL_location_accuracy = FL_location_accuracy,
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
            


            return render_template('SiteQuery1.html',
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
            return render_template('OpenSites1.html',
                open_site_list = open_site_list,
                num_sites = len(open_site_list),
                ) 


@app.route('/Map', methods=['GET','POST'])
def SarsatMap():
    if request.method == 'GET':
        if request.args.get('KML', None):
            return render_template('Cesium_Map.html', KMLFILE = request.args.get('KML'))
        else: 
            return render_template('Cesium_Map.html')

@app.route('/MEOData', methods=['GET','POST'])
def meodata():
    if request.method == 'GET':
        # Send the user the form
        return render_template('MeoDataCollection.html')
    elif request.method == 'POST':
        result = request.form
        if result.get('beaconID', False):
            beaconId = result['beaconID']
        else:
            beaconId = '%'
        if result.get('EndTime', False):
            EndTime = datetime.datetime.strptime(result['EndTime'],'%Y-%m-%dT%H:%M')
        else:
            EndTime = datetime.datetime.utcnow()
        if result.get('StartTime', False):
            StartTime = datetime.datetime.strptime(result['StartTime'],'%Y-%m-%dT%H:%M')
        else:
            StartTime = EndTime - datetime.timedelta(hours = float(168))
        if 'MEOLUT' in result: 
            MEOLUTList = [int(x) for x in result.getlist('MEOLUT')]
        else:
            MEOLUTList = [None]
        filesaved = False
        if result.get('zipFile',False):
            f = request.files['zip_inputfile'] 
            filesaved = os.path.join(approot, UPLOAD_FOLDER, secure_filename(f.filename))
            f.save(filesaved)
        filelist = MEOInput_Analysis.MeoDataCollection(beaconId, MEOLUTList, StartTime, EndTime, config_dict, filesaved) 
        return render_template('MeoDataCollection.html', linklist = filelist)
    else: 
        return '<h2> Invalid Request </h2>'

@app.route('/api/sitesum/<int:sitenum>', methods=['GET','POST'])
def sitereturn(sitenum):
    if request.method == 'GET':
        SiteData = MEOInput_Analysis.api_site_sum_query(sitenum, config_dict)
        try: 
            data = SiteData
        except IndexError:
            abort(404)
        return jsonify(data)

@app.route('/api/MEO/location_accuracy/<int:MEOLUT_ID>', methods=['GET'])
def meolut_location_accuracy(MEOLUT_ID):
    '''
    Get Location stats per MEOLUT. Optional args StartTime, EndTime, hours, days, minutes
    If no args are supplied, uses current time as StartTime and 60 minutes 
    Example of using args: 
    /api/MEO/location_accuracy/3385?StartTime=2019-01-21 01:00:00&EndTime=2019-01-21 02:00:00
    '''
    kwargs = {}
    if 'EndTime' in request.args:
        EndTime = datetime.datetime.strptime(request.args.get('EndTime'), '%Y-%m-%d %H:%M:%S')
    else: EndTime = datetime.datetime.utcnow()
    if 'hours' in request.args: hours = float(request.args.get('hours'))
    else: hours = 0
    minutes = hours*60
    if 'days' in request.args: days = float(request.args.get('days'))
    else: days = 0
    minutes += days*24*60
    if 'minutes' in request.args: 
        minutes_to_add = float(request.args.get('minutes'))
        minutes += minutes_to_add
    if minutes == 0: minutes = 60
    if 'StartTime' in request.args:
        StartTime = datetime.datetime.strptime(request.args.get('StartTime'), '%Y-%m-%d %H:%M:%S')
    if request.args.get('StartTime') is None: StartTime = EndTime - datetime.timedelta(minutes = minutes)
    beaconId = request.args.get('beaconId',None)
    #StartTime = datetime.datetime(2019,01,21,01,00)
    #EndTime = datetime.datetime(2019,01,21,02,00)
    output = MEOInput_Analysis.api_meo_location_accuracy(MEOLUT_ID, StartTime, EndTime, config_dict, beaconId = beaconId)
    output[MEOLUT_ID]['StartTime'] = StartTime
    output[MEOLUT_ID]['EndTime'] = EndTime
    return jsonify(output)

@app.route('/api/MEO/packet_throughput/<int:MEOLUT_ID>', methods=['GET'])
def meolut_packet_throughput(MEOLUT_ID):
    '''
    Get antenna burst stats per MEOLUT. Optional args StartTime, EndTime, hours, days, minutes, beaconId, rep_rate
    If no args are supplied, uses current time as StartTime and 60 minutes
    Must pass rep_rate to get burst percentage, and won't make sense (too high) unless beaconId passed as well
    Example of using args: 
    /api/MEO/location_accuracy/3385?StartTime=2019-01-21 01:00:00&EndTime=2019-01-21 02:00:00
    '''
    kwargs = {}
    if 'EndTime' in request.args:
        EndTime = datetime.datetime.strptime(request.args.get('EndTime'), '%Y-%m-%d %H:%M:%S')
    else: EndTime = datetime.datetime.utcnow()
    if 'hours' in request.args: hours = float(request.args.get('hours'))
    else: hours = 0
    minutes = hours*60
    if 'days' in request.args: days = float(request.args.get('days'))
    else: days = 0
    minutes += days*24*60
    if 'minutes' in request.args: 
        minutes_to_add = float(request.args.get('minutes'))
        minutes += minutes_to_add
    if minutes == 0: minutes = 60
    if 'StartTime' in request.args: 
        StartTime = datetime.datetime.strptime(request.args.get('StartTime'), '%Y-%m-%d %H:%M:%S')
    else: 
        StartTime = EndTime - datetime.timedelta(minutes = minutes)
    rep_rate = request.args.get('rep_rate',None)
    beaconId = request.args.get('beaconId',None)
    packets = MEOInput_Analysis.api_meo_packet_throughput(MEOLUT_ID, StartTime, EndTime, config_dict, 
                                                          rep_rate = rep_rate, minutes = minutes, beaconId = beaconId)
    packets['StartTime'] = StartTime
    packets['EndTime'] = EndTime
    return jsonify(packets)


@app.route('/api/site/<table>/<int:sitenum>', methods = ['GET','POST'])
def api_site(table, sitenum):
    # can return any table where a sitenum is defined -- ie alertsitesol, (default if not defined), alertsitesum , outsolution 
    input_data = request.args.to_dict()
    if table not in ['alertsitesol', 'alertsitesum' , 'outsolution', 'leo','meo','enc']:
        raise TypeError("table must be type 'alertsitesol', 'alertsitesum', 'outsolution', 'leo','meo' or 'enc' not {}".format(table))
        return render_templat('error.html',404) 
    outdata = MEOInput_Analysis.api_site(config_dict, sitenum, table)
    #print outdata[0]
    return jsonify(outdata)

@app.route('/api/leogeo/sols', methods = ['GET','POST'])
def api_leo_geo_sols():
    # can return leo or geo solutions from lut406solution - available params are bcnid15, starttime, endtime, lut, sat
    data = request.args.to_dict()
    outdata = MEOInput_Analysis.api_leo_geo_sols(data, config_dict)
    return outdata

@app.route('/api/JSON/leogeo/sols', methods = ['GET','POST'])
def api_JSON_leo_geo_sols():
    # can return leo or geo solutions from lut406solution - available params are bcnid15, starttime, endtime, lut, sat
    data = request.args.to_dict()
    outdata = MEOInput_Analysis.api_JSON_leo_geo_sols(data, config_dict)
    return outdata

@app.route('/api/<type>/<int:sitenum>', methods = ['GET','POST'])
def api_comp_sols(type, sitenum):
    # returns all type (leo, meo, comp, enc) of locations for a site
    urlbase = url_for('index', _external = True)
    url = urlbase + "api/site/alertsitesol/{}".format(sitenum)
    composite_columns = ['alertsitenum','gentime', 'addtime','complat','complon','altitude','matchdistance', 
                         'enclat','enclon', 'encmatchdistance', 'inputdatatype',  'alertmsgstate', 'bcnid15', 'bcnid30', 
                        'sourceid', 'sourcename', 'sat','satelliteids','numbursts','numpackets','numsatellites','dop',
                        'sourceantennaids', 'indlocweight', 'indencdistance','rcvtime']
    leo_columns = ['alertsitenum','gentime', 'addtime','a_lat','a_lon','tca','complat','complon','altitude','matchdistance', 
                         'enclat','enclon', 'encmatchdistance', 'inputdatatype',  'alertmsgstate', 'bcnid15', 'bcnid30', 
                        'sourceid', 'sourcename', 'sat', 'orbit', 'points', 'a_prob', 'indlocweight', 'indencdistance', 'rcvtime']
    data = requests.get(url,verify=False).json()
    out_dict = {}
    for row in data:
        if type == 'comp' or type == 'all':
            if row['complat'] != "null":
                out_dict[row['alertsitesolid']] = {x:row[x] for x in composite_columns}
        if type == 'leo' or type == 'all':
            if row['a_lat'] != "null":
                out_dict[row['alertsitesolid']] = {x:row[x] for x in leo_columns}
    return jsonify(out_dict)
    #return leo_columns

@app.route('/api/output/sols/<int:sitenum>', methods = ['GET'])
def api_output_sols(sitenum):
    data = request.args.to_dict()
    columns, outdata = MEOInput_Analysis.api_output_sols(data, config_dict, sitenum)
    columns = [columns]
    for i in outdata:
        columns.append(i)
    return jsonify(columns)

@app.route('/api/JSON/output/sols/<int:sitenum>', methods = ['GET'])
def api_JSON_output_sols(sitenum):
    data = request.args.to_dict()
    outdata = MEOInput_Analysis.api_JSON_output_sols(data, config_dict, sitenum)
    return outdata


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

#Generate and return CZML file of MEOLUT input solutions by sitenum)
@app.route("/api/czml/meo/site/<int:sitenum>")
def czml_meo_input_by_site(sitenum):
    MeoInput = MEOInput_Analysis.czml_site_meo_input(sitenum, servername, oppsdatabase)
    return jsonify(MeoInput)

#Generate and return CZML file of Composite/MEO/LEO locations by sitenum

@app.route("/api/czml/site/<type>/<int:sitenum>")
def czml_alert_site(type, sitenum):
    urlbase = url_for('index', _external = True)
    url = urlbase + "api/"+type+"/{}".format(sitenum)
    print '/api/czml/site/<type>/<int:sitenum'
    print 'pointing to > '
    print url
    data = requests.get(url,verify=False).json()
    outczml = MEOInput_Analysis.czml_alert_site(type, sitenum, data) 
    return jsonify(outczml)


@app.route("/api/czml/meo/orbit/<date:input_date>")
def czml_meo_sat_orbit_date(input_date):
    endtime = input_date + datetime.timedelta(days = 1)
    starttime = input_date - datetime.timedelta(days = 1)
    OrbitData = MEOInput_Analysis.czml_meo_orbit_all(starttime, endtime, config_dict) #, satnum)
    return jsonify(OrbitData)

@app.route("/api/czml/meo/orbit")
def czml_meo_sat_orbit_now():
    endtime = datetime.datetime.utcnow()
    starttime = endtime - datetime.timedelta(days = 2)
    OrbitData = MEOInput_Analysis.czml_meo_orbit_all(starttime, endtime, config_dict) #, satnum)
    return jsonify(OrbitData)

@app.route("/api/czml/meo/per/<int:sourceId>")
def czml_meolut_ant_per(sourceId):
    EndTime = datetime.datetime.utcnow()
    num_hours = 4 
    StartTime = EndTime - datetime.timedelta(hours = num_hours)
    if sourceId == 3669: beaconId =  'ADDC00202020201'
    if sourceId == 3385: beaconId =  'AA5FC0000000001'
    packet_percent = MEOInput_Analysis.api_meo_packet_throughput(sourceId, StartTime, EndTime, config_dict, 
                                                          rep_rate = 50, minutes = num_hours*60, beaconId = beaconId)
    meo_czml = MEOInput_Analysis.czml_meo_ant_per(packet_percent, StartTime, EndTime,)
    return jsonify(meo_czml)

@app.route("/api/czml/leo/orbit")
def czml_leo_sat_orbit():
    #starttime = datetime.datetime(2017,8,19)
    #endtime = datetime.datetime(2017,8, 22)
    endtime = datetime.datetime.utcnow() + datetime.timedelta(days = 1)
    starttime = endtime - datetime.timedelta(days = 1)
    OrbitData = MEOInput_Analysis.czml_leo_orbit_all(starttime, endtime, servername, oppsdatabase ) #, satnum)
    return jsonify(OrbitData)

@app.route("/api/czml/meo/sched")
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