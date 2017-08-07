var LUTsczml =
    [{"id" : "document",
    "version" : "1.0"
    },
    {"id" : "NSOF",
    "label":{"text":"NSOF"},
        "position":{"cartographicDegrees":[-76.93677,38.850913,17]},
        "description":"NOAA Satellite Operations Facility",
        "billboard":{
            "color":{
                "rgba":[
                 0,255,255,255
                ]
            },
            "horizontalOrigin":"CENTER",
            "image":"/static/icons/NOAA_logo.svg.png",
            "scale":0.05,
        },
    },
    {"id" : "FL",
    "label":{"text":"FLLUTs"},
        "description":"Florida LEO/MEOLUTs",
        "position":{"cartographicDegrees":[-80.383274,25.617562,0]},
        "point": {
            "color": { "rgba": [0,0,255,255] },
        }
    },
    {"id" : "HI",
    "label":{"text":"HILUTs"},
        "description":"Hawaii LEO/MEOLUTs",
        "position":{"cartographicDegrees":[-158.001297,21.524410,0]},
    },
    {"id" : "AK",
    "label":{"text":"FCDAS"},
        "description":"Fairbanks Command and Data Acquisition Station",
        "position":{"cartographicDegrees":[-147.515622,64.973725,0]},
    },
    {"id" : "GU",
    "label":{"text":"GULUTs"},
        "description":"Guam LEO LUTs",
        "position":{"cartographicDegrees":[144.939074,13.578298,0]},
    }];

var czmlSource = new Cesium.CzmlDataSource();
viewer.dataSources.add(czmlSource);
czmlSource.load(LUTsczml);