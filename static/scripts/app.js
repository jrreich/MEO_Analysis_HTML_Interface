var app = (function () {
    var viewer = {};
    var _initCesium = function () {
        Cesium.BingMapsApi.defaultKey = 'AroVSp3EEqOsbIrQmLLaavG0aGanIvBJ3iVmsayjLrmWFcU5KSCx1zCLE5AkByXq'; // For use in this application only. Do not reuse!
        viewer = new Cesium.Viewer('cesiumContainer', {
            imageryProvider : new Cesium.ArcGisMapServerImageryProvider({
                url : 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer',
                credit : 'testing credits'
            }),
            //Use standard Cesium terrain
            /*
            terrainProvider : new Cesium.CesiumTerrainProvider({
                url : 'https://assets.agi.com/stk-terrain/v1/tilesets/world/tiles'
            }),
            baseLayerPicker : false
            */
            });
        
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

        //return {
        //viewer: viewer
        //};
    };

    var _realTime = function () {
        var currentTime = new Date();
        $.ajax({
            url: "/stream",
            type: "GET",
            success: function (result,status){
				if (result !== "") {
					_addCzmlDataSource(result);
				}
				else{
					alert("No Passes");
				}
			},
			error: function(error){
				alert(error.responseText);
			}
        });

        //_addCzmlDataSource('/api/czml/site/'+siteNum.value);
    };
    var _addSite = function () {
        var siteNum = $('#siteNumber')[0];
        var czmlDataSource = Cesium.CzmlDataSource.load("/api/czml/site/"+siteNum.value);        
        viewer.dataSources.add(czmlDataSource).then(function() {
            viewer.flyTo(czmlDataSource, 
                {offset : new Cesium.HeadingPitchRange(0, (-Math.PI / 2), 200000)}
            );        
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
        });

        //_addCzmlDataSource('/api/czml/site/'+siteNum.value);
    };
    
    var _addCzmlDataSource = function (data) {
        czmlDataSource = new Cesium.CzmlDataSource.load(data);
        viewer.dataSources.add(czmlDataSource);
    };
    
    var _addKmlDataSource = function (data) {
        var kmlDataSource = Cesium.KmlDataSource.load(data);
        viewer.dataSources.add(kmlDataSource);
    };

    var _homeView = function () {
        var centerAOR = viewer.entities.getById('USAOR_Center');
        viewer.flyTo(centerAOR, 
            {offset : new Cesium.HeadingPitchRange(0, (-Math.PI / 2), 20000000)}
        )
    };
    
    var _setCurrentTime = function () {
        viewer.clock.clockStep = Cesium.ClockStep.SYSTEM_CLOCK;
    };
    
    var _toggleLuts = function() {
        var lutEntity = czmlDataSource.entities.getById('NSOF')
        lutEntity.show = !lutEntity.show
    };
          
        
    return {
        initCesium: _initCesium,
        realTime: _realTime,
        addSite: _addSite,
        addCzmlDataSource: _addCzmlDataSource,
        addKmlDataSource: _addKmlDataSource,
        homeView: _homeView,
        setCurrentTime: _setCurrentTime,
        toggleLuts: _toggleLuts
    };
})();