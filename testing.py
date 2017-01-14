import pandas as pd
import datetime
import pypyodbc

#servername = r'.\SQLEXPRESS'
#databasename = 'mccoperational'
def MEOLUT_alarms(StartTime, EndTime, servername = r'.\SQLEXPRESS', databasename = 'mccoperational', **kwargs):
    conn = pypyodbc.connect(r'Driver={SQL Server};Server=' + servername + ';Database=' + databasename + ';Trusted_Connection=yes;')
    #c = conn.cursor()
    query_params = [StartTime, EndTime]
    sql_query = ('SELECT * from MeolutAlarms '
        'WHERE '
        'AddTime BETWEEN ? AND ? '
    )
    df = pd.read_sql_query(sql_query,conn, index_col = 'msgtime', params=query_params)
    df.sort_index().ix[StartTime:EndTime]
    dfClosed = df.alarmid[df.alarmtimeon.isnull()].tolist()
    print 'Closed ='
    print dfClosed
    dfOpen = df[~df.alarmid.isin(dfClosed)]
    if dfOpen.empty: 
        print 'No active alarms at ' + EndTime
    else: 
        openalarms = dfOpen.alarmid.unique().tolist()
        print 'Open (' + str(len(openalarms))+') ='
        print openalarms
        for alarm in openalarms:
            print '\nalarmid = ' + str(dfOpen[(dfOpen.alarmid == alarm)].iloc[0].alarmid)
            print 'meolut = ' + str(dfOpen[(dfOpen.alarmid == alarm)].iloc[0].meolutid)
            print 'alarmtext = ' + str(dfOpen[(dfOpen.alarmid == alarm)].iloc[0].alarmtext)
            print 'open at =' + str(dfOpen[(dfOpen.alarmid == alarm)].iloc[0].alarmtimeon)
            print 'still open as of = '+ str(dfOpen[(dfOpen.alarmid == alarm)].iloc[-1].alarmtimeon)

    

Start = datetime.datetime(2017,1,1)
End = datetime.datetime(2017,1,6,21,30)
print Start
print End

MEOLUT_alarms(Start, End)