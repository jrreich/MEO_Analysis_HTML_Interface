from werkzeug.utils import secure_filename
from werkzeug.routing import BaseConverter, ValidationError
from flask import Flask, url_for, request, render_template, jsonify, redirect, make_response
import decodehex2
import definitions
from decodefunctions import is_number, dec2bin
import pypyodbc
import MEOInput_Analysis
import SiteAnalysis
import datetime
import csv
import sys
import os
import simplejson as json
import requests 
from requests import get
from collections import OrderedDict
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
    oppsdatabase_old = 'mccoperationalRpt' #for deploying on operational MCC data from 2018 
    oppsdatabase = 'MccMeoLutMonitor' #for deploying on MCC - new db
    mcctestLGM = 'MccMeoLutMonitor' #for deploying on MCC - new db
    #urlbase = 'https://sar-reportsrv'
elif Deploy_on == 'other1':
    servername = r'.\SQLEXPRESS' #for deploying on REICHJ-PC - 2018 and on
    oppsdatabase_old = 'mccoperationalRpt' 
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
        return render_template('BeaconDecoder1.html')
    else: 
        print(request.form)
        hexcode = str(request.form['hexcode']).strip()
        return redirect(url_for('decodedhex',hexcode=hexcode))

@app.route('/beacon/<hexcode>')
def decodedhex(hexcode):
    # read beacon ID and save it
    geocoord = (0, 0)
    locationcheck = False
    #decode and return it
    hexcode = hexcode.replace(" ","")
    beacon = decodehex2.Beacon(hexcode)

    error=''
    if len(beacon.errors)>0 :
        error = ', '.join(beacon.errors)

    # if beacon.gentype=='first':
    #     tmp = 'encodelongfirst.html'
    #     # redirect with the hexcode, beacon type - different inputs depending on type of first gen
    # elif beacon.gentype=='second':
    #     tmp = 'encodelongsecond.html'
    # elif beacon.gentype=='secondtruncated':
    #     tmp = 'output.html'

    tmp = 'BeaconDecode1.html'

    #return results
        
    if beacon.has_loc() and is_number(beacon.location[0]) and is_number(beacon.location[1]):
        geocoord = (float(beacon.location[0]),float(beacon.location[1]))
        print(geocoord)
        locationcheck=True

    # return render_template('BeaconDecode1.html', \
    #     beaconID = beaconID, \
    #     beaconID15 = bcn1.bcnID15, \
    #     countrycode = int(bcn1.country_code,2), \
    #     protocolcode = bcn1.protocol,
    #     bcn = bcn1)

    return render_template(tmp, 
        hexcode=hexcode.upper(), 
        decoded=beacon.tablebin, 
        locationcheck=locationcheck,
        geocoord=geocoord, 
        genmsg=beacon.genmsg)

@app.route('/beaconjson/<hexcode>')
def decodedhexjson(hexcode):
    # read beacon ID and save it
    #decode and return it
    hexcode = hexcode.replace(" ","")
    beacon = decodehex2.Beacon(hexcode)
    outdict = {}
    
    for num, item in enumerate(beacon.tablebin):
        fielddict = {}
        fielddict['bits'] = item[0]
        fielddict['bitvalue'] = item[1]
        fielddict['value'] = item[3]
        outdict[item[2]] = fielddict

    if beacon.has_loc() and is_number(beacon.location[0]) and is_number(beacon.location[1]):
        outdict['lat'] = float(beacon.location[0])
        outdict['lon'] = float(beacon.location[1])




    return jsonify(outdict)

@app.route("/bch/<hexcode>")
def download_bch(hexcode):
    beacon = decodehex2.Beacon(hexcode)
    bchout=beacon.bchstring
    response = make_response(bchout)
    cd = 'attachment; filename=mybch.txt'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response


@app.route('/rawburst', methods=['GET'])
def rawburst():
    arg_dict = {} 
    arg_dict.update(request.args)
    if len(request.args)==0: return render_template('BurstAnalysisForm1.html')
    arg_dict = url_arg_processor(request.args, 4)
    #MEOLUTList, StartTime, EndTime, filesaved, filesaved_zip, output_format = arg_processor(result)
    for key, val in arg_dict.items():
        print(key, val) 
    #print MEOLUTList, StartTime, EndTime, filesaved, filesaved_zip
    if not arg_dict.get('MEOLUTList'): arg_dict['MEOLUTList'] = ['%']  ## probably not needed
    if arg_dict.get('inputsource') in ["excelfile", "zipfile", "sqldbfile"]:
        """f = request.files['inputfile']   # < - Will need to do POST to do this 
        filesaved = os.path.join(approot, UPLOAD_FOLDER,secure_filename(f.filename))
        f.save(filesaved)
        #if result['inputsource'] == 'excelfile':
            #MEOInput_Analysis.xlx_analysis(UPLOAD_FOLDER, secure_filename(f.filename), MEOLUT, StartTime, EndTime, result)
        """
        return jsonify('File uploads not currently supported')
    else: 
        arg_dict.get('inputsource') == 'mccdb'
        filelist = MEOInput_Analysis.MSSQL_burst(arg_dict, config_dict) #,sql_login = 'yes') # sql_login uses FreeTDS and sql login rather than windows auth - used for linux
        return render_template('BurstAnalysisForm1.html', filelist=filelist, MEOLUTList=arg_dict['MEOLUTList'], StartTime=arg_dict['StartTime'], EndTime=arg_dict['EndTime'] )

