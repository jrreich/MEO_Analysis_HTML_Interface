import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import csv
from collections import OrderedDict, defaultdict
import simplekml
import pypyodbc as odbc
from polycircles import polycircles
import matplotlib.pyplot as plt
from matplotlib.dates import (
    DayLocator,
    HourLocator,
    DateFormatter,
    MinuteLocator,
    drange,
)

# Set some variable

MEOLUTName = {3669: "Florida", 3385: "Hawaii", 3677: "Maryland"}
MEOList = [3669, 3385, 3677]
MEORefLoc = {
    3669: (25.6162, -80.3843),
    3385: (21.52071, -157.9963),  # Reference Beacon Locations
    3677: (38.999121, -76.853789),
}  # Goddard beacon antenna unknown
MEOLUTref = {3669: "Florida-1", 3385: "Hawaii-1", 3677: "NASA_Goddard"}
ReferenceBeacons = {
    "Florida-1": {
        "beaconId": "ADDC00202020201",
        "beaconLat": 25.61622,
        "beaconLon": -80.38422,
        "repRate": 50,
    },
    "Hawaii-1": {
        "beaconId": "AA5FC0000000001",
        "beaconLat": 21.52075,
        "beaconLon": -157.9963,
        "repRate": 50,
    },
    "California": {
        "beaconId": "ADFC000001D0033",
        "beaconLat": 34.6625,
        "beaconLon": -120.5515,
        "repRate": 50,
    },
    "Edmonton": {
        "beaconId": "A79EEE26E32E1D0",
        "beaconLat": 53.678667,
        "beaconLon": -113.315,
        "repRate": 50,
    },
    "Ottawa": {
        "beaconId": "A79EEE26E32E190",
        "beaconLat": 45.3291,
        "beaconLon": -75.6745,
        "repRate": 50,
    },
    "McMurdo": {
        "beaconId": "ADC268F8E0D3730",
        "beaconLat": -77.846033,
        "beaconLon": 166.71178,
        "repRate": 50,
    },
    "NASA_Goddard": {
        "beaconId": "ADFFFFFFFFFFFFC",
        "beaconLat": 38.99895,
        "beaconLon": -76.841599,
        "repRate": 50,
    },
    "ToulouseTCAL": {
        "beaconId": "9C6000000000001",
        "beaconLat": 43.5605,
        "beaconLon": 1.4808,
        "repRate": 30,
    },
    "ToulouseOrb": {
        "beaconId": "9C634E2AB509240",
        "beaconLat": 43.5605,
        "beaconLon": 1.4808,
        "repRate": 30,
    },
    "ToulouseMeoQMS": {
        "beaconId": "9C62BE29630F1D0",
        "beaconLat": 43.56053521,
        "beaconLon": 1.480896128,
        "repRate": 50,
    },
    "SpitsbergenMeoQMS": {
        "beaconId": "A042BE29630F190",
        "beaconLat": 78.23075718,
        "beaconLon": 15.37056787,
        "repRate": 50,
    },
    "MaspalomasMeoQMS": {
        "beaconId": "9C02BE29630F0A0",
        "beaconLat": 27.76150509,
        "beaconLon": -15.63427686,
        "repRate": 50,
    },
}

# Date Formats
timepacket_format = "%Y-%m-%d %H:%M:%S.%f"
sec_f = "%S.%f"
plot_fmt = DateFormatter("%m-%d %H:%M")
Hours = MinuteLocator(interval=30)
FiveMinutes = MinuteLocator(interval=5)


data_cols = [
    "DataType",
    "BcnId15",
    "BcnId30",
    "SourceId",
    "TimeFirst",
    "TimeLast",
    "Latitude",
    "Longitude",
    "Altitude",
    "NumBursts",
    "NumPackets",
    "DOP",
    "ExpectedHorzError",
]
data_cols = [0, 1, 2, 4, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 36, 37, 47]
ant_list = list(range(1, 7))
MEOLUTLoc = {
    3669: (25.617645, -80.383211),
    3385: (21.5244, -158.0012),  # MEOLUT Locations
    3677: (38.999121, -76.853789),
    2276: (43.56053521, 1.480896128),
}

Miami_height = 1
NSOF_height = 10
Wahiawa_height = 1

MEOLUT_antenna_locations = {
    3669: {
        1: (25.617661, -80.383376, Miami_height),
        2: (25.617754, -80.383177, Miami_height),
        3: (25.617641, -80.382956, Miami_height),
        4: (25.617425, -80.382982, Miami_height),
        5: (25.617309, -80.383185, Miami_height),
        6: (25.617440, -80.383412, Miami_height),
        7: (25.617234, -80.383470, Miami_height),
        8: (25.617200, -80.382950, Miami_height),
        9: (38.852473, -76.936823, NSOF_height),
    },
    3385: {
        1: (21.524682, -158.001442, Wahiawa_height),
        2: (21.524711, -158.001071, Wahiawa_height),
        3: (21.524414, -158.000923, Wahiawa_height),
        4: (21.524086, -158.001048, Wahiawa_height),
        5: (21.524123, -158.001459, Wahiawa_height),
        6: (21.524392, -158.001614, Wahiawa_height),
        7: (21.525110, -158.001270, Wahiawa_height),
        8: (21.525090, -158.000895, Wahiawa_height),
    },
}

