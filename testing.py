import pandas as pd
import datetime
import pypyodbc

#servername = r'.\SQLEXPRESS'
#databasename = 'mccoperational'
def MEOLUT_status(StartTime, EndTime, servername = r'.\SQLEXPRESS', databasename = 'mccoperational', **kwargs):
    conn = pypyodbc.connect(r'Driver={SQL Server};Server=' + servername + ';Database=' + databasename + ';Trusted_Connection=yes;')
    query_params = [StartTime, EndTime]
    sql_query = ('SELECT * from MeolutStatus '
        'WHERE '
        'AddTime BETWEEN ? AND ? '
    )
    df = pd.read_sql_query(sql_query,conn, index_col = 'msgtime', params=query_params)
    df.sort_index().ix[StartTime:EndTime]
    if df.empty: print 'no status messages in window between start and end time'
    print df.head(5)
    dfHIcurrentmsgnum = int(df[(df.meolutid == 3385)].iloc[-1].msgnum)
    dfFLcurrentmsgnum = int(df[(df.meolutid == 3669)].iloc[-1].msgnum)
    dfHI = df[(df.meolutid == 3385) & (df.msgnum == dfHIcurrentmsgnum)]
    dfFL = df[(df.meolutid == 3669) & (df.msgnum == dfFLcurrentmsgnum)]
    print dfHI.head(5)
    print dfFL.head(5)
    statusHIlist = []
    for item, row in dfHI.iterrows():
        print 'itme = '
        print item
        statusHI = {
            'component': row['component'],
            'msgtime': item,
            'status': int(row['status']),
            }
        statusHIlist.append(statusHI)
    return statusHIlist
 
         
    #if dfOpen.empty: 
    #    print 'No active alarms at ' + EndTime
    #else: 
    #    openalarms = dfOpen.alarmid.unique().tolist()
    #    print 'Open (' + str(len(openalarms))+') ='
    #    print openalarms
    #    for alarm in openalarms:
    #        print '\nalarmid = ' + str(dfOpen[(dfOpen.alarmid == alarm)].iloc[0].alarmid)
    #        print 'meolut = ' + str(dfOpen[(dfOpen.alarmid == alarm)].iloc[0].meolutid)
    #        print 'alarmtext = ' + str(dfOpen[(dfOpen.alarmid == alarm)].iloc[0].alarmtext)
    #        print 'open at =' + str(dfOpen[(dfOpen.alarmid == alarm)].iloc[0].alarmtimeon)
    #        print 'still open as of = '+ str(dfOpen[(dfOpen.alarmid == alarm)].iloc[-1].alarmtimeon)

    

Start = datetime.datetime(2017,1,1)
End = datetime.datetime(2017,1,8,21,30)
print Start
print End

statusHIlist = MEOLUT_status(Start, End)
print statusHIlist