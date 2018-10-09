var serverAPIURL = 'http://127.0.0.1:8001/';

var EsriWorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});

var myMap = L.map('map', {
   center: [14.0583, 108.2772],
   zoom: 7,
   layers: [EsriWorldImagery]
});

var loadLayerFromGEE = function (data) {
    var layer = L.tileLayer('https://earthengine.googleapis.com/map/' + data.eeMapId + '/{z}/{x}/{y}?token=' + data.eeMapToken);
    layer.addTo(myMap);
};

// Map Data
$.ajax({
    'url' : serverAPIURL,
    'type' : 'GET',
    'success' : function (data) {
        loadLayerFromGEE(data);
    }
});

// Download URL
$.ajax({
    'url' : serverAPIURL + 'download-url',
    'type' : 'GET',
    'data' : {
        'start' : '2008-01-01',
        'end'   : '2012-11-30'
    },
    'success' : function (data) {
        console.log('your download url is: '+ data);
        alert('your download url is: \n'+ data);
    }
});
