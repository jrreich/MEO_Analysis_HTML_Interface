import decodehex2
import definitions
from decodefunctions import is_number, dec2bin

def decode(hexcode):
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
    else:
        outdict['lat'] = None
        outdict['lon'] = None



    return outdict