@app.route('/MEOInputAnalysis', methods=['GET','POST'])
def MEOInputAnalysis():
    if request.method == 'GET':
        result = request.args
        
        if len(result)==0: return render_template('MEOInputAnalysisForm1.html')
    elif request.method == 'POST':
        # read input
        result = request.form

    else: 
        return '<h2> Invalid Request </h2>'
    arg_dict = url_arg_processor(result)
    MEOLUTList, StartTime, EndTime = arg_dict['MEOLUTList'], arg_dict['StartTime'], arg_dict['EndTime']
    if not result.get('inputsource'): result['inputsource']  = 'mccdb'
    """
    if result.get('inputsource') in ["excelfile", "zipfile", "sqldbfile"]:
        f = request.files['inputfile'] 
        filesaved = os.path.join(approot, UPLOAD_FOLDER,secure_filename(f.filename))
        f.save(filesaved)
        if result.get('inputsource') == 'excelfile':
            MEOInput_Analysis.xlx_analysis(filesaved, OUTPUTFOLDER, MEOLUTList, StartTime, EndTime, result) # need to add approot if this will be functional on apache
    """
    #elif result.get('inputsource') == 'mccdb':
    if TimeLog: print('Starting MSSQL_analysis - ' + str(datetime.datetime.utcnow())) 
    csvoutfile, filelist = MEOInput_Analysis.MSSQL_analysis(result, MEOLUTList, StartTime, EndTime, config_dict)
    if TimeLog: print('Finished MSSQL_analysis - ' + str(datetime.datetime.utcnow()))  
    if csvoutfile == None:
        return render_template('MEOInputAnalysisForm1.html', NODATA = True, result=result, StartTime = StartTime, EndTime = EndTime, data = filelist)
    rdr= csv.reader( open(os.path.join(approot,csvoutfile), "r" ))
    csv_data = [ row for row in rdr ]
    return render_template('MEOInputAnalysisForm1.html', data=csv_data,  linklist = filelist)

@app.route('/MEOBeaconAnalysis', methods=['GET'])
def MEOBeaconAnalysis():
    result = request.args
    if len(result)==0: return render_template('MEOBeaconAnalysisForm1.html')
    ### get inputs for MSSQL_beacon_analysis
    arg_dict = url_arg_processor(result)
    ### use old database if selected
    if result.get('inputsource') == 'mcc_operational_rpt': config_dict['oppsdatabase'] = oppsdatabase_old
    MEOLUTList, StartTime, EndTime, filesaved = arg_dict['MEOLUTList'], arg_dict['StartTime'], arg_dict['EndTime'], arg_dict.get('filesaved')
    fileout_dict = {}
    filelist1_dict = None
    #Calling appropriate functions
    if TimeLog: print('Starting Analysis calls - ' + str(datetime.datetime.utcnow())) 
    if result.get('Jdata',False) or result.get('AllSiteSols', False):
        if TimeLog: print('  Starting MeoDataCollection - ' + str(datetime.datetime.utcnow())) 
        filelist1_dict, beacon_out = MEOInput_Analysis.MeoDataCollection(result, MEOLUTList, StartTime, EndTime, config_dict) 
    if TimeLog: print('  Starting MSSQL_beacon_analysis - ' + str(datetime.datetime.utcnow())) 
    beacon_out, csvoutfile, imglist, filelist_dict = MEOInput_Analysis.MSSQL_beacon_analysis(result, MEOLUTList, StartTime, EndTime, config_dict, filesaved) 
    if TimeLog: print('  Done MSSQL_beacon_analysis - ' + str(datetime.datetime.utcnow())) 
    
    #Creating Summary Table if available
    if csvoutfile == None: 
        SummaryData = False
        sum_data = None
    else: 
        SummaryData = True
        rdr= csv.reader( open(os.path.join(approot,csvoutfile), "r" ))
        sum_data = [ row for row in rdr ]
    if filelist1_dict is not None: fileout_dict.update(filelist1_dict)
    if filelist_dict is not None: fileout_dict.update(filelist_dict)
    if csvoutfile is not None: fileout_dict.update({csvoutfile:'Summary Stats'})
    output_data = {'StartTime': StartTime,
                'EndTime': EndTime,
                'beaconID': beacon_out,
                'MEOLUTList': ", ".join(str(MEO) for MEO in MEOLUTList),
                'csvoutfile': csvoutfile,
                'imglist': imglist,
                'linklist': fileout_dict,
                'BeaconType': result['UseBeaconID'],
                'siteID': result['siteID'],
                'SummaryData': SummaryData}
    return render_template('MEOBeaconAnalysisForm1.html', data=sum_data, output_data=output_data )


