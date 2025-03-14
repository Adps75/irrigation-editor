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
    address: str  # Adresse fournie par Bubble
    zones: List[Zone]  # Zones dessinées par l'utilisateur
    points_eau: List[Point]  # Liste de points d'eau principaux
    pression: float  # Pression du point d'eau (en bars)
    zoom: int  # Niveau de zoom (pour gérer l'échelle)
    fill_time: float  # Temps de remplissage d'un arroseur de 10L (en secondes)

@app.post("/generate_plan")
async def generate_plan(data: IrrigationData):
    """
    Endpoint qui reçoit les données d'irrigation et génère un plan optimisé.
    """
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    zone_areas = []
    zone_centroids = []
    for zone in data.zones:
        coords = [(pt.lng, pt.lat) for pt in zone.coords]
        if len(coords) < 3:
            zone_areas.append(0)
            continue
        poly = Polygon(coords)
        poly_proj = shapely.ops.transform(transformer.transform, poly)
        area = poly_proj.area  # surface en m²
        zone_areas.append(area)
        zone_centroids.append(poly.centroid)

    # Création du graphe pour optimiser le tracé des tuyaux
    G = nx.Graph()
    for i, point in enumerate(data.points_eau):
        G.add_node(f"point_eau_{i}", pos=(point.lng, point.lat))
    for i, centroid in enumerate(zone_centroids):
        G.add_node(f"zone_{i}", pos=(centroid.x, centroid.y))
        for j, point in enumerate(data.points_eau):
            G.add_edge(f"point_eau_{j}", f"zone_{i}", weight=centroid.distance(ShapelyPoint(point.lng, point.lat)))
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
