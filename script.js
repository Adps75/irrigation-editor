let map = L.map('map').setView([48.8566, 2.3522], 13);

let satellite = L.tileLayer(
    "https://wxs.ign.fr/pratique/geoportail/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile" +
    "&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}" +
    "&FORMAT=image/jpeg", { attribution: "IGN - Geoportail", maxZoom: 19 });

let cadastre = L.tileLayer(
    "https://wxs.ign.fr/pratique/geoportail/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile" +
    "&LAYER=CADASTRAL.PARCELS&STYLE=PCI&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}" +
    "&FORMAT=image/png", { attribution: "IGN - Cadastre", maxZoom: 19, opacity: 0.7 });

satellite.addTo(map);

function toggleSatellite() {
    map.addLayer(satellite);
}

function toggleCadastre() {
    map.addLayer(cadastre);
}

let pointsEau = [];
let zones = [];

function addPointEau() {
    map.on('click', function (e) {
        let marker = L.marker([e.latlng.lat, e.latlng.lng]).addTo(map);
        pointsEau.push({ lat: e.latlng.lat, lng: e.latlng.lng });
        map.off('click');
    });
}

function sendData() {
    let data = { address: "Adresse Test", zones: zones, points_eau: pointsEau, pression: 3.5, zoom: map.getZoom(), fill_time: 10 };

    fetch("http://127.0.0.1:5000/generate_plan", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data)
    })
    .then(response => response.json()).then(result => console.log("Plan généré :", result))
    .catch(error => console.error("Erreur :", error));
}
