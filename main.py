from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import uvicorn
import networkx as nx
from shapely.geometry import Polygon, Point as ShapelyPoint
import shapely.ops
from pyproj import Transformer

app = FastAPI()

# Transformer GPS -> mètres
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

# Modèle pour un point (latitude, longitude)
class Point(BaseModel):
    lat: float
    lng: float

# Modèle pour une zone, qui est une liste de points
class Zone(BaseModel):
    id: int
    coords: List[Point]

# Modèle des données envoyées par Bubble
class IrrigationData(BaseModel):
    address: str
    zones: List[Zone]
    points_eau: List[Point]
    pression: float
    zoom: int
    fill_time: float

# Fonction pour convertir les coordonnées GPS en mètres
def convert_gps_to_meters(lat, lng):
    return transformer.transform(lng, lat)

# Fonction pour calculer une distance en mètres entre deux points
def distance_meters(lat1, lng1, lat2, lng2):
    p1 = convert_gps_to_meters(lat1, lng1)
    p2 = convert_gps_to_meters(lat2, lng2)
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5

@app.post("/generate_plan")
async def generate_plan(data: IrrigationData):
    zone_areas = []
    zone_centroids = []
    
    for zone in data.zones:
        coords = [(pt.lng, pt.lat) for pt in zone.coords]
        if len(coords) < 3:
            zone_areas.append(0)
            continue
        poly = Polygon(coords)
        poly_proj = shapely.ops.transform(transformer.transform, poly)
        area = poly_proj.area  # Surface en m²
        zone_areas.append(area)
        zone_centroids.append(poly_proj.centroid)

    # Création du graphe pour optimiser le tracé des tuyaux
    G = nx.Graph()
    for i, point in enumerate(data.points_eau):
        G.add_node(f"point_eau_{i}", pos=(point.lng, point.lat))
    for i, centroid in enumerate(zone_centroids):
        G.add_node(f"zone_{i}", pos=(centroid.x, centroid.y))
        for j, point in enumerate(data.points_eau):
            G.add_edge(f"point_eau_{j}", f"zone_{i}", weight=distance_meters(point.lat, point.lng, centroid.y, centroid.x))
    mst = nx.minimum_spanning_tree(G)

    tuyaux = [{"start": G.nodes[u]['pos'], "end": G.nodes[v]['pos'], "pipe_type": "32mm"} for u, v in mst.edges]

    # Génération des équipements
    electrovanes = [{"location": G.nodes[f"zone_{i}"]['pos'], "type": "24V"} for i in range(len(zone_centroids))]
    arroseurs = [{"location": G.nodes[f"zone_{i}"]['pos'], "radius": 5} for i in range(len(zone_centroids))]

    result = {
        "zone_areas": zone_areas,
        "tuyaux": tuyaux,
        "electrovanes": electrovanes,
        "arroseurs": arroseurs,
        "scale_info": {"zoom": data.zoom},
        "hydraulic_info": {"pression": data.pression, "fill_time": data.fill_time}
    }
    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
