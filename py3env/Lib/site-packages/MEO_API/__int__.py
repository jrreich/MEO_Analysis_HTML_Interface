import pypyodbc
import numpy as np
import czml



def api_site_query(Sitenum, servername = 'localhost', databasename='mccoperational', **kwargs):
    if 'sql_login' in kwargs:
        conn = pypyodbc.connect(r'Driver={FreeTDS};Server='+servername+';Database='+databasename+'; UID='+UID+'; PWD=' + PWD)
    else:
        conn = pypyodbc.connect(r'Driver={SQL Server};Server='+servername+';Database='+databasename+';Trusted_Connection=yes;',readonly=True)
    UseMCC = True
       
    fieldlist = ['BcnId15', 'Closed', 'OpenTime', 'CloseTime']
    sql_query_field_list = ', '.join(fieldlist)
    print sql_query_field_list
    sql_query = ('select top 1 ' + sql_query_field_list + ' FROM '
                'AlertSiteSum WHERE '
                'AlertSiteNum = ? '
                'ORDER BY TimeLast '
                )
    params=[Sitenum]
    c = conn.cursor()
    c.execute(sql_query, params)
    out = c.fetchall()
    for i in out:
        r = {fieldlist[j]: value for j, value in enumerate(i)}
    print r
    return r






     
    