@app.route('/RealTimeMonitor', methods=['GET'])
def realtimemonitor():
    urlbase = url_for('index', _external = True)
    ### Simple chane of this flag enables the use of the specially developed SQL table (MeolutRealTimeMonitor) for antenna percentages as opposed to pulling all of the data and 
    ### analyzing each refresh -> True should be far quicker as long as the background service to populate this table is running 
    use_realtimemonitor_sql_db = False
    #use_realtimemonitor_sql_db = True
    
    startofscript = datetime.datetime.utcnow()
    if request.args.get('days') != None:
        days = request.args.get('days')
    else:
        days = 4
    if request.args.get('refreshtimer', None):
        refreshtimer = float(request.args.get('refreshtimer'))
    else:
        refreshtimer = 300
    if request.args.get('burstwindow') != None:
        burstwindow = float(request.args.get('burstwindow'))
    else:
        burstwindow = 60
    EndTime = datetime.datetime.utcnow()
    #EndTime_str = EndTime.strftime('%Y-%m-%d %H:%M:%S')
    StartTime = EndTime - datetime.timedelta(days=float(days)) 
    #StartTime_str = StartTime.strftime('%Y-%m-%d %H:%M:%S')
    BurstStartTime = EndTime - datetime.timedelta(minutes=burstwindow)
    #BurstStartTime_str = BurstStartTime.strftime('%Y-%m-%d %H:%M:%S')
    alarmlist, closedalarms, numalarms = MEOInput_Analysis.MEOLUT_alarms(StartTime,EndTime, servername,oppsdatabase) #, sql_login = 'yes')
    if TimeLog: print('1 - MEO Alarms - ' + str(datetime.datetime.utcnow() - startofscript))
    statusHI, statusFL = MEOInput_Analysis.MEOLUT_status(StartTime,EndTime, servername,oppsdatabase)  #, sql_login = 'yes')
    if TimeLog: print('2 - MEO Status - ' + str(datetime.datetime.utcnow() - startofscript))
    HI_location_accuracy = MEOInput_Analysis.api_meo_location_accuracy(3385, BurstStartTime, EndTime, config_dict)[3385]
    #HI_location_accuracy = json.loads(get(url_for('meolut_location_accuracy', MEOLUT_ID = 3385, _external = True, 
    #                                              StartTime = BurstStartTime_str, EndTime = EndTime_str),verify = False).content)
    if TimeLog: print('3 - HI loc accuracy - ' + str(datetime.datetime.utcnow() - startofscript))
    if use_realtimemonitor_sql_db:
        url = urlbase + "api/MEO/real_time_packet_stats/3385"
        HI_packet_percent =  requests.get(url,verify=False).json()
        HI_packet_percent['antenna']=OrderedDict()
        for i in range(1,9):
            HI_packet_percent['antenna'][i] = OrderedDict()
            HI_packet_percent['antenna'][i]['count'] = int(HI_packet_percent['ant'+str(i)+'burstcount'])
            HI_packet_percent['antenna'][i]['percent'] = float(HI_packet_percent['ant'+str(i)+'burstpercent']) 
    else:
        HI_packet_percent = MEOInput_Analysis.api_meo_packet_throughput(3385, BurstStartTime, EndTime, config_dict, 
                                                        beaconId = 'AA5FC0000000001', rep_rate = 50, minutes = burstwindow)
    #HI_packet_percent = json.loads(get(url_for('meolut_packet_throughput', MEOLUT_ID = 3385, rep_rate = 50, 
    #                                           StartTime = BurstStartTime_str, EndTime = EndTime_str, beaconId = 'AA5FC0000000001', 
    #                                           _external = True),verify = False).content)
    if TimeLog: print('4 - HI packet percent - ' + str(datetime.datetime.utcnow() - startofscript)) 
    FL_location_accuracy = MEOInput_Analysis.api_meo_location_accuracy(3669, BurstStartTime, EndTime, config_dict)[3669]
    #FL_location_accuracy = json.loads(get(url_for('meolut_location_accuracy', MEOLUT_ID = 3669, _external = True,
    #                                              StartTime = BurstStartTime_str, EndTime = EndTime_str), verify = False).content)
    if TimeLog: print('5 - FL loc accuracy - ' + str(datetime.datetime.utcnow() - startofscript)) 
    if use_realtimemonitor_sql_db:
        url = urlbase + "api/MEO/real_time_packet_stats/3669"
        FL_packet_percent =  requests.get(url,verify=False).json()
        FL_packet_percent['antenna'] = OrderedDict()
        for i in range(1,9):
            FL_packet_percent['antenna'][i] = OrderedDict()
            FL_packet_percent['antenna'][i]['count'] = int(FL_packet_percent['ant'+str(i)+'burstcount'])
            FL_packet_percent['antenna'][i]['percent'] = float(FL_packet_percent['ant'+str(i)+'burstpercent']) 

    else:
        FL_packet_percent = MEOInput_Analysis.api_meo_packet_throughput(3669, BurstStartTime, EndTime, config_dict, 
                                                        beaconId = 'ADDC00202020201', rep_rate = 50, minutes = burstwindow)
    #FL_url = url_for('meolut_packet_throughput', MEOLUT_ID = 3669, rep_rate = 50, 
    #                                           beaconId = 'ADDC00202020201', _external = True, 
    #                                           StartTime = BurstStartTime_str, EndTime = EndTime_str)
    #FL_packet_percent = json.loads(get(FL_url, verify = False).content)
    if TimeLog: 
        print('6 - FL packet percent - (total load time) = ' + str(datetime.datetime.utcnow() - startofscript))    
    #open_site_list = MEOInput_Analysis.Open_Sites(servername,oppsdatabase)
   
    open_site_list =  requests.get(urlbase + "api/sitesum",verify=False, params = {'open_closed':'all_open'}).json()
    num_sites = len(open_site_list)-1
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
        num_sites = num_sites
        )


