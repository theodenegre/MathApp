import geopandas as gpd
import shapely.geometry as geometry
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import fiona
import numpy as np


def create_filled_circle_shapefile(center, radius, num_points, output_file):
    """
    Crée un fichier Shapefile contenant un cercle rempli (une boule de \mathbb{R}^2).

    Args:
        center (tuple): Coordonnées (x, y) du centre du cercle.
        radius (float): Rayon de la boule (cercle rempli).
        num_points (int): Nombre de segments pour approximer le bord du cercle.
        output_file (str): Chemin du fichier Shapefile de sortie.

    Returns:
        None
    """
    # Créer le cercle (approximé par un polygone régulier avec num_points sommets)
    circle = Point(center).buffer(radius, resolution=num_points)
    # `buffer()` génère un polygone rempli basé sur un rayon autour du centre

    # Créer un GeoDataFrame à partir de ce polygone
    gdf = gpd.GeoDataFrame([{'geometry': circle, 'radius': radius}],
                           crs="EPSG:4326")
    # EPSG:4326 est le système de coordonnées WGS 84 (global)
    # Vous pouvez ajuster ce CRS selon vos besoins.

    # Exporter au format Shapefile
    gdf.to_file(output_file, driver="ESRI Shapefile")
    print(f"Shapefile créé : {output_file}")


# Exemple d'utilisation
if __name__ == "__main__":
    # Définitions des paramètres de la boule (cercle) de R^2
    center = (0, 0)  # Centre de la boule (par exemple, coordonnées x=0, y=0)
    radius = 1  # Rayon de la boule
    num_points = 100  # Précision : Nombre de points pour approximer le bord du cercle

    # Nom du fichier de sortie
    output_file = "simpleSHP/filled_circle_r2.shp"

    # Création du shapefile
    create_filled_circle_shapefile(center, radius, num_points, output_file)
