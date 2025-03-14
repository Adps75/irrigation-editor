// Initialisation de la carte
let map = L.map('map').setView([48.8566, 2.3522], 13);

// Définition des couches de carte IGN (sans clé API)
let satellite = L.tileLayer(
    "https://wxs.ign.fr/pratique/geoportail/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile" +
    "&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}" +
    "&FORMAT=image/jpeg",
    { attribution: "IGN - Geoportail", maxZoom: 19 }
);

let cadastre = L.tileLayer(
    "https://wxs.ign.fr/pratique/geoportail/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile" +
    "&LAYER=CADASTRAL.PARCELS&STYLE=PCI&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}" +
    "&FORMAT=image/png",
    { attribution: "IGN - Cadastre", maxZoom: 19, opacity: 0.7 }
);

// Ajout d'un fond de carte par défaut
let baseMaps = {
    "Satellite IGN": satellite,
    "Cadastre IGN": cadastre
};

// Ajout du contrôle Leaflet pour basculer entre les fonds
L.control.layers(baseMaps).addTo(map);

// Activation du fond satellite par défaut
satellite.addTo(map);

// Gestion des tracés
let pointsEau = [];
let zones = [];
let drawing = false;
let currentPolygon = [];

// Ajout d'un point d'eau
function addPointEau() {
    map.once('click', function (e) {
        let marker = L.marker([e.latlng.lat, e.latlng.lng], { draggable: true }).addTo(map);
        pointsEau.push({ lat: e.latlng.lat, lng: e.latlng.lng });

        marker.on('dragend', function (event) {
            let newPos = event.target.getLatLng();
            let index = pointsEau.findIndex(p => p.lat === e.latlng.lat && p.lng === e.latlng.lng);
            pointsEau[index] = { lat: newPos.lat, lng: newPos.lng };
        });
    });
}

// Démarrer le tracé des zones
function startDrawing() {
    drawing = true;
    currentPolygon = [];
    alert("Cliquez sur la carte pour dessiner une zone, double-cliquez pour terminer.");

    map.on('click', function (e) {
        if (!drawing) return;
        currentPolygon.push([e.latlng.lat, e.latlng.lng]);
        L.circleMarker([e.latlng.lat, e.latlng.lng], { radius: 3, color: 'blue' }).addTo(map);
    });

    map.on('dblclick', function () {
        if (currentPolygon.length > 2) {
            let polygon = L.polygon(currentPolygon, { color: 'green' }).addTo(map);
            zones.push({ coords: currentPolygon });
        }
        drawing = false;
        map.off('click');
    });
}

// Réinitialiser la carte
function clearMap() {
    map.eachLayer(layer => {
        if (!!layer.toGeoJSON) {
            map.removeLayer(layer);
        }
    });
    pointsEau = [];
    zones = [];
}

// Envoyer les données au backend
function sendData() {
    if (pointsEau.length === 0 || zones.length === 0) {
        alert("Ajoutez au moins un point d’eau et une zone avant d’envoyer les données !");
        return;
    }

    let data = {
        address: "Adresse Test",
        zones: zones,
        points_eau: pointsEau,
        pression: 3.5,
        zoom: map.getZoom(),
        fill_time: 10
    };

    fetch("http://127.0.0.1:5000/generate_plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => console.log("Plan généré :", result))
    .catch(error => console.error("Erreur :", error));
}