@app.route('/SiteQuery')
def site_query():
    urlbase = url_for('index', _external = True)
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
            open_site_list =  requests.get(urlbase + "api/sitesum",verify=False, params = {'open_closed':'all_open'}).json()
            all_site_list = requests.get(urlbase + "api/sitesum",verify=False).json()
            no_all_sites = False
            if all_site_list == "None": no_all_sites = True
            return render_template('OpenSites1.html',
                open_site_list = open_site_list,
                num_open_sites = len(open_site_list)-1,
                all_site_list = all_site_list,
                num_all_sites = len(all_site_list)-1,
                no_all_sites = no_all_sites
                ) 


@app.route('/Map', methods=['GET','POST'])
def SarsatMap():
    if request.method == 'GET':
        if request.args.get('KML', None):
            return render_template('Cesium_Map.html', KMLFILE = request.args.get('KML'))
        if request.args.get('CZML',None): 
            return render_template('Cesium_Map.html', CZMLFILE = request.args.get('CZML'))
        else: 
            return render_template('Cesium_Map.html')

@app.route('/MEOSchedule', methods=['GET'])
def meo_schedule():
    """/api/MEO/schedule?MEOLUT=3385&StartTime=2019-01-21 01:00:00&EndTime=2019-01-21 02:00:00
    """
    arg_dict = url_arg_processor(request.args)
    urlbase = url_for('index', _external = True)
    out_request = requests.get(urlbase + 'api/MEO/schedule', params = {'StartTime': arg_dict['StartTime'], 'EndTime': arg_dict['EndTime'], 'output_format':'data_list'}, verify=False)
    arg_dict['no_data']= False
    if out_request.json() == "None":
        arg_dict['no_data'] = True
    return render_template('MEOSchedule.html', arg_dict=arg_dict, json_data = out_request.json())

@app.route('/MEO/CF')
def meo_cf():
    arg_dict = url_arg_processor(request.args,24)
    urlbase = url_for('index', _external = True)
    url = urlbase + "api/MEO/reference_beacon_locations"
    json_data = requests.get(url,verify=False, params = {'StartTime': arg_dict['StartTime'], 'EndTime': arg_dict['EndTime'], 'output_format':'json'})
    NODATA = None
    if (json_data.json() == "None" or json_data.json() is None):
        NODATA = True 
        num_passes = 0
    else: 
        num_passes = len(json_data.json())
    #return jsonify(json_data.json())
    return render_template('MEO_CrossFilter2.html', json_data_url=json_data.url, json_obj = json_data.json(), NODATA = NODATA, arg_dict = arg_dict, num_passes = num_passes)

