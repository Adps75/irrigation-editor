// script.js

// Initialisation de la carte Leaflet centrée sur Paris
let map = L.map('map').setView([48.8566, 2.3522], 13);

// --- FONDS DE CARTE ---

// 1) Fond OSM par défaut
let osmBase = L.tileLayer(
  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
  {
    attribution: "© OpenStreetMap contributors",
    maxZoom: 19
  }
).addTo(map);

// 2) Fond Satellite IGN (sans clé)
let satelliteIGN = L.tileLayer(
  "https://wxs.ign.fr/geoportail/wmts?" +
  "SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=ORTHOIMAGERY.ORTHOPHOTOS" +
  "&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/jpeg",
  {
    attribution: "IGN - Geoportail",
    tileSize: 256,
    zoomOffset: 0,
    minZoom: 2,
    maxZoom: 19
  }
);

// 3) Fond Cadastre IGN (sans clé)
let cadastreIGN = L.tileLayer(
  "https://wxs.ign.fr/geoportail/wmts?" +
  "SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=CADASTRAL.PARCELS" +
  "&STYLE=PCI&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/png",
  {
    attribution: "IGN - Cadastre",
    tileSize: 256,
    zoomOffset: 0,
    minZoom: 2,
    maxZoom: 19,
    opacity: 0.7
  }
);

// Contrôle de couches pour basculer entre les fonds de carte
let baseMaps = {
  "Plan (OSM)": osmBase,
  "Satellite IGN": satelliteIGN,
  "Cadastre IGN": cadastreIGN
};
L.control.layers(baseMaps).addTo(map);

// --- GESTION DES TRACÉS ---

let pointsEau = [];
let zones = [];

/**
 * Fonction permettant d'ajouter un point d'eau (Marker) sur la carte
 * L'utilisateur clique pour placer le point, et celui-ci est draggable
 */
function addPointEau() {
  map.once('click', function (e) {
    let marker = L.marker([e.latlng.lat, e.latlng.lng], { draggable: true }).addTo(map);

    // Stockage initial
    pointsEau.push({ lat: e.latlng.lat, lng: e.latlng.lng });

    // Mise à jour des coordonnées lorsque l'utilisateur déplace le marker
    marker.on('dragend', function (event) {
      let newPos = event.target.getLatLng();
      // Retrouver l'ancien index
      let index = pointsEau.findIndex(p => p.lat === e.latlng.lat && p.lng === e.latlng.lng);
      if (index !== -1) {
        pointsEau[index] = { lat: newPos.lat, lng: newPos.lng };
      }
    });
  });
}

/**
 * Exemple minimal pour tracer un polygone "à la main"
 * (Ex: l'utilisateur clique successivement, puis dblclick termine la zone)
 */
let currentPolygon = [];
let polylineLayer = null;
let polygonLayer = null;
let drawing = false;

function startDrawingZone() {
  drawing = true;
  currentPolygon = [];

  // Si on a déjà un layer d'affichage temporaire, on le retire
  if (polylineLayer) {
    map.removeLayer(polylineLayer);
    polylineLayer = null;
  }
  if (polygonLayer) {
    map.removeLayer(polygonLayer);
    polygonLayer = null;
  }

  map.on('click', onMapClickZone);
  map.on('dblclick', onMapDblClickZone);
}

function onMapClickZone(e) {
  if (!drawing) return;
  currentPolygon.push([e.latlng.lat, e.latlng.lng]);

  // Mise à jour visuelle
  if (polylineLayer) {
    map.removeLayer(polylineLayer);
  }
  polylineLayer = L.polyline(currentPolygon, { color: 'red' }).addTo(map);
}

function onMapDblClickZone(e) {
  if (!drawing) return;
  drawing = false;

  // Ajouter le dernier point
  currentPolygon.push([e.latlng.lat, e.latlng.lng]);

  // Fermer la zone en reliant le dernier point au premier
  if (currentPolygon.length >= 3) {
    polygonLayer = L.polygon(currentPolygon, { color: 'blue', fillOpacity: 0.3 }).addTo(map);
    
    // Sauvegarder la zone
    let zoneCoords = currentPolygon.map(coord => {
      return { lat: coord[0], lng: coord[1] };
    });
    zones.push({ 
      id: zones.length + 1,
      coords: zoneCoords
    });
  }

  // Nettoyage
  if (polylineLayer) {
    map.removeLayer(polylineLayer);
    polylineLayer = null;
  }
  currentPolygon = [];

  // Retirer les listeners
  map.off('click', onMapClickZone);
  map.off('dblclick', onMapDblClickZone);
}

