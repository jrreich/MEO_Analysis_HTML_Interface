var app = (function () {
    //var viewer = {};
    var _initCesium = function () {
        Cesium.BingMapsApi.defaultKey = 'AroVSp3EEqOsbIrQmLLaavG0aGanIvBJ3iVmsayjLrmWFcU5KSCx1zCLE5AkByXq'; // For use in this application only. Do not reuse!
        Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIzNTBmODQyNi1mODlhLTRjMGYtYTQ3Zi1kMzdiNGIyZmQyN2IiLCJpZCI6MTA3NjgsInNjb3BlcyI6WyJhc3IiLCJnYyJdLCJpYXQiOjE1NTczMzI4NDF9.CjdCeI3wLGmDhHNf_jEPghiVrcM7cV8RvjL9HtqcY1c';
        viewer = new Cesium.Viewer('cesiumContainer', {
            imageryProvider: new Cesium.ArcGisMapServerImageryProvider({
                url: 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer',
                credit: 'testing credits'
            })
        });

        var cartographic = new Cesium.Cartographic();
        var cartesian = new Cesium.Cartesian3();
        var camera = viewer.scene.camera;
        var ellipsoid = viewer.scene.mapProjection.ellipsoid;
        var toolbar = document.getElementById('toolbar');
        toolbar.innerHTML = '<div id="hud"></div>' +
            '<button type="button" class="cesium-button" id="h1km">1km height</button>' +
            '<button type="button" class="cesium-button" id="h10km">10km height</button>' +
            '<button type="button" class="cesium-button" id="h500km">500km height</button>';

        toolbar.setAttribute('style', 'background: rgba(42,42,42,0.9); border-radius: 5px;');

        var hud = document.getElementById('hud');

        viewer.clock.onTick.addEventListener(function (clock) {
            ellipsoid.cartesianToCartographic(camera.positionWC, cartographic);
            hud.innerHTML =
                'Lon: ' + Cesium.Math.toDegrees(cartographic.longitude).toFixed(3) + ' deg<br/>' +
                'Lat: ' + Cesium.Math.toDegrees(cartographic.latitude).toFixed(3) + ' deg<br/>' +
                'Alt: ' + (cartographic.height * 0.001).toFixed(1) + ' km';
        });

        function setHeightKm(heightInKilometers) {
            ellipsoid.cartesianToCartographic(camera.position, cartographic);
            cartographic.height = heightInKilometers * 1000;  // convert to meters
            ellipsoid.cartographicToCartesian(cartographic, cartesian);
            camera.position = cartesian;
        }

        document.getElementById('h1km').addEventListener('click', function () {
            setHeightKm(1);
        }, false);

        document.getElementById('h10km').addEventListener('click', function () {
            setHeightKm(10);
        }, false);

        document.getElementById('h500km').addEventListener('click', function () {
            setHeightKm(500);
        }, false);
        //viewer.extend(Cesium.viewerDragDropMixin);
        czmlDataSource = new Cesium.CzmlDataSource();
        viewer.dataSources.add(czmlDataSource);
        kmlDataSource = new Cesium.KmlDataSource();
        viewer.dataSources.add(kmlDataSource);
            //Use standard Cesium terrain
            /*
            terrainProvider : new Cesium.CesiumTerrainProvider({
                url : 'https://assets.agi.com/stk-terrain/v1/tilesets/world/tiles'
            }),
            baseLayerPicker : false
            */
           
        
        var options = {
            camera : viewer.scene.camera,
            canvas : viewer.scene.canvas
        };
        var centerAOR = viewer.entities.add({
            id : 'USAOR_Center',
            name : 'USAOR_Center',
            label : 'center',
            position : Cesium.Cartesian3.fromDegrees(-118,34),
            point : {
                show : 'False'
            }
        });
        viewer.extend(Cesium.viewerDragDropMixin);
        viewer.dropError.addEventListener(function(viewerArg, source, error) {
            window.alert('Error processing ' + source + ':' + error);
        });


    };

    var _reset = function () {
        czmlDataSource.entities.removeAll();
        kmlDataSource.entities.removeAll();
    };
    var _realTime = function () {
        var currentTime = new Date();
        $.ajax({
            url: "/stream",
            type: "GET",
            success: function (result, status) {
                if (result !== "") {
                    _addCzmlDataSource(result);
                }
                else {
                    alert("No Passes");
                }
            },
            error: function (error) {
                alert(error.responseText);
            }
        });
        if ($("#realtimesites").length < 1) {
            //$('<br />').appendTo('#buttonHolder');
            $('<input />', {
                type: 'checkbox', id: 'realtimesites', name: 'realtimesites', checked: 'True'
            })
                .change(function () {
                    var sitechanged = $(this).prop('name');
                    _toggleEntity(sitechanged);
                })
                .insertBefore('#realTimeSiteButton');
        }
    };
    var _addMeoSats = function () {
        _addCzmlDataSource(baseUrl + "api/czml/meo/orbit");
        if ($("#meoSats").length < 1) {
            $('<input />', {
                type: 'checkbox', id: 'meoSats', name: 'meoSats', checked: 'True'
            })
                .change(function () {
                    var sitechanged = $(this).prop('name');
                    _toggleEntity(sitechanged);
                })
                .insertBefore('#meoSatButton');
        }
    };
    var _addMeoPer = function (meolist) {
        $.each(meolist, function (ind, meo) {
            _addCzmlDataSource(baseUrl + "api/czml/meo/per/" + meo);
            if ($("#meoPer").length < 1) {
                $('<input />', {
                    type: 'checkbox', id: 'meoPer', name: 'meoPer-' + meo, checked: 'True'
                })
                    .change(function () {
                        var sitechanged = $(this).prop('name');
                        _toggleEntity(sitechanged);
                    })
                    .insertBefore('#meoPerButton');
            }
        });
    };
        
        //_addCzmldataSource('/api/czml/site/'+siteNum.value);
    var _addSite = function () {
        var siteNum = $('#siteNumber')[0];
        //czmlSiteDataSource = new Cesium.CzmlDataSource();
        //viewer.dataSources.add(czmlSiteDataSource);
        //czmlSiteDataSource.load("/api/czml/site/" + siteNum.value);     
        if (!$('#leo' + siteNum.value).length) {
            //Add MEO Input Locations
            //_addCzmlDataSource("/api/czml/site/" + siteNum.value);
            _addCzmlDataSource("/api/czml/site/meo/" + siteNum.value);
            $('<br />').appendTo('#siteButtonHolder');
            $('<input />', { type: 'checkbox', id: 'meo' + siteNum.value, name: 'meo' + siteNum.value, checked: 'True' })
                .change(function () {
                    var sitechanged = $(this).prop('name');
                    _toggleEntity(sitechanged);
                })
                .appendTo('#siteButtonHolder');
            $('<label />', { for: 'meo'+ siteNum.value, text: '  meo -'+siteNum.value }).appendTo('#siteButtonHolder');

            //Add LEO Locations
            _addCzmlDataSource("/api/czml/site/leo/" + siteNum.value);
            $('<br />').appendTo('#siteButtonHolder');
            $('<input />', { type: 'checkbox', id: 'leo' + siteNum.value, name: 'leo' + siteNum.value, checked: 'True' })
                .change(function () {
                    var sitechanged = $(this).prop('name');
                    _toggleEntity(sitechanged);
                })
                .appendTo('#siteButtonHolder');
            $('<label />', { for: 'leo'+ siteNum.value, text: '  leo -'+siteNum.value }).appendTo('#siteButtonHolder');
        }
        if (!$('#comp' + siteNum.value).length) {
            _addCzmlDataSource("/api/czml/site/comp/" + siteNum.value);
            //Add Composite Locations
            $('<br />').appendTo('#siteButtonHolder');
            $('<input />', { type: 'checkbox', id: 'comp' + siteNum.value, name: 'comp' + siteNum.value, checked: 'True' })
                .change(function () {
                    var sitechanged = $(this).prop('name');
                    _toggleEntity(sitechanged);
                })
                .appendTo('#siteButtonHolder');
            $('<label />', { for: 'comp'+siteNum.value, text: 'comp -' + siteNum.value }).appendTo('#siteButtonHolder');

        }
        viewer.flyTo(czmlDataSource.entities.getById('comp'+siteNum.value),
            { offset: new Cesium.HeadingPitchRange(0, (-Math.PI / 2), 200000) }
        );
        viewer.selectedEntity = czmlDataSource.entities.getById('comp'+siteNum.value);
        $('.cesium-viewer-infoBoxContainer').show();
    };
        
        /*
        $.ajax({
            url: "/api/czml/site/"+siteNum.value,
            type: "GET",
            success: function (result,status){
                console.log(result);
				if (result !== "") {
					_addCzmlDataSource(result);
                    viewer.flyTo(_czmlDataSource, options)
				}
				else{
					alert("No Passes");
				}
			},
			error: function(error){
				alert(error.responseText);
			}
            */

        //_addCzmlDataSource('/api/czml/site/'+siteNum.value);
    
    var _addCzmlDataSource = function (data) {
        viewer.dataSources.add(czmlDataSource.process(data));
	};
    
    var _addKmlDataSource = function (data) {
        alert(baseUrl + data);
        viewer.dataSources.add(kmlDataSource.process(baseUrl + data));
    };

    var _homeView = function () {
        var centerAOR = viewer.entities.getById('USAOR_Center');
        viewer.flyTo(centerAOR,
            { offset: new Cesium.HeadingPitchRange(0, (-Math.PI / 2), 20000000) }
        );
    };
    
    var _setCurrentTime = function () {
        viewer.clock.clockStep = Cesium.ClockStep.SYSTEM_CLOCK;
    };
    
    var _toggleEntity = function (id_list) {
        var entity;
        if (Array.isArray(id_list)) {
            for (i = 0; i < id_list.length; i++) {

                entity = czmlDataSource.entities.getById(id_list[i]);

                //alert(lutEntity.id);
                //var testLutEntity = viewer.dataSources.entities.getById('NSOF');
                //alert(testLutEntity.name);
                entity.show = !entity.show;
            }
        }
        else {
            entity = czmlDataSource.entities.getById(id_list);
            console.log(id_list);
            entity.show = !entity.show;
        }
    };

    var _updateLuts = function () {
        $.getJSON(baseUrl + "api/MEO/location_accuracy/3669", function (data) {
        })
            .done(function (data) {
            });
    };   

    var _showLatLon = function () {
        // Mouse over the globe to see the cartographic position
        var handler;
        var scene = viewer.scene;
        var entity = viewer.entities.add({
            label: {
                show: false,
                showBackground: true,
                font: '14px monospace',
                horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
                verticalOrigin: Cesium.VerticalOrigin.TOP,
                pixelOffset: new Cesium.Cartesian2(15, 0)
            }
        });
        handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);
        handler.setInputAction(function (movement) {
            var cartesian = viewer.camera.pickEllipsoid(movement.endPosition, scene.globe.ellipsoid);
            if (cartesian) {
                var cartographic = Cesium.Cartographic.fromCartesian(cartesian);
                var longitudeString = Cesium.Math.toDegrees(cartographic.longitude).toFixed(4);
                var latitudeString = Cesium.Math.toDegrees(cartographic.latitude).toFixed(4);

                entity.position = cartesian;
                entity.label.show = true;
                entity.label.text =
                    'Lon: ' + ('   ' + longitudeString).slice(-9) + '\u00B0' +
                    '\nLat: ' + ('   ' + latitudeString).slice(-9) + '\u00B0';
            } else {
                entity.label.show = false;
            }
        }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);
    };

    var _doubleClickSelect = function () {
        viewer.screenSpaceEventHandler.removeInputAction(Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);

        var handler2 = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
        handler2.setInputAction(function (click) {
            event.preventDefault();//OR click.preventDefault();
            var pickedObject = viewer.scene.pick(click.position);
            if (Cesium.defined(pickedObject)) {
                
                //var czmlSite = new Cesium.CzmlDataSource();
                //viewer.dataSources.add(czmlSite);
                var pickedId = pickedObject.id._id;
                $("#siteNumber").val(pickedId);
                _addSite();
                //czmlSite.load('/api/czml/site/' + pickedObject.id._id).then(function () {
                //    viewer.flyTo(czmlSite, {
                //       duration: 5,
                //        offset: new Cesium.HeadingPitchRange(0, -Math.PI / 4, 150000)
                //    });
                //});
                //if (pickedObject.id._name) {
                //   $('.cesium-viewer-infoBoxContainer').show();
                //    flyTo(pickedObject.id._id);
                //    console.log('showing something in the info box')
                //}
            }
        }, Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);
    };

    var _handleKeyPress = function (e) {
        var key = e.keyCode || e.which;
        if (key === 13) {
            _addSite();
        }
    };

    return {
        initCesium: _initCesium,
        reset: _reset,
        realTime: _realTime,
        addSite: _addSite,
        addCzmlDataSource: _addCzmlDataSource,
        addKmlDataSource: _addKmlDataSource,
        homeView: _homeView,
        setCurrentTime: _setCurrentTime,
        toggleEntity: _toggleEntity,
        addMeoSats: _addMeoSats,
        addMeoPer: _addMeoPer,
        updateLuts: _updateLuts,
        showLatLon: _showLatLon,
        handleKeyPress: _handleKeyPress,
        doubleClickSelect: _doubleClickSelect
    };
})();