@app.route('/SiteAnalysis', methods = ['GET','POST'])
def site_analysis():
    result = request.args
    if len(result)==0: return render_template('SiteAnalysisForm.html')

    # Need Data Source (list), and Beacon or site ID to get data
    if result.get('UseBeaconID',False) == 'SiteInput':
        site_num = result.get('siteID',False)
    else: 
        raise ValidationError()

    ### use old database if selected
    if result.get('inputsource') == 'mcc_operational_rpt': config_dict['oppsdatabase'] = oppsdatabase_old

    data_sources = result.getlist('LUT')

    if TimeLog: print('Starting Data Collection - ' + str(datetime.datetime.utcnow())) 
    data_source_dict = {}
    for ds in data_sources:
        data_source_dict[ds] = json.loads(api_site_sols(ds, site_num).get_data().decode("utf-8"))

    print(data_source_dict)

    # Create diction of output files 
    fileout_dict = {}
    histoout_dict = {}
    filelist1_dict = None

    # Get ground truth source 
    if result.get('GTSource', False) is None:
        gt_type = None
        gt = None
    elif result.get('GTSource', False) == 'enc':
        gt_type = 'enc'
        # don't think you need to get the enc location below, just use them in each location
        #gt = api_site_sols('enc', site_num)
        gt = None
    elif result.get('GTSource', False) == 'GTLatLon':
        gt_type = 'latlon'
        gt =(float(result.get('beaconLat')),float(result.get('beaconLat')))
    elif result.get('GTSource', False) == 'GTFile':
        gt_type = 'file'
        return '<p> File upload not working yet </p>'
        # process gt into a csv file - 
    
    if gt_type is None:
        print('dt')
        data_collect_only = True
    else: 
        # send data and gt to function to analyze
        print(' should have errors ')
        for data_type, data in data_source_dict.items():
            data_out = SiteAnalysis.data_source_compare(data_type, data , gt, gt_type) 
            print('data out = ') 
            print(data_out)
            #fileout_dict[data_set], histoout_dict[data_set] = 
    

    print('is this thing on?')
    
    #Creating Summary Table if available
    if csvoutfile == None: 
        SummaryData = False
        sum_data = None
    else: 
        SummaryData = True
        rdr= csv.reader( open(os.path.join(approot,csvoutfile), "r" ))
        sum_data = [ row for row in rdr ]
    if filelist1_dict is not None: fileout_dict.update(filelist1_dict)
    if filelist_dict is not None: fileout_dict.update(filelist_dict)
    if csvoutfile is not None: fileout_dict.update({csvoutfile:'Summary Stats'})
    output_data = {'StartTime': StartTime,
                'EndTime': EndTime,
                'beaconID': beacon_out,
                'MEOLUTList': ", ".join(str(MEO) for MEO in MEOLUTList),
                'csvoutfile': csvoutfile,
                'imglist': imglist,
                'linklist': fileout_dict,
                'BeaconType': result['UseBeaconID'],
                'siteID': result['siteID'],
                'SummaryData': SummaryData}
    return render_template('MEOBeaconAnalysisForm1.html', data=sum_data, output_data=output_data )


    

@app.route('/LMDB/CF')
def dc():
    arg_dict = url_arg_processor(request.args,7*24)
    urlbase = url_for('index', _external = True)
    url = urlbase + "api/LEO/LMDB"
    json_data = requests.get(url,verify=False, params = {'StartTime': arg_dict['StartTime'], 'EndTime': arg_dict['EndTime'], 'output_format':'json'})
    NODATA = None
    if json_data.json() == "None":
        NODATA = True 
    return render_template('LMDB_CrossFilter.html', json_data_url=json_data.url, json_obj = json_data.json(), NODATA = NODATA, arg_dict = arg_dict, num_passes = len(json_data.json()))

@app.route('/LMDB', methods=['GET'])
def lmdb():
    """/LMDB?StartTime=2019-01-21 01:00:00&EndTime=2019-01-21 02:00:00&LEOLUT=AK1
    """
    arg_dict = url_arg_processor(request.args,5*24)
    arg_dict['output_format'] = 'data_list'
    arg_dict.pop('MEOLUTList',None)
    arg_dict.pop('minutes',None)
    arg_dict.pop('rep_rate', None)
    urlbase = url_for('index', _external = True)
    out_request = requests.get(urlbase + 'api/LEO/LMDB', params = arg_dict, verify=False)
    if out_request:
        return render_template('LMDB.html', arg_dict=arg_dict, json_data = out_request.json())
    return jsonify("No data")

@app.route('/api/sitesum', methods=['GET','POST'])
def sitereturn():
    """ Returns site summaries, arg_dict keys open_closed = [open, closed, all_open], StartTime, EndTime, sitenum  
    Note: if sitenum is set all other inputs are ignored, if all_open is set all other inputs are ignored """
    
    input_dict = {}
    for key, val in request.args.items():
        input_dict.update({key:val})
    if not request.args: input_dict.update({'days':5})
    arg_dict = url_arg_processor(input_dict)
    if request.args.get('open_closed', False): arg_dict['open_closed'] =  request.args.get('open_closed')
    else: arg_dict['open_closed'] =  'all'
    if request.args.get('sitenum', False): arg_dict['sitenum'] = request.args.get('sitenum')
    arg_dict.pop('MEOLUTList',None)
    arg_dict.pop('minutes',None)
    outdata = MEOInput_Analysis.api_site_sum_query(arg_dict, config_dict)
    if outdata: return jsonify(outdata)
    else: return jsonify('None')

