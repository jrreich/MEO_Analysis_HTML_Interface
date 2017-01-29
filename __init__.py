import numpy as np
import pandas as pd
from itertools import repeat
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, MinuteLocator, drange
from matplotlib.backends.backend_pdf import PdfPages
import math
import sys
import os
import xlrd
from datetime import datetime, timedelta
import csv
from collections import OrderedDict, defaultdict
import simplekml
import re
import beacon_decode as bcn
import pypyodbc


kml = simplekml.Kml()
UID = 'jesse'
PWD = 'nopw'

pd.options.mode.chained_assignment = None # turn off SettingWithCopyWarning

#def read_config_file(configfile,row_start,row_end,column_key):
#    configdict = {}
#    wb = xlrd.open_workbook(configfile)
#    sh = wb.sheet_by_index(0)
#    for i in range(row_start-1,row_end-1): 
#        try: 
#            cell_value = sh.cell(i,column_key).value
#            cell_key = sh.cell(i,column_key-1).value
#            configdict[cell_key] = cell_value
#        except Exception:
#            break
#    return configdict

def haversine(x):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    for i in x:
        #print 'i = '
        #print type(i)
        #print i
        if i == None:
            #print i
            #print 'N/A'
            return None

    lat1, lon1, lat2, lon2 = map(np.radians, [x[0], x[1], x[2], x[3]])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    r = 6373 # Radius of earth in kilometers. Use 3956 for miles
    #print c*r         
    return c * r

def singleburst_loc(df, lat_GT, lon_GT, MEOLUT):
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
    #print df3.iloc[180:240,:]
    df3['last_in_window'] = (df3.timestart_diff > pd.Timedelta(minutes = 9)) & (df3.timestart_diff2 > pd.Timedelta(minutes = 3))    
    #print df3[['TimeFirst','timestart_diff','timestart_diff2','last_in_window']]
    df3 = df3[((df3.timestart_diff > pd.Timedelta(minutes = 9)) & (df3.timestart_diff2 > pd.Timedelta(minutes = 3))) | df3.timestart_diff.isnull()] 
    return df3  

def find_packets(databasename='MccTestLGM', beaconid = '%', start_date = 0, end_date = None, MEOLUT = '%',ant_i = '%', sat = '%', **kwargs):
    if 'sql_login' in kwargs:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server=reichj-pc\SQLEXPRESS;Database='+databasename+'; UID='+UID+'; PWD=' + PWD)
    else:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database='+databasename+';Trusted_Connection=yes;')
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
    #cursor.execute("Select * from MEOInputSolution where BcnId15 like ?", [BeaconQuery])
    #cursor.execute(sql_query,[MEOLUT,StartTime, EndTime, BeaconQuery])
    #for dataRow in cursor.fetchall():
    #    print(dataRow)
    #    crsr.execute(sql, dataRow)
    #df = pd.read_sql_query(sql_query,conn, index_col = 'addtime', params=query_params)
    #print df.head(5)
    # return df
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
        
    #print mintime
    #print maxtime
    #alt = [np.linalg.norm(x) for x in posilist]    
    #rangelist = [np.linalg.norm(MEOLUTLocDict[MEOLUT] - x) for x in posilist]
    #plotting TLE positional difference below
    #fig, ax = plt.subplots()
    #ax.plot_date(timelist, frequencylist, '-')
    #font = {'family' : 'normal',
            #'weight' : 'bold',
            #'size'   : 22}
    #matplotlib.rc('font', **font)
    #print frequencylist
    plt.figure(MEOLUT, figsize=(40,20))
    if ant_i == ant_list[0]:
        ax1 = plt.subplot(len(ant_list),1,1)
    else:
        plt.subplot(len(ant_list),1,ant_list.index(ant_i)+1, sharex = ax1, sharey = ax1)
    
    plt.plot(timelist, frequencylist,'ro')
    plt.title('{} - antenna {} -- {} packets = {:.1f}%'.format(MEOLUT,ant_i,packets_found,percent_packets))
    #plt.title('{} - antenna {} ---- {} packets'.format(MEOLUT,ant_i,packets_found)) #,percent_packets))
    plt.grid(True)
    plt.gca().xaxis.set_major_locator(Hours)
    plt.gca().xaxis.set_major_formatter(plot_fmt)
    plt.gca().xaxis.set_minor_locator(FiveMinutes)
    plt.gca().set_xlim(start_time,end_time)

