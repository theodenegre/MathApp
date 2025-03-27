import shapely.geometry as geometry
from shapely.ops import unary_union
import geopandas as gpd
import numpy as np
from shapely import is_valid, make_valid  # correction ici
import re
from shapely.wkt import loads
from shapely import simplify
import matplotlib.pyplot as plt

def peano_curve(iterations, size=1):
    """
    Génère une approximation de la courbe de Peano sous forme de polygones.

    Args:
        iterations: Le nombre d'itérations de la courbe. Plus le nombre est élevé, plus l'approximation est fine.
        size: La taille du carré dans lequel la courbe est dessinée.

    Returns:
        Une liste d'objets Polygon représentant la courbe de Peano.
    """

    def create_base_segment(offset_x=0, offset_y=0, scale=1):
        """Crée un segment de base de la courbe de Peano, transformé par un offset et une échelle."""
        points = [
            (0, 0), (0, 1), (1/2, 1), (1/2, 0), (1, 0), (1, 1)
        ]

        # Appliquer la mise à l'échelle et le décalage
        scaled_points = [(x * scale + offset_x, y * scale + offset_y) for x, y in points]
        return geometry.Polygon(scaled_points)

    polygons = [geometry.Polygon([(0,0), (size,0), (size, size), (0, size)])] # Carré initial

    def subdivide(polygons, iteration):

        if iteration == 0:
            return polygons

        new_polygons = []

        for polygon in polygons:
            minx, miny, maxx, maxy = polygon.bounds
            width = maxx - minx
            height = maxy - miny

            sub_size_x = width / 3
            sub_size_y = height / 3

            # Créer 9 sous-carrés et les ajouter à la liste
            # L'ordre est celui de la courbe de Peano

            # Première ligne
            new_polygons.append(create_base_segment(minx, miny, sub_size_x))
            new_polygons.append(create_base_segment(minx + sub_size_x, miny, sub_size_x))
            new_polygons.append(create_base_segment(minx + 2*sub_size_x, miny, sub_size_x))
            # Deuxième ligne
            new_polygons.append(create_base_segment(minx + 2*sub_size_x, miny + sub_size_y, sub_size_x))
            new_polygons.append(create_base_segment(minx + sub_size_x, miny + sub_size_y, sub_size_x))
            new_polygons.append(create_base_segment(minx, miny + sub_size_y, sub_size_x))

            # Troisième ligne
            new_polygons.append(create_base_segment(minx, miny + 2*sub_size_y, sub_size_x))
            new_polygons.append(create_base_segment(minx + sub_size_x, miny + 2*sub_size_y, sub_size_x))
            new_polygons.append(create_base_segment(minx + 2*sub_size_x, miny + 2*sub_size_y, sub_size_x))

        return subdivide(new_polygons, iteration - 1)

    return subdivide(polygons, iterations)


def make_geometries_valid(geometries):
    valid_geometries = []
    for geom in geometries:
        if not is_valid(geom):  # Correction ici
            valid_geom = geom.buffer(0)  # Une petite mise en mémoire tampon résout souvent les problèmes
            if not is_valid(valid_geom):  # Correction ici
                print("Impossible de corriger complètement une géométrie.  Vérifier manuellement.")
            valid_geometries.append(valid_geom)
        else:
            valid_geometries.append(geom)
    return valid_geometries

def simplify_geometries(geometries, tolerance=0.00001):
    simplified_geometries = [simplify(geom, tolerance, preserve_topology=False) for geom in geometries]
    return simplified_geometries

def round_coordinates(geometries, precision=6):
    rounded_geometries = []
    for geom in geometries:
        # Convertir la géométrie en WKT (Well-Known Text)
        wkt = geom.wkt
        # Arrondir les coordonnées dans la chaîne WKT
        rounded_wkt = re.sub(r"(\d+\.\d+)", lambda m: f"{float(m.group(0)):.{precision}f}", wkt)
        # Reconstruire la géométrie à partir du WKT arrondi
        rounded_geom = loads(rounded_wkt)
        rounded_geometries.append(rounded_geom)
    return rounded_geometries


def create_peano_shapefile(iterations, output_file, size=1):
    """
    Crée un shapefile à partir d'une approximation de la courbe de Peano.

    Args:
        iterations: Le nombre d'itérations de la courbe.
        output_file: Le chemin du fichier shapefile à créer.
        size: La taille du carré dans lequel la courbe est dessinée.
    """

    # Générer la courbe de Peano
    polygons = peano_curve(iterations, size)

    # Appliquer les corrections de géométrie
    polygons = round_coordinates(polygons, precision=6)
    polygons = simplify_geometries(polygons, tolerance=0.00001)
    polygons = make_geometries_valid(polygons)



    # Créer un GeoDataFrame
    gdf = gpd.GeoDataFrame(geometry=polygons)

    # Définir le système de coordonnées (ici WGS 84)
    gdf.crs = "EPSG:4326"

    # Sauvegarder en shapefile
    gdf.to_file(output_file)


# Exemple d'utilisation
if __name__ == "__main__":
    create_peano_shapefile(
            iterations=5,  # Ajuster le nombre d'itérations pour plus de détails
            output_file="peano_curve.shp",
            size=1
    )

    gdf = gpd.read_file("peano_curve.shp")
    gdf.plot()
    plt.title("Courbe de Peano")
    plt.axis('off')
    plt.show()