def url_arg_processor(url_args, default_hours = 24):
    
    out_dict = {}
    out_dict.update(dict((key,val) for key, val in url_args.items()))
    # Determine End Time for RealTime
    if url_args.get('RealPastTime') == "RT_yes":
        EndTime = datetime.datetime.utcnow()  
        if url_args.get('EndTime',False): 
            if url_args.get('EndTime').find("T") != -1: EndTime = datetime.datetime.strptime(url_args['EndTime'],'%Y-%m-%dT%H:%M')
            else: EndTime = datetime.datetime.strptime(url_args['EndTime'],'%Y-%m-%d %H:%M:%S') 
    # Determine End Time for past time
    else:
        if url_args.get('EndTime',False): 
            if url_args.get('EndTime').find("T") != -1: EndTime = datetime.datetime.strptime(url_args['EndTime'],'%Y-%m-%dT%H:%M')
            else: EndTime = datetime.datetime.strptime(url_args['EndTime'],'%Y-%m-%d %H:%M:%S')
        else: EndTime = datetime.datetime.utcnow().replace(microsecond=0)


    # Determine StartTime 
    if url_args.get('realtimehours'): hours = float(url_args.get('realtimehours'))
    else: hours = 0
    minutes = hours*60
    if url_args.get('days'): days = float(url_args.get('days'))
    else: days = 0
    minutes += days*24*60
    if url_args.get('minutes'): 
        minutes += float(url_args.get('minutes'))
    if minutes == 0: minutes = default_hours*60
    StartTime = EndTime - datetime.timedelta(minutes = minutes)
    
    if url_args.get('StartTime'): 
        if url_args.get('StartTime').find("T") != -1: 
            StartTime = datetime.datetime.strptime(url_args['StartTime'],'%Y-%m-%dT%H:%M')
        else: StartTime = datetime.datetime.strptime(url_args['StartTime'],'%Y-%m-%d %H:%M:%S')

    if url_args.get('MEOLUT'): 
        MEOLUTList = [int(x) for x in url_args.getlist('MEOLUT')]
    else:
        MEOLUTList = [3669, 3385]
    if url_args.get('output_format') == 'json':
        output_format = 'json'
    elif url_args.get('output_format') == 'csv':
        output_format = 'csv'
    else:
        output_format = 'data_list'
    
    rep_rate = url_args.get('rep_rate',None)
    beaconId = url_args.get('beaconId',None)
    out_dict.update({'EndTime': EndTime,
                'StartTime': StartTime,
                'rep_rate': rep_rate,
                'beaconId': beaconId,
                'MEOLUTList': MEOLUTList,
                'minutes': minutes,
                'output_format': output_format})
    return out_dict

@app.route('/api/MEO/location_accuracy/<int:MEOLUT_ID>', methods=['GET'])
def meolut_location_accuracy(MEOLUT_ID):
    '''
    Get Location stats per MEOLUT. Optional args StartTime, EndTime, hours, days, minutes
    If no args are supplied, uses current time as StartTime and 60 minutes 
    Example of using args: 
    /api/MEO/location_accuracy/3385?StartTime=2019-01-21 01:00:00&EndTime=2019-01-21 02:00:00
    '''
    kwargs = {}
    arg_dict = url_arg_processor(request.args)
    #StartTime = datetime.datetime(2019,01,21,01,00)
    #EndTime = datetime.datetime(2019,01,21,02,00)
    output = MEOInput_Analysis.api_meo_location_accuracy(MEOLUT_ID, arg_dict['StartTime'], arg_dict['EndTime'], config_dict, beaconId = arg_dict['beaconId'])
    output[MEOLUT_ID]['StartTime'] = arg_dict['StartTime']
    output[MEOLUT_ID]['EndTime'] = arg_dict['EndTime']
    return jsonify(output)

@app.route('/api/MEO/location_accuracy/all',methods=['GET'])
def api_meo_location_accuracy_all():
    """ returns MEOLUT Location Accuracy from table [MeolutRealTimeLocationMonitor] for specified period"""
    arg_dict = url_arg_processor(request.args)
    
    arg_dict['MEOLUTList'] = [x for x in request.args.getlist('MEOLUT')] # defaults to emptylist (all if not specified)
    outdata = MEOInput_Analysis.api_meo_accuracy_all(config_dict, arg_dict, request.args.get('output_format',None))
    if outdata: 
        if arg_dict['output_format'] == 'csv': return outdata
        return jsonify(outdata)
    return jsonify("None")