sat_list = [302, 315, 324, 430, 329, 408, 422, 319, 306, 317, 422, 430]
""" see http://www.cospas-sarsat.int/en/system/space-segment-status-pro/current-space-segment-status-and-sar-payloads-pro  for full list """
all_sarsats = [
    401,
    402,
    403,
    404,
    405,
    407,
    408,
    409,
    414,
    418,
    419,
    420,
    422,
    424,
    426,
    430,
    501,
    502,
    301,
    302,
    303,
    306,
    308,
    309,
    310,
    312,
    315,
    316,
    317,
    318,
    319,
    323,
    324,
    326,
    327,
    329,
    330,
    332,
]
us_sarsats = allsats = [
    408,
    409,
    419,
    422,
    424,
    426,
    430,
    301,
    302,
    303,
    306,
    308,
    309,
    310,
    312,
    315,
    316,
    317,
    318,
    319,
    323,
    324,
    326,
    327,
    329,
    330,
    332,
]

datetime_format = "%y %j %H%M %S.%f"

USMCC = False

if USMCC == True:
    icon_list = {
        "blue_dot": "/static/icons/blue_pog.png",
        "red_dot": "/static/icons/placemark_circle_highlight.png",
        "white_dot": "/static/icons/placemark_circle.png",
        "blue_square": "/static/icons/track-none.png",
        "black_square": "/static/icons/icon61.png",
        "white_circle": "/static/icons/icon18.png",
        "green_circle": "/static/icons/icon17.png",
        "red_cross": "/static/icons/icon63.png",
        "yellow_pin": "/static/icons/ylw-blank.png",
        "red_pin": "/static/icons/red-circle.png",
        "blue_pin": "/static/icons/blu-blank.png",
        "white_arrow": "/static/icons/arrow.png",
        "green_arrow": "/static/icons/green_arrow.png",
        "circle_E": "/static/icons/iconE.png",
        "circle_M": "/static/icons/iconM.png",
        "circle_L": "/static/icons/iconL.png",
        "little_E": "/static/icons/littleE.png",
        "little_M": "/static/icons/littleM.png",
        "little_L": "/static/icons/littleL.png",
        "M": "/static/icons/M.png",
        "L": "/static/icons/L.png",
        "One": "/static/icons/1.png",
    }

else:
    icon_list = {
        "blue_dot": "http://maps.google.com/mapfiles/kml/paddle/blu-blank-lv.png",
        "red_dot": "http://maps.google.com/mapfiles/kml/pal4/icon49.png",
        "white_dot": "http://maps.google.com/mapfiles/kml/pal4/icon57.png",
        "blue_square": "http://earth.google.com/images/kml-icons/track-directional/track-none.png",
        "black_square": "http://maps.google.com/mapfiles/kml/pal4/icon56.png",
        "white_circle": "http://maps.google.com/mapfiles/kml/pal2/icon18.png",
        "green_circle": "http://maps.google.com/mapfiles/kml/pal4/icon17.png",
        "red_cross": "http://maps.google.com/mapfiles/kml/pal4/icon63.png",
        "yellow_pin": "http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png",
        "red_pin": "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
        "blue_pin": "http://maps.google.com/mapfiles/kml/paddle/blu-blank.png",
        "white_arrow": "http://maps.google.com/mapfiles/kml/shapes/arrow.png",
        "green_arrow": "https://www.google.com/mapfiles/arrow.png",
        "circle_E": "http://maps.google.com/mapfiles/kml/pal5/icon52.png",
        "circle_M": "http://maps.google.com/mapfiles/kml/pal5/icon36.png",
        "circle_L": "http://maps.google.com/mapfiles/kml/pal5/icon35.png",
        "little_E": "http://maps.google.com/mapfiles/kml/pal5/icon60l.png",
        "little_M": "http://maps.google.com/mapfiles/kml/pal5/icon36l.png",
        "little_L": "http://maps.google.com/mapfiles/kml/pal5/icon43l.png",
        "M": "http://maps.google.com/mapfiles/kml/paddle/M.png",
        "L": "http://maps.google.com/mapfiles/kml/paddle/L.png",
        "One": "http://maps.google.com/mapfiles/kml/paddle/1.png",
    }

# functions for dealing with times
def xldate_to_datetime(xldate):
    temp = datetime(1900, 1, 1)
    delta = timedelta(days=(xldate - 1))
    return temp + delta


def time_to_datetime(timein):
    if isinstance(timein, datetime):
        return timein
    if isinstance(timein, str):
        return datetime.strptime(timein, timepacket_format)
    if isinstance(timein, float):
        return xldate_to_datetime(timein)
    else:
        raise TypeError(
            "timein is unrecognized type, must be a datetime, string, or excel serial float, not a %s"
            % type(timein)
        )


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
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6373  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


# safe division (don't fail for divide by 0, return 0)
def safe_div(a, b):
    if b <= 0:
        return 0
    else:
        return a / float(b)


# function to iterate using fetchmany yield
def ResultIter(cursor, arraysize=1000):
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result


def JSON_to_csv(url, csvout):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    file_out = r"D:\Reich_disk1\Documents\Coding\Python\JSON_to_csv\test.csv"
    with open(file_out, "wb") as out_file:
        csv_w = csv.writer(out_file)
        for i_r in data:
            csv_w.writerow(i_r)
    return None


def data_source_compare(data_type, data, gt, gt_type):
    for loc in data:
        print(loc)
        if gt_type == "enc":
            if loc["enclat"] is not None:
                loc["error"] = haversine(
                    (loc["lat"], loc["lon"], loc["enclat"], loc["enclon"])
                )
            else:
                loc["error"] = None
        if gt_type == "latlon":
            loc["error"] = haversine((loc["lat"], loc["lon"], gt[0], gt[1]))
    return data
