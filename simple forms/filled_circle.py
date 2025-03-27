import geopandas as gpd
import shapely.geometry as geometry
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import numpy as np
import json
from shapely.geometry import mapping, Point

def create_filled_circle_geojson(center, radius, num_points, output_file):
    """
    Crée un fichier GeoJSON contenant un cercle rempli (une boule de R^2).

    Args:
        center (tuple): Coordonnées (x, y) du centre du cercle.
        radius (float): Rayon de la boule (cercle rempli).
        num_points (int): Nombre de segments pour approximer le bord du cercle.
        output_file (str): Chemin du fichier GeoJSON de sortie.

    Returns:
        None
    """
    # Créer le cercle (approximé par un polygone régulier avec num_points sommets)
    circle = Point(center).buffer(radius, resolution=num_points)
    # `buffer()` génère un polygone rempli basé sur un rayon autour du centre

    # Construire l'entité GeoJSON
    feature = {
        "type": "Feature",
        "geometry": mapping(circle),
        "properties": {"radius": radius}
    }

    # Structure GeoJSON
    geojson_data = {
        "type": "FeatureCollection",
        "features": [feature]
    }

    # Écriture dans un fichier GeoJSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=4)

    print(f"GeoJSON créé : {output_file}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Définitions des paramètres de la boule (cercle) de R^2
    center = (0, 0)  # Centre de la boule (par exemple, coordonnées x=0, y=0)
    radius = 1  # Rayon de la boule
    num_points = 100  # Précision : Nombre de points pour approximer le bord du cercle

    # Nom du fichier de sortie
    output_file = "simpleGEO/filled_circle_r2.geojson"

    # Création du GeoJSON
    create_filled_circle_geojson(center, radius, num_points, output_file)