@app.route('/api/MEO/reference_location_accuracy/<int:MEOLUT_ID>', methods=['GET'])
def api_meolut_referenece_location_accuracy(MEOLUT_ID):
    '''
    Get Location stats per MEOLUT. Optional args StartTime, EndTime, hours, days, minutes
    If no args are supplied, uses current time as StartTime and 60 minutes 
    Example of using args: 
    /api/MEO/location_accuracy/3385?StartTime=2019-01-21 01:00:00&EndTime=2019-01-21 02:00:00
    '''
    kwargs = {}
    arg_dict = url_arg_processor(request.args)
    #StartTime = datetime.datetime(2019,01,21,01,00)
    #EndTime = datetime.datetime(2019,01,21,02,00)
    output = MEOInput_Analysis.api_meo_ref_beacon_accuracy(MEOLUT_ID, arg_dict['StartTime'], arg_dict['EndTime'], arg_dict,config_dict)
    return jsonify(output)

@app.route('/api/MEO/reference_beacon_locations', methods=['GET'])
def api_meolut_referenece_beacon_locations():
    '''
    Get reference beacon locations for MEOLUTs. Optional args MEOLUT, StartTime, EndTime, hours, days, minutes
    If no args are supplied, uses current time as StartTime and 7 days, uses all MEOLUTs
    Example of using args: 
    /api/MEO/reference_beacon_locations?StartTime=2019-01-21 01:00:00&EndTime=2019-01-21 02:00:00
    '''
    kwargs = {}
    arg_dict = url_arg_processor(request.args)
    if not request.args.get('MEOLUT',False): arg_dict.pop('MEOLUTList', False)
    output = MEOInput_Analysis.api_meo_ref_beacon_locations(arg_dict,config_dict)
    return jsonify(output)

@app.route('/api/MEO/real_time_packet_stats/<int:MEOLUT_ID>', methods=['GET'])
def real_time_packet_stats(MEOLUT_ID):
    if 'Time' in request.args:
        Time = datetime.datetime.strptime(request.args.get('Time'), '%Y-%m-%d %H:%M:%S')
    else: Time = datetime.datetime.utcnow()
    output = MEOInput_Analysis.real_time_packet_stats(MEOLUT_ID, Time, config_dict)
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
    arg_dict = url_arg_processor(request.args)
    packets = MEOInput_Analysis.api_meo_packet_throughput(MEOLUT_ID, arg_dict['StartTime'], arg_dict['EndTime'], config_dict, 
                                                          rep_rate = arg_dict['rep_rate'], minutes = arg_dict['minutes'], beaconId = arg_dict['beaconId'])
    packets['StartTime'] = arg_dict['StartTime']
    packets['EndTime'] = arg_dict['EndTime']
    return jsonify(packets)

@app.route('/api/MEO/schedule', methods=['GET'])
def api_meo_sched():
    """/api/MEO/schedule?MEOLUT=3385&StartTime=2019-01-21 01:00:00&EndTime=2019-01-21 02:00:00
    """
    arg_dict = url_arg_processor(request.args)
    outdata = MEOInput_Analysis.api_meo_schedule(arg_dict['MEOLUTList'], arg_dict['StartTime'], arg_dict['EndTime'], arg_dict['output_format'], config_dict)
    if outdata: 
        if arg_dict['output_format'] == 'csv': return outdata
        return jsonify(outdata)
    return jsonify("None")

@app.route('/api/LEO/LMDB', methods=['GET'])
def api_leo_lmdb():
    """ returns LMDB for specified period"""
    arg_dict = url_arg_processor(request.args)
    
    arg_dict['LEOLUTList'] = [x for x in request.args.getlist('LEOLUT')] # defaults to emptylist (all if not specified)
    arg_dict['SATList'] = [int(x) for x in request.args.getlist('SAT')] # defaults to emptylist (all if not specified)
    outdata = MEOInput_Analysis.api_leo_lmdb(config_dict, arg_dict, request.args.get('output_format',None))
    if outdata: 
        if arg_dict['output_format'] == 'csv': return outdata
        return jsonify(outdata)
    return jsonify("None")