MEOLUTName ={3669:'Florida',3385:'Hawaii',3677:'Maryland'}
MEOList = [3669, 3385, 3677]
MEOref = {3669:'ADDC002%', 3385:'AA5FC00%', 3677:'ADDC002%'}

#Date Formats
timepacket_format = '%Y-%m-%d %H:%M:%S.%f'
sec_f = '%S.%f'
plot_fmt = DateFormatter('%m-%d %H:%M')
Hours = MinuteLocator(interval = 30)
FiveMinutes = MinuteLocator(interval=5)


data_cols = ['DataType','BcnId15','BcnId30','SourceId','TimeFirst','TimeLast','Latitude',
    'Longitude','Altitude','NumBursts','NumPackets','DOP','ExpectedHorzError']
data_cols = [0,1,2,4,8,9,10,11,12,13,14,17,18,19,20,21,22,36,37,47]
ant_list = range(1,7)

def xlx_analysis(UPLOADFOLDER, OUTPUTFOLDER, XLSFILENAME, MEOLUT, TimeStart, TimeEnd, result, Lat_GT=0, Long_GT=0, Location='', **kwargs):
    InputMEO_excelfile = UPLOADFOLDER +'/' + XLSFILENAME
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
    
    print('\n\nImporting - ' + InputMEO_excelfile)
    df = pd.read_excel(InputMEO_excelfile, index_col = 'TimeSolutionAdded', parse_cols =  data_cols) #parse_dates = True,
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
    print dfMB.head(5)
    if df3.empty: 
        print "Data Frame is empty after filtering out Beacon ID = " + BeaconID

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

    print timefirst

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

    #print df3.head(5)

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
    
    with open(OUTfile, 'wb') as csvfile:
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

    #print '\nWrite KML? - ' + result['KMLgen']

    if 'KMLgen' in result:
        KMLfile = OUTPUTFOLDER + '\KML' + outfiletag +'.kml'
        print '\nCreating KML file'
        if 'SingleBurstGen' in result:
            print 'Writing Single Burst Locations to KML' 
            with open(SBLfile, 'rb') as csvfile:
                csvfile.next()
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
                    pntSBL.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
        if 'EncLocGen' in result:
            print 'Writing Encoded Locations to KML'
            with open(SBLfile, 'rb') as csvfile:
                csvfile.next()
                filereader = csv.reader(csvfile)
                folEnc = kml.newfolder(name = 'Encoded Locations - '+ str(MEOLUT))                
                for row in filereader:
                    if row[17] <> '':  
                        pntEnc = folEnc.newpoint(coords=[(float(row[15]),float(row[14]))], 
                            description = 'Encoded Location - Beacon = ' + row[2] + '\n\nTimeSolutionAdded = ' + row[0] + '\nLat,Long = (' + row[14] + ', ' +row[15] + ')'  
                            )
                        pntEnc.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                        pntEnc.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal5/icon52.png'
                        pntEnc.style.iconstyle.scale = 0.8
                        pntEnc.style.labelstyle.color = '00ff0000'  # Red
                    #pnt.snippet.content = 'this is content'
                    #print row[0],row[7],row[8]
        with open(MBLfile, 'rb') as csvfile:
            csvfile.next()
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
                pntMBL.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png'
                pntMBL.style.labelstyle.color = 'ff0000ff'  # Red
                #pnt.snippet.content = 'this is content'
                #print row[0],row[7],row[8]
    

    
    if 'LEOgen' in result:
        LEOinputfile = UPLOADFOLDER +'\\' + kwargs['LEOGEO_file']
        print 'Reading LEO file - ' + LEOinputfile
        print 'Writing LEO bursts to KML'
        LEOoutfile = OUTPUTFOLDER + '\LEO' + outfiletag + '.csv'
        df = pd.read_excel(LEOinputfile, index_col = 'AddTime') #, parse_dates = True)
        df = df[(df.BcnId15 == BeaconID)]
        if df.empty: 
            print(LEOinputfile + ' - did not contain any data that matched')    
        else:
            dfLEO = df[df.Orbit.notnull()]
            dfLEO_loc = dfLEO[dfLEO.A_Lat.notnull()]
            dfLEO_loc.to_csv(LEOoutfile)
            with open(LEOoutfile, 'rb') as csvfile:
                filereader = csv.reader(csvfile)
                csvfile.next()
                fol_LEO = kml.newfolder(name='LEO Locations - '+ str(MEOLUT))
                for row in filereader:            
                    pnt_LEO = fol_LEO.newpoint(coords=[(float(row[22]),float(row[21]))], 
                        description = 'LEO Location \nBeacon = ' + row[15] + '\n\nA_Tca = ' + row[23] + '\nMCCTime = ' + row[0] + '\n\nLUT = ' + row[2] + '\nSat = ' + row[3] +
                        '\nOrbit = ' + str(int(float(row[4]))) + '\n\nNominal = ' + row[73] +  
                        '\nNum of Points = ' +row[18] + '\nA_Cta =' + row[24] + '\nA_prob = ' +row[17] + '\nSolId = ' + row[1]  
                        )   
                    pnt_LEO.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                    pnt_LEO.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png'
                    #pnt_LEO.style.iconstyle.icon.href = 'file://C:/Users/Jesse/Documents/Programming/Python/MEO_Input_Processor/MEO_Input_Processor_v2_w_KML/icon35.png'
                    pnt_LEO.style.iconstyle.scale = 0.7
                    pnt_LEO.style.labelstyle.color = 'ffff0000'  # Red

    kml.save(CSVoutfolder + '\KML_' + csvoutfilename + '.kml')

