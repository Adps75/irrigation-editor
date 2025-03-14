document.addEventListener("DOMContentLoaded", function () {
    var map = L.map('map').setView([48.8566, 2.3522], 13); // Paris par défaut

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    var drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polygon: true,
            marker: true, // Ajout d'un point d'eau principal
            circle: false,
            rectangle: true,
            polyline: false
        }
    });

    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, function (event) {
        var layer = event.layer;
        drawnItems.addLayer(layer);
    });

    document.getElementById('saveData').addEventListener('click', function () {
        var data = [];
        drawnItems.eachLayer(function (layer) {
            if (layer instanceof L.Polygon || layer instanceof L.Rectangle) {
                data.push({ type: 'zone', coords: layer.getLatLngs() });
            } else if (layer instanceof L.Marker) {
                data.push({ type: 'point_eau', coords: layer.getLatLng() });
            }
        });

        console.log("Données enregistrées :", JSON.stringify(data));

        // Envoi des données à Bubble via postMessage
        if (window.parent.postMessage) {
            window.parent.postMessage({ type: "leaflet_data", content: data }, "*");
        }

        alert("Les données ont été enregistrées et envoyées à Bubble !");
    });
});