@app.route('/api/site/<table>/<int:sitenum>', methods = ['GET','POST'])
def api_site(table, sitenum):
    # can return any table where a sitenum is defined -- ie alertsitesol, (default if not defined), alertsitesum , outsolution 
    input_data = request.args.to_dict()
    type = 'all'
    if table not in ['alertsitesol', 'alertsitesum' , 'outsolution', 'leo','meo','enc','comp']:
        raise TypeError("table must be type 'alertsitesol', 'alertsitesum', 'outsolution', 'leo','meo' or 'enc' not {}".format(table))
        return render_template('error.html',404) 
    if table in ['leo','meo','enc','comp']:
        type = table 
        table = 'alertsitesol'
    outdata = MEOInput_Analysis.api_site(config_dict, sitenum, table, type)
    print('returning table: ' + table + ', type: ' + type) 
    print(str(len(outdata)) + ' rows')
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
def api_site_sols(type, sitenum):
    # returns solutions of all types (all, leo, meo, comp, enc, - out, outleo, outmeo, outcomp, outenc) a site
    urlbase = url_for('index', _external = True)
    url = urlbase + "api/site/alertsitesol/{}".format(sitenum)
    if type[:3] == 'out': url = urlbase + "api/site/outsolution/{}".format(sitenum)
    composite_columns = ['alertsitenum','alertsitesolid', 'gentime', 'addtime','complat','complon','matchdistance', 
                         'enclat','enclon', 'encmatchdistance', 'inputdatatype',  'alertmsgstate', 'bcnid15', 'bcnid30', 
                        'sourceid', 'sourcename', 'sat','satelliteids','numbursts','numpackets','numsatellites','dop',
                        'sourceantennaids', 'indlocweight', 'indencdistance','rcvtime']
    leo_columns = ['alertsitenum','alertsitesolid','gentime', 'addtime','a_lat','a_lon','tca','complat','complon','altitude','matchdistance', 
                         'enclat','enclon', 'encmatchdistance', 'inputdatatype',  'alertmsgstate', 'bcnid15', 'bcnid30', 
                        'sourceid', 'sourcename', 'sat', 'orbit', 'points', 'a_prob', 'indlocweight', 'indencdistance', 'rcvtime']
    meo_columns = ['alertsitenum','alertsitesolid','gentime', 'addtime','complat','complon','matchdistance', 
                         'enclat','enclon', 'encmatchdistance', 'inputdatatype',  'alertmsgstate', 'bcnid15', 'bcnid30', 
                        'sourceid', 'sourcename', 'sat','satelliteids','sourceantennaids','latitude', 'longitude', 'altitude', 'numbursts',
                        'numpackets','numsatellites','dop', 'sourceantennaids', 'indlocweight', 'indencdistance','rcvtime']
    enc_columns = ['alertsitenum','alertsitesolid','gentime', 'addtime','complat','complon','altitude','matchdistance', 'enclatcoarse', 'encloncoarse',
                         'enclat','enclon', 'encmatchdistance', 'inputdatatype',  'alertmsgstate', 'bcnid15', 'bcnid30', 
                        'sourceid', 'sourcename', 'sat','satelliteids',  'indlocweight', 'indencdistance','rcvtime']
    print(url) 

    data = requests.get(url,verify=False).json()
    
    out_dict = []
    field_to_check_dict = {'comp': 'complat', 'leo': 'a_lat', 'enc': 'enclat', 'meo': 'latitude', 
            'outcomp': 'complat', 'outleo': 'a_lat', 'outenc': 'enclat', 'outmeo': 'latitude'}
    columns_dict = {'comp': composite_columns, 'leo': leo_columns, 'enc': enc_columns, 'meo': meo_columns, 
            'outcomp': composite_columns, 'outleo': leo_columns, 'outenc': enc_columns, 'outmeo': meo_columns} 
    loc_dict = {'comp': ('complat', 'complon'), 'leo': ('a_lat','a_lon'), 'enc': ('enclat','enclon'), 'meo': ('latitude','longitude'), 
            'outcomp': ('complat', 'complon'), 'outleo': ('a_lat','a_lon'), 'outenc': ('enclat','enclon'), 'outmeo': ('latitude','longitude') }
    
    if type == 'all' or type == 'output':
        out_dict = data
    else:
        field_to_check = field_to_check_dict[type]
        columns = columns_dict[type]
        if type[:3] == 'out':
            columns.extend(['outmsgid', 'updatetype','alertmsgstate','frequency','positionconfflag', 'solreal',
            'encreal','srr','regtype','pooraccwarn','srrname1','srrname2','srrname3','mid','midname','craftid',
            'homing','manufact','model','serialnum','bcntype','activtype','specprogramname','tacnumber',
            'positionmatchinfo','isbeaconsgb'])
            cols_to_remove = ['gentime', 'matchdistance','encmatchdistance','inputdatatype','sourcename',
                        'orbit','indlocweight','indencdistance','rcvtime','sourceantennaids','enclatcoarse',
                        'encloncoarse', 'sourceantennaids']
            for col in cols_to_remove: 
                if col in columns: columns.remove(col)
        for row in data:
            if row[field_to_check] != "null" and row[field_to_check] is not None:
                row_dict = {x:row[x] for x in columns}
                row_dict.update({'lat': row[loc_dict[type][0]], 'lon': row[loc_dict[type][1]]})
                out_dict.append(row_dict)

            
    print(type) 
    print(str(len(out_dict)) + ' rows')
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