def MSSQL_analysis(result, MEOLUT, TimeStart, TimeEnd, OUTPUTFOLDER, databasename='mccoperational', Lat_GT=0, Long_GT=0, Location='', **kwargs):
    if 'sql_login' in kwargs:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server=reichj-pc\SQLEXPRESS;Database='+databasename+'; UID='+UID+'; PWD=' + PWD)
    else:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database='+databasename+';Trusted_Connection=yes;')
    #cursor = conn.cursor()
    if 'beaconID' in result: 
        BeaconQuery = '%' + result['beaconID']+'%'
        BeaconID = result['beaconID']
    else: 
        BeaconQuery = '%' 
    #if 'siteID' in result: 
    #    SiteQuery = '%' + result['siteID'] + '%'
    #else:
    #    SiteQuery = '%' 
    if ('Long' in kwargs): 
        Long_GT = kwargs['Long']
        MEO_dist = haversine([Lat_GT,Long_GT,MEOLUTLoc[MEOLUT][0],MEOLUTLoc[MEOLUT][1]])
    else: 
        Long_GT = None
        MEO_dist = 'NA'
    sql_query = ('SELECT * from InputMEOSolution '
        'WHERE '
        'SourceId = ? '
        'AND '
        'TimeSolutionGenerated between ? AND ? '
        'AND '
        'BcnId15 LIKE ?')
    params=[MEOLUT,TimeStart, TimeEnd, BeaconQuery]
    df = pd.read_sql_query(sql_query,conn, index_col = 'timesolutionadded', params=params)
    #    parse_dates=['timefirst','timelast', 'timesolutiongenerated','timesolutionadded'])
    #df = pd.DataFrame(cursor.fetchall())
    #print df.head(5)
    #df.columns = pd.DataFrame(np.matrix(cursor.description))[0]
    df2 = df[['datatype','bcnid15','bcnid30','sourceid','timefirst','timelast','latitude',
        'longitude','altitude','numbursts','numpackets','dop','expectedhorzerror']]
    df3 = df2.sort_index().ix[TimeStart:TimeEnd]
    #df3 = df2[(df2.BcnId15 == BeaconID)]
    dfSB = df3[(df3.datatype == 3)] 
    dfMB = df3[(df3.datatype == 0)] 
    if df3.empty: print "Data Frame is empty after filtering out Beacon ID = " + BeaconID
    
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

    #print df3.head(5)

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
    SBLfile = OUTPUTFOLDER + r'SBL' + str(MEOLUT)    + outfiletag +'.csv'
    MBLfile = OUTPUTFOLDER + r'MBL' + str(MEOLUT) + outfiletag +'.csv'
    OUTfile = OUTPUTFOLDER + r'OUT' + str(MEOLUT) + outfiletag +'.csv'
    LEOGEO_file = OUTPUTFOLDER + r'LEO' + outfiletag + '.csv'
    RCC_Output_file = OUTPUTFOLDER + r'RCC' + outfiletag + '.csv'
    #outfilenamelist = list()
    outfilelist = OrderedDict()
    outfilelist[OUTfile] = 'Output Summary'
    outfilelist[SBLfile] = 'Single Burst Solutions'
    outfilelist[MBLfile] = 'Multi Burst Solutions'




    
    if 'KMLgen' in result: 
        KMLfile = OUTPUTFOLDER + r'KML' + outfiletag +'.kml'
        outfilelist[KMLfile] = 'KML File Output'
    df_SBL.to_csv(SBLfile)
    df_MBL.to_csv(MBLfile)
    #OrderedDict(reversed(list(outfilelist.items())))
    #outfilelist.append(SBLfile)
    #outfilelist.append(MBLfile)
    #outfilelist.append(OUTfile)


    with open(OUTfile, 'wb') as csvfile:
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
        print '\nCreating KML file'
        if 'SingleBurstGen' in result:
            print 'Writing Single Burst Locations to KML' 
            with open(SBLfile, 'rb') as csvfile:
                csvfile.next()
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
                    pntSBL.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
        if 'EncLocGen' in result:
            print 'Writing Encoded Locations to KML'
            with open(SBLfile, 'rb') as csvfile:
                csvfile.next()
                filereader = csv.reader(csvfile)
                folEnc = kml.newfolder(name = 'Encoded Locations - '+ str(MEOLUT))                
                for row in filereader:
                    if row[17] <> '':  
                        pntEnc = folEnc.newpoint(coords=[(float(row[15]),float(row[14]))], 
                            description = 'Encoded Location - Beacon = ' + row[2] + '\n\nTimeSolutionAdded = ' + row[0] + '\nLat,Long = (' + row[14] + ', ' +row[15] + ')'  
                            )
                        pntEnc.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                        pntEnc.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal5/icon52.png'
                        pntEnc.style.iconstyle.scale = 0.8
                        pntEnc.style.labelstyle.color = '00ff0000'  # Red
        with open(MBLfile, 'rb') as csvfile:
            csvfile.next()
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
                pntMBL.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png'
                pntMBL.style.labelstyle.color = 'ff0000ff'  # Red
        if 'LEOGen' in result:
            outfilelist[LEOGEO_file] = 'LEO Solutions'
            sql_query = ('SELECT b.AddTime, a.* from Lut406Solution a, inputmessage b '
                'WHERE a.InMsgId = b.InMsgId '
                'AND '
                'Orbit IS NOT NULL '  #this gets LEO solutions
                'AND '
                'A_Tca between ? AND ? '
                'AND '
                'BcnId15 LIKE ? '
                )
            params=[TimeStart, TimeEnd, BeaconQuery]
            df = pd.read_sql_query(sql_query,conn, index_col = 'addtime', params=params)
            #df = df[(df.BcnId15 == BeaconID)]
            #print df.a_lat.head(5)
            dfLEO_loc = df[df.a_lat <> 'null']
            if df.empty: 
                print('query did not find any data that matched')    
            else:
                #dfLEO = df[df.Orbit.notnull()]
                #dfLEO_loc = df[df.a_lat.notnull()]
                #print dfLEO_loc.head(5)
                dfLEO_loc.to_csv(LEOGEO_file)
                with open(LEOGEO_file, 'rb') as csvfile:
                    filereader = csv.reader(csvfile)
                    csvfile.next()
                    fol_LEO = kml.newfolder(name='LEO Locations')
                    for row in filereader:            
                        pnt_LEO = fol_LEO.newpoint(coords=[(float(row[22]),float(row[21]))], 
                            description = 'LEO Location \nBeacon = ' + row[15] + '\n\nA_Tca = ' + row[23] + '\nMCCTime = ' + row[0] + '\n\nLUT = ' + row[2] + '\nSat = ' + row[3] +
                            '\nOrbit = ' + str(int(float(row[4]))) + '\n\nNominal = ' + row[73] +  
                            '\nNum of Points = ' +row[18] + '\nA_Cta =' + row[24] + '\nA_prob = ' +row[17] + '\nSolId = ' + row[1]  
                            )   
                        pnt_LEO.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                        pnt_LEO.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png'
                        #pnt_LEO.style.iconstyle.icon.href = 'file://C:/Users/Jesse/Documents/Programming/Python/MEO_Input_Processor/MEO_Input_Processor_v2_w_KML/icon35.png'
                        pnt_LEO.style.iconstyle.scale = 0.7
                        pnt_LEO.style.labelstyle.color = 'ffff0000'  # Red
        if 'OutputSolution' in result:
            outfilelist[RCC_Output_file] = 'RCC Output Solutions'
            sql_query = ('SELECT * from outsolution '
                'WHERE '
                'AddTime between ? AND ? '
                'AND '
                'BcnId15 LIKE ? '
                )
            params=[TimeStart, TimeEnd, BeaconQuery]
            df = pd.read_sql_query(sql_query,conn, index_col = 'addtime', params=params)
            #df = df[(df.BcnId15 == BeaconID)]
            print df.head(5)
            if df.empty: 
                print('query did not find any data that matched')    
            else:
                #dfLEO = df[df.Orbit.notnull()]
                dfRCC_loc = df[df.a_lat.notnull()]
                dfRCC_loc.to_csv(RCC_Output_file)
                with open(RCC_Output_file, 'rb') as csvfile:
                    filereader = csv.reader(csvfile)
                    csvfile.next()
                    fol_RCC = kml.newfolder(name='RCC Output Locations')
                    for row in filereader:            
                        pnt_RCC = fol_RCC.newpoint(coords=[(float(row[27]),float(row[28]))], 
                            description = 'RCC Solution \nBeacon = ' + row[15] + '\n\nA_Tca = ' + row[23] + '\nMCCTime = ' + row[0] + '\n\nLUT = ' + row[2] + '\nSat = ' + row[3] +
                            '\nOrbit = ' + str(int(float(row[4]))) + '\n\nNominal = ' + row[73] +  
                            '\nNum of Points = ' +row[18] + '\nA_Cta =' + row[24] + '\nA_prob = ' +row[17] + '\nSolId = ' + row[1]  
                            )   
                        pnt_RCC.timespan.begin = row[0][:10] + 'T' + row[0][11:19]
                        pnt_RCC.style.iconstyle.icon.href = 'http://earth.google.com/images/kml-icons/track-directional/track-none.png'
                        #pnt_LEO.style.iconstyle.icon.href = 'file://C:/Users/Jesse/Documents/Programming/Python/MEO_Input_Processor/MEO_Input_Processor_v2_w_KML/icon35.png'
                        pnt_RCC.style.iconstyle.scale = 0.7
                        pnt_RCC.style.labelstyle.color = 'FFFFFF'  # Red
            
        kml.save(KMLfile)
    
    return OUTfile, outfilelist

