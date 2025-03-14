let map = L.map('map').setView([48.8566, 2.3522], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

let pointsEau = [];
let zones = [];
let drawing = false;
let currentPolygon = [];

map.on('zoomend', function() {
    console.log("Zoom actuel :", map.getZoom());
});

function addPointEau() {
    map.on('click', function (e) {
        let marker = L.marker([e.latlng.lat, e.latlng.lng], { draggable: true }).addTo(map);
        pointsEau.push({ lat: e.latlng.lat, lng: e.latlng.lng });

        marker.on('dragend', function (event) {
            let newPos = event.target.getLatLng();
            let index = pointsEau.findIndex(p => p.lat === e.latlng.lat && p.lng === e.latlng.lng);
            pointsEau[index] = { lat: newPos.lat, lng: newPos.lng };
        });

        map.off('click');
    });
}

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

function sendData() {
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
