# main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List
import uvicorn

# Pour calculer les surfaces
from shapely.geometry import Polygon
import shapely.ops
from pyproj import Transformer

app = FastAPI()

# Modèle pour un point (latitude, longitude)
class Point(BaseModel):
    lat: float
    lng: float

# Modèle pour une zone, qui est une liste de points
class Zone(BaseModel):
    coords: List[Point]

# Modèle des données envoyées par Bubble
class IrrigationData(BaseModel):
    address: str      # Adresse fournie par Bubble
    zones: List[Zone] # Zones dessinées par l'utilisateur
    point_eau: Point  # Point d'eau principal
    pression: float   # Pression du point d'eau (en bars)
    zoom: int         # Niveau de zoom (pour gérer l'échelle)

@app.get("/", response_class=HTMLResponse)
async def get_editor():
    # Sert le fichier HTML de l'éditeur
    with open("static/editor.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.post("/generate_plan")
async def generate_plan(data: IrrigationData):
    """
    Endpoint qui reçoit les données d'irrigation (adresse, zones, point d'eau, pression, zoom).
    Il calcule par exemple la surface de chaque zone pour que l'algorithme puisse travailler sur un plan.
    """
    # Transformer pour convertir de WGS84 (EPSG:4326) vers Web Mercator (EPSG:3857)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    zone_areas = []
    for zone in data.zones:
        # Convertir la liste de points en tuple (lng, lat) car la transformation attend x, y
        coords = [(pt.lng, pt.lat) for pt in zone.coords]
        if len(coords) < 3:
            # On ignore les zones qui ne forment pas un polygone
            zone_areas.append(0)
            continue
        poly = Polygon(coords)
        # Transformer le polygone en coordonnées projetées
        poly_proj = shapely.ops.transform(transformer.transform, poly)
        area = poly_proj.area  # surface en m²
        zone_areas.append(area)

    # Pour cet exemple, on renvoie aussi une réponse statique (à remplacer par votre algorithme complet)
    result = {
        "zone_areas": zone_areas,  # Surface de chaque zone en m²
        "tuyaux": [
            [ (data.point_eau.lat, data.point_eau.lng),
              (data.point_eau.lat + 0.001, data.point_eau.lng + 0.001) ]
        ],
        "electrovannes": [
            {"lat": data.point_eau.lat + 0.001, "lng": data.point_eau.lng + 0.001}
        ],
        "arroseurs": [
            {"lat": data.point_eau.lat + 0.002, "lng": data.point_eau.lng + 0.002, "rayon": 5}
        ],
        "color_zones": {
            "zone1": "#FF0000"
        },
        "scale_info": {
            "zoom": data.zoom,
            "remarque": "Le zoom est utilisé pour adapter l'affichage et le calcul des surfaces."
        }
    }
    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