def MSSQL_burst(result, MEOLUTlist, TimeStart, TimeEnd, OUTPUTFOLDER, databasename='MccTestLGM', **kwargs):
    if result['UseBeaconID'] == "FLref": 
        beaconIDstring = "ADDC002%"
        ref_flag = True
    elif result['UseBeaconID'] == "HIref": 
        beaconIDstring = "AA5FC00%"
        ref_flag = True
    elif 'beaconID' in result:
        beaconIDstring = result['beaconID']
    else:
        beaconIDstring = '%'

    if result['RealPastTime'] == 'RT_yes':
        TimeEnd = datetime.utcnow()
        print TimeEnd
        print result['realtimehours']
        TimeStart = TimeEnd - timedelta(hours = float(result['realtimehours']))
    TimeSpan = TimeEnd - TimeStart
    num_bursts = TimeSpan.total_seconds() / 50
    filetimetag = datetime.strftime(datetime.utcnow(),"%Y%m%d_%H%M%S")
    print num_bursts
    ref_flag = False
    filelist = list()
    MEOnamelist = list()
    for MEOLUT in MEOLUTlist:
        for ant_i in ant_list:
            if result['UseBeaconID'] == 'REFref': 
                beaconIDstring = MEOref[MEOLUT]
                ref_flag = True
            outpackets = find_packets(databasename,beaconIDstring, TimeStart,TimeEnd, MEOLUT, ant_i, **kwargs) # sat 
            packets_found = len(outpackets)
            percent_packets = (packets_found/num_bursts)*100
            print '{} - antenna {} ->  {} packets found -- {:.1f}% '.format(MEOLUT, ant_i, packets_found, percent_packets)
            plot_packets(outpackets, MEOLUT, ant_i,TimeStart,TimeEnd, packets_found, percent_packets)
        filename = OUTPUTFOLDER + str(MEOLUT) + '_' + filetimetag + '_output.png'
        filelist.append(filename)
        MEOnamelist.append(MEOLUTName[MEOLUT])
        plt.savefig(filename) #, bbox_inches='tight')
    print MEOnamelist
    return filelist
        
