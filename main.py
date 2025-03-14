/************************************************************
  Initialisation de la carte Leaflet centrée sur Paris
*************************************************************/
let map = L.map('map').setView([48.8566, 2.3522], 13);

/************************************************************
  1) Fond de carte OpenStreetMap (OSM)
     - Utilisé par défaut
*************************************************************/
let osmBase = L.tileLayer(
  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
  {
    attribution: "© OpenStreetMap contributors",
    maxZoom: 19
  }
).addTo(map);

/************************************************************
  2) Fond de carte IGN SCAN 25 via la Géoplateforme
     - Accès privé + clé partagée ign_scan_ws
     - URL et LAYER à adapter selon le SCAN souhaité
*************************************************************/
/**
 * L’URL basique indiquée dans la doc mentionne:
 *   https://data.geopf.fr/private/wmts?SERVICE=WMTS&VERSION=1.0.0
 *   &REQUEST=GetTile
 *   &apikey=ign_scan_ws
 * Puis vous ajoutez &LAYER=...&TILEMATRIXSET=PM&TILEMATRIX={z} etc.
 *
 * Dans l'exemple ci-dessous, on suppose que la couche "SCAN25FRA" existe.
 * Vous pouvez inspecter le GetCapabilities pour trouver le bon nom de LAYER.
 */
let scan25IGN = L.tileLayer(
  "https://data.geopf.fr/private/wmts?" +
    "SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0" +
    "&LAYER=SCAN25FRA" +                 // <-- Nom de couche à vérifier (ex: SCAN25FRA)
    "&STYLE=normal" +
    "&TILEMATRIXSET=PM" +
    "&TILEMATRIX={z}" +
    "&TILEROW={y}" +
    "&TILECOL={x}" +
    "&FORMAT=image/png" +
    "&apikey=ign_scan_ws",              // <-- Clé partagée IGN pour usage gratuit
  {
    attribution: "IGN - SCAN25",
    tileSize: 256,
    minZoom: 2,
    maxZoom: 19
  }
);

/************************************************************
  Contrôle de couches : l’utilisateur peut basculer
  entre OSM et le SCAN IGN
*************************************************************/
let baseMaps = {
  "OSM (par défaut)": osmBase,
  "IGN SCAN 25": scan25IGN
};
L.control.layers(baseMaps).addTo(map);

/************************************************************
  GESTION DES POINTS D’EAU
  - L’utilisateur clique : on place un marker
  - Le marker est draggable
*************************************************************/
let pointsEau = [];

function addPointEau() {
  map.once('click', function (e) {
    let marker = L.marker([e.latlng.lat, e.latlng.lng], { draggable: true }).addTo(map);

    // Stockage initial
    pointsEau.push({ lat: e.latlng.lat, lng: e.latlng.lng });

    // Mise à jour quand on déplace le marker
    marker.on('dragend', function (event) {
      let newPos = event.target.getLatLng();
      // Retrouver l'ancien index en comparant lat/lng
      let index = pointsEau.findIndex(p => p.lat === e.latlng.lat && p.lng === e.latlng.lng);
      if (index !== -1) {
        pointsEau[index] = { lat: newPos.lat, lng: newPos.lng };
      }
    });
  });
}

/************************************************************
  GESTION DES ZONES (Polygones "à la main")
  - L’utilisateur clique pour ajouter des points
  - Double-clic pour clôturer
*************************************************************/
let zones = [];
let drawing = false;
let currentPolygon = [];
let polylineLayer = null;
let polygonLayer = null;

function startDrawingZone() {
  drawing = true;
  currentPolygon = [];

  // Retire d'éventuels tracés temporaires
  if (polylineLayer) map.removeLayer(polylineLayer);
  if (polygonLayer) map.removeLayer(polygonLayer);

  polylineLayer = null;
  polygonLayer = null;

  map.on('click', onMapClickZone);
  map.on('dblclick', onMapDblClickZone);
}

function onMapClickZone(e) {
  if (!drawing) return;
  currentPolygon.push([e.latlng.lat, e.latlng.lng]);

  // Mise à jour visuelle (ligne provisoire)
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

  // Former un vrai polygone si >= 3 points
  if (currentPolygon.length >= 3) {
    polygonLayer = L.polygon(currentPolygon, { color: 'blue', fillOpacity: 0.2 }).addTo(map);

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

  // Enlever les listeners de dessin
  map.off('click', onMapClickZone);
  map.off('dblclick', onMapDblClickZone);
}

/************************************************************
  Exemple d’utilisation :
  - Bouton "Ajouter un point d’eau" → addPointEau()
  - Bouton "Tracer une zone" → startDrawingZone()
*************************************************************/

/** Fin du script.js **/

