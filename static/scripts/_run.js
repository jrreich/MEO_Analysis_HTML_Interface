$(function () {
    console.log(app);
    app.initCesium();
	$('#startDate')[0].valueAsDate = new Date();
    
    
    var LUTsczml =
        [{"id" : "document",
        "version" : "1.0"
        },
        {"id" : "NSOF",
        "name" : "NSOF",
        "label": {
            "text":"NSOF",
            "horizontalOrigin": "CENTER",
            "pixelOffset": {
                "cartesian2" : [0, -20]
            },
            "fillColor": {
                "rgba": [63, 191, 191, 255]
            }
        },
        "position": {
            "cartographicDegrees":[-76.93677,38.850913,17]
        },
        "description":"NOAA Satellite Operations Facility",
        "billboard":{
            "horizontalOrigin":"CENTER",
            "image":"/static/icons/NOAA_svg.png",
            "scale":0.06,
            "outlineWidth": 2,
            "outlineColor": {
                "rgba":[255, 255, 255, 255] 
            },           
            "pixelOffset": {
                "cartesian2": [ 0, 10 ]
            }
        }/* ,
        "point": {
            "color": {
                "rgba":[63, 191, 191, 255]
            },
            "pixelSize" : 20
        }*/
        },
        {"id" : "FL",
        "name" : "FL",
        "label": {
            "text":"FLLUTs",
            "horizontalOrigin": "CENTER",
            "pixelOffset": {
                "cartesian2" : [0, -20]
            }
        },
        "description":"Florida LEO/MEOLUTs",
        "position":{"cartographicDegrees":[-80.383274,25.617562,0]},
        "point": {
            "color": { "rgba": [0,0,255,255] },
            "pixelSize" : 20
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
        app.addCzmlDataSource(LUTsczml);
})