#servername = r'.\SQLEXPRESS'
#databasename = 'mccoperational'
def MEOLUT_alarms(StartTime, EndTime, servername = r'.\SQLEXPRESS', databasename = 'mccoperational', **kwargs):
    print '--this should print ' 
    if 'sql_login' in kwargs:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server=reichj-pc\SQLEXPRESS;Database='+databasename+'; UID='+UID+'; PWD=' + PWD)
        print 'used sql login'
    else:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server=servername;Database='+databasename+';Trusted_Connection=yes;')
        print 'used win auth'
    query_params = [StartTime, EndTime]
    print 'anyone home here?'
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
            'closedat': dfClosed[(dfClosed.alarmid == alarm) & (dfClosed.alarmtimeon.isnull())].iloc[0].alarmtimeoff
            
        }
        #closedate = dfClosed[(dfClosed.alarmid == alarm) & (dfClosed.alarmtimeon.isnull())].alarmtimeoff
        #print closedate    
        closedalarmlist.append(alarms)
    return alarmlist, closedalarmlist, numalarms

def MEOLUT_status(StartTime, EndTime, servername = r'.\SQLEXPRESS', databasename = 'mccoperational', **kwargs):
    if 'sql_login' in kwargs:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server=reichj-pc\SQLEXPRESS;Database='+databasename+'; UID='+UID+'; PWD=' + PWD)
    else:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server=servername;Database='+databasename+';Trusted_Connection=yes;')
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

def MEOLUT_percent(StartTime, EndTime, servername = r'.\SQLEXPRESS', databasename = 'MccTestLGM', **kwargs):
    print 'anyone home here?'
    if 'sql_login' in kwargs:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server=reichj-pc\SQLEXPRESS;Database='+databasename+'; UID='+UID+'; PWD=' + PWD)
    else:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server=servername;Database='+databasename+';Trusted_Connection=yes;')
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
    antlist = range(1,7)
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