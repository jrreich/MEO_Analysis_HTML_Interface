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
            terrainProvider : new Cesium.CesiumTerrainProvider({
                url : 'https://assets.agi.com/stk-terrain/v1/tilesets/world/tiles'
            }),
            baseLayerPicker : false
            });
        
        var options = {
            camera : viewer.scene.camera,
            canvas : viewer.scene.canvas
        };
        
        viewer.extend(Cesium.viewerDragDropMixin);
        viewer.dropError.addEventListener(function(viewerArg, source, error) {
            window.alert('Error processing ' + source + ':' + error);
        });
    };
    var _realTime = function () {
        var currentTime = new Date();
        console.log(currentTime);
        $.ajax({
            url: "/stream",
            type: "GET",
            success: function (result,status){
                console.log(result);
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
        console.log(siteNum.value);
        $.ajax({
            url: "/api/czml/site/"+siteNum.value,
            type: "GET",
            success: function (result,status){
                console.log(result);
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
    
    var _addCzmlDataSource = function (data) {
        var czmlDataSource = Cesium.CzmlDataSource.load(data);
        viewer.dataSources.add(czmlDataSource);
    };
        
    return {
        initCesium: _initCesium,
        realTime: _realTime,
        addSite: _addSite,
        addCzmlDataSource: _addCzmlDataSource,
    };
})();