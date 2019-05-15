import logging
import os
import zipfile
import itertools
from lxml import etree 
#from czml import czml

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename= os.path.dirname(os.path.abspath(__file__)) + "MEOimportlog.txt",
                    filemode='w')
import numpy as np
import pandas as pd
from itertools import repeat
logging.info('numpy pandas and itertools')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, MinuteLocator, drange
from matplotlib.backends.backend_pdf import PdfPages
logging.info('imported matplotlib')
import math
import sys
import xlrd
logging.info('imported math, sys, os and xlrd')
from datetime import datetime, timedelta
import csv
logging.info('datetime and csv')
from collections import OrderedDict, defaultdict
import simplekml
logging.info('collections and simplekml')
import re
import beacon_decode as bcn
logging.info('re and beacon decode')
import pypyodbc as odbc 
#import pyodbc as odbc
logging.info('pyodbc imported - all modules imported')
from polycircles import polycircles
from decimal import *

getcontext().prec = 3


UID = 'jesse'
PWD = 'nopw'

pd.options.mode.chained_assignment = None # turn off SettingWithCopyWarning

# Set some variable

MEOLUTName ={3669:'Florida',3385:'Hawaii',3677:'Maryland'}
MEOList = [3669, 3385, 3677]
MEORefLoc = {3669:(25.6162, -80.3843),3385:(21.52071, -157.9963), #Reference Beacon Locations
    3677:(38.999121, -76.853789)} # Goddard beacon antenna unknown
MEOLUTref = {3669: 'Florida-1', 3385:'Hawaii-1', 3677:'NASA_Goddard'}
ReferenceBeacons = {'Florida-1':{'beaconId': 'ADDC00202020201',
                                'beaconLat': 25.61622,
                                'beaconLon': -80.38422,
                                'repRate': 50},
                    'Hawaii-1': {'beaconId': 'AA5FC0000000001',
                                'beaconLat': 21.52075,
                                'beaconLon': -157.9963,
                                'repRate': 50},
                    'California': {'beaconId': 'ADFC000001D0033',
                                'beaconLat': 34.6625,
                                'beaconLon': -120.5515,
                                'repRate': 50},
                    'Edmonton': {'beaconId': 'A79EEE26E32E1D0',
                                'beaconLat': 53.678667,
                                'beaconLon': -113.315,
                                'repRate': 50},
                    'Ottawa': {'beaconId': 'A79EEE26E32E190',
                                'beaconLat': 45.3291,
                                'beaconLon': -75.6745,
                                'repRate': 50},
                    'McMurdo': {'beaconId': 'ADC268F8E0D3730',
                                'beaconLat': -77.846033,
                                'beaconLon': 166.71178,
                                'repRate': 50},
                    'NASA_Goddard': {'beaconId': 'ADFFFFFFFFFFFFC',
                                'beaconLat': 38.99895,
                                'beaconLon': -76.841599,
                                'repRate': 50},
                    'ToulouseTCAL': {'beaconId': '9C6000000000001',
                                'beaconLat': 43.5605,
                                'beaconLon': 1.4808,
                                'repRate': 30},
                    'ToulouseOrb': {'beaconId': '9C634E2AB509240',
                                'beaconLat': 43.5605,
                                'beaconLon': 1.4808,
                                'repRate': 30},
                    'ToulouseMeoQMS': {'beaconId': '9C62BE29630F1D0',
                                'beaconLat': 43.56053521,
                                'beaconLon': 1.480896128,
                                'repRate': 50},
                    'SpitsbergenMeoQMS': {'beaconId': 'A042BE29630F190',
                                'beaconLat': 78.23075718,
                                'beaconLon': 15.37056787,
                                'repRate': 50},
                    'MaspalomasMeoQMS': {'beaconId': '9C02BE29630F0A0',
                                'beaconLat': 27.76150509,
                                'beaconLon': -15.63427686,
                                'repRate': 50},
                }

#Date Formats
timepacket_format = '%Y-%m-%d %H:%M:%S.%f'
datetime_format = '%y %j %H%M %S.%f'
GMT_format = '%a, %d %b %Y %H:%M:%S %Z'
sec_f = '%S.%f'
plot_fmt = DateFormatter('%m-%d %H:%M')
Hours = MinuteLocator(interval = 30)
FiveMinutes = MinuteLocator(interval=5)


data_cols = ['DataType','BcnId15','BcnId30','SourceId','TimeFirst','TimeLast','Latitude',
    'Longitude','Altitude','NumBursts','NumPackets','DOP','ExpectedHorzError']
data_cols = [0,1,2,4,8,9,10,11,12,13,14,17,18,19,20,21,22,36,37,47]
ant_list = list(range(1,7))
MEOLUTLoc = {3669:(25.617645, -80.383211), 3385:(21.5244, -158.0012), #MEOLUT Locations
    3677:(38.999121, -76.853789), 2276:(43.56053521, 1.480896128)}

Miami_height = 1
NSOF_height = 10
Wahiawa_height = 1

MEOLUT_antenna_locations = {3669:{1:(25.617661, -80.383376, Miami_height),2: (25.617754, -80.383177, Miami_height), 
                                  3: (25.617641, -80.382956, Miami_height), 4:(25.617425, -80.382982, Miami_height),
                                  5: (25.617309, -80.383185, Miami_height), 6:(25.617440, -80.383412, Miami_height),
                                  7: (25.617234, -80.383470, Miami_height), 8:(25.617200, -80.382950, Miami_height),
                                  9: (38.852473, -76.936823, NSOF_height)},
                            3385:{1:(21.524682, -158.001442, Wahiawa_height), 2: (21.524711, -158.001071, Wahiawa_height),
                                  3:(21.524414, -158.000923, Wahiawa_height), 4: (21.524086, -158.001048, Wahiawa_height),
                                  5:(21.524123, -158.001459, Wahiawa_height), 6: (21.524392, -158.001614, Wahiawa_height),
                                  7:(21.525110, -158.001270, Wahiawa_height), 8: (21.525090, -158.000895, Wahiawa_height)}}

sat_list = [302, 315, 324, 430, 329, 408, 422, 319, 306, 317, 422, 430]
''' see http://www.cospas-sarsat.int/en/system/space-segment-status-pro/current-space-segment-status-and-sar-payloads-pro  for full list '''
all_sarsats = [401, 402, 403, 404, 405, 407, 408, 409, 414, 418, 419, 420, 422, 
               424, 426, 430, 501, 502, 301, 302, 303, 306, 308, 309, 310, 312, 
               315, 316, 317, 318, 319, 323, 324, 326, 327, 329, 330, 332]
us_sarsats = allsats = [408, 409, 419, 422, 424, 426, 430, 301, 302, 303, 306, 
                        308, 309, 310, 312, 315, 316, 317, 318, 319, 323, 324, 
                        326, 327, 329, 330, 332]



USMCC = False

if USMCC == True:
    icon_list = {
        'blue_dot': '/static/icons/blue_pog.png',
        'red_dot': '/static/icons/placemark_circle_highlight.png',
        'white_dot': '/static/icons/placemark_circle.png',
        'blue_square': '/static/icons/track-none.png',
        'black_square': '/static/icons/icon61.png',
        'white_circle': '/static/icons/icon18.png',
        'green_circle': '/static/icons/icon17.png',
        'red_cross': '/static/icons/icon63.png',
        'yellow_pin': '/static/icons/ylw-blank.png',
        'red_pin': '/static/icons/red-circle.png',
        'blue_pin': '/static/icons/blu-blank.png',
        'white_arrow': '/static/icons/arrow.png',
        'green_arrow': '/static/icons/green_arrow.png',
        'circle_E': '/static/icons/iconE.png',
        'circle_M': '/static/icons/iconM.png',
        'circle_L': '/static/icons/iconL.png',
        'little_E': '/static/icons/littleE.png',
        'little_M': '/static/icons/littleM.png',
        'little_L': '/static/icons/littleL.png',
        'M': '/static/icons/M.png',
        'L': '/static/icons/L.png',
        'One': '/static/icons/1.png',
        }

else: 
    icon_list = {
        'blue_dot': 'http://maps.google.com/mapfiles/kml/paddle/blu-blank-lv.png',
        'red_dot': 'http://maps.google.com/mapfiles/kml/pal4/icon49.png',
        'white_dot': 'http://maps.google.com/mapfiles/kml/pal4/icon57.png',
        'blue_square': 'http://earth.google.com/images/kml-icons/track-directional/track-none.png',
        'black_square': 'http://maps.google.com/mapfiles/kml/pal4/icon56.png',
        'white_circle': 'http://maps.google.com/mapfiles/kml/pal2/icon18.png',
        'green_circle': 'http://maps.google.com/mapfiles/kml/pal4/icon17.png',
        'red_cross': 'http://maps.google.com/mapfiles/kml/pal4/icon63.png',
        'yellow_pin': 'http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png',
        'red_pin': 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png',
        'blue_pin': 'http://maps.google.com/mapfiles/kml/paddle/blu-blank.png',
        'white_arrow': 'http://maps.google.com/mapfiles/kml/shapes/arrow.png',
        'green_arrow': 'https://www.google.com/mapfiles/arrow.png',
        'circle_E': 'http://maps.google.com/mapfiles/kml/pal5/icon52.png',
        'circle_M': 'http://maps.google.com/mapfiles/kml/pal5/icon36.png',
        'circle_L': 'http://maps.google.com/mapfiles/kml/pal5/icon35.png',
        'little_E': 'http://maps.google.com/mapfiles/kml/pal5/icon60l.png',
        'little_M': 'http://maps.google.com/mapfiles/kml/pal5/icon36l.png',
        'little_L': 'http://maps.google.com/mapfiles/kml/pal5/icon43l.png',
        'M': 'http://maps.google.com/mapfiles/kml/paddle/M.png',
        'L': 'http://maps.google.com/mapfiles/kml/paddle/L.png',
        'One': 'http://maps.google.com/mapfiles/kml/paddle/1.png',
        }

#functions for dealing with times
def xldate_to_datetime(xldate):
    temp = datetime(1900, 1, 1)
    delta = timedelta(days=(xldate-1))
    return temp+delta

def time_to_datetime(timein):
    if isinstance(timein, datetime): 
        return timein
    if isinstance(timein, str):
        try: 
            return datetime.strptime(timein, timepacket_format)
        except:
            pass
        try: 
            return datetime.strptime(timein, datetime_format)
        except: pass
        try: return datetime.strptime(timein, GMT_format)
        except: TypeError('timein string does not match available formats') 
    if isinstance(timein, float): return xldate_to_datetime(timein)
    else: raise TypeError('timein is unrecognized type, must be a datetime, string, or excel serial float, not a %s' % type(timein))
        
def haversine(x):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    for i in x:
        if i == None:
            return None

    lat1, lon1, lat2, lon2 = list(map(np.radians, [x[0], x[1], x[2], x[3]]))
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    r = 6373 # Radius of earth in kilometers. Use 3956 for miles     
    return c * r

#safe division (don't fail for divide by 0, return 0) 
def safe_div(a,b):
    if b<=0:
        return 0
    else: return a/float(b)
#function to iterate using fetchmany yield 
def ResultIter(cursor, arraysize=1000):
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result

#Write function that filters data based on one field (filter field, filter criteria) 
def filter1(df, field, criteria):
    return df[df[field]==float(criteria)]
def JSON_to_csv(url, csvout):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    file_out = r'D:\Reich_disk1\Documents\Coding\Python\JSON_to_csv\test.csv'
    with open( file_out, 'w', newline="" ) as out_file:
        csv_w = csv.writer( out_file )
        for i_r in data:
            csv_w.writerow( i_r )
    return None

#Write function that filters data based on range of one field (filter field, filter criteria_low, filter criteria_high) 
def filter_range(df, field, criteria_low, criteria_high):
    return df[((df[field] >= float(criteria_low)) & (df[field] <= float(criteria_high)))]

def singleburst_loc(df, lat_GT, lon_GT, MEOLUT):
    df2 = df
    if MEOLUT:
        df2 = df[(df.sourceid == MEOLUT)]
    if df2.empty: return df2

    df2['Lat_GT'],df2['Lon_GT'] = lat_GT, lon_GT
    df2['Error_GT'] = df2[['latitude','longitude', 'Lat_GT','Lon_GT']].apply(haversine, axis = 1)
    df2['Error_Enc'] = df2[['latitude','longitude','Enc_Lat','Enc_Lon']].apply(haversine, axis = 1)
    dfSB = df2.sort_values('timelast')
    dfSB = dfSB.drop(['Lat_GT','Lon_GT'],axis = 1)
    dfSB['timestart_diff'] = dfSB['timefirst'].shift(-1) - dfSB['timefirst']
    dfSB['TimeToMcc'] = dfSB.index - dfSB['timelast']
    dfSB['TimeToGenerate'] = dfSB.index - dfSB['timelast']
    dfSB = dfSB[(dfSB.timestart_diff > pd.Timedelta(seconds = 5)) | (dfSB.timestart_diff.isnull())] ###PROBLEM
    return dfSB

def multiburst_loc(df,lat_GT,lon_GT,MEOLUT, window_span):
    timefirst = df.timefirst.min()
    timelast = df.timelast.max()
    df2 = df[(df.sourceid == MEOLUT)]
    if df2.empty: return df2
    df2['Lat_GT'],df2['Lon_GT'] = lat_GT, lon_GT
    df2['Error_GT'] = df2[['latitude','longitude', 'Lat_GT','Lon_GT']].apply(haversine, axis = 1)
    df2['Error_Enc'] = df2[['latitude','longitude','Enc_Lat','Enc_Lon']].apply(haversine, axis = 1)

    ##df2 = df2.sort_values('TimeFirst')
    df3 = df2.drop(['Lat_GT','Lon_GT'],axis = 1)
    
    # Sorting and finding windows
    df3 = df3.sort_values('timelast') #Rethink how you do windows 12/9 -- I think it was solved previously 1/8/17
    df3['timestart_diff'] = df3['timefirst'].shift(-1) - df3['timefirst']
    df3['timestart_diff2'] = df3['timefirst'].shift(-2) - df3['timefirst']
    df3['TimeToMcc'] = df3.index - df3['timelast']
    df3['TimeToGenerate'] = df3.index - df3['timelast']
    df3['last_in_window'] = (df3.timestart_diff > pd.Timedelta(minutes = 9)) & (df3.timestart_diff2 > pd.Timedelta(minutes = 3))    
    df3 = df3[((df3.timestart_diff > pd.Timedelta(minutes = 9)) & (df3.timestart_diff2 > pd.Timedelta(minutes = 3))) | df3.timestart_diff.isnull()] 
    return df3 

def write_headers(filetype,csvoutfile, approot, J1_header):
    with open(os.path.join(approot,csvoutfile), 'w', newline="") as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        if (filetype == "packet" or filetype == "TOA_FOA_DATA"): wr.writerow(J1_header)
        elif filetype == 'status': wr.writerow(Statusfileheader)
    return None
def xml_process(filename, filetype, country= 'USA', beaconId = False):
    packets = list()
    if (filetype == 'packet' or filetype == 'TOA_FOA_DATA'):
        for event, element in etree.iterparse(filename, tag='TOA_FOA_DATA'):
            if country == 'Canada':
                namespace = e.tag[1:].split("}")[0]
                packets = e.findall(".//{%s}TOA_FOA_DATA" % namespace)
            elif beaconId:
                for child in element:
                    if child.tag == 'MF22' and child.text == beaconId: packets.append(element)
            else:
                packets = e.findall(".//{}".format(filetype))
    else:
        for i, item in ET1:
            if (item.tag == 'solutionsMessage'):
                packets = ET2
    return packets
#def find_str_in_tag(filename, searchtag, searchstr):
#    packetlist = list()
#    for event, element in etree.iterparse(filename, tag='TOA_FOA_DATA'):
#        for child in element:
#            if child.tag == searchtag and child.text == searchstr: packetlist.append(element)
#    return packetlist

def search_zip_output(MEOLUT, zip,zipmatches,filetypesearch,csvoutfile, approot, J1_header, country = 'USA', beaconId = False):
    #open file and write headers which erases data in it
    #write_headers_USSHARE(csvoutfile) - Need new Functions to write different headers other than USSHARE raw data
    #if filetypesearch == 'packet': write_headers_USSHARE(csvoutfile)
    write_headers(filetypesearch,csvoutfile, approot, J1_header)
    with zipfile.ZipFile(zip, 'r') as myzip:
        for files in zipmatches:
            file = myzip.open(files)
            filename = str(file)          
            packets = xml_process(file,filetypesearch, country, beaconId)
            if packets:
                write_bursts_csv(packets,csvoutfile,filetypesearch, files, approot)
def file_search_regex(filetypesearch, country):
    if (filetypesearch == "packet" or filetypesearch == "TOA_FOA_DATA"):
        if country == 'USA':
            my_regex = r"(.*)"+ re.escape("USSHARE") + r"(.*)"
        if country == 'Canada':
            my_regex = r"(.*)"+ re.escape("HGTMEO") + r"(.*)"
    else:
        my_regex = r"(.*)"+ re.escape("USMCC") + r"(.*)"
    return my_regex
def write_bursts_csv(packets,csvoutfile, filetypesearch, filename, approot, bcnId = False):
    burst = list()
    componentlist = list()
    with open(os.path.join(approot,csvoutfile), 'a', newline="") as csvfile:
        csvoutwriter = csv.writer(csvfile, delimiter=',',
                                quoting=csv.QUOTE_MINIMAL)
        if (filetypesearch == "packet" or filetypesearch == "TOA_FOA_DATA"):   
            for packet in packets:
                for MF in packet:
                    burst.append(MF.text)
                TOA = datetime.strptime(burst[6],datetime_format)
                newrow = [0, burst[4], burst[3], TOA, burst[7], burst[9],TOA,burst[8],burst[10],burst[11],burst[2],burst[0],burst[1],burst[5]]
                csvoutwriter.writerow(newrow)
                burst=list()
# Return list of files of in zip file matching searchstring
def find_file_inzip(zipfilename,searchstring):
    with zipfile.ZipFile(zipfilename, 'r') as myzip:
        ziplist = myzip.namelist()
        matches = [string for string in ziplist if re.match(searchstring, string)]
        print('num of files in ' + zipfilename + ' = ' + str(len(ziplist)))
        print('returning ' + str(len(matches)) + ' files in zip with search string ' + searchstring) 
        return matches

def find_packets(servername= 'localhost', databasename='MccTestLGM', beaconid = '%', start_date = 0, end_date = None, MEOLUT = '%',ant_i = '%', sat = '%', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit=True)
    else:
        conn = odbc.connect(r'Driver={SQL Server}; Server='+servername+'; Database='+databasename+'; Trusted_Connection=yes',readonly=True, autocommit=True)
    c = conn.cursor()
    query_params = ['%'+beaconid+'%', MEOLUT, start_date, end_date, ant_i, sat]
    sql_query = ('SELECT UplinkTOADate, UplinkFOA from MeolutPackets '
        'WHERE '
        'BcnId15 like ? '
        'AND '
        'MeolutId like ? '
        'AND ' 
        'AddTime between ? AND ? '
        'AND '
        'AntennaId like ? '
        'AND '
        'SatId like ? ' )
    c.execute(sql_query, query_params)
    packets = c.fetchall()
    return packets

def plot_packets(packets, MEOLUT, ant_i,start_time,end_time, packets_found, percent_packets):
    global ax1
    frequencylist = list()
    timelist = list()
    velolist = list() 
    for packet in packets:
        frequencylist.append(packet[1])
        timelist.append(packet[0])
        #timelist.append(datetime.strptime(packet[12],timepacket_format))
    #if timelist:
    #    mintime = min(timelist)
    #    maxtime = max(timelist)
    #else:
    #alt = [np.linalg.norm(x) for x in posilist]    
    #rangelist = [np.linalg.norm(MEOLUTLocDict[MEOLUT] - x) for x in posilist]
    #plotting TLE positional difference below
    #fig, ax = plt.subplots()
    #ax.plot_date(timelist, frequencylist, '-')
    #font = {'family' : 'normal',
            #'weight' : 'bold',
            #'size'   : 22}
    #matplotlib.rc('font', **font)
    plt.figure(MEOLUT, figsize=(40,20))
    if ant_i == ant_list[0]:
        ax1 = plt.subplot(len(ant_list),1,1)
    else:
        plt.subplot(len(ant_list),1,ant_list.index(ant_i)+1, sharex = ax1, sharey = ax1)
    
    plt.plot(timelist, frequencylist,'ro')
    plt.title('{} - antenna {} -- {} packets = {:.1f}%'.format(MEOLUT,ant_i,packets_found,percent_packets))
    #plt.title('{} - antenna {} ---- {} packets'.format(MEOLUT,ant_i,packets_found)) #,percent_packets))
    plt.grid(True)
    #plt.gca().xaxis.set_major_locator(Hours)
    plt.gca().xaxis.set_major_formatter(plot_fmt)
    #plt.gca().xaxis.set_minor_locator(FiveMinutes)
    plt.gca().set_xlim(start_time,end_time)

def xlx_analysis(UPLOADFILE, OUTPUTFOLDER, MEOLUT, TimeStart, TimeEnd, result, Lat_GT=0, Long_GT=0, Location='', **kwargs):
    # need to add approot to any place a file is written if this will be functional on apache 
    # - done 7/12/17 in routes.py, UPLOADFILE is now full path - change may be needed in over functions 
    InputMEO_excelfile = UPLOADFILE
    CSVoutfolder = OUTPUTFOLDER
    BeaconID = result['beaconID']
    if ('Lat' in kwargs): 
        Lat_GT = kwargs['Lat']
    else: 
        Lat_GT = None
    if ('Long' in kwargs): 
        Long_GT = kwargs['Long']
        MEO_dist = haversine([Lat_GT,Long_GT,MEOLUTLoc[MEOLUT][0],MEOLUTLoc[MEOLUT][1]])
    else: 
        Long_GT = None
        MEO_dist = 'NA'
    df = pd.read_excel(InputMEO_excelfile, index_col = 'TimeSolutionAdded') #, parse_dates = True) #, parse_cols =  data_cols) #parse_dates = True,
    df['TimeFirst']=pd.to_datetime(df['TimeFirst'], errors = 'ignore') ### FIX THIS WHEN TimeFirst is already a datetime.time 12/9 
    df['TimeLast']=pd.to_datetime(df['TimeLast'], errors = 'ignore')
    df['TimeSolutionGenerated']=pd.to_datetime(df['TimeSolutionGenerated'], errors = 'ignore')
    #df['TimeSolutionAdded']=pd.to_datetime(df['TimeSolutionAdded'])

    #df['DataType'] = df['DataType']
    #df.set_index(df['TimeSolutionAdded'],inplace = True)
    #df = df.drop(['BcnId36','FbiasDev', 'FreqDrift','SitFunc','MsgNum','QualityIndicator','NumAntennas','Srr', \
        #'PositionConfFlag','SortId','SortType','Distance'], axis = 1) -- No longer needed if I just slice into sub table
    #df.sort_values('TimeSolutionAdded').head()

    df2 = df[['DataType','BcnId15','BcnId30','SourceId','TimeFirst','TimeLast','Latitude',
        'Longitude','Altitude','NumBursts','NumPackets','DOP','ExpectedHorzError']]
    df2.index = df2.index.map(str.lower)
    df2 = df2.sort_index().ix[TimeStart:TimeEnd]
    df3 = df2[(df2.bcnid15 == BeaconID)]
    dfSB = df3[(df3.datatype == 3)] 
    dfMB = df3[(df3.datatype == 0)] 
    if df3.empty: 
        print("Data Frame is empty after filtering out Beacon ID = " + BeaconID)

    lat_fun = lambda hexin: bcn.beacon(hexin).lat
    lon_fun = lambda hexin: bcn.beacon(hexin).lon
    dfSB['Enc_Lat'] = dfSB['bcnid30'].apply(lat_fun)
    dfSB['Enc_Lon'] = dfSB['bcnid30'].apply(lon_fun)
    dfMB['Enc_Lat'] = dfMB['bcnid30'].apply(lat_fun)
    dfMB['Enc_Lon'] = dfMB['bcnid30'].apply(lon_fun)

    df_SBL = singleburst_loc(dfSB,Lat_GT,Long_GT,MEOLUT)
    SBL = len(df_SBL)
    df5 = df_SBL[df_SBL.Error_GT < 5] if not df_SBL.empty else df_SBL
    df5_enc = df_SBL[df_SBL.Error_Enc < 5] if not df_SBL.empty else df_SBL
    df10 = df_SBL[df_SBL.Error_GT < 10] if not df_SBL.empty else df_SBL
    df10_enc = df_SBL[df_SBL.Error_Enc < 10] if not df_SBL.empty else df_SBL
    df20_enc = df_SBL[df_SBL.Error_Enc < 20] if not df_SBL.empty else df_SBL

    timefirst = df3.TimeFirst.min()
    timelast = df3.TimeLast.max()
    timediff = timelast - timefirst

    SBL_5 = len(df5)
    SBL_5_enc = len(df5_enc)
    SBL_10 = len(df10)
    SBL_10_enc = len(df10_enc)
    SBL_20_enc = len(df20_enc)

    error_SBL = df_SBL.Error_GT if not df_SBL.empty else df_SBL # not used currently

    expected_bursts = int(timediff/pd.Timedelta(seconds = 50))
    prob_SBL = float(SBL)/expected_bursts if expected_bursts != 0 else 0
    prob_SBL_5 =float(SBL_5)/SBL if SBL !=0 else 0
    prob_SBL_5_enc =float(SBL_5_enc)/SBL if SBL !=0 else 0
    prob_SBL_10 = float(SBL_10)/SBL if SBL !=0 else 0
    prob_SBL_10_enc = float(SBL_10_enc)/SBL if SBL !=0 else 0
    prob_SBL_20_enc = float(SBL_20_enc)/SBL if SBL !=0 else 0

    #print 'Analysis of MEOLUT -> {} - {}'.format(MEOLUTName[MEOLUT],MEOLUT)
    #print '\n Beacon Ground Truth Location used = {}, {}'.format(Lat_GT,Long_GT)
    #print ' Distance from MEOLUT = {:.1f} km'.format(haversine([Lat_GT,Long_GT,MEOLUTLoc[MEOLUT][0],MEOLUTLoc[MEOLUT][1]]))
    ##print ' Distance from MEOLUT = {:.1f} km'.format(haversine([Lat_GT,Long_GT,MEOlat,MEOlon]))
    #print ' Time of first burst = {:%Y-%m-%d %H:%M:%S}'.format(timefirst)
    #print ' Time of Last burst = {:%Y-%m-%d %H:%M:%S}'.format(timelast)
    #print ' Time Span = {}'.format(timediff)

    #print '\nSINGLE BURST ANALYSIS'
    #print 'Expected single burst locations = {}'.format(expected_bursts)
    #print '\n'
    #print 'Number of single burst locations = {}'.format(SBL)
    #print 'Probability of single burst location = {:.2%}'.format(prob_SBL)
    #print '\n'
    #print 'Number of single burst locations within 5 km = {}'.format(SBL_5)
    #print 'Percent of single burst locations within 5 km = {:.2%}'.format(prob_SBL_5)
    #print 'Number of single burst locations within 5 km (vs Encoded Location) = {}'.format(SBL_5_enc)
    #print 'Percent of single burst locations within 5 km (vs Encoded Location) = {:.2%}'.format(prob_SBL_5_enc)
    #print '\n'
    #print 'Number of single burst locations within 10 km = {}'.format(SBL_10)
    #print 'Percent of single burst locations within 10 km = {:.2%}'.format(prob_SBL_10)
    #print 'Number of single burst locations within 10 km (vs Encoded Location) = {}'.format(SBL_10_enc)
    #print 'Percent of single burst locations within 10 km (vs Encoded Location) = {:.2%}'.format(prob_SBL_10_enc)
    #print '\n'
    #print 'Number of single burst locations within 20 km (vs Encoded Location) = {}'.format(SBL_20_enc)
    #print 'Percent of single burst locations within 20 km (vs Encoded Location) = {:.2%}'.format(prob_SBL_20_enc)

    ## Multi Burst (Windowed) Section
    window_time = 20 #minutes - no longer used since now just look for change in TimeFirst
    window_span = pd.Timedelta(minutes = window_time)
    expected_windows = math.ceil(timediff/window_span)

    df_MBL = multiburst_loc(dfMB, Lat_GT, Long_GT, MEOLUT, window_span)
    df_MBL5 = df_MBL[df_MBL.Error_GT < 5] if not df_MBL.empty else df_MBL
    df_MBL5_enc = df_MBL[df_MBL.Error_Enc < 5] if not df_MBL.empty else df_MBL
    df_MBL10 = df_MBL[df_MBL.Error_GT < 10] if not df_MBL.empty else df_MBL
    df_MBL10_enc = df_MBL[df_MBL.Error_Enc < 10] if not df_MBL.empty else df_MBL
    df_MBL20_enc = df_MBL[df_MBL.Error_Enc < 20] if not df_MBL.empty else df_MBL

    MBL = len(df_MBL)
    MBL_5 = len(df_MBL5)
    MBL_5_enc = len(df_MBL5_enc)
    MBL_10 = len(df_MBL10)
    MBL_10_enc = len(df_MBL10_enc)
    MBL_20_enc = len(df_MBL20_enc)

    error_MBL = df_MBL.Error_GT if not df_MBL.empty else df_MBL # not used currently

    prob_MBL = float(MBL)/expected_windows if expected_windows != 0 else 0
    prob_MBL_5 =float(MBL_5)/MBL if MBL !=0 else 0
    prob_MBL_5_enc =float(MBL_5_enc)/MBL if MBL !=0 else 0
    prob_MBL_10 = float(MBL_10)/MBL if MBL !=0 else 0
    prob_MBL_10_enc = float(MBL_10_enc)/MBL if MBL !=0 else 0
    prob_MBL_20_enc = float(MBL_20_enc)/MBL if MBL !=0 else 0

    #print '\n\nMULTIPLE BURST ANALYSIS'
    #print 'Multiple Burst (windowed) locations, Window = {}'.format(window_span)
    #print 'Expected number of windows = {}'.format(int(expected_windows))
    #print '\n'
    #print 'Number of windowed locations = {}'.format(MBL)
    #print 'Probability of windowed location = {:.2%}'.format(prob_MBL)
    #print '\n'
    #print 'Number of windowed locations within 5 km = {}'.format(MBL_5)
    #print 'Percent of windowed locations within 5 km = {:.2%}'.format(prob_MBL_5)
    #print 'Number of windowed locations within 5 km (vs Encoded Location) = {}'.format(MBL_5_enc)
    #print 'Percent of windowed locations within 5 km (vs Encoded Location) = {:.2%}'.format(prob_MBL_5_enc)
    #print '\n'
    #print 'Number of windowed locations within 10 km = {}'.format(MBL_10)
    #print 'Percent of windowed locations within 10 km = {:.2%}'.format(prob_MBL_10)
    #print 'Number of windowed locations within 10 km (vs Encoded Location) = {}'.format(MBL_10_enc)
    #print 'Percent of windowed locations within 10 km (vs Encoded Location) = {:.2%}'.format(prob_MBL_10_enc)
    #print '\n'
    #print 'Number of windowed locations within 20 km (vs Encoded Location) = {}'.format(MBL_20_enc)
    #print 'Percent of windowed locations within 20 km (vs Encoded Location) = {:.2%}'.format(prob_MBL_20_enc)

    outfilelist = list()
    outfiletag = '{}_{}_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}'.format(MEOLUT,BeaconID,TimeStart,TimeEnd)
    SBLfile = OUTPUTFOLDER + '\SBL'+outfiletag +'.csv'
    MBLfile = OUTPUTFOLDER + '\MBL'+outfiletag +'.csv'
    OUTfile = OUTPUTFOLDER + '\OUT' + outfiletag +'.csv'
    df_SBL.to_csv(SBLfile)
    df_MBL.to_csv(MBLfile)
    outfilelist.append(SBLfile)
    outfilelist.append(MBLfile)
    outfilelist.append(OUTfile)
    
    with open(OUTfile, 'w', newline="") as csvfile:
        csvoutwriter = csv.writer(csvfile, delimiter=',',
                                quoting=csv.QUOTE_MINIMAL)
        csvoutwriter.writerow(['MEOLUT', MEOLUTName[MEOLUT]])
        csvoutwriter.writerow(['MEOLUT_ID', MEOLUT])
        csvoutwriter.writerow(['BeaconID',BeaconID])
        csvoutwriter.writerow(['Location',Location])
        csvoutwriter.writerow(['TimeStart',TimeStart])
        csvoutwriter.writerow(['TimeEnd',TimeEnd])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['Ground Truth Lat',Lat_GT])
        csvoutwriter.writerow(['Ground Truth Long',Long_GT])
        csvoutwriter.writerow(['Distance From MEOLUT',MEO_dist]) #'{:.2f}'.format(MEO_dist)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['Time First Burst','{:%Y-%m-%d %H:%M:%S}'.format(timefirst)])    
        csvoutwriter.writerow(['Time Last Burst', '{:%Y-%m-%d %H:%M:%S}'.format(timelast)])
        csvoutwriter.writerow(['Time Span', timediff])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['SINGLE BURST LOCATIONS'])
        csvoutwriter.writerow(['ExpSBL',expected_bursts])
        csvoutwriter.writerow(['NumSBL',SBL])
        csvoutwriter.writerow(['ProbSBL','{:.2%}'.format(prob_SBL)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumSBL <5km', SBL_5])
        csvoutwriter.writerow(['% SBL <5km', '{:.2%}'.format(prob_SBL_5)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumSBL <10km', SBL_10])
        csvoutwriter.writerow(['% SBL <10km', '{:.2%}'.format(prob_SBL_10)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumSBL <5km (vs Enc)', SBL_5_enc])
        csvoutwriter.writerow(['% SBL <5km (vs Enc)', '{:.2%}'.format(prob_SBL_5_enc)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumSBL <10km (vs Enc)', SBL_10_enc])
        csvoutwriter.writerow(['% SBL <10km (vs Enc)', '{:.2%}'.format(prob_SBL_10_enc)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumSBL <20km (vs Enc)', SBL_20_enc])
        csvoutwriter.writerow(['% SBL <20km (vs Enc)', '{:.2%}'.format(prob_SBL_20_enc)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['MULTIPLE BURST LOCATIONS'])
        csvoutwriter.writerow(['Window Period', window_span])
        csvoutwriter.writerow(['ExpMBL',expected_windows])
        csvoutwriter.writerow(['NumMBL',MBL])
        csvoutwriter.writerow(['ProbMBL','{:.2%}'.format(prob_MBL)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumMBL <5km', MBL_5])
        csvoutwriter.writerow(['% MBL <5km', '{:.2%}'.format(prob_MBL_5)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumMBL <10km', MBL_10])
        csvoutwriter.writerow(['% MBL <10km','{:.2%}'.format(prob_MBL_10)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumMBL <5km (vs Enc)', MBL_5_enc])
        csvoutwriter.writerow(['% MBL <5km (vs Enc)', '{:.2%}'.format(prob_MBL_5_enc)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumMBL <10km (vs Enc)', MBL_10_enc])
        csvoutwriter.writerow(['% MBL <10km (vs Enc)','{:.2%}'.format(prob_MBL_10_enc)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumMBL <20km (vs Enc)', MBL_20_enc])
        csvoutwriter.writerow(['% MBL <20km (vs Enc)','{:.2%}'.format(prob_MBL_20_enc)])

    if 'KMLgen' in result:
        kml = simplekml.Kml()
        KMLfile = OUTPUTFOLDER + '\KML' + outfiletag +'.kml'
        #print '\nCreating KML file - ' + KMLfile
        if 'SingleBurstGen' in result:
            #print 'Writing Single Burst Locations to KML' 
            with open(SBLfile, 'r') as csvfile:
                next(csvfile)
                filereader = csv.reader(csvfile)
                folSBL = kml.newfolder(name='Single Burst Locations - '+ str(MEOLUT))
                folEnc = kml.newfolder(name = 'Encoded Locations - '+ str(MEOLUT))
                for row in filereader:            
                    pntSBL = folSBL.newpoint(coords=[(float(row[8]),float(row[7]),float(row[9]))], 
                        description = 'Single Burst Solution \nBeacon = ' + row[2] + '\n\nTimeSolutionAdded = ' + row[0] + '\nTimeFirst = ' +row[5] + '\nTimeLast = ' +row[6] + 
                        '\nMEOLUT = ' + row[4] + '\nGT_Error = ' + row[16] + '\nEnc_Error = ' + row[17] +
                        '\nNum of Bursts = ' + row[10] + '\nNum of Packets = ' +row[11] +'\nDOP = ' + row[12] + 
                        '\nEHE = ' + row[13]
                        )
                    # name=str(row[0][11:19])
                    pntSBL.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                    pntSBL.style.iconstyle.icon.href = icon_list['white_dot']
        if 'EncLocGen' in result:
            #print 'Writing Encoded Locations to KML'
            with open(SBLfile, 'r') as csvfile:
                next(csvfile)
                filereader = csv.reader(csvfile)
                folEnc = kml.newfolder(name = 'Encoded Locations - '+ str(MEOLUT))                
                for row in filereader:
                    if row[17] != '':  
                        pntEnc = folEnc.newpoint(coords=[(float(row[15]),float(row[14]))], 
                            description = 'Encoded Location - Beacon = ' + row[2] + '\n\nTimeSolutionAdded = ' + row[0] + '\nLat,Long = (' + row[14] + ', ' +row[15] + ')'  
                            )
                        pntEnc.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                        pntEnc.style.iconstyle.icon.href = icon_list['little_E']
                        pntEnc.style.iconstyle.scale = 0.8
                        pntEnc.style.labelstyle.color = '00ff0000'  # Red
                    #pnt.snippet.content = 'this is content'
                    #print row[0],row[7],row[8]
        with open(MBLfile, 'r') as csvfile:
            next(csvfile)
            filereader = csv.reader(csvfile)
            folMBL = kml.newfolder(name='Multi Burst Locations - '+ str(MEOLUT))
            for row in filereader:            
                pntMBL = folMBL.newpoint(coords=[(float(row[8]),float(row[7]),float(row[9]))], 
                    description = 'Multi Burst Location - Beacon = ' + row[2] + '\n\nTimeSolutionAdded = ' + row[0] + '\nTimeFirst = ' +row[5] + '\nTimeLast = ' +row[6] + 
                    '\nMEOLUT = ' + row[4] + '\nGT_Error = ' + row[16] + '\nEnc_Error = ' + row[17] + 
                    '\nNum of Bursts = ' + row[10] + '\nNum of Packets = ' +row[11] +'\nDOP = ' + row[12] + 
                    '\nEHE = ' + row[13]
                    )
                pntMBL.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                pntMBL.style.iconstyle.icon.href = icon_list['little_M']
                pntMBL.style.labelstyle.color = 'ff0000ff'  # Red
                #pnt.snippet.content = 'this is content'
                #print row[0],row[7],row[8]
    

    
    if 'LEOgen' in result:
        LEOinputfile = UPLOADFOLDER +'\\' + kwargs['LEOGEO_file']
        #print 'Reading LEO file - ' + LEOinputfile
        #print 'Writing LEO bursts to KML'
        LEOoutfile = OUTPUTFOLDER + '\LEO' + outfiletag + '.csv'
        df = pd.read_excel(LEOinputfile, index_col = 'AddTime') #, parse_dates = True)
        df = df[(df.BcnId15 == BeaconID)]
        if df.empty: 
            print((LEOinputfile + ' - did not contain any data that matched'))    
        else:
            dfLEO = df[df.Orbit.notnull()]
            dfLEO_loc = dfLEO[dfLEO.A_Lat.notnull()]
            dfLEO_loc.to_csv(LEOoutfile)
            with open(LEOoutfile, 'r') as csvfile:
                filereader = csv.reader(csvfile)
                next(csvfile)
                fol_LEO = kml.newfolder(name='LEO Locations - '+ str(MEOLUT))
                for row in filereader:            
                    pnt_LEO = fol_LEO.newpoint(coords=[(float(row[22]),float(row[21]))], 
                        description = 'LEO Location \nBeacon = ' + row[15] + '\n\nA_Tca = ' + row[23] + '\nMCCTime = ' + row[0] + '\n\nLUT = ' + row[2] + '\nSat = ' + row[3] +
                        '\nOrbit = ' + str(int(float(row[4]))) + '\n\nNominal = ' + row[73] +  
                        '\nNum of Points = ' +row[18] + '\nA_Cta =' + row[24] + '\nA_prob = ' +row[17] + '\nSolId = ' + row[1]  
                        )   
                    pnt_LEO.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                    pnt_LEO.style.iconstyle.icon.href = icon_list['little_L']
                    #pnt_LEO.style.iconstyle.icon.href = 'file://C:/Users/Jesse/Documents/Programming/Python/MEO_Input_Processor/MEO_Input_Processor_v2_w_KML/icon35.png'
                    pnt_LEO.style.iconstyle.scale = 0.7
                    pnt_LEO.style.labelstyle.color = 'ffff0000'  # Red

    kml.save(CSVoutfolder + '\KML_' + csvoutfilename + '.kml')

def parse_results(result, MEOList): 
    if result.get('Location', False): 
        Location = result['Location']
    else: Location = 'NA'
    if result.get('UseBeaconID') == "UseRefBeacon": 
        BeaconID = ReferenceBeacons[result.get("refbeacon")]['beaconId']
        BeaconQuery = BeaconID
        Lat_GT = ReferenceBeacons[result.get("refbeacon")]['beaconLat']
        Long_GT = ReferenceBeacons[result.get("refbeacon")]['beaconLon']
        Location = result.get("refbeacon")
    else:
        if result.get('beaconID', False):
            BeaconID = result['beaconID']
            BeaconQuery = '%' + BeaconID +'%' 
        else:
            BeaconID = 'All'
            BeaconQuery = '%'
            
        if 'beaconLat' in result and result['beaconLat'] != '':
            Lat_GT = float(result['beaconLat'])
        if 'beaconLon' in result and result['beaconLon'] != '':
            Long_GT = float(result['beaconLon'])
        else: 
            Lat_GT = None
            Long_GT = None

    
    MEO_dist = []
    for MEO in MEOList:
        MEO_dist.append(haversine([Lat_GT,Long_GT,MEOLUTLoc[MEO][0],MEOLUTLoc[MEO][1]]))

    return BeaconQuery, BeaconID, Lat_GT, Long_GT, Location, MEO_dist

def MSSQL_analysis(result, MEOLUTList, TimeStart, TimeEnd, config_dict=False, Lat_GT=0, Long_GT=0, Location='', **kwargs):
    OUTPUTFOLDER, approot, servername, databasename =  config_dict["OUTPUTFOLDER"], config_dict["approot"], config_dict["servername"], config_dict["oppsdatabase"]
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, autocommit=True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit=True)
    if MEOLUTList==None: MEOLUTList = MEOList
    BeaconQuery, BeaconID, Lat_GT, Long_GT, Location, MEO_dist = parse_results(result,MEOLUTList)
    sql_query = ('SELECT * FROM '
                    'InputMEOSolution ' 
                    'WHERE ' 
                    'TimeSolutionGenerated between ? AND ? '
                    'AND '
                    'BcnId15 LIKE ? '
                    )
    params=[TimeStart, TimeEnd, BeaconQuery]

    df = pd.read_sql_query(sql_query,conn, index_col = 'timesolutionadded', params=params)
    df_data = []
    for MEO in MEOLUTList:
        df_data.append(filter1(df,'sourceid',MEO))
    dfMEO = pd.concat(df_data)
    if len(MEOLUTList) > 1:
        MEOLUT = None
        MEOStr = ", ".join([str(MEO) for MEO in MEOList])
    else: 
        MEOLUT = MEOList[0]
        MEOStr = MEOLUTName[MEOLUT]

    #    parse_dates=['timefirst','timelast', 'timesolutiongenerated','timesolutionadded'])
    #df = pd.DataFrame(cursor.fetchall())
    #df.columns = pd.DataFrame(np.matrix(cursor.description))[0]
    df2 = dfMEO[['datatype','bcnid15','bcnid30','sourceid','timefirst','timelast','latitude',
        'longitude','altitude','numbursts','numpackets','dop','expectedhorzerror']]
    df3 = df2.sort_index().ix[TimeStart:TimeEnd]
    #df3 = df2[(df2.BcnId15 == BeaconID)]
    dfSB = df3[(df3.datatype == 3)] 
    dfMB = df3[(df3.datatype == 0)] 
    if df3.empty: 
        print("Data Frame is empty after filtering out Beacon ID = " + BeaconID)
        return None, { 'MEOLUT': MEOLUT,
                        'TimeStart': TimeStart,
                        'TimeEnd': TimeEnd,
                        'Beacon': BeaconQuery,
                      }
    
    lat_fun = lambda hexin: bcn.beacon(hexin).lat
    lon_fun = lambda hexin: bcn.beacon(hexin).lon
    dfSB['Enc_Lat'] = dfSB['bcnid30'].apply(lat_fun)
    dfSB['Enc_Lon'] = dfSB['bcnid30'].apply(lon_fun)
    dfMB['Enc_Lat'] = dfMB['bcnid30'].apply(lat_fun)
    dfMB['Enc_Lon'] = dfMB['bcnid30'].apply(lon_fun)
    
    df_SBL = singleburst_loc(dfSB,Lat_GT,Long_GT,MEOLUT)
    SBL = len(df_SBL)
    df5 = df_SBL[df_SBL.Error_GT < 5] if not df_SBL.empty else df_SBL
    df5_enc = df_SBL[df_SBL.Error_Enc < 5] if not df_SBL.empty else df_SBL
    df10 = df_SBL[df_SBL.Error_GT < 10] if not df_SBL.empty else df_SBL
    df10_enc = df_SBL[df_SBL.Error_Enc < 10] if not df_SBL.empty else df_SBL
    df20_enc = df_SBL[df_SBL.Error_Enc < 20] if not df_SBL.empty else df_SBL

    timefirst = df3.timefirst.min()
    timelast = df3.timelast.max()
    timediff = timelast - timefirst

    SBL_5 = len(df5)
    SBL_5_enc = len(df5_enc)
    SBL_10 = len(df10)
    SBL_10_enc = len(df10_enc)
    SBL_20_enc = len(df20_enc)

    error_SBL = df_SBL.Error_GT if not df_SBL.empty else df_SBL # not used currently

    expected_bursts = int(timediff/pd.Timedelta(seconds = 50))
    prob_SBL = float(SBL)/expected_bursts if expected_bursts != 0 else 0
    prob_SBL_5 =float(SBL_5)/SBL if SBL !=0 else 0
    prob_SBL_5_enc =float(SBL_5_enc)/SBL if SBL !=0 else 0
    prob_SBL_10 = float(SBL_10)/SBL if SBL !=0 else 0
    prob_SBL_10_enc = float(SBL_10_enc)/SBL if SBL !=0 else 0
    prob_SBL_20_enc = float(SBL_20_enc)/SBL if SBL !=0 else 0

    ## Multi Burst (Windowed) Section
    window_time = 20 #minutes - no longer used since now just look for change in TimeFirst
    window_span = pd.Timedelta(minutes = window_time)
    expected_windows = math.ceil(timediff/window_span)

    df_MBL = multiburst_loc(dfMB, Lat_GT, Long_GT, MEOLUT, window_span)
    df_MBL5 = df_MBL[df_MBL.Error_GT < 5] if not df_MBL.empty else df_MBL
    df_MBL5_enc = df_MBL[df_MBL.Error_Enc < 5] if not df_MBL.empty else df_MBL
    df_MBL10 = df_MBL[df_MBL.Error_GT < 10] if not df_MBL.empty else df_MBL
    df_MBL10_enc = df_MBL[df_MBL.Error_Enc < 10] if not df_MBL.empty else df_MBL
    df_MBL20_enc = df_MBL[df_MBL.Error_Enc < 20] if not df_MBL.empty else df_MBL

    MBL = len(df_MBL)
    MBL_5 = len(df_MBL5)
    MBL_5_enc = len(df_MBL5_enc)
    MBL_10 = len(df_MBL10)
    MBL_10_enc = len(df_MBL10_enc)
    MBL_20_enc = len(df_MBL20_enc)

    error_MBL = df_MBL.Error_GT if not df_MBL.empty else df_MBL # not used currently

    prob_MBL = float(MBL)/expected_windows if expected_windows != 0 else 0
    prob_MBL_5 =float(MBL_5)/MBL if MBL !=0 else 0
    prob_MBL_5_enc =float(MBL_5_enc)/MBL if MBL !=0 else 0
    prob_MBL_10 = float(MBL_10)/MBL if MBL !=0 else 0
    prob_MBL_10_enc = float(MBL_10_enc)/MBL if MBL !=0 else 0
    prob_MBL_20_enc = float(MBL_20_enc)/MBL if MBL !=0 else 0
    

    outfiletag = '_{}_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}'.format(BeaconID,TimeStart,TimeEnd)
    SBLfile = os.path.join(OUTPUTFOLDER, 'SBL' + str(MEOLUT) + outfiletag +'.csv')
    MBLfile = os.path.join(OUTPUTFOLDER, 'MBL' + str(MEOLUT) + outfiletag +'.csv')
    OUTfile = os.path.join(OUTPUTFOLDER, 'OUT' + str(MEOLUT) + outfiletag +'.csv')
    LEOGEO_file = os.path.join(OUTPUTFOLDER, 'LEO' + outfiletag + '.csv')
    RCC_Output_file = os.path.join(OUTPUTFOLDER, 'RCC' + outfiletag + '.csv')
    #outfilenamelist = list()
    outfilelist = OrderedDict()
    outfilelist[OUTfile] = 'Output Summary'
    outfilelist[SBLfile] = 'Single Burst Solutions'
    outfilelist[MBLfile] = 'Multi Burst Solutions'




    
    if 'KMLgen' in result: 
        KMLfile = os.path.join(OUTPUTFOLDER, 'KML' + outfiletag +'.kml')
        Mapfile = os.path.join('/MapTest?KML=' + KMLfile).replace("\\","/")
        outfilelist[KMLfile] = 'KML File Output'
        outfilelist[Mapfile] = 'MapIt'
    df_SBL.to_csv(os.path.join(approot,SBLfile))
    df_MBL.to_csv(os.path.join(approot,MBLfile))
    #OrderedDict(reversed(list(outfilelist.items())))
    #outfilelist.append(SBLfile)
    #outfilelist.append(MBLfile)
    #outfilelist.append(OUTfile)


    with open(os.path.join(approot,OUTfile), 'w', newline="") as csvfile:
        csvoutwriter = csv.writer(csvfile, delimiter=',',
                                quoting=csv.QUOTE_MINIMAL)
        csvoutwriter.writerow(['MEOLUT', MEOStr])
        csvoutwriter.writerow(['MEOLUT_ID', MEOLUT])
        csvoutwriter.writerow(['BeaconID',BeaconID])
        csvoutwriter.writerow(['Location',Location])
        csvoutwriter.writerow(['TimeStart',TimeStart])
        csvoutwriter.writerow(['TimeEnd',TimeEnd])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['Ground Truth Lat',Lat_GT])
        csvoutwriter.writerow(['Ground Truth Long',Long_GT])
        csvoutwriter.writerow(['Distance From MEOLUT',MEO_dist]) #'{:.2f}'.format(MEO_dist)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['Time First Burst','{:%Y-%m-%d %H:%M:%S}'.format(timefirst)])    
        csvoutwriter.writerow(['Time Last Burst', '{:%Y-%m-%d %H:%M:%S}'.format(timelast)])
        csvoutwriter.writerow(['Time Span', timediff])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['SINGLE BURST LOCATIONS'])
        csvoutwriter.writerow(['ExpSBL',expected_bursts])
        csvoutwriter.writerow(['NumSBL',SBL])
        csvoutwriter.writerow(['ProbSBL','{:.2%}'.format(prob_SBL)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumSBL <5km', SBL_5])
        csvoutwriter.writerow(['% SBL <5km', '{:.2%}'.format(prob_SBL_5)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumSBL <10km', SBL_10])
        csvoutwriter.writerow(['% SBL <10km', '{:.2%}'.format(prob_SBL_10)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumSBL <5km (vs Enc)', SBL_5_enc])
        csvoutwriter.writerow(['% SBL <5km (vs Enc)', '{:.2%}'.format(prob_SBL_5_enc)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumSBL <10km (vs Enc)', SBL_10_enc])
        csvoutwriter.writerow(['% SBL <10km (vs Enc)', '{:.2%}'.format(prob_SBL_10_enc)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumSBL <20km (vs Enc)', SBL_20_enc])
        csvoutwriter.writerow(['% SBL <20km (vs Enc)', '{:.2%}'.format(prob_SBL_20_enc)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['MULTIPLE BURST LOCATIONS'])
        csvoutwriter.writerow(['Window Period', window_span])
        csvoutwriter.writerow(['ExpMBL',expected_windows])
        csvoutwriter.writerow(['NumMBL',MBL])
        csvoutwriter.writerow(['ProbMBL','{:.2%}'.format(prob_MBL)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumMBL <5km', MBL_5])
        csvoutwriter.writerow(['% MBL <5km', '{:.2%}'.format(prob_MBL_5)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumMBL <10km', MBL_10])
        csvoutwriter.writerow(['% MBL <10km','{:.2%}'.format(prob_MBL_10)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumMBL <5km (vs Enc)', MBL_5_enc])
        csvoutwriter.writerow(['% MBL <5km (vs Enc)', '{:.2%}'.format(prob_MBL_5_enc)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumMBL <10km (vs Enc)', MBL_10_enc])
        csvoutwriter.writerow(['% MBL <10km (vs Enc)','{:.2%}'.format(prob_MBL_10_enc)])
        csvoutwriter.writerow([])
        csvoutwriter.writerow(['NumMBL <20km (vs Enc)', MBL_20_enc])
        csvoutwriter.writerow(['% MBL <20km (vs Enc)','{:.2%}'.format(prob_MBL_20_enc)])

    if 'KMLgen' in result:
        #print '\nCreating KML file'
        kml = simplekml.Kml()
        if Lat_GT != 0:
            firstrad = 5000
            secondrad = 10000
            folEnc = kml.newfolder(name = 'Ground Truth - '+ str(MEOLUT))                
            polycircle1 = polycircles.Polycircle(latitude=Lat_GT,
                                    longitude=Long_GT,
                                    radius=firstrad,
                                    number_of_vertices=36)            
            pol1 = kml.newpolygon(name="5km",
                                         outerboundaryis=polycircle1.to_kml())
            pol1.style.polystyle.color = \
                simplekml.Color.changealphaint(100, simplekml.Color.green)
            # Second region

            polycircle2outer = polycircles.Polycircle(latitude=Lat_GT,
                                    longitude=Long_GT,
                                    radius=secondrad,
                                    number_of_vertices=36)            

            pol2 = kml.newpolygon(name="10km",
                                         outerboundaryis=polycircle2outer.to_kml(),
                                         innerboundaryis = polycircle1.to_kml())
            pol2.style.polystyle.color = \
                simplekml.Color.changealphaint(100, simplekml.Color.yellow)
            pntEnc = folEnc.newpoint(
                name = 'Ground Truth',
                coords=[(Long_GT,Lat_GT)], 
                description = 'Lat,Long = (' + str(Lat_GT) + ', ' + str(Long_GT) + ')'  
                )
            pntEnc.style.iconstyle.icon.href = icon_list['little_L']
            pntEnc.style.iconstyle.scale = 0.8
            pntEnc.style.labelstyle.color = '00ff0000'  # Red
        if 'SingleBurstGen' in result:
            with open(os.path.join(approot,SBLfile), 'r') as csvfile:
                next(csvfile)
                filereader = csv.reader(csvfile)
                folSBL = kml.newfolder(name='Single Burst Locations - '+ str(MEOLUT))
                folEnc = kml.newfolder(name = 'Encoded Locations - '+ str(MEOLUT))
                for row in filereader:            
                    pntSBL = folSBL.newpoint(
                        name = row[0],
                        coords=[(float(row[8]),float(row[7]),float(row[9]))], 
                        description = 'Single Burst Solution \nBeacon = ' + row[2] + '\nLat,Long,Alt = ' + row[7] + 
                        ', ' + row[8] + ', ' + row[9] + 
                        '\nTimeSolutionAdded = ' + row[0] + '\nTimeFirst = ' +row[5] + '\nTimeLast = ' +row[6] + 
                        '\nMEOLUT = ' + row[4] + '\nGT_Error = ' + row[16] + '\nEnc_Error = ' + row[17] +
                        '\nNum of Bursts = ' + row[10] + '\nNum of Packets = ' +row[11] +'\nDOP = ' + row[12] + 
                        '\nEHE = ' + row[13]
                        )
                    # name=str(row[0][11:19])
                    pntSBL.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                    pntSBL.style.iconstyle.icon.href = icon_list['little_L']
        if 'EncLocGen' in result:
            with open(os.path.join(approot,MBLfile), 'r') as csvfile:
                next(csvfile)
                filereader = csv.reader(csvfile)
                folEnc = kml.newfolder(name = 'Encoded Locations - '+ str(MEOLUT))                
                for row in filereader:
                    if row[17] != '':  
                        pntEnc = folEnc.newpoint(
                            name= row[0],
                            coords=[(float(row[15]),float(row[14]))], 
                            description = 'Encoded Location - Beacon = ' + row[2] + '\nTimeSolutionAdded = ' + 
                        row[0] + '\nLat,Long = (' + row[14] + ', ' +row[15] + ')'  
                            )
                        pntEnc.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                        pntEnc.style.iconstyle.icon.href = icon_list['little_E']
                        pntEnc.style.iconstyle.scale = 0.8
                        pntEnc.style.labelstyle.color = '00ff0000'  # Red
                        pntEnc.style.labelstyle.scale = 0 
        with open(os.path.join(approot,MBLfile), 'r') as csvfile:
            next(csvfile)
            filereader = csv.reader(csvfile)
            folMBL = kml.newfolder(name='Multi Burst Locations - '+ str(MEOLUT))
            for row in filereader:            
                pntMBL = folMBL.newpoint(
                    name=row[0],
                    coords=[(float(row[8]),float(row[7]),float(row[9]))], 
                    description = 'Multi Burst Location - Beacon = ' + row[2] + '\nLat,Long,Alt = ' + row[7] + 
                    ', ' + row[8] + ', ' + row[9] + '\nTimeSolutionAdded = ' + row[0] + '\nTimeFirst = ' + 
                    row[5] + '\nTimeLast = ' +row[6] + 
                    '\nMEOLUT = ' + row[4] + '\nGT_Error = ' + row[16] + '\nEnc_Error = ' + row[17] + 
                    '\nNum of Bursts = ' + row[10] + '\nNum of Packets = ' +row[11] +'\nDOP = ' + row[12] + 
                    '\nEHE = ' + row[13]
                    )
                pntMBL.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                pntMBL.style.iconstyle.icon.href = icon_list['little_M']
                pntMBL.style.iconstyle.scale = 0.8 
                pntMBL.style.labelstyle.color = 'ff0000ff'  # Red
                pntMBL.style.labelstyle.scale = 0 
        if 'LEOGen' in result:
            outfilelist[LEOGEO_file] = 'LEO Solutions'
            sql_query = ('SELECT b.AddTime, a.* from Lut406Solution a, inputmessage b '
                'WHERE a.InMsgId = b.InMsgId '
                'AND '
                'Orbit <> ? '  #this gets LEO solutions
                'AND '
                'A_Tca between ? AND ? '
                'AND '
                'BcnId15 LIKE ? '
                )
            params=['Null',TimeStart, TimeEnd, BeaconQuery]
            df = pd.read_sql_query(sql_query,conn, index_col = 'addtime', params=params)
            #df = df[(df.BcnId15 == BeaconID)]
            dfLEO_loc = df[df['a_lat'] != 'NULL']
            if df.empty: 
                print('query did not find any data that matched')    
            else:
                #dfLEO = df[df.Orbit.notnull()]

                dfLEO_loc.to_csv(os.path.join(approot,LEOGEO_file))
                with open(os.path.join(approot,LEOGEO_file), 'r') as csvfile:
                    filereader = csv.reader(csvfile)
                    next(csvfile)
                    fol_LEO = kml.newfolder(name='LEO Locations')
                    for row in filereader:            
                        pnt_LEO = fol_LEO.newpoint(coords=[(float(row[22]),float(row[21]))], 
                            description = 'LEO Location \nBeacon = ' + row[15] + '\n' + '\nLat,Long = ' + 
                            row[21] + ', ' + row[22] + 
                            '\n\nA_Tca = ' + row[23] + '\nMCCTime = ' + row[0] + '\n\nLUT = ' + row[2] + '\nSat = ' + row[3] +
                            '\nOrbit = ' + str(int(float(row[4]))) + '\n\nNominal = ' + row[73] +  
                            '\nNum of Points = ' +row[18] + '\nA_Cta =' + row[24] + '\nA_prob = ' +row[17] + '\nSolId = ' + row[1]  
                            )   
                        pnt_LEO.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                        pnt_LEO.style.iconstyle.icon.href = icon_list['little_L']
                        #pnt_LEO.style.iconstyle.icon.href = 'file://C:/Users/Jesse/Documents/Programming/Python/MEO_Input_Processor/MEO_Input_Processor_v2_w_KML/icon35.png'
                        pnt_LEO.style.iconstyle.scale = 0.7
                        pnt_LEO.style.labelstyle.color = 'ffff0000'  # Red
        if 'OutputSolution' in result:
            outfilelist[RCC_Output_file] = 'RCC Output Solutions'
            sql_query = (' '
                #'declare @bcnid as varchar(15) '
                #'declare @bcnid2 as varchar(17) '
                #'set @bcnid= ? '
                #'set @bcnid2= "%" + @bcnid + "%" '
                'SELECT b.AddTime, b.AlertSiteSolId, b.TimeFirst, b.TimeLast,b.Tca, a.MsgName, '
                'b.SolReal, b.EncReal, b.AlertMsgState, c.ComSiteName, c.DestMcc, '
                'b.PrevSarNameList, b.CurSarNameList, b.SourceId,b.SourceId2, b.EncLat, '
                'b.EncLon, b.Latitude, b.Longitude, b.A_Lat, b.A_Lon, b.B_Lat, b.B_Lon, '
                'a.TableName, a.InMsgId, b.SourceNameRccMsg, b.BcnId15, b.RegBcnId15, '
                'b.SatelliteIds, b.Sat, c.SitNum, b.ASiteDuration  '
                'FROM OutputMessage a, OutSolution b, OutputProcess c '
                'WHERE '
                'b.TimeFirst > ? '
                'AND ' 
                'b.TimeLast < ? '
                'AND '
                'b.BcnId15 like ? '
                'AND (b.OutMsgId=a.OutMsgId AND c.OutMsgId=a.OutMsgId) '                
                )
            params=[TimeStart, TimeEnd, BeaconQuery]
            df = pd.read_sql_query(sql_query,conn, params=params)
            #df = df[(df.BcnId15 == BeaconID)]
            if df.empty: 
                print('query did not find any RCC output data that matched')    
            else:
                #dfLEO = df[df.Orbit.notnull()]
                dfRCC_loc = df[df.a_lat.notnull()]
                dfRCC_loc.to_csv(os.path.join(approot,RCC_Output_file))
                with open(os.path.join(approot,RCC_Output_file), 'r') as csvfile:
                    filereader = csv.reader(csvfile)
                    next(csvfile)
                    fol_RCC = kml.newfolder(name='RCC Output Locations')
                    for row in filereader:  
                        if row[18]:
                            pnt_RCC = fol_RCC.newpoint(coords=[(float(row[19]),float(row[18]))], 
                                description = 'RCC Solution \nBeacon = ' + row[27] + '\n' 
                                '\nLat,Long = {0:.2f}'.format(float(row[18])) + ',{0:.2f}'.format(float(row[19])) +
                                '\nAddTime = ' + row[1] + '\nAlertSiteSolId = ' + row[2] +
                                '\nMsgName = ' + row[6] + '\n\nLUT = ' + row[14] + '\nSat = ' 
                                )   
                            pnt_RCC.timespan.begin = row[1][:10] + 'T' + row[1][11:19]
                            pnt_RCC.style.iconstyle.icon.href = icon_list['green_arrow']
                            #pnt_LEO.style.iconstyle.icon.href = 'file://C:/Users/Jesse/Documents/Programming/Python/MEO_Input_Processor/MEO_Input_Processor_v2_w_KML/icon35.png'
                            pnt_RCC.style.iconstyle.scale = 0.7
                            pnt_RCC.style.labelstyle.color = 'FFFFFF'  # Red
            
        kml.save(os.path.join(approot,KMLfile))
    return OUTfile, outfilelist

def MSSQL_burst(arg_dict, config_dict, **kwargs):
    servername, databasename, OUTPUTFOLDER, approot = config_dict["servername"], config_dict["oppsdatabase"], config_dict["OUTPUTFOLDER"], config_dict["approot"]
    
    beaconIDstring = arg_dict.get('beaconID', "%")
    TimeSpan = arg_dict.get('EndTime') - arg_dict.get('StartTime')
    num_bursts = TimeSpan.total_seconds() / 50
    filetimetag = datetime.strftime(datetime.utcnow(),"%Y%m%d_%H%M%S")
    ref_flag = False
    filelist = list()
    MEOnamelist = list()
    for MEOLUT in arg_dict['MEOLUTList']:
        for ant_i in ant_list:
            if arg_dict.get('UseBeaconID') == "UseRefBeacon": 
                ref_flag = True
                if arg_dict.get('refbeacon') == 'FL-HI-Ref': 
                    beaconIDstring = ReferenceBeacons[MEOLUTref[MEOLUT]]['beaconId']
                else: 
                    beaconIDstring = ReferenceBeacons[arg_dict.get("refbeacon")]['beaconId']
            else:
                beaconIDstring = arg_dict.get('beaconID', "%")
            outpackets = find_packets(servername, databasename,beaconIDstring, arg_dict['StartTime'],arg_dict['EndTime'], MEOLUT, ant_i, **kwargs) # sat 
            num_packets_found = len(outpackets)
            percent_packets = (num_packets_found/num_bursts)*100
            plot_packets(outpackets, MEOLUT, ant_i,arg_dict['StartTime'],arg_dict['EndTime'], num_packets_found, percent_packets)
        filename = os.path.normpath(os.path.join(OUTPUTFOLDER, str(MEOLUT) + '_' + filetimetag + '_output.png'))
        filelist.append(filename)
        MEOnamelist.append(MEOLUTName[MEOLUT])
        plt.savefig(os.path.join(approot, filename)) #, bbox_inches='tight')
        plt.clf()
        plt.cla()
    return filelist

def MEOLUT_alarms(StartTime, EndTime, servername = 'localhost', databasename = 'mccoperational', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    odbc.lowercase = True
    query_params = [StartTime, EndTime]
    sql_query = ('SELECT * from MeolutAlarms '
        'WHERE '
        'AddTime BETWEEN ? AND ? '
    )
    df = pd.read_sql_query(sql_query,conn, index_col = 'msgtime', params=query_params)
    df.sort_index().ix[StartTime:EndTime]

    dfClosedlist = df.alarmid[df.alarmtimeon.isnull()].tolist()
    dfClosed = df[df.alarmid.isin(dfClosedlist)]
     #list of closed alarmes between start and end time
    closedalarms = dfClosed.alarmid.unique().tolist()    
    #list of open alarms as of end time
    dfOpen = df[~df.alarmid.isin(dfClosedlist)]

    openalarms = dfOpen.alarmid.unique().tolist()
    numalarms = len(openalarms)
    alarmlist = []
    for alarm in openalarms:    
        alarms = {
            'alarmid': int(dfOpen[(dfOpen.alarmid == alarm)].iloc[0].alarmid),
            'meolutname': dfOpen[(dfOpen.alarmid == alarm)].iloc[0].meolutname,
            'alarmtext': dfOpen[(dfOpen.alarmid == alarm)].iloc[0].alarmtext,
            'openat': dfOpen[(dfOpen.alarmid == alarm)].iloc[0].alarmtimeon,
            'stillopen': dfOpen[(dfOpen.alarmid == alarm)].iloc[-1].alarmtimeon
        }
        alarmlist.append(alarms)
    closedalarmlist = []
    for alarm in closedalarms:    
        alarms = {
            'alarmid': int(dfClosed[(dfClosed.alarmid == alarm)].iloc[0].alarmid),
            'meolutname': dfClosed[(dfClosed.alarmid == alarm)].iloc[0].meolutname,
            'alarmtext': dfClosed[(dfClosed.alarmid == alarm)].iloc[0].alarmtext,
            'openat': dfClosed[(dfClosed.alarmid == alarm)].iloc[0].alarmtimeon,
            'closedate': dfClosed[(dfClosed.alarmid == alarm) & (dfClosed.alarmtimeon.isnull())].iloc[0].alarmtimeoff
            
        }
        closedalarmlist.append(alarms)
    return alarmlist, closedalarmlist, numalarms

def MEOLUT_status(StartTime, EndTime, servername = 'localhost', databasename = 'mccoperational', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit=True)
    #StartTime = StartTime - timedelta(days=5) ### REMOVE this when you have data that is more current
    query_params = [StartTime, EndTime]
    sql_query = ('SELECT * from MeolutStatus '
        'WHERE '
        'AddTime BETWEEN ? AND ? '
    )
    df = pd.read_sql_query(sql_query,conn, index_col = 'msgtime', params=query_params)
    df.sort_index().ix[StartTime:EndTime]
    if df.empty: 
        HI = {'component': 'N/A',
            'msgtime': 'N/A',
            'status': 'N/A',
            }
        FL = {'component': 'N/A',
            'msgtime': 'N/A',
            'status': 'N/A',
            }
        return HI, FL
        #raise Exception('no status messages in window between start and endtime')
    else:
        dfHIcurrentmsgnum = int(df[(df.meolutid == 3385)].iloc[-1].msgnum)
        dfFLcurrentmsgnum = int(df[(df.meolutid == 3669)].iloc[-1].msgnum)
        dfHI = df[(df.meolutid == 3385) & (df.msgnum == dfHIcurrentmsgnum)]
        dfFL = df[(df.meolutid == 3669) & (df.msgnum == dfFLcurrentmsgnum)]
        statusHIlist = []
        statusFLlist = []
        statusHI = OrderedDict
        statusFL = OrderedDict
        for item, row in dfHI.iterrows():
            statusHI = {
                'component': row['component'],
                'msgtime': item,
                'status': int(row['status']),
                }
            statusHIlist.append(statusHI)
        for item, row in dfFL.iterrows():
            statusFL = {
                'component': row['component'],
                'msgtime': item,
                'status': int(row['status']),
                }
            statusFLlist.append(statusFL)
    return statusHIlist, statusFLlist

def MEOLUT_percent(StartTime, EndTime, servername = 'localhost', databasename = 'MccTestLGM', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit=True)
    c = conn.cursor()
    def get_packets(BeaconID, MEOLUT, Antenna, StartTime, EndTime):
        query_params = [BeaconID, MEOLUT,  Antenna, StartTime, EndTime]
        sql_query = ('SELECT COUNT(*) from MeolutPackets '
            'WHERE '
            'BcnId15 like ? '
            'AND '
            'MeolutId like ? '
            'AND ' 
            'AntennaId like ? '
            'AND '
            'UplinkTOADate between ? AND ? '
             )
        c.execute(sql_query, query_params)
        numpackets = c.fetchone()[0]
        return numpackets

    TimeSpan = EndTime - StartTime
    expected_bursts = TimeSpan.total_seconds() / 50
    antlist = list(range(1,7))
    percentdict = defaultdict(dict)

    beaconIDstring = "ADDC002%"
    for ant in ant_list:
        numpackets = get_packets(beaconIDstring, 3669, ant, StartTime,EndTime)
        percentdict['FL'][ant] = round((numpackets / expected_bursts) * 100,2)
    beaconIDstring = "AA5FC00%"
    for ant in ant_list:
        numpackets = get_packets(beaconIDstring, 3385, ant, StartTime,EndTime)
        percentdict['HI'][ant] = round((numpackets / expected_bursts) * 100,2)
    return percentdict

def Open_Sites(servername = 'localhost', databasename = 'MccTestLGM', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit=True)
    c = conn.cursor()
    params = ['N']
    sql_query = ('SELECT alertsitenum, bcnid15, midname, '
        'complat, complon, opentime, lastupdtime, numpasses, '
        'numsol, numleogeosol, nummeosol, numdopsol, numdoasol '
        ' from AlertSiteSum '
        'WHERE '
        'Closed = ? '
        )
    c.execute(sql_query, params)
    return c.fetchall()

def alertsitesum_query(sitenum, OUTPUTFOLDER, approot,servername = 'localhost', databasename = 'MccTestLGM', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit=True)
    c = conn.cursor()
    params = [sitenum]
    sql_query = ('SELECT alertsitenum, bcnid15, midname, '
        'complat, complon, opentime, lastupdtime, numpasses, '
        'numsol, numleogeosol, nummeosol, numdopsol, numdoasol '
        ' from AlertSiteSum '
        'WHERE '
        'alertsitenum = ? '
        )
    c.execute(sql_query, params)
    return c.fetchall()

def alertsitesol_query(sitenum, OUTPUTFOLDER, approot,servername = 'localhost', databasename = 'MccTestLGM', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit=True)
    c = conn.cursor()
    params = [sitenum]
    sql_query = ('select alertsitesolid, inputdatatype, bcnid15, framesync, '
        'complat, complon, sitfunc, gentime, addtime, sourceid, sourcename, '
        'sourcemccname, numbursts, numpackets, numsatellites, dop, latitude, '
        'longitude, a_lat, a_lon, MatchDistance, AlertMsgState, ExpectedHorzError, Sat, Tca '
        'from AlertSiteSol where '
        'AlertSiteNum = ? '
        'order by gentime '
        )
    c.execute(sql_query, params)
    insols = c.fetchall()
    KMLfile = False
    if "makeKML" in kwargs:
        if kwargs.get("makeKML"):
            KMLfile = os.path.join(OUTPUTFOLDER, 'KML_Input_site_' + sitenum +'.kml')
            kml = simplekml.Kml()
            fol_RCC = kml.newfolder(name='Input Locations')
            for row in insols:  
                        if (row[16] != 'NULL') or row[18]:
                            if row[16] != 'NULL':
                                pnt_RCC = fol_RCC.newpoint(
                                    coords=[(float(row[17]),float(row[16]))], 
                                    description = 'MEO Solution \nBeacon = ' + str(row[2]) + '\n' 
                                    '\nLat,Long = {0:.4f}'.format(float(row[16])) + ',{0:.4f}'.format(float(row[17])) +
                                    '\nAddTime = ' + str(row[8]) + '\nAlertSiteSolId = ' + str(int(row[0])) +
                                    '\nAlertMsgName = ' + str(row[21]) + '\n\nSource = ' + str(row[10]) + 
                                    '\nNumBursts = ' + str(int(row[12])) + '\nNumPackets = ' + str(int(row[13])) +
                                    '\nNumSats = ' + str(int(row[14])) + '\nDOP = ' + str(row[15]) + 
                                    '\nEHE = ' + str(row[22])
                                    )
                                pnt_RCC.style.iconstyle.icon.href = icon_list['circle_M']
                                pnt_RCC.style.iconstyle.scale = 0.5
                            elif row[18] :
                                pnt_RCC = fol_RCC.newpoint(
                                    coords=[(float(row[19]),float(row[18]))], 
                                    description = 'LEO Solution \nBeacon = ' + str(row[2]) + '\n' 
                                    '\nLat,Long = {0:.4f}'.format(float(row[18])) + ',{0:.4f}'.format(float(row[19])) +
                                    '\nAddTime = ' + str(row[8]) + '\nAlertSiteSolId = ' + str(int(row[0])) +
                                    '\nAlertMsgName = ' + str(row[21]) + '\n\nSource = ' + str(row[10]) + 
                                    '\nSat = ' + str(row[23]) + '\nTCA = ' + str(row[24])
                                    )
                                pnt_RCC.style.iconstyle.icon.href = icon_list['circle_L']
                                pnt_RCC.style.iconstyle.scale = 0.8
                            pnt_RCC.timespan.begin = str(row[8])[:10] + 'T' + str(row[8])[11:19]
                            pnt_RCC.style.labelstyle.color = 'FFFFFF'              
            kml.save(os.path.join(approot,KMLfile))
    return insols, KMLfile

def outsol_query(sitenum, OUTPUTFOLDER, approot, servername = 'localhost', databasename = 'MccTestLGM', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, autocommit=True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit=True)
    c = conn.cursor()
    params = [sitenum]
    sql_query = (' '
        #'declare @bcnid as varchar(15) '
        #'declare @bcnid2 as varchar(17) '
        #'set @bcnid= ? '
        #'set @bcnid2= "%" + @bcnid + "%" '
        'SELECT b.AddTime, b.AlertSiteSolId, b.TimeFirst, b.TimeLast, b.Tca, a.MsgName, '
        'b.SolReal, b.EncReal, b.AlertMsgState, c.ComSiteName, c.DestMcc, '
        'b.PrevSarNameList, b.CurSarNameList, b.SourceId,b.SourceId2, b.EncLat, '
        'b.EncLon, b.Latitude, b.Longitude, b.A_Lat, b.A_Lon, b.B_Lat, b.B_Lon, '
        'a.TableName, a.InMsgId, b.SourceNameRccMsg, b.BcnId15, b.RegBcnId15, '
        'b.SatelliteIds, b.Sat, c.SitNum, b.ASiteDuration  '
        'FROM OutputMessage a, OutSolution b, OutputProcess c '
        'WHERE '
        'b.alertsitenum = ? '
        'AND (b.OutMsgId=a.OutMsgId AND c.OutMsgId=a.OutMsgId) '
        'order by addtime '                 
        )
    c.execute(sql_query, params)
    outsols = c.fetchall()
    KMLfile = False
    if "makeKML" in kwargs:
        if kwargs.get("makeKML"):
            KMLfile = os.path.join(OUTPUTFOLDER, 'KML_RCC_site_' + sitenum +'.kml')
            kml = simplekml.Kml()
            fol_RCC = kml.newfolder(name='RCC Output Locations')
            for row in outsols:
                if ((row[17] is not None) and (row[17] != 'NULL')) or ((row[19] is not None) and (row[19] != 'NULL')):
                    if (row[17] is not None) and (row[17] != 'NULL'):
                        pnt_RCC = fol_RCC.newpoint(coords=[(float(row[18]),float(row[17]))], 
                            description = 'RCC Solution \nBeacon = ' + str(row[26]) + '\n' 
                            '\nLat,Long = {0:.4f}'.format(float(row[17])) + ',{0:.4f}'.format(float(row[18])) +
                            '\nAddTime = ' + str(row[0]) + '\nAlertSiteSolId = ' + str(int(row[1])) +
                            '\nMsgName = ' + str(row[5]) + '\n\nLUT = ' + str(int(row[13])) + '\nSats = ' + str(row[28])
                            )
                    if (row[19] is not None) and (row[19] != 'NULL'):
                        pnt_RCC = fol_RCC.newpoint(coords=[(float(row[20]),float(row[19]))], 
                            description = 'RCC Solution \nBeacon = ' + str(row[26]) + '\n' 
                            '\nLat,Long = {0:.4f}'.format(float(row[19])) + ',{0:.4f}'.format(float(row[20])) +
                            '\nAddTime = ' + str(row[0]) + '\nAlertSiteSolId = ' + str(int(row[1])) +
                            '\nMsgName = ' + str(row[5]) + '\n\nLUT = ' + str(int(row[13])) + '\nSat = ' + str(row[29]) 
                            )
                    pnt_RCC.timespan.begin = str(row[0])[:10] + 'T' + str(row[0])[11:19]
                    pnt_RCC.style.iconstyle.scale = 0.9
                    pnt_RCC.style.labelstyle.color = 'FFFFFF'  
                    if row[5] == 'MEOFirstAlertDOA':
                        pnt_RCC.style.iconstyle.icon.href = icon_list['One']
                    elif row[5] == '406BlownCompDoppler':
                        pnt_RCC.style.iconstyle.icon.href = icon_list['red_cross']
                    elif row[5] == 'MEOBlownCompDOA':
                        pnt_RCC.style.iconstyle.icon.href = icon_list['red_cross']
                    elif row[5] == 'MEONocrDOA':
                        pnt_RCC.style.iconstyle.icon.href = icon_list['green_arrow']
                    elif row[5] == 'MEOUpdatedNoCompDOA':
                        pnt_RCC.style.iconstyle.icon.href = icon_list['yellow_pin']
                    elif row[5] == 'MEOUpdatedCompDOA':
                        pnt_RCC.style.iconstyle.icon.href = icon_list['M']
                    elif row[5] == '406UpdatedCompDoppler':
                        pnt_RCC.style.iconstyle.icon.href = icon_list['L']
                    else:
                        pnt_RCC.style.iconstyle.icon.href = icon_list['red_pin']

               
            kml.save(os.path.join(approot,KMLfile))
    return outsols, KMLfile

def both_kml(sitenum, OUTPUTFOLDER, approot, servername = 'localhost', databasename = 'MccTestLGM', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, autocommit=True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit=True)
    c = conn.cursor()
    params = [sitenum]
    sql_query = (' '
        #'declare @bcnid as varchar(15) '
        #'declare @bcnid2 as varchar(17) '
        #'set @bcnid= ? '
        #'set @bcnid2= "%" + @bcnid + "%" '
        'SELECT b.AddTime, b.AlertSiteSolId, b.TimeFirst, b.TimeLast, b.Tca, a.MsgName, '
        'b.SolReal, b.EncReal, b.AlertMsgState, c.ComSiteName, c.DestMcc, '
        'b.PrevSarNameList, b.CurSarNameList, b.SourceId,b.SourceId2, b.EncLat, '
        'b.EncLon, b.Latitude, b.Longitude, b.A_Lat, b.A_Lon, b.B_Lat, b.B_Lon, '
        'a.TableName, a.InMsgId, b.SourceNameRccMsg, b.BcnId15, b.RegBcnId15, '
        'b.SatelliteIds, b.Sat, c.SitNum, b.ASiteDuration  '
        'FROM OutputMessage a, OutSolution b, OutputProcess c '
        'WHERE '
        'b.alertsitenum = ? '
        'AND (b.OutMsgId=a.OutMsgId AND c.OutMsgId=a.OutMsgId) '
        'order by addtime '                 
        )
    c.execute(sql_query, params)
    outsols = c.fetchall()
    KMLfile = False
    KMLfile = os.path.join(OUTPUTFOLDER, 'KML_site_' + sitenum +'.kml')
    Mapfile = os.path.join('/MapTest?KML=' + KMLfile).replace("\\","/")
    kml = simplekml.Kml()
    fol_RCC = kml.newfolder(name='RCC Output Locations')
    for row in outsols:

        if ((row[17] is not None) and (row[17] != 'NULL')) or ((row[19] is not None) and (row[19] != 'NULL')):
            if (row[17] is not None) and (row[17] != 'NULL'):
                pnt_RCC = fol_RCC.newpoint(coords=[(float(row[18]),float(row[17]))], 
                    description = 'RCC Solution \nBeacon = ' + str(row[26]) + '\n' 
                    '\nLat,Long = {0:.4f}'.format(float(row[17])) + ',{0:.4f}'.format(float(row[18])) +
                    '\nAddTime = ' + str(row[0]) + '\nAlertSiteSolId = ' + str(int(row[1])) +
                    '\nMsgName = ' + str(row[5]) + '\n\nLUT = ' + str(int(row[13])) + '\nSats = ' + str(row[28])
                    )
            if (row[19] is not None) and (row[19] != 'NULL'):
                pnt_RCC = fol_RCC.newpoint(coords=[(float(row[20]),float(row[19]))], 
                    description = 'RCC Solution \nBeacon = ' + str(row[26]) + '\n' 
                    '\nLat,Long = {0:.4f}'.format(float(row[19])) + ',{0:.4f}'.format(float(row[20])) +
                    '\nAddTime = ' + str(row[0]) + '\nAlertSiteSolId = ' + str(int(row[1])) +
                    '\nMsgName = ' + str(row[5]) + '\n\nLUT = ' + str(int(row[13])) + '\nSat = ' + str(row[29]) 
                    )
            pnt_RCC.timespan.begin = str(row[0])[:10] + 'T' + str(row[0])[11:19]
            pnt_RCC.style.iconstyle.scale = 0.9
            pnt_RCC.style.labelstyle.color = 'FFFFFF'  
            if row[5] == 'MEOFirstAlertDOA':
                pnt_RCC.style.iconstyle.icon.href = icon_list['One']
            elif row[5] == '406BlownCompDoppler':
                pnt_RCC.style.iconstyle.icon.href = icon_list['red_cross']
            elif row[5] == 'MEOBlownCompDOA':
                pnt_RCC.style.iconstyle.icon.href = icon_list['red_cross']
            elif row[5] == 'MEONocrDOA':
                pnt_RCC.style.iconstyle.icon.href = icon_list['green_arrow']
            elif row[5] == 'MEOUpdatedNoCompDOA':
                pnt_RCC.style.iconstyle.icon.href = icon_list['yellow_pin']
            elif row[5] == 'MEOUpdatedCompDOA':
                pnt_RCC.style.iconstyle.icon.href = icon_list['M']
            elif row[5] == '406UpdatedCompDoppler':
                pnt_RCC.style.iconstyle.icon.href = icon_list['L']
            else:
                pnt_RCC.style.iconstyle.icon.href = icon_list['red_pin']

    ## Now get MEOLUT input 
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, autocommit=True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit=True)
    c = conn.cursor()
    params = [sitenum]
    sql_query = ('select alertsitesolid, inputdatatype, bcnid15, framesync, '
        'complat, complon, sitfunc, gentime, addtime, sourceid, sourcename, '
        'sourcemccname, numbursts, numpackets, numsatellites, dop, latitude, '
        'longitude, a_lat, a_lon, MatchDistance, AlertMsgState, ExpectedHorzError, Sat, Tca '
        'from AlertSiteSol where '
        'AlertSiteNum = ? '
        'order by gentime '
        )
    c.execute(sql_query, params)
    insols = c.fetchall()
    fol_MEO = kml.newfolder(name='Input Locations')
    for row in insols:  
                if ((row[16] is not None) and (row[16] != 'NULL')) or ((row[18] is not None) and (row[18] != 'NULL')):
                    if ((row[16] is not None) and (row[16] != 'NULL')):
                        pnt_MEO = fol_MEO.newpoint(coords=[(float(row[17]),float(row[16]))], 
                            description = 'MEO Solution \nBeacon = ' + str(row[2]) + '\n' 
                            '\nLat,Long = {0:.4f}'.format(float(row[16])) + ',{0:.4f}'.format(float(row[17])) +
                            '\nAddTime = ' + str(row[8]) + '\nAlertSiteSolId = ' + str(int(row[0])) +
                            '\nAlertMsgName = ' + str(row[21]) + '\n\nSource = ' + str(row[10]) + 
                            '\nNumBursts = ' + str(int(row[12])) + '\nNumPackets = ' + str(int(row[13])) +
                            '\nNumSats = ' + str(int(row[14])) + '\nDOP = ' + str(row[15]) + 
                            '\nEHE = ' + str(row[22])
                            )
                        pnt_MEO.style.iconstyle.icon.href = icon_list['little_M']
                        pnt_MEO.style.iconstyle.scale = 0.5
                    elif ((row[18] is not None) and (row[18] != 'NULL')):
                        pnt_MEO = fol_MEO.newpoint(coords=[(float(row[19]),float(row[18]))], 
                            description = 'LEO Solution \nBeacon = ' + str(row[2]) + '\n' 
                            '\nLat,Long = {0:.4f}'.format(float(row[18])) + ',{0:.4f}'.format(float(row[19])) +
                            '\nAddTime = ' + str(row[8]) + '\nAlertSiteSolId = ' + str(int(row[0])) +
                            '\nAlertMsgName = ' + str(row[21]) + '\n\nSource = ' + str(row[10]) + 
                            '\nSat = ' + str(row[23]) + '\nTCA = ' + str(row[24])
                            )
                        pnt_MEO.style.iconstyle.icon.href = icon_list['little_L']
                        pnt_MEO.style.iconstyle.scale = 0.8
                    pnt_MEO.timespan.begin = str(row[8])[:10] + 'T' + str(row[8])[11:19]
                    pnt_MEO.style.labelstyle.color = 'FFFFFF'                          
    kml.save(os.path.join(approot,KMLfile))
    return KMLfile, Mapfile
def MSSQL_beacon_analysis(result, MEOLUTList, TimeStart, TimeEnd, config_dict, gt_file = False, Lat_GT=0, Long_GT=0, Location='', **kwargs):
    servername, databasename, OUTPUTFOLDER, approot = config_dict["servername"], config_dict["oppsdatabase"], config_dict["OUTPUTFOLDER"], config_dict["approot"]
    filetimetag = datetime.strftime(datetime.utcnow(),"%Y%m%d_%H%M%S")

    filelist = OrderedDict()
    imglist = []
    if MEOLUTList==None: MEOLUTList = MEOList
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, autocommit=True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit=True)

    BeaconQuery, BeaconID, Lat_GT, Long_GT, Location, MEO_dist = parse_results(result,MEOLUTList)
    MEOList_str = '_'.join([str(MEO) for MEO in MEOLUTList])
    outfiletag = '_{}_{}_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}'.format(BeaconID,MEOList_str, TimeStart,TimeEnd)   
    #Generate stats on a df (<5km, 10, 20 , median, quintiles)  
    def stats(df,dist_list, q_list):
        ''' Returns a tuple of total num solutions in df, # within dist_list[0], % within dist_list[0], etc, 
        median, number of burst within quintile[0], etc.  
        then mean and 95%
        '''
        distout = []
        perout = []
        outlist = []
        totnum = df.shape[0]
        outlist.append(totnum)
        ave = round(df[errorname].mean(),3)
        median = round(df[errorname].quantile(.5),3)
        win_5km = round(safe_div(df[df[errorname]<5].shape[0],totnum),3)
        win_10km = round(safe_div(df[df[errorname]<10].shape[0],totnum),3)
        q95 = round(df[errorname].quantile(.95),3)
        outlist.append(ave)
        for dist in dist_list:
            distout.append(df[df[errorname]<dist].shape[0])
            perout.append(round(safe_div(df[df[errorname]<dist].shape[0],totnum),2))
        distlistout = [val for pair in zip(distout, perout) for val in pair] #interleaves two lists of same length
        outlist.extend(distlistout)
        qout = df[errorname].quantile(q_list)
        qout = [round(q,2) for q in qout]

        outlist.extend(qout)
        return outlist, ave, median,  q95, win_5km, win_10km

    #Return dataframe where a certain satellite is used
    def sat_find(df, sat):
        dfsat = df[df[satidsname].str.contains(sat)]
        return dfsat

    def get_cmap(n, name='brg'):
        '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
        RGB color; the keyword argument name must be a standard mpl colormap name.'''
        return plt.cm.get_cmap(name, n)

    def hist_cum_plot(df,list1,maxrange,title, textstr,legendhandles,textstr2, **args):
        # add filter out of where df[errorname] == None 
        df = df[df[errorname].notnull()]
        bin_range = np.arange(0, maxrange+2)
        dfall = np.clip(df[errorname],bin_range[0],bin_range[-1])
        count, division = np.histogram(dfall, bins = bin_range)
        ax1 = dfall.hist(bins=division, stacked = True, color = 'grey')
        ax1.set_ylabel('Number of Locations Produced')
        ax1.set_xlabel('Location Error (km)')
        cumulative = np.cumsum(count).astype(np.float64)
        x = np.linspace(0,bin_range[-1],cumulative.size)
        cumulative/=cumulative.max()
        cumulative*=100.
        ax2 = ax1.twinx()
        ax2.set_ylabel('Cumulative Error (%)')
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
        props2 = dict(boxstyle='round', facecolor='white', alpha=0.3)
        ax2.text(bin_range.mean(), 30, textstr, fontsize=10,
            verticalalignment='bottom', bbox = props)
        if textstr2:
            ax2.text(bin_range.mean(), 70, textstr2, fontsize=10,
                verticalalignment='center', bbox = props2)
        plt.plot(x,cumulative,'o-', color = 'black')
        cmap = get_cmap(len(list1)+1)
        plotdf = []
        #print 'len list1 ' + str(len(list1))

        # Loop below builds the cumulative error plots and arrays for stacked histogram
        if list1: 
            for i, df1 in enumerate(list1):
                df2 = np.clip(df1[errorname],bin_range[0],bin_range[-1])
                plotdf.append(df2)
                count, division = np.histogram(df2, bins = bin_range, range=(bin_range.min(),bin_range.max()))
                cumulative = np.cumsum(count).astype(np.float64)
                x = np.linspace(0,bin_range[-1],cumulative.size)
                cumulative/=cumulative.max()
                cumulative*=100.
                plt.plot(x,cumulative, color=cmap(i), linestyle='dashed', linewidth=2)
                ax2.legend(legendhandles, fontsize = 10, loc = 'right')
        else:
            df2 = np.clip(df[errorname],bin_range[0],bin_range[-1])
            plotdf.append(df2)
            count, division = np.histogram(df2, bins = bin_range, range=(bin_range.min(),bin_range.max()))
            cumulative = np.cumsum(count).astype(np.float64)
            x = np.linspace(0,bin_range[-1],cumulative.size)
            cumulative/=cumulative.max()
            cumulative*=100.
            plt.plot(x,cumulative, linestyle='dashed', linewidth=2)
            ax2.legend(legendhandles, fontsize = 10, loc = 'right')
            
        # This builds the df for stacked histogram and color list
        plotlist = []
        colors = []
        for i, df4 in enumerate(plotdf):
            plotlist.append(df4)
            colors.append(cmap(i))
        ax1.hist(plotlist, division, histtype='bar', stacked = True, 
                 color=colors, rwidth=0.85, alpha = 0.65) #, range = (0, 51)) 
                 #,range = (plotlist[1].min(),plotlist[1].max()))
        plt.title(title, fontsize = 14)
        ax1.set_xlim([bin_range[0],bin_range[-1]])
        ax2.set_ylim([0,100])
        #if plotmean: plt.axvline(df[errorname].mean(), color='gray', linestyle='dashed', linewidth=1)
        #if plotmedian: plt.axvline(df[errorname].median(), color='gray', linestyle='dashed', linewidth=1)
        return plt

    UseMCC = True
    if result.get('UseBeaconID') == 'SiteInput':
        bcn_or_site = 'Site'
        Sitenum = result.get('siteID')
    else:
        bcn_or_site = 'Beacon'
    dist = [5, 10, 20]
    q = [0.5, .75, .9, .95]
    errorname = 'Error_GT'

    ''' Define the column names for data below'''
    fieldname = OrderedDict()
    if UseMCC:
        fieldname['datatypename'] = 'datatype'
        fieldname['bcn15name'] = 'bcnid15'
        fieldname['bcn30name'] = 'bcnid30'
        fieldname['sourceidname'] = 'sourceid'
        fieldname['timefirstname'] = 'timefirst'
        fieldname['timelastname'] = 'timelast'
        fieldname['latname'] = 'latitude'
        fieldname['lonname'] = 'longitude'
        fieldname['altname'] = 'altitude'
        fieldname['numburstsname'] = 'numbursts'
        fieldname['numpacketsname'] = 'numpackets'
        fieldname['numsatsname'] = 'numsatellites'
        fieldname['dopname'] = 'dop'
        fieldname['cn0name'] = 'averagecn0'
        fieldname['ehename'] = 'expectedhorzerror'
        fieldname['satidsname'] = 'satelliteids'
       

    else:
        datatypename = 'dataUsed'
        errorname = 'locError_km'
        errorname = 'Error'
        numsatsname = 'nbSat'
        numburstsname = 'nbBursts'
        satidsname = 'listSatID'

    fieldlist = []
    for key, value in fieldname.items():
        fieldlist.append(value)
    sql_query_field_list = ", ".join(fieldlist)
    
    if bcn_or_site == 'Site':
        sql_query = ('declare @bcnid varchar(16) = ( '
                     'select top 1 BcnId15 From AlertSiteSum where '
                     'AlertSiteNum = ? '
                     'ORDER BY TimeLast desc) '
                     'SELECT ' + sql_query_field_list + ' FROM '
                     'InputMEOSolution '
                     'WHERE '
                     'BcnId15 = @bcnid AND '
                     'TimeFirst between ? AND ? '
                     )
        params=[Sitenum, TimeStart, TimeEnd]
    else:
        sql_query = ('SELECT ' + sql_query_field_list + ' FROM '
                     'InputMEOSolution ' 
                     'WHERE ' 
                     'TimeSolutionGenerated between ? AND ? '
                     'AND '
                     'BcnId15 LIKE ? '
                     )
        params=[TimeStart, TimeEnd, BeaconQuery]
    df = pd.read_sql_query(sql_query,conn, params= params) #, index_col = 'timesolutionadded', params=params)
    df_data = []
    for MEO in MEOLUTList:
        df_data.append(filter1(df,'sourceid',MEO))
    dfMEO = pd.concat(df_data)
    #Use only multiburst data type
    df_filter = filter1(dfMEO,fieldname['datatypename'],0)

    filterlist = []
    if result.get('filter1check',False):
        if result.get('filter1sel') == 'filter1ran':
            df_filter =  filter_range(df_filter, fieldname[result.get('filter1')], result.get('filter1rangelow',0), result.get('filter1rangehigh',100))
            filterlist.append(fieldname[result.get('filter1')] + ' between ' + result.get('filter1rangelow',0) + ' and ' + result.get('filter1rangehigh',100))
        else:
            df_filter = filter1(df_filter, fieldname[result.get('filter1')], result.get('filter1value',0))
            filterlist.append(fieldname[result.get('filter1')] + ' = ' + result.get('filter1value',0))
    if result.get('filter2check',False):
        if result.get('filter2sel') == 'filter2ran':
            df_filter =  filter_range(df_filter, fieldname[result.get('filter2')], result.get('filter2rangelow',0), result.get('filter2rangehigh',100))
            filterlist.append(fieldname[result.get('filter2')] + ' between ' + result.get('filter2rangelow',0) + ' and ' + result.get('filter2rangehigh',100))
        else:
            df_filter = filter1(df_filter, fieldname[result.get('filter2')], result.get('filter2value',0))
            filterlist.append(fieldname[result.get('filter2')] + ' = ' + result.get('filter2value',0))
    if result.get('filter3check',False):
        if result.get('filter3sel') == 'filter3ran':
            df_filter =  filter_range(df_filter, fieldname[result.get('filter3')], result.get('filter3rangelow',0), result.get('filter3rangehigh',100))
            filterlist.append(fieldname[result.get('filter3')] + ' between ' + result.get('filter3rangelow',0) + ' and ' + result.get('filter3rangehigh',100))
        else:
            df_filter = filter1(df_filter, fieldname[result.get('filter3')], result.get('filter3value',0))
            filterlist.append(fieldname[result.get('filter3')] + ' = ' + result.get('filter3value',0))
    if df_filter.empty: 
        print('no data ') 
        return BeaconID, None, None, None
    
    #dfout = sat_find(dfout1,'330') 
    #### Need to implement sat find
    
    # Fill in encoded locations
    lat_fun = lambda hexin: bcn.beacon(hexin).lat
    lon_fun = lambda hexin: bcn.beacon(hexin).lon
    df_filter['Enc_Lat'] = df_filter['bcnid30'].apply(lat_fun)
    df_filter['Enc_Lon'] = df_filter['bcnid30'].apply(lon_fun)

    # if GT value is passed (stationary) write Lat_GT, Long_GT and Error_GT to DF
    if (Lat_GT is not None) and (Long_GT is not None):
        df_filter['Lat_GT'],df_filter['Lon_GT'] = Lat_GT, Long_GT
        df_filter['Error_GT'] = df_filter[['latitude','longitude', 'Lat_GT','Lon_GT']].apply(haversine, axis = 1)
    elif gt_file:
        # If GT file is passed, read it, interpolate, write KML if passed, write Error_GT
        if gt_file[-3:] == 'csv': 
            df_gt = pd.read_csv(gt_file, index_col = 'time', parse_dates = ['time']) 
        else:
            df_gt = pd.read_excel(gt_file, index_col = 'time') 
        # add ability to read excel files 

        #gt_starttime = df_gt.index.min()
        #gt_endtime = df_gt.index.max()
        sol_starttime = df_filter[fieldname['timefirstname']].min()
        sol_endtime = df_filter[fieldname['timelastname']].max()
        df_gt = df_gt.iloc[::10]
        df_gt = df_gt.loc[df_gt.index > TimeStart ]#sol_starttime - timedelta(minutes=10)]
        df_gt = df_gt.loc[df_gt.index < TimeEnd] #sol_endtime + timedelta(minutes=10)]
        if result.get('KMLgen'):
            kml = simplekml.Kml()
            GT_fol = kml.newfolder(name='GT-Track')
            for row in df_gt.itertuples():
                GT_point = GT_fol.newpoint(
                name= 'GT-' + str(row[0]),
                coords=[(float(row[2]),float(row[1]))],
                description= str(row[0]) 
                )
                GT_point.timespan.begin = str(row[0])[:10] + 'T' + str(row[0])[11:19]
                #GT_point.style.iconstyle.icon.href = 'static/icons/blue_pog.png'
                GT_point.style.iconstyle.icon.href = icon_list['blue_dot']
                GT_point.style.labelstyle.scale = 0 
                GT_point.style.iconstyle.scale = 0.3
        def get_lat_lon_time(df,dateandtime):
            if dateandtime not in df.index:
                newrow = pd.DataFrame(data = [np.nan], index = [dateandtime])
                df = df.append(newrow)
            LON = pd.Series(index=df.index, data= df.lon.values).sort_index().interpolate(method='time')[dateandtime]
            LAT = pd.Series(index=df.index, data= df.lat.values).sort_index().interpolate(method='time')[dateandtime]
            return LAT, LON, dateandtime

        for index, row in df_filter.iterrows():
            lat, lon, timeat = get_lat_lon_time(df_gt,row['timelast'])
            df_filter.set_value(index,'Lat_GT', lat)
            df_filter.set_value(index,'Lon_GT', lon)
            #df_filter.set_value(index,'Time_GT', timeat)



        df_filter['Error_GT'] = df_filter[['Lat_GT','Lon_GT','latitude','longitude']].apply(haversine, axis = 1)
        if 'Enc_Lat' in df_filter.columns: 
            df_filter['Error_Enc_Loc_GT'] = df_filter[['Lat_GT','Lon_GT','Enc_Lat','Enc_Lon']].apply(haversine, axis = 1)
   
    #else write Error_GT is 'NA'
    else:
        df_filter['Error_GT'] = 0

    df_filter['Error_Enc'] = df_filter[['latitude','longitude','Enc_Lat','Enc_Lon']].apply(haversine, axis = 1)



    
    
    
    ### still need to add column for location error here

    # Need to write sols to file if checked or if you need to generate KML file
    if result.get('SolutionsOut',False) or result.get('KMLgen',False):
        Solutionfilename = os.path.normpath(os.path.join(OUTPUTFOLDER, filetimetag + '_Solutions.csv'))
        df_filter.to_csv(os.path.join(approot,Solutionfilename))
        filelist[Solutionfilename] = 'Histo/KML Solutions file'

    statsout, mean, median, q95, win_5km, win_10km = stats(df_filter,dist,q)

    ### This is for generating plots
    if result.get('histcum',False):
        textstr1 = 'Total Stats \n\nNum Locations = %.d\nmean = %.1f km\nmedian = %.1f km\n95%% = %.1f km\n\n%% within 5 km = %.1f%%\n%% within 10 km = %.1f%%'%(statsout[0], mean, median,  q95, 100*win_5km, 100*win_10km)# ' % (statsout[0])#\nmean=%.2f$\nmedian=%.2f$\n95=%.2f'%(statsout[0], mean, median, q95)
        legendhandles = ['all']

        dflist = []
        titleheader = []
        titlelist = []
        filtertext = None
        #Generate text box for filters
        if len(filterlist) > 0: 
            filtertextlist = ['Filters \n']
            for item in filterlist:
                filtertextlist.append(item)
            filtertext = '\n'.join(filtertextlist)
        
        #Building Plot Title 
        if result.get('Location'):
            titleheader.append(result.get('Location')+ ': ')
            titleheader.append(BeaconID + '\n')
        if (result.get('beaconLat') and result.get('beaconLon')): 
            titleheader.append('(' + result.get('beaconLat') + ', ' +result.get('beaconLon')+')')
        if result.get('UseBeaconID') == 'UseRefBeacon':
            titleheader.append('Ref Beacon: '+ result.get('refbeacon')+' - '+ BeaconID + '\n')
            titleheader.append('Location: (' + str(ReferenceBeacons[result.get('refbeacon')]['beaconLat']) + ', ' +str(ReferenceBeacons[result.get('refbeacon')]['beaconLat'])+')')
        titlelist.append(' '.join(titleheader))
        MEOListstring = ['MEOLUT(s): ']
        for MEO in MEOLUTList:
            MEOListstring.append(str(MEO))

        titlelist.append(' '.join(MEOListstring))

        #Need to get the field to vary and set it below
        if result.get('plotvary'):
            varyfield = fieldname[result.get('plotvaryby')]
            titlelist.append('Varying ' + varyfield)
            if varyfield == 'numsatellites':
                satrangediff = 1
                satrange = list(range(3,11,satrangediff)) # could be variable          
                for i in satrange:
                    if i == satrange[-1]:
                        dflist.append(filter_range(df_filter,varyfield,i,20))
                        legendhandles.append(varyfield + ': ' + str(i) + '+ ')
                    else:
                        dflist.append(filter1(df_filter,varyfield,i))
                        legendhandles.append(varyfield + ': ' + str(i))
            if varyfield == 'dop':
                doprangediff = 1
                doprange = list(range(0,7,doprangediff)) # could be variable 
                for i in doprange:
                    if i == doprange[-1]:
                        dflist.append(filter_range(df_filter,varyfield,i,100))
                        legendhandles.append(varyfield + ': ' + str(i) + '+ ')
                    else:
                        dflist.append(filter_range(df_filter,varyfield,i,i+doprangediff))
                        legendhandles.append(varyfield + ': ' + str(i) + ' - ' + str(i+doprangediff))
            if varyfield == 'expectedhorzerror':
                eherangediff = 2
                eherange = list(range(0,10,eherangediff)) # could be variable 
                for i in eherange:
                    if i == eherange[-1]:
                        dflist.append(filter_range(df_filter,varyfield,i,100))
                        legendhandles.append(varyfield + ': ' + str(i) + '+ ')
                    else:
                        dflist.append(filter_range(df_filter,varyfield,i,i+eherangediff))
                        legendhandles.append(varyfield + ': ' + str(i) + ' - ' + str(i+eherangediff))
            if varyfield == 'numbursts':
                numburstrangediff = 3
                numburstrange = [1, 2]
                numburstrange.extend(list(range(3,30,numburstrangediff))) # could be variable 
                for i in numburstrange:
                    if i == 1 or i == 2:
                        dflist.append(filter1(df_filter,varyfield,i))
                        legendhandles.append(varyfield + ': ' + str(i) )                    
                    elif i == numburstrange[-1]:
                        dflist.append(filter_range(df_filter,varyfield,i,100))
                        legendhandles.append(varyfield + ': ' + str(i) + '+ ')
                    else:
                        dflist.append(filter_range(df_filter,varyfield,i,i+numburstrangediff))
                        legendhandles.append(varyfield + ': ' + str(i) + ' - ' + str(i+numburstrangediff))
            if varyfield == 'numpackets':
                numpacketsrangediff = 10
                numpacketsrange = list(range(0,100,numpacketsrangediff)) # could be variable 
                for i in numpacketsrange:
                    if i == numpacketsrange[-1]:
                        dflist.append(filter_range(df_filter,varyfield,i,200))
                        legendhandles.append(varyfield + ': ' + str(i) + '+ ')
                    else:
                        dflist.append(filter_range(df_filter,varyfield,i,i+numpacketsrangediff))
                        legendhandles.append(varyfield + ': ' + str(i) + ' - ' + str(i+numpacketsrangediff))
            if varyfield == 'averagecn0':
                cn0rangediff = 2
                cn0range = list(range(30,50,cn0rangediff)) # could be variable 
                for i in cn0range:
                    if i == cn0range[-1]:
                        dflist.append(filter_range(df_filter,varyfield,i,100))
                        legendhandles.append(varyfield + ': ' + str(i) + '+ ')
                    else:
                        dflist.append(filter_range(df_filter,varyfield,i,i+cn0rangediff))
                        legendhandles.append(varyfield + ': ' + str(i) + ' - ' + str(i+cn0rangediff))


        title = "\n".join(titlelist)
        # range needs to be chosen correct for what field is varying - currently good for numsats 

        plt1 = plt.figure(figsize=(16, 9), dpi=400, facecolor='w', edgecolor='k')
        plt1 = hist_cum_plot(df_filter,dflist,50,title, textstr1,legendhandles, filtertext) 

        filename = os.path.normpath(os.path.join(OUTPUTFOLDER, 'histogram' + outfiletag +'_' + filetimetag + '.png'))
        imglist.append(filename)
        plt1.savefig(os.path.join(approot, filename)) #, bbox_inches='tight')
        plt.clf()
        plt.cla()
        plt.close('all')
    statsfile = os.path.normpath(os.path.join(OUTPUTFOLDER, 'out_stats_sum' + filetimetag + '_out_stats_sum.csv'))
    rw = []
    rw.extend(statsout)
    
    headerlist = []
    statslist = []
    headerlist.append(bcn_or_site)
    if bcn_or_site == 'Site':
        statslist.append(Sitenum)
    else:
        statslist.append(BeaconID)
    if result.get('Location'): 
        headerlist.append('Location')
        statslist.append(result.get('Location'))
    if (result.get('beaconLat') and result.get('beaconLon')): 
        headerlist.append('BeaconLat')
        headerlist.append('BeaconLon')
        statslist.append(result.get('beaconLat'))
        statslist.append(result.get('beaconLon'))

    MEOListstring = []
    for i, MEO in enumerate(MEOLUTList):
        headerlist.append('MEO-' + str(i+1))
        statslist.append(str(MEO))
        headerlist.append('MEO-' + str(i+1) + ' dist (km)')
        if MEO_dist[i] != None: 
            statslist.append(str(round(MEO_dist[i],1)))
        else:
            statslist.append('NA')
    
    for i, filter in enumerate(filterlist):
        headerlist.append('Filter-' + str(i+1))
        statslist.append(filter)


    #headrow = [','.join(headerlist)]
    headrow = []
    
    headrow2 = ['# locations','ave','# <5 km','% < 5 km','# < 10 km','% < 10 km','# < 20 km','% < 20 km','median (km)','75% (km)','90% (km)','95% (km)']
    headrow.extend(headerlist)
    headrow.extend(headrow2)

    statsrow = []
    statsrow.extend(statslist)
    statsrow.extend(rw)

    with open(os.path.join(approot, statsfile), 'a', newline="") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(headrow)
        csvwriter.writerow(statsrow)


    

    if result.get('KMLgen'): 
        KMLfile = os.path.join(OUTPUTFOLDER, 'KML' + filetimetag +'.kml')
        Mapfile = os.path.join('/MapTest?KML=' + KMLfile).replace("\\","/")
        filelist[KMLfile] = 'KML File Output'
        filelist[Mapfile] = 'MapIt'
        if not gt_file: 
            print('making kml')
            kml = simplekml.Kml()
        if (result.get('GTSource') == 'GTLatLon') and (result.get('beaconLat')) != '':
            firstrad = 5000
            secondrad = 10000
            folEnc = kml.newfolder(name = 'Ground Truth ')                
            polycircle1 = polycircles.Polycircle(latitude=Lat_GT,
                                    longitude=Long_GT,
                                    radius=firstrad,
                                    number_of_vertices=36)            
            pol1 = kml.newpolygon(name="5km",
                                         outerboundaryis=polycircle1.to_kml())
            pol1.style.polystyle.color = \
                simplekml.Color.changealphaint(100, simplekml.Color.green)
            # Second region

            polycircle2outer = polycircles.Polycircle(latitude=Lat_GT,
                                    longitude=Long_GT,
                                    radius=secondrad,
                                    number_of_vertices=36)            

            pol2 = kml.newpolygon(name="10km",
                                         outerboundaryis=polycircle2outer.to_kml(),
                                         innerboundaryis = polycircle1.to_kml())
            pol2.style.polystyle.color = \
                simplekml.Color.changealphaint(100, simplekml.Color.yellow)
            pntEnc = folEnc.newpoint(
                name = 'Ground Truth',
                coords=[(Long_GT,Lat_GT)], 
                description = 'Lat,Long = (' + str(Lat_GT) + ', ' + str(Long_GT) + ')'  
                )
            pntEnc.style.iconstyle.icon.href = icon_list['white_arrow']
            pntEnc.style.iconstyle.scale = 0.8
            pntEnc.style.labelstyle.color = '00ff0000'  # Red

        with open(os.path.join(approot,Solutionfilename), 'r') as csvfile:
            next(csvfile)
            filereader = csv.reader(csvfile)
            try: 
                kml
            except:
                kml = simplekml.Kml()
            folEnc = kml.newfolder(name = 'Encoded Locations')                
            for row in filereader:
                if (row[17] != 'NULL') and (row[17] is not None) and (row[17] != ''):  
                    pntEnc = folEnc.newpoint(
                        name= row[6],
                        coords=[(float(row[18]),float(row[17]))], 
                        description = 'Encoded Location - Beacon = ' + row[2] + '\nTimeLast = ' + 
                    row[6] + '\nLat,Long = (' + row[17] + ', ' +row[18] + ')'  
                        )
                    pntEnc.timespan.begin = row[6][:10] + 'T' + row[6][11:19]
                    pntEnc.style.iconstyle.icon.href = icon_list['circle_E']
                    pntEnc.style.iconstyle.scale = 0.8
                    pntEnc.style.labelstyle.color = '00ff0000'  # Red
                    pntEnc.style.labelstyle.scale = 0 
        with open(os.path.join(approot,Solutionfilename), 'r') as csvfile:
            next(csvfile)
            filereader = csv.reader(csvfile)
            folMBL = kml.newfolder(name='MEOLUT Locations')
            for row in filereader:            
                try: 
                    GT_error = '{0:.2f}'.format(float(row[21]))
                except: 
                    GT_error = 'NA' 
                try: 
                    Enc_error = '{0:.2f}'.format(float(row[22]))
                except: 
                    Enc_error = 'NA' 
                
                pntMBL = folMBL.newpoint(
                    name=row[6],
                    coords=[(float(row[8]),float(row[7]),float(row[9]))], 
                    description = 'Multi Burst Location - Beacon = ' + row[2] + '\nLat,Long,Alt = ' + row[7] + 
                    ', ' + row[8] + ', ' + row[9] + '\nTimeLast = ' + row[6] + '\nTimeFirst = ' + 
                    row[5] + '\nMEOLUT = ' + row[4] + '\nGT_Error = ' + GT_error + 
                    '\nEnc_Error = '+ Enc_error +  
                    '\nNum of Bursts = ' + row[10] + '\nNum of Packets = ' +row[11] +'\nNum Sats = ' + row[12] + 
                    '\nDOP = ' +row[13] + '\nAveCN0 = ' +row[14] + '\nEHE = ' + row[15] + '\nSats-' + row[16]

                    )
                pntMBL.timespan.begin = row[6][:10] + 'T' + row[6][11:19]
                pntMBL.style.iconstyle.icon.href = icon_list['little_M']
                pntMBL.style.iconstyle.scale = 0.4
                pntMBL.style.labelstyle.color = 'ff0000ff'  # Red
                pntMBL.style.labelstyle.scale = 0  

                if (result.get('ErrorLines') and (GT_error != 'NA')):
                    if 'Error Lines' not in [x.name for x in kml.containers]:
                        GT_loc_fol = kml.newfolder(name='Error Lines')
                    GT_errorline = GT_loc_fol.newlinestring(name='Error - ' + row[6])
                    GT_errorline.coords = [(float(row[8]),float(row[7]),float(row[9])),(float(row[20]), float(row[19]), 0)]
                    GT_errorline.timespan.begin = str(row[6])[:10] + 'T' + str(row[6])[11:19]
                    GT_errorline.style.iconstyle.icon.href = icon_list['blue_dot']
                    GT_errorline.style.labelstyle.scale = 0 

        kml.save(os.path.join(approot,KMLfile))
    return BeaconID, statsfile, imglist, filelist
    #for sat in us_sarsats:
    #    dfsat = sat_find(dfout1,str(sat))
    #    dfout = dfsat
    #    statsout, mean, median, q95, win_5km, win_10km = stats(dfout,dist,q)
    #    rw = [sat]
    #    rw.extend(statsout)
    #    with open('out_sat_stats_sum.csv', 'a') as csvfile:
    #        csvwriter = csv.writer(csvfile, delimiter=',')
    #        csvwriter.writerow(rw)
def MeoDataCollection(result, MEOLUTList, StartTime, EndTime, config_dict, zip_file = False , **kwargs):
    servername, databasename, OUTPUTFOLDER, approot = config_dict["servername"], config_dict["oppsdatabase"], config_dict["OUTPUTFOLDER"], config_dict["approot"]
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    UseMCC = True
    meoListString = "_".join([str(i) for i in MEOLUTList])
    placeholders = ",".join("?" * len(MEOLUTList))
    BeaconQuery, BeaconID, Lat_GT, Long_GT, Location, MEO_dist = parse_results(result,MEOLUTList)
    outfiletag = '_{}_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}'.format(BeaconID,StartTime,EndTime)
    outfile_dict = OrderedDict()
    
    if result.get('AllSiteSols',False):
        # Get and make all alertsitesols file
        sql_query = """\
            SELECT * FROM [MccMeoLutMonitor].[dbo].[AlertSiteSol] 
            WHERE TimeFirst > ? 
            AND AddTime < ?
            AND BcnId15 like ?

            """
        params = [StartTime, EndTime, BeaconQuery]
        c = conn.cursor()
        c.execute(sql_query, params)
        columns = [column[0] for column in c.description]
        out = c.fetchall()
        if out:
            allsols_file = os.path.join(OUTPUTFOLDER, 'all_alert_site_sols' + outfiletag +'.csv')
            outfile_dict[allsols_file] = 'All Alert Site Solutions'
            with open(os.path.join(approot,allsols_file), 'w', newline="") as csvfile:
                csvoutwriter = csv.writer(csvfile, delimiter=',',
                                        quoting=csv.QUOTE_MINIMAL)
                csvoutwriter.writerow(columns)
                for row in out:
                    csvoutwriter.writerow(row)

    if result.get('J1data',False):
        J1_header = ['BurstId', 'BcnId30','BcnId15','Received','FOA','FOAOff','TOA', 'TOAOff','CN0','BitRate', 'Ant','Sat','MEOLUT','BCH_Errors']
        # Get the J1 data or return blank file name 

        
        sql_query = """\
            SELECT 
            DbId as 'BurstId', BcnId30, BcnId15, AddTime as 'Received', 
            UplinkFOA as 'FOA', DownLinkFOAOffset as 'FOAOff', 
            dateadd(ns, UplinkTOANanoSecs, convert(datetime2, UplinkTOAdate)) as 'TOA',
            DownlinkTOAOffset as 'TOAOff', CarrierToNoise as 'CN0', BitRate, AntennaId as 'Ant', 
            SatId as 'Sat', MeolutId as 'MEOLUT', NumBCHErrs
            FROM [MccMeoLutMonitor].[dbo].[MeolutPackets] 
            WHERE 
            BcnId15 like ? AND
            UplinkTOADate between ? AND ? 
            AND
            MeolutId in (%s) 
            """ % placeholders
        params = [BeaconQuery, StartTime, EndTime]
        params.extend(MEOLUTList)
        c = conn.cursor()
        c.execute(sql_query, params)
        columns = [column[0] for column in c.description]
        out = c.fetchall()
        if out:
            J1_file = os.path.join(OUTPUTFOLDER, 'J1_' + meoListString + outfiletag +'.csv')
            outfile_dict[J1_file] = 'J1 - Raw Bursts'
            with open(os.path.join(approot,J1_file), 'w', newline="") as csvfile:
                csvoutwriter = csv.writer(csvfile, delimiter=',',
                                        quoting=csv.QUOTE_MINIMAL)
                csvoutwriter.writerow(columns)
                for row in out:
                    csvoutwriter.writerow(row)
            
        # write a second J1 file from zip if needed 
        if zip_file:
            J1_file_zip = os.path.join(OUTPUTFOLDER, 'J1_from_zip_' + meoListString + outfiletag +'.csv')
            outfile_dict[J1_file_zip] = 'J1 - Raw Bursts from zip file'
            filetypesearch = "TOA_FOA_DATA"
            country = "USA"
            for MEO in MEOLUTList:
                my_regex = file_search_regex(filetypesearch, country)
                zipmatches = find_file_inzip(zip_file, my_regex)
                burstlist = list()
                search_zip_output(MEO, zip_file, zipmatches, filetypesearch, J1_file_zip, approot, J1_header, country, beaconId)
        print('done making J1 file at ' + str(datetime.utcnow()))    

    if result.get('J2data',False):
        #J2 - Format - 
        sql_query = """\
            SELECT	SolId as 'Solution ID', 
                SourceId as 'LUT ID', 
                TimeFirst as 'Time of First Burst', 
                TimeLast as 'Time of Last Burst', 
                FileTime as 'Time Solution Sent', 
                BcnId15 as 'Beacon 15 Hex ID', 
                FreqBias/1000000 as 'Detection Frequency', 
                BcnId36 as 'Beacon 36 Hex ID', 
                NumBursts, NULL as 'Data Used', 
                SourceAntennaIds as 'Antenna IDs',
                NumPackets as 'Number of Packets used', 
                NumSatellites as 'Number of Satellites used', 
                SatelliteIds as 'Sat IDs', 
                DOP, 
                ExpectedHorzError as 'EHE',
                QualityFactor, 
                NULL as 'Location Methodology', 
                Latitude, 
                Longitude, 
                Altitude 
            FROM [MccMeoLutMonitor].[dbo].[InputMEOSolution]
            WHERE TimeLast > ? 
            AND TimeFirst < ?
            AND BCNID15 like ? 
            AND datatype = 0 
            AND SourceId in (%s)
            """ % placeholders
        params = [StartTime, EndTime, BeaconQuery]
        params.extend(MEOLUTList)
        c = conn.cursor()
        c.execute(sql_query, params)
        columns = [column[0] for column in c.description]
        out = c.fetchall()
        if out:
            J2_file = os.path.join(OUTPUTFOLDER, 'J2_' + meoListString + outfiletag +'.csv')
            outfile_dict[J2_file] = 'J2 - MEOLUT Solutions'
            with open(os.path.join(approot,J2_file), 'w', newline="") as csvfile:
                csvoutwriter = csv.writer(csvfile, delimiter=',',
                                        quoting=csv.QUOTE_MINIMAL)
                csvoutwriter.writerow(columns)
                for row in out:
                    csvoutwriter.writerow(row)

    if result.get('J3data',False):
        # Get and make J3 (schedule)
        sql_query = """\
            --J3 Format--MEO
            declare @starttime datetime, @endtime datetime
            select @starttime = ?
            select @endtime = ?
            select distinct	t.LutId as 'MEOLUT ID', 
                    t.AntennaId as 'Antenna ID', 
                    t.SatId as 'Sat ID', 
                    t.AOSStr as 'AOS_Time', 
                    t.LOSStr as 'LOS_Time', 
                    DATEDIFF(second,t.AOSStr,t.LOSStr)/60 as 'Duration', 
                    NULL as 'Azimuth at AOS',
                    NULL as 'Elevation at AOS', 
                    NULL as 'Azimuth at LOS', 
                    NULL as 'Elevation at LOS' 
            FROM [MccMeoLutMonitor].[dbo].[PassesTaken] t
            WHERE
                t.AntennaId <> 7 AND (t.AntennaId <> 8)
                AND ((@starttime between t.AOSStr and t.LOSStr) 
                    or (@endtime between t.AOSStr and t.LOSStr)
                    or (t.LOSStr between @starttime and @endtime) 
                    OR (t.AOSStr between @starttime and @endtime)
                    )
                    AND t.LutId in (%s)
                    order by aos_time
            """ % placeholders

        params = [StartTime, EndTime]
        params.extend(MEOLUTList)
        c = conn.cursor()
        c.execute(sql_query, params)
        columns = [column[0] for column in c.description]
        out = c.fetchall()
        if out:   
            J3_file = os.path.join(OUTPUTFOLDER, 'J3_' + meoListString + '_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}'.format(StartTime, EndTime) + '.csv')
            outfile_dict[J3_file] = 'J3 - MEOLUT Tracked Passes'
            with open(os.path.join(approot,J3_file), 'w', newline="") as csvfile:
                csvoutwriter = csv.writer(csvfile, delimiter=',', 
                                        quoting=csv.QUOTE_MINIMAL)
                csvoutwriter.writerow(columns)
                for row in out:
                    csvoutwriter.writerow(row)
    return outfile_dict, BeaconID

def api_meo_accuracy_all( config_dict, arg_dict, output_format = 'data_list'):
    servername, databasename, OUTPUTFOLDER, approot = config_dict["servername"], config_dict["oppsdatabase"], config_dict["OUTPUTFOLDER"], config_dict["approot"]
    conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    meoListString = "_".join([str(i) for i in arg_dict['MEOLUTList']])
    sql_query = """\
        select * FROM [MccMeoLutMonitor].[dbo].[MeolutRealTimeLocationMonitor]
        where AddTime between ? and ? 
        """
    params = [datetime.strftime(arg_dict.get('StartTime'), datetime_format), datetime.strftime(arg_dict.get('EndTime'), datetime_format)]
    params = [arg_dict.get('StartTime'),arg_dict.get('EndTime')]
    if arg_dict.get('MEOLUTList',False):
        placeholders = ",".join("?" * len(arg_dict.get('MEOLUTList')))
        sql_query += 'and LUT in ({})'.format(placeholders)
        params.extend(arg_dict.get('MEOLUTList'))        
    c = conn.cursor()
    c.execute(sql_query, tuple(params))
    columns = [column[0] for column in c.description]
    out = c.fetchall()
    if out:
        meoListString = "_".join([str(i) for i in arg_dict.get('MEOLUTList')])
        out_file_string = meoListString + '_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}.csv'.format(arg_dict.get('StartTime'), arg_dict.get('EndTime'))    
        output = sql_outputer(out, output_format, c,
                            approot = approot,  
                            OUTPUTFOLDER=OUTPUTFOLDER,
                            out_file_string= out_file_string,
                            ) 
        return output
    return None

def api_meo_ref_beacon_locations( arg_dict, config_dict, output_format = 'json'):
    servername, databasename, OUTPUTFOLDER, approot = config_dict["servername"], config_dict["oppsdatabase"], config_dict["OUTPUTFOLDER"], config_dict["approot"]
    conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    if arg_dict.get('MEOLUTList',False): 
        meoListString = "_".join([str(i) for i in arg_dict['MEOLUTList']])
        out_file_string = meoListString + '_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}.csv'.format(arg_dict.get('StartTime'), arg_dict.get('EndTime'))    
    sql_query = """\
        select * FROM [MccMeoLutMonitor].[dbo].[MeolutRefBeaconLocations]
        where AddTime between ? and ? 
        """
    params = [datetime.strftime(arg_dict.get('StartTime'), datetime_format), datetime.strftime(arg_dict.get('EndTime'), datetime_format)]
    params = [arg_dict.get('StartTime'),arg_dict.get('EndTime')]
    if arg_dict.get('MEOLUTList',False):
        placeholders = ",".join("?" * len(arg_dict.get('MEOLUTList')))
        sql_query += 'and MeolutId in ({})'.format(placeholders)
        params.extend(arg_dict.get('MEOLUTList'))        
    c = conn.cursor()
    cur = c.execute(sql_query, tuple(params))
    columns = [column[0] for column in c.description]
    out = list()
    for j in cur:
        out.append(j) 
    if out:
        out_file_string = '{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}.csv'.format(arg_dict.get('StartTime'), arg_dict.get('EndTime'))        
        output = sql_outputer(out, output_format, c,
                            approot = approot,  
                            OUTPUTFOLDER=OUTPUTFOLDER,
                            out_file_string= out_file_string,
                            ) 
        return output
    return None

def api_leo_lmdb( config_dict, arg_dict, output_format = 'data_list'):
    servername, databasename, OUTPUTFOLDER, approot = config_dict["servername"], config_dict["oppsdatabase"], config_dict["OUTPUTFOLDER"], config_dict["approot"]
    conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    leoListString = "_".join([str(i) for i in arg_dict['LEOLUTList']])
    columns = ['LUT','SAT','ORBIT','AOS','LOS','AzAOS','AzTCA','AzLOS','SCHEDULED','CONFLICT',
    'PassMissed','PassMissedReason','MissExcused','MissExcuseReason','MaxElavation','PassRcvdMCC',
    'INSPEC','Num406','NumINT','MccRcvd','PassSummaryReceived','TimeStamp']
    sql_query = """\
        select {} FROM [MccMeoLutMonitor].[dbo].[LMDB]
        where AOS between ? and ? 
        """.format(",".join(columns))
    params = [datetime.strftime(arg_dict.get('StartTime'), datetime_format), datetime.strftime(arg_dict.get('EndTime'), datetime_format)]
    params = [arg_dict.get('StartTime'),arg_dict.get('EndTime')]
    if arg_dict.get('LEOLUTList',False):
        placeholders = ",".join("?" * len(arg_dict.get('LEOLUTList')))
        sql_query += 'and LUT in ({})'.format(placeholders)
        params.extend(arg_dict.get('LEOLUTList'))        
    c = conn.cursor()
    c.execute(sql_query, tuple(params))
    columns = [column[0] for column in c.description]
    out = c.fetchall()
    if out:
        leoListString = "_".join([str(i) for i in arg_dict.get('LEOLUTList')])
        out_file_string = leoListString + '_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}.csv'.format(arg_dict.get('StartTime'), arg_dict.get('EndTime'))    
        output = sql_outputer(out, output_format, c,
                            approot = approot,  
                            OUTPUTFOLDER=OUTPUTFOLDER,
                            out_file_string= out_file_string,
                            ) 
        return output
    return None
    

def api_meo_schedule(MEOLUTList, StartTime, EndTime, output_format, config_dict):
    servername, databasename, OUTPUTFOLDER, approot = config_dict["servername"], config_dict["oppsdatabase"], config_dict["OUTPUTFOLDER"], config_dict["approot"]
    conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    meoListString = "_".join([str(i) for i in MEOLUTList])
    placeholders = ",".join("?" * len(MEOLUTList))
    sql_query = """\
        --J3 Format--MEO
        declare @starttime datetime, @endtime datetime
        select @starttime = ?
        select @endtime = ?
        select distinct	t.LutId as 'MEOLUT ID', 
                t.AntennaId as 'Antenna ID', 
                t.SatId as 'Sat ID', 
                t.AOSStr as 'AOS_Time', 
                t.LOSStr as 'LOS_Time', 
                DATEDIFF(second,t.AOSStr,t.LOSStr)/60 as 'Duration', 
                NULL as 'Azimuth at AOS',
                NULL as 'Elevation at AOS', 
                NULL as 'Azimuth at LOS', 
                NULL as 'Elevation at LOS' 
        FROM [MccMeoLutMonitor].[dbo].[PassesTaken] t
        WHERE
            t.AntennaId <> 7 AND (t.AntennaId <> 8)
            AND ((@starttime between t.AOSStr and t.LOSStr) 
                or (@endtime between t.AOSStr and t.LOSStr)
                or (t.LOSStr between @starttime and @endtime) 
                OR (t.AOSStr between @starttime and @endtime)
                )
                AND t.LutId in (%s)
                order by aos_time
        """ % placeholders

    params = [StartTime, EndTime]
    params.extend(MEOLUTList)
    c = conn.cursor()
    c.execute(sql_query, params)
    columns = [column[0] for column in c.description]
    out = c.fetchall()
    if out:
        meoListString = "_".join([str(i) for i in MEOLUTList])
        out_file_string='J3_' + meoListString + '_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}.csv'.format(StartTime, EndTime)    
        return sql_outputer(out, output_format, c,
                            approot = approot,  
                            OUTPUTFOLDER=OUTPUTFOLDER,
                            out_file_string= out_file_string,
                            )
        # if output_format == 'csv':   
        #     meoListString = "_".join([str(i) for i in MEOLUTList])
        #     J3_file = os.path.join(OUTPUTFOLDER, 'J3_' + meoListString + '_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}.csv'.format(StartTime, EndTime) )
        #     with open(os.path.join(approot,J3_file), 'w') as csvfile:
        #         csvoutwriter = csv.writer(csvfile, delimiter=',',
        #                                 quoting=csv.QUOTE_MINIMAL)
        #         csvoutwriter.writerow(columns)
        #         for row in out:
        #             csvoutwriter.writerow(row)
        #     return J3_file
        # if output_format == 'json':
        #     r = [dict((c.description[i][0], value) \
        #     for i, value in enumerate(row)) for row in out]
        #     return (r[0] if r else None) if one else r
        # else:
        #     outdata = [columns]
        #     for row in out:
        #         outdata.append(row)
        #     return outdata

def sql_outputer(outdata, output_format, c, one=False, **kwargs ):
    columns = [column[0] for column in c.description]
    if output_format == 'csv':   
        csv_out_file = os.path.join(kwargs.get('OUTPUTFOLDER') + kwargs.get('out_file_string'))
        with open(os.path.join(kwargs.get('approot'),csv_out_file), 'w', newline="") as csvfile:
            csvoutwriter = csv.writer(csvfile, delimiter=',',
                                    quoting=csv.QUOTE_MINIMAL)
            csvoutwriter.writerow(columns)
            for row in outdata:
                csvoutwriter.writerow(row)
        return csv_out_file
    if output_format == 'json':
        r = [dict((c.description[i][0], value) \
            for i, value in enumerate(row)) for row in outdata]
        return (r[0] if r else None) if one else r
    else:
        output_data = [columns]
        for row in outdata:
            output_data.append(row)
        return output_data

def api_meo_ref_beacon_accuracy(MEOLUT, StartTime, EndTime, arg_dict, config_dict, **kwargs):
    servername, databasename  = config_dict["servername"], config_dict["oppsdatabase"]
    timedelta_secs = (EndTime - StartTime).total_seconds()
    expected_locations = timedelta_secs/50.0
    if not kwargs.get('distlist',False):
        distlist = [2, 5, 10, 20]
        outdistdict = {}
    keylist = ['percent_less_than_'+str(dist)+'km' for dist in distlist]
    numlist = ['number_less_than_'+str(dist)+'km' for dist in distlist]
    RefBeacon = arg_dict.get('RefBeacon', MEOLUTref[MEOLUT])
    beacon = ReferenceBeacons[RefBeacon]
    conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    sql_query = """ Select Latitude, Longitude FROM [MccMeoLutMonitor].[dbo].[InputMeoSolution] 
        WHERE Datatype = 0 AND SourceId = ? 
        AND bcnId15 = ? 
        AND TimeLast between ? AND ? """
    params = [MEOLUT, beacon['beaconId'], StartTime, EndTime]
    c = conn.cursor()
    c.execute(sql_query, params)
    out = c.fetchall()
    output = {'SourceId': MEOLUT, 'RefBeacon': RefBeacon, 'StartTime': StartTime, 
                'EndTime': EndTime, 'beaconId': beacon['beaconId'], 'expected_locations': expected_locations,
                'beaconLat': beacon['beaconLat'], 'beaconLon': beacon['beaconLon']}
    if not out: 
        output.update({"mean": None, 
        "median": None, 
        "num_of_locations": 0, 
        "p75": None, 
        "p90": None, 
        "p95": None, 
        "percent_locations": 0})
        for key in keylist: 
            output.update({key: None})
        for num in numlist: 
            output.update({num: None})
        return output 
    else: 
        out_dict = [dict((c.description[i][0], value) \
            for i, value in enumerate(row)) for row in out]
        out_distlist = []
        num_of_locations = len(out)
        output.update({'num_of_locations': num_of_locations})
        for row in out_dict:
            out_distlist.append(haversine((row['latitude'],row['longitude'],beacon['beaconLat'],beacon['beaconLon'])))
        output.update({'p75': np.percentile(out_distlist, 75),
                        'p90': np.percentile(out_distlist, 90),
                        'p95': np.percentile(out_distlist, 95)})
        for i, dist in enumerate(distlist):
            under_dist = [x for x in out_distlist if x < dist]
            output.update({keylist[i]: (100.0*len([x for x in out_distlist if x < dist]))/num_of_locations,
                            numlist[i]: len([x for x in out_distlist if x < dist])})
        output.update({'percent_locations': 100.0*len(out_distlist)/expected_locations})
        return output
        

    
# check if out and then update output dict (locations, percentages) before returning 

def api_meo_location_accuracy(MEOLUT, StartTime, EndTime, config_dict, **kwargs):
    output = {}
    output[MEOLUT]={}
    servername, databasename  = config_dict["servername"], config_dict["oppsdatabase"]
    timedelta_secs = (EndTime - StartTime).total_seconds()
    if not kwargs.get('distList',False):
        distList = [2, 5, 10, 20]
        outdistdict = {}
    keylist = ['percent_less_than_'+str(dist)+'km' for dist in distList]
    numlist = ['number_less_than_'+str(dist)+'km' for dist in distList]
    
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    sql_query = """\
        select TOP(1)
            
            num_of_locations = count(distance) OVER (PARTITION BY SourceId),
            mean = avg(distance) OVER (PARTITION BY SourceId), 
            median = PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY distance) OVER (PARTITION BY [SourceId]), 
            P75 = PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY distance) OVER (PARTITION BY [SourceId]), 
            P90 = PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY distance) OVER (PARTITION BY [SourceId]), 
            P95 = PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY distance) OVER (PARTITION BY [SourceId]) 
        FROM [MccMeoLutMonitor].[dbo].[InputMeoSolution] 
        WHERE Distance is not null 
        AND SourceId = ?
        AND TimeLast between ? AND ? 
        """
    params = [MEOLUT, StartTime, EndTime]
    if kwargs.get('beaconId',False):
        beacon_string = kwargs.get('beaconId')
        sql_query += 'AND bcnId15 like ?'
        params.append(beacon_string)
    c = conn.cursor()
    c.execute(sql_query, params)
    columns = [column[0] for column in c.description]
    out = c.fetchone()

    if out: 
        #output['count'] = int(out[1])
        for ind, col in enumerate(columns):
            output[MEOLUT][col] = out[ind]
    else: 
        for ind, col in enumerate(columns):
            output[MEOLUT][col] = 0
            #output['count'] = 0
        for dist in distList:
            output[MEOLUT]['percent_less_than_'+str(dist)+'km'] = 0
            output[MEOLUT]['number_less_than_'+str(dist)+'km'] = 0
        output[MEOLUT]['percent_locations'] = 0
        return output
    
    # Only get down here if you have any solutions - ie out has data 
    output[MEOLUT]['percent_locations'] = 100.0* output[MEOLUT]['num_of_locations']/(float(timedelta_secs/50))
    sql_query = """\
        SELECT DISTANCE
        FROM [MccMeoLutMonitor].[dbo].[InputMeoSolution] 
        WHERE Distance is not null 
        AND SourceId = ?
        AND TimeLast between ? AND ? 
        
        """
    params = [MEOLUT, StartTime, EndTime]
    if kwargs.get('beaconId',False):
        beacon_string = kwargs.get('beaconId')
        sql_query += 'AND bcnId15 like ?'
        params.append(beacon_string)

    c = conn.cursor()
    c.execute(sql_query, params)
    out = c.fetchall()
    for dist in distList:
        outdistdict[dist] = sum(i[0] < dist for i in out)
        output[MEOLUT]['number_less_than_' + str(dist)+'km'] = sum(i[0] < dist for i in out)
        output[MEOLUT]['percent_less_than_' + str(dist)+'km'] = (100.0*sum(i[0] < dist for i in out))/float(output[MEOLUT]['num_of_locations'])
    return output

def real_time_packet_stats(MEOLUT, Time, config_dict):
    servername, databasename  = config_dict["servername"], config_dict["oppsdatabase"]
    conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;', readonly=True, autocommit = True)
    sql_query = """\
        SELECT TOP (1) *
        FROM [MccMeoLutMonitor].[dbo].[MeolutRealTimeMonitor]
        where MeolutId = ? and 
        AddTime < ?
        order by AddTime desc 
        """
    params = [MEOLUT, Time]
    c = conn.cursor()
    c.execute(sql_query, params)
    out = c.fetchall()
    columns = [column[0] for column in c.description]
    r = [dict((c.description[i][0], str(value)) \
    for i, value in enumerate(row)) for row in out]
    return (r[0] if r else None)

def api_meo_packet_throughput(MEOLUT, StartTime, EndTime, config_dict, rep_rate, minutes, **kwargs):
    servername, databasename  = config_dict["servername"], config_dict["oppsdatabase"]
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;', readonly=True, autocommit = True)
    sql_query = """\
        select DISTINCT
            [antennaId],
            num = count(DbId) OVER (PARTITION BY antennaId) 
        FROM [MccMeoLutMonitor].[dbo].[MeolutPackets] 
        WHERE MeolutId = ?
        AND UplinkTOADate between ? AND ? 
    """
    timedelta_secs = (EndTime - StartTime).total_seconds()
    params = [MEOLUT, StartTime, EndTime]
    if kwargs['beaconId']:
        beacon_string = kwargs.get('beaconId')
        sql_query += 'AND bcnId15 like ?'
        params.append(beacon_string)
    c = conn.cursor()
    c.execute(sql_query, params)
    columns = [column[0] for column in c.description]
    out = c.fetchall()
    output = {'MEOLUT': MEOLUT, 'antenna': OrderedDict()}
    if (MEOLUT == 3669):
        ant_len = 9
    elif (MEOLUT == 3385):
        ant_len = 8 
    else:
        ant_len = 2
    for i in range(1,ant_len+1):
        output['antenna'][i] = {'count': 0, 'percent' : 0}
    for j in out: 
        output['antenna'][j[0]]['count'] = j[1]
        if rep_rate:
            output['antenna'][j[0]]['percent'] = 100.0*float(j[1])/float(timedelta_secs / float(rep_rate))

    return output
def api_site_sum_query(arg_dict, config_dict, **kwargs):
    servername, databasename, OUTPUTFOLDER, approot = config_dict["servername"], config_dict["oppsdatabase"], config_dict["OUTPUTFOLDER"], config_dict["approot"]
    conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
     
    fieldlist = ['AlertSiteNum, BcnId15', 'BcnId30', 'BcnType', 'MidName', 'CompLat', 'CompLon', 'Closed', 
                 'OpenTime', 'CloseTime', 'TimeFirst', 'TimeLast', 'LastUpdTime', 'NumMsgSent', 
                 'MsgTimeLast', 'NumPasses', 'NumSol', 'NumLeoGeoSol', 'NumDopSol', 'NumMeoSol']   
    sql_query_field_list = ', '.join(fieldlist)
    params = []
    NOMAS = False # as in "No mas" - set to True to stop adding to query string
    print('in init')
    print(arg_dict)
    if arg_dict.get('sitenum'):
        sql_query = """ select top 1 {} FROM 
            AlertSiteSum WHERE 
            AlertSiteNum = ? 
            ORDER BY TimeLast """.format(sql_query_field_list)
        params.append(arg_dict['sitenum'])
        NOMAS = True
    else:    
        sql_query = """ SELECT {} from AlertSiteSum """.format(sql_query_field_list)
        if arg_dict.get('open_closed') == 'closed':
            sql_query+=' WHERE Closed = ? '
            params.append('Y')
        elif arg_dict.get('open_closed') == 'open': 
            sql_query+=' WHERE Closed = ? ' 
            params.append('N')

    if arg_dict.get('StartTime') and not NOMAS:
        if sql_query.find("WHERE") == -1: sql_query+= ' WHERE LastUpdTime > ?'
        else: sql_query+=(' AND LastUpdTime > ?')
        params.append(arg_dict['StartTime'])
    if arg_dict.get('EndTime') and not NOMAS:
        if sql_query.find("WHERE") ==-1: sql_query+= ' WHERE TimeFirst < ?'
        else: sql_query+=(' AND TimeFirst < ? ')
        params.append(arg_dict['EndTime'])

    if arg_dict.get('open_closed')=='all_open':
        sql_query = """
            SELECT {} from AlertSiteSum 
            WHERE CLOSED = ? """.format(sql_query_field_list)
        params = ['N']
    c = conn.cursor()
    c.execute(sql_query, tuple(params))
    out = c.fetchall()
    columns = [column[0] for column in c.description]
    if out:
        out_file_string = '_SiteSum_{:%Y-%m-%d-%H%M}_{:%Y-%m-%d-%H%M}.csv'.format(arg_dict.get('StartTime'), arg_dict.get('EndTime'))    
        output = sql_outputer(out, arg_dict['output_format'], c,
                            approot = approot,  
                            OUTPUTFOLDER=OUTPUTFOLDER,
                            out_file_string= out_file_string,
                            ) 
        return output
    else: return None
def api_site(config_dict, sitenum = None, table = None, type = 'all', one= False, **kwargs):
    servername, databasename  = config_dict["servername"], config_dict["oppsdatabase"]    
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD,readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    if 'data' in kwargs:
        if not table: table = data.get('table','alertsitesol')
        if not sitenum: sitenum = data.get('sitenum',None)
    sql_query = """ SELECT * FROM [MccMeoLutMonitor].[dbo].[%s] 
        WHERE AlertSiteNum = ?
        """ % table
    if type == 'leo':
        sql_query+= 'AND a_lat is not NULL'
    if type == 'meo':
        sql_query+= "AND InputDataType = 'M'"
    if type == 'enc':
        sql_query+= "AND EncLat is not NULL"
    if type == 'comp':
        sql_query+= "AND CompLat is not NULL "

    params = [sitenum]
    c = conn.cursor()
    c.execute(sql_query, params)
    r = [dict((c.description[i][0], value) \
        for i, value in enumerate(row)) for row in c.fetchall()]
    columns = [column[0] for column in c.description]
    return (r[0] if r else None) if one else r

def api_JSON_leo_geo_sols(data, config_dict, **kwargs):
    servername, databasename  = config_dict["servername"], config_dict["oppsdatabase"]
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD,readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    sql_query = """\
        SELECT CAST( (SELECT * FROM [MccMeoLutMonitor].[dbo].[Lut406Solution] 
        """ 
    where = []
    params = []
    if data.get('bcnId15', None):
        where.append(" bcnId15 like ? ")
        params.append(data['bcnId15'])
    if data.get('startTime', None):
        where.append(" A_Tca > ? ")
        params.append(data['startTime'])
    if data.get('endTime', None):
        where.append(" A_Tca < ? ")
        params.append(data['endTime'])
    if data.get('lut', None):
        where.append(" lut like ? ")
        params.append(data['lut'])
    if data.get('sat', None):
        where.append(" sat = ? ")
        params.append(data['sat'])
    if where: 
        sql_query = '{} WHERE {}'.format(sql_query, ' AND '.join(where))
    sql_query_end = """\
        FOR JSON PATH) 
        AS VARCHAR(MAX))
        """
    sql_query += sql_query_end  
    c = conn.cursor()
    c.execute(sql_query, params)
    columns = [column[0] for column in c.description]
    out = c.fetchone()
    return out 

def api_output_sols(data, config_dict, sitenum = None, **kwargs):
    servername, databasename  = config_dict["servername"], config_dict["oppsdatabase"]
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD,readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    sql_query = """\
        SELECT * FROM [MccMeoLutMonitor].[dbo].[OutSolution] 
        WHERE AlertSiteNum = ?
        """ 
    params = [sitenum]
    c = conn.cursor()
    c.execute(sql_query, params)
    columns = [column[0] for column in c.description]
    outdata = c.fetchall()


    return columns, outdata

def api_JSON_output_sols(data, config_dict, sitenum = None, **kwargs):
    servername, databasename  = config_dict["servername"], config_dict["oppsdatabase"]
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    sql_query = """\
        SELECT CAST( (SELECT * FROM [MccMeoLutMonitor].[dbo].[OutSolution] 
        WHERE AlertSiteNum = ?
        FOR JSON PATH) 
        AS VARCHAR(MAX)) 
        """ 
    params = [sitenum]
    c = conn.cursor()
    c.execute(sql_query, params)
    columns = [column[0] for column in c.description]
    out = c.fetchone()
    return out

def czml_all_sites_sum_query(servername = 'localhost', databasename='mccoperational', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    fieldname = OrderedDict()      
    fieldlist = ['AlertSiteNum', 'BcnId15', 'MidName', 'BcnType', 'OpenTime', 'LastUpdTime', 
                 'CompLat', 'CompLon','NumSol', 'NumMeoSol', 'NumDopSol', 'NumEncSol', 
                 'NumCompCalc', 'NumMsgSent', 'MsgTimeLast', 'CurSarNameList', 'BcnIsRegistered']
    sql_query_field_list = ', '.join(fieldlist)
    sql_query = ('select ' + sql_query_field_list + ' FROM '
                'AlertSiteSum WHERE '
                'Closed = ? '
                'ORDER BY OpenTime DESC '
                )
    params=['N']
    c = conn.cursor()
    c.execute(sql_query, params)
    out = c.fetchall()
    r = OrderedDict()
    idlist = [{"id":"document", "version":"1.0"}]
    for i in out:
        r[i[0]]= {fieldlist[j]: value for j, value in enumerate(i)}
        if i[7] != "NULL" and i[6] != "NULL" and i[6] is not None:
            idlist.append({"id": str(int(i[0])),
                           "parent": 'realtimesites',
                           "label": {
                               "text": str(int(i[0])),
                               "show": True,
                               "horizontalOrigin": "CENTER",
                               "pixelOffset": {
                                   "cartesian2" : [0, 20]
                                },
                               "font": "14pt Verdana"
                            },  
                            "position": {
                                "cartographicDegrees": [float(i[7]),float(i[6]),0]
                            }, 
                            "point": {
                                "color": { "rgba": [0,0,255,255] },
                                "pixelSize": math.ceil(i[8]/100),
                                "outlineColor": {
                                    "rgba": [255, 0, 0, 255]
                                },
                                "outlineWidth" : 1
                            },
                            "description": "<br>".join([str(fieldlist[j]) + " : " + str(value) for j, value in enumerate(i)])})
    try:
        return idlist
    except: 
        return None

def czml_meolut_ant_per(attime, bcnid, sourceid, servername = 'localhost', databasename='mccoperational', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    UseMCC = True
    fieldname = OrderedDict()      
    fieldlist = ['RecordTime', 'RunStartTime', 'RunEndTime', 'Ant01Per', 
                'Ant02Per', 'Ant03Per', 'Ant04Per', 'Ant05Per', 'Ant06Per']
    sql_query_field_list = ', '.join(fieldlist)
    sql_query = ('select top 1 ' + sql_query_field_list + ' FROM '
                '[MccTestLGM].[dbo].[MeolutMonitor] WHERE '
                'SourceId = ? AND '
                'BcnId15 = ? AND '
                'RecordTime < ? '
                'ORDER BY RecordTime DESC '
                )
    params=[sourceid, bcnid, attime]
    c = conn.cursor()
    c.execute(sql_query, params)
    out = c.fetchall()
    doc = czml.CZML()
    packet1 = czml.CZMLPacket(id='document', version= '1.0')
    doc.packets.append(packet1)
    packet2 = czml.CZMLPacket(id = 'FL_MEO_Percent')
    ant1 = czml.Point(position = 1, show = True)
    ant1.color = {'rgba': [0, 255, 127, 55]}
    packet2.billboard = ant1
    doc.packets.append(packet2)
    
    doc.write('example.czml')
    try:
        return doc.dumps()
    except: 
        return None


def czml_site_meo_input(Sitenum, servername = 'localhost', databasename='mccoperational', **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)
    UseMCC = True
    fieldname = OrderedDict()
    if UseMCC:
        fieldname['datatypename'] = 'datatype'
        fieldname['bcn15name'] = 'bcnid15'
        fieldname['bcn30name'] = 'bcnid30'
        fieldname['sourceidname'] = 'sourceid'
        fieldname['timefirstname'] = 'timefirst'
        fieldname['timelastname'] = 'timelast'
        fieldname['latname'] = 'latitude'
        fieldname['lonname'] = 'longitude'
        fieldname['altname'] = 'altitude'
        fieldname['numburstsname'] = 'numbursts'
        fieldname['numpacketsname'] = 'numpackets'
        fieldname['numsatsname'] = 'numsatellites'
        fieldname['dopname'] = 'dop'
        fieldname['cn0name'] = 'averagecn0'
        fieldname['ehename'] = 'expectedhorzerror'
        fieldname['satidsname'] = 'satelliteids'    
    fieldlist = [fieldname[key] for i, key in enumerate(fieldname)]
  
    sql_query_field_list = ', '.join(fieldlist)
    sql_query = ('select ' + sql_query_field_list + ' FROM '
                'InputMeoSolution where '
                ' bcnid15 = '
                '(select top 1 BcnId15 from '
                'AlertSiteSum where AlertSiteNum = ? ORDER BY TimeLast ) '
                )
    params=[Sitenum]
    c = conn.cursor()
    c.execute(sql_query, params)
    out = c.fetchall()
    sql_query2 = ('select top 1 LastUpdTime from AlertSiteSum where AlertSiteNum = ? ')
    c2 = conn.cursor()
    c2.execute(sql_query2, [Sitenum])
    LastUpdTime = c2.fetchone()
    r = OrderedDict()
    idlist = [{"id":"document", "version":"1.0"}]
    for i in out:

        r[i[0]]= {fieldlist[j]: value for j, value in enumerate(i)}
        if (i[7] is not None) or (i[6] is not None):
            idlist.append({"id": str((i[5])),
                           "name": i[5].isoformat(),
                           #"availability":"2017-08-04T16:00:00Z/2017-09-04T17:00:00Z",
                           "parent": Sitenum,
                           "availability":i[5].isoformat() + 'Z/' + LastUpdTime[0].isoformat() + 'Z',
                           "label": {
                               "text": str(int(i[0])),
                               "show": False,
                               "horizontalOrigin": "CENTER",
                               "pixelOffset": {
                                   "cartesian2" : [0, 20]
                                },
                               "font": "14pt Verdana"
                            },  
                            "position": {
                                "cartographicDegrees": [float(i[7]),float(i[6]),0]
                            }, 
                            "point": {
                                "color": { 
                                    "rgba": [255,255,255,255] 
                                    },
                                "pixelSize": 5,
                                "outlineColor": {
                                    "rgba": [233, 127, 21, 255]
                                },
                                "outlineWidth" : 2
                            },
                            "description": "<br>".join(['Site : ' + str(int(Sitenum))] + [str(fieldlist[j]) + " : " + str(value) for j, value in enumerate(i)])})
    try:
        return idlist
    except: 
        return None


def czml_alert_site(type, sitenum, jsonIn):
    r = OrderedDict()
    idlist = [{"id":"document", "version":"1.0"}]
    delta = timedelta(minutes=(60))
    if type == "comp":
        pointcolor = [200,25,25,200]
        nameheader = "composite location: "
        pointsize = 15
        lonfield, latfield ='complon', 'complat'
    if type == "leo":
        pointcolor = [100,100,100,100]
        nameheader = "leo location: "
        pointsize = 10
        lonfield, latfield = 'a_lat', 'a_lon'
    for solid, solution in enumerate(jsonIn):
        #for field, value in solution.items():
        #idlist.append({field: value})
        idlist.append({"id": str(solid),
                        "name": nameheader + str(solid),
                        #"availability":"2017-08-04T16:00:00Z/9999-12-31T24:00:00Z",
                        "parent": str(sitenum),
                        "availability":time_to_datetime(solution['addtime']).isoformat() +'Z/' + (time_to_datetime(solution['rcvtime'])+delta).isoformat() +'Z',
                        "label": {
                            "text": str(solid),
                            "show": False,
                            "horizontalOrigin": "CENTER",
                            "pixelOffset": {
                                "cartesian2" : [0, 20]
                            },
                            "font": "8pt Verdana"
                        },  
                        "position": {
                            "cartographicDegrees": [solution[lonfield], solution[latfield],0]
                        }, 
                        "point": {
                            "color": { 
                                "rgba": pointcolor 
                                },
                            "pixelSize": pointsize,
                            "outlineColor": {
                                "rgba": [255, 255, 255, 255]
                            },
                            "outlineWidth" : 1
                        },
                        "description": "<br>".join(['Site : ' + str(sitenum)] + [str(field) + " : " + str(value) for field, value in solution.items()])})
    try:
        return idlist
    except: 
        return None


def czml_meo_orbit_all(starttime, endtime, config_dict, satnum = False, **kwargs):
    servername, databasename  = config_dict["servername"], config_dict["oppsdatabase"]
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)

    satdict = OrderedDict()
    sql_query = ("select distinct sat from OrbitVector WHERE (Epoch between ? AND ?) AND LEFT(sat, 1) in ('3','4') order by sat " )
    c = conn.cursor()
    params = [starttime, endtime]
    c.execute(sql_query, params)
    out = c.fetchall()
    if satnum: 
        out = [(satnum,)]
    for sat in out: 
        if sat[0] is not None:
            params = [sat[0], starttime, endtime]
            sql_query2 = ('select Epoch, SatXPos, SatYPos, SatZPos, SatXVel, SatYVel, SatZVel from OrbitVector WHERE sat = ? '
                            'AND Epoch between ? AND ? '
                            )
            c2 = conn.cursor()
            c2.execute(sql_query2, params)
            outsatlist = c2.fetchall()
            satdict[sat[0]]= outsatlist 
    satlist = [{"id":"document", "version":"1.0"}]
    for i, value in enumerate(satdict):
        poslist = []
        if satdict[value]:
            if str(value)[0] == "3":
                pointprop = {"color": {
                                "rgba": [0,0,255,255] 
                            },
                            "pixelSize": 5,
                            "outlineColor": {
                                "rgba": [0, 127, 255, 200]
                            },
                            "outlineWidth" : 1
                            }
            else:
                pointprop = {"color": {
                                "rgba": [255,0,0,255] 
                            },
                            "pixelSize": 5,
                            "outlineColor": {
                                "rgba": [0, 127, 255, 200]
                            },
                            "outlineWidth" : 1
                            }
            for j in range(len(satdict[value])):
                poslist.extend([satdict[value][j][0].isoformat()+'Z'])
                poslist.extend([satdict[value][j][i]*1000 for i in range(1,7)])
            satlist.append({"id": int(value),
                            "name": int(value),
                            "description": "<p>Satellite - " + str(int(value)) + "</p>",
                            "parent": "meoSats",
                            "label": {
                                "text": str(int(value)),
                                "font": "10pt Verdana",
                                "horizontalOrigin": "CENTER",
                                "pixelOffset": {
                                    "cartesian2" : [0, 20]
                                }
                            },
                            "availability":starttime.isoformat() + 'Z/' + endtime.isoformat() + 'Z',
                            "position": {
                                "interpolationAlgorithm": "LAGRANGE",
                                "interpolationDegree": 5,
                                "referenceFrame": "FIXED",
                                "cartesianVelocity": 
                                    poslist
                            },
                            "point": pointprop
                            })
    try:
        return satlist
    except: 
        return None

def czml_meo_ant_per(data, StartTime, EndTime):
    czml_list = [{"id":"document", 
                  "version":"1.0",
                  "name" : "MEOLUT Antenna Percentages"}]
    id_list = []
    for key, val in data.items():
        if key == 'MEOLUT':
            MEOLUT = val
        if key == 'antenna':
            for ant, stat in val.items():
                id_list.append((ant,stat['percent']))
                if stat['percent'] > 0.8: 
                    rgba = [0 , 255, 0, 100]
                    rgb = (0,255,0)
                if stat['percent'] < 0.5: 
                    rgba = [255 , 0, 0, 100]
                    rgb = (255, 0, 0) 
                if 0.5 < stat['percent'] < 0.8: 
                    rgba = [(stat['percent']-1.7)*(-212.5) , (stat['percent']-0.5)*850, 0, 100]
                    rgb = ((stat['percent']-1.7)*(-212.5) , (stat['percent']-0.5)*850, 0)
                czml_list.append({
                    "id": str(MEOLUT) + "-" + str(int(ant)),
                    "name": str(MEOLUT) + "-" + str(int(ant))+ " percent",
                    "parent": "meoPer-" + str(MEOLUT),
                    "position" : {
                        "cartographicDegrees" : [MEOLUT_antenna_locations[MEOLUT][ant][1], 
                                                 MEOLUT_antenna_locations[MEOLUT][ant][0], 
                                                 MEOLUT_antenna_locations[MEOLUT][ant][2]]},
                    "cylinder" : {
                        "length" : 3+30.0*stat['percent'],
                        #"length" : 30.0,
                        "topRadius" : 8.0,
                        "bottomRadius" : 8.0,
                        "material" : {
                            "solidColor" : {
                                "color" : {
                                    "rgba" : rgba
                                }
                            }
                        },
                        "outline" : "true",
                        "outlineColor" : {
                            "rgba" : [0, 0, 0, 255]
                        },
                    },
                    "description" : "<p style='color:rgb" + str(rgb) + "'>" + "percent = " + '{:.1%}'.format(stat['percent']) + "</p>"
                        
                    
                })
    return czml_list
                #czml_list.append({
                #"id": key+"-"})

    #"id" : "shape1",
    #"name" : "Green cylinder with black outline",
    #"position" : {
    #    "cartographicDegrees" : [-100.0, 40.0, 200000.0]
    #},
    #"cylinder" : {
    #    "length" : 400000.0,
    #    "topRadius" : 200000.0,
    #    "bottomRadius" : 200000.0,
    #    "material" : {
    #        "solidColor" : {
    #            "color" : {
    #                "rgba" : [0, 255, 0, 128]
    #            }
    #        }
    #    },
    #    "outline" : true,
    #    "outlineColor" : {
    #        "rgba" : [0, 0, 0, 255]
    #    }
def czml_leo_orbit_all(starttime, endtime, servername = 'localhost', databasename='mccoperational',  satnum = False, **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)

    satdict = OrderedDict()
    sql_query = ('select distinct Sat from LutOrbitVectorOut order by Sat ' )
    c = conn.cursor()
    c.execute(sql_query)
    out = c.fetchall()
    if satnum: 
        out = [(satnum,)]

    for sat in out: 
        if sat[0] is not None:
            params = [sat[0], starttime, endtime]
            sql_query2 = ('select Epoch, SatXPos, SatYPos, SatZPos, SatXVel, SatYVel, SatZVel, Orbit from LutOrbitVectorOut WHERE sat = ? '
                            'AND Epoch > ? '
                            'AND Epoch < ? '
                            )
            c2 = conn.cursor()
            c2.execute(sql_query2, params)
            outsatlist = c2.fetchall()
            satdict[sat[0]]= outsatlist 
    satlist = [{"id":"document", "version":"1.0"}]
    for i, value in enumerate(satdict):
        poslist = []
        for j in range(len(satdict[value])):
            poslist.extend([satdict[value][j][0].isoformat()+'Z'])
            poslist.extend([satdict[value][j][i]*1000 for i in range(1,7)])
        satlist.append({"id": value,
                        "name": value,
                        "label": {
                            "text": str(value),
                            "font": "10pt Verdana",
                            "horizontalOrigin": "CENTER",
                            "pixelOffset": {
                                "cartesian2" : [0, 20]
                            }
                        },
                        "availability":starttime.isoformat() + 'Z/' + endtime.isoformat() + 'Z',
                        "position": {
                            "interpolationAlgorithm": "LAGRANGE",
                            "interpolationDegree": 2,
                            "referenceFrame": "FIXED",
                            "cartesianVelocity": 
                                poslist
                        },

                        #"availability":"2017-08-04T16:00:00Z/2017-09-04T17:00:00Z",
                        #"availability":i[5].isoformat() + 'Z/' + LastUpdTime[0].isoformat() + 'Z',

                        #    "pixelOffset": {
                        #        "cartesian2" : [0, 20]
                        #    },
                        #    "font": "14pt Verdana"
                        #}
                        #"position": {
                        #    "cartographicDegrees": [float(i[7]),float(i[6]),0]
                        #}, 
                        "point": {
                            "color": { 
                                #"rgba": [63,191,191,120] 
                                "rgba": [255,255,255,255] 
                                },
                            "pixelSize": 5,
                            "outlineColor": {
                                "rgba": [0, 127, 255, 200]
                            },
                            "outlineWidth" : 2
                        }
                        })


                        #"description": "<br>".join(['Site : ' + str(int(Sitenum))] + [str(fieldlist[j]) + " : " + str(value) for j, value in enumerate(i)])})
    try:
        return satlist
    except: 
        return None


def czml_meo_sched_all(starttime, endtime, servername = 'localhost', databasename='mccoperational',  antnum = False, **kwargs):
    if 'sql_login' in kwargs:
        conn = odbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD, readonly=True, autocommit = True)
    else:
        conn = odbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True, autocommit = True)

    for LUT in [3669, 3385]:
        satdict = OrderedDict()
        params = [starttime, endtime, LUT]
        sql_query = ('select LutId, AntennaId, SatId, AOSStr, LOSStr, TimeRecordAdded from PassesPlanned '
                    'where TimeRecordAdded = (select top 1 TimeRecordAdded from PassesPlanned where '
                    'AOSStr > ? and LOSStr < ? AND LutId = ? '
                    'order by TimeRecordAdded desc) '
                    )
        c = conn.cursor()
        c.execute(sql_query, params)
        out = c.fetchall()
        for sat in out: 
            if sat[0] is not None:
                params = [str(sat[0]), starttime, endtime]
                sql_query2 = ('select Epoch, SatXPos, SatYPos, SatZPos, SatXVel, SatYVel, SatZVel, Orbit from LutOrbitVectorOut WHERE sat = ? '
                                'AND Epoch > ? '
                                'AND Epoch < ? '
                                )
                c2 = conn.cursor()
                c2.execute(sql_query2, params)
                outsatlist = c2.fetchall()
                satdict[sat[0]]= outsatlist 
        satlist = [{"id":"document", "version":"1.0"}]
        for i, value in enumerate(satdict):
            passlist = []
            for j in range(len(satdict[value])):
                passlist.extend([satdict[value][j][0].isoformat()+'Z'])
                passlist.extend([satdict[value][j][i]*1000 for i in range(1,7)])
            satlist.append({"id": value,
                            "name": value,
                            "label": {
                                "text": str(value),
                                "font": "10pt Verdana",
                                "horizontalOrigin": "CENTER",
                                "pixelOffset": {
                                    "cartesian2" : [0, 20]
                                }
                            },
                            "availability":starttime.isoformat() + 'Z/' + endtime.isoformat() + 'Z',
                            "position": {
                                "interpolationAlgorithm": "LAGRANGE",
                                "interpolationDegree": 2,
                                "referenceFrame": "FIXED",
                                "cartesianVelocity": 
                                    poslist
                            },

                            #"availability":"2017-08-04T16:00:00Z/2017-09-04T17:00:00Z",
                            #"availability":i[5].isoformat() + 'Z/' + LastUpdTime[0].isoformat() + 'Z',

                            #    "pixelOffset": {
                            #        "cartesian2" : [0, 20]
                            #    },
                            #    "font": "14pt Verdana"
                            #}
                            #"position": {
                            #    "cartographicDegrees": [float(i[7]),float(i[6]),0]
                            #}, 
                            "point": {
                                "color": { 
                                    #"rgba": [63,191,191,120] 
                                    "rgba": [255,255,255,255] 
                                    },
                                "pixelSize": 5,
                                "outlineColor": {
                                    "rgba": [0, 127, 255, 200]
                                },
                                "outlineWidth" : 2
                            }
                            })


                        #"description": "<br>".join(['Site : ' + str(int(Sitenum))] + [str(fieldlist[j]) + " : " + str(value) for j, value in enumerate(i)])})
    try:
        return satlist
    except: 
        return None
     
    