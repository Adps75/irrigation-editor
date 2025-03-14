# main.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import uvicorn
import networkx as nx
from shapely.geometry import Polygon
import shapely.ops
from pyproj import Transformer

app = FastAPI()

# Transformer GPS -> mètres (WGS84 -> Web Mercator)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

# Modèles Pydantic
class Point(BaseModel):
    lat: float
    lng: float

class Zone(BaseModel):
    id: int
    coords: List[Point]

class IrrigationData(BaseModel):
    address: str
    zones: List[Zone]
    points_eau: List[Point]
    pression: float
    zoom: int
    fill_time: float

@app.post("/generate_plan")
async def generate_plan(data: IrrigationData):
    zone_areas = []
    zone_centroids = []
    
    # Calcul de surface pour chaque zone
    for zone in data.zones:
        coords = [(pt.lng, pt.lat) for pt in zone.coords]
        if len(coords) < 3:
            zone_areas.append(0)
            continue
        poly = Polygon(coords)
        poly_proj = shapely.ops.transform(transformer.transform, poly)
        area = poly_proj.area  # surface en m²
        zone_areas.append(area)
        zone_centroids.append(poly_proj.centroid)

    # Exemple d'optimisation de réseau de tuyaux (simplifié)
    G = nx.Graph()
    # Ajouter les points d'eau
    for i, point in enumerate(data.points_eau):
        G.add_node(f"point_eau_{i}", pos=(point.lng, point.lat))
    # Ajouter les centroides de zones
    for i, centroid in enumerate(zone_centroids):
        G.add_node(f"zone_{i}", pos=(centroid.x, centroid.y))

    result = {
        "zone_areas": zone_areas,
        "tuyaux": [],       # A calculer plus tard
        "electrovanes": [], # A calculer plus tard
        "arroseurs": [],    # A calculer plus tard
    }
    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
