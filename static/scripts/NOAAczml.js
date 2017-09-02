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

var czmlSource = new Cesium.CzmlDataSource();
viewer.dataSources.add(czmlSource);
czmlSource.load(LUTsczml);

var czmlStreamStartSource = new Cesium.CzmlDataSource();
viewer.dataSources.add(czmlStreamStartSource);
czmlStreamStartSource.load('/stream')

viewer.screenSpaceEventHandler.removeInputAction(Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);

var handler2 = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
handler2.setInputAction(function(click) {
        event.preventDefault();//OR click.preventDefault();
        var pickedObject = viewer.scene.pick(click.position);
        if (Cesium.defined(pickedObject)) {
                var czmlSite = new Cesium.CzmlDataSource();
                viewer.dataSources.add(czmlSite);
                czmlSite.load('/api/czml/site/' + pickedObject.id._id).then(function() {
                    viewer.flyTo(czmlSite, {
                        duration: 5,
                        offset: new Cesium.HeadingPitchRange(0, -Math.PI / 4, 150000)
                    });
                });
                if(pickedObject.id._name) {
                        $('.cesium-viewer-infoBoxContainer').show();
                        flyTo(pickedObject.id._id);
                        console.log('showing something in the info box')
                }
        }
}, Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);

/*
var czmlSite = new Cesium.CzmlDataSource();
viewer.dataSources.add(czmlSite);
czmlSite.load('/api/czml/site/' + sitenum)
*/