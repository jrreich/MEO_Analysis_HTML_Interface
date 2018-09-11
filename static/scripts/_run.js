$(function () {
    app.initCesium();
    //$('#startDate')[0].valueAsDate = new Date();
    //app.homeView();

    var NSOFczml =
        [{
            "id": "document",
            "version": "1.0"
        },
        {
            "id": "NSOF",
            "parent": "lutSites",
            "name": "NSOF",
            "label": {
                "text": "NSOF",
                "horizontalOrigin": "CENTER",
                "pixelOffset": {
                    "cartesian2": [0, -20]
                },
                "fillColor": {
                    "rgba": [63, 191, 191, 255]
                }
            },
            "position": {
                "cartographicDegrees": [-76.9367, 38.8520, 10]
            },
            "description": "NOAA Satellite Operations Facility",
            "billboard": {
                "horizontalOrigin": "CENTER",
                "image": "/static/icons/NOAA_svg.png",
                "scale": 0.06,
                "outlineWidth": 2,
                "outlineColor": {
                    "rgba": [255, 255, 255, 255]
                },
                "pixelOffset": {
                    "cartesian2": [0, 10]
                }
            }
        }];
            /* ,
        "point": {
            "color": {
                "rgba":[63, 191, 191, 255]
            },
            "pixelSize" : 20
        }*/
    var LUTsczml =
        [{
            "id": "document",
            "version": "1.0"
        },
        {
            "id": "FL",
            "parent": "lutSites",
            "name": "FL",
            "label": {
                "text": "FLLUTs",
                "horizontalOrigin": "CENTER",
                "pixelOffset": {
                    "cartesian2": [0, -20]
                }
            },
            "description": "Florida ",
            "position": { "cartographicDegrees": [-80.383274, 25.617562, 0] },
            "point": {
                "color": { "rgba": [0, 0, 255, 255] },
                "pixelSize": 10
            }
        },
        {
            "id": "HI",
            "parent": "lutSites",
            "label": { "text": "HILUTs" },
            "description": "Hawaii LEO/MEOLUTs",
            "position": { "cartographicDegrees": [-158.001297, 21.524410, 0] }
        },
        {
            "id": "AK",
            "parent": "lutSites",
            "label": { "text": "FCDAS" },
            "description": "Fairbanks Command and Data Acquisition Station",
            "position": { "cartographicDegrees": [-147.515622, 64.973725, 0] }
        },
        {
            "id": "GU",
            "parent": "lutSites",
            "label": { "text": "GULUTs" },
            "description": "Guam LEO LUTs",
            "position": { "cartographicDegrees": [144.939074, 13.578298, 0] }
        }];
    app.addCzmlDataSource(NSOFczml);
    app.addCzmlDataSource(LUTsczml);
    app.updateLuts(); //have this add LUT percentages? 
    //add LEOLUT last passes 
});