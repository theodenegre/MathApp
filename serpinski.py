import shapely.geometry as geometry
from shapely.ops import unary_union
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt


def sierpinski_triangle(iterations, size=1):
    def get_middle_points(p1, p2):
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    # Points initiaux du triangle
    points = [
        (0, 0),
        (size / 2, size * np.sqrt(3) / 2),
        (size, 0)
    ]

    triangles = [geometry.Polygon(points)]

    for _ in range(iterations):
        new_triangles = []
        for triangle in triangles:
            # Obtenir les coordonnées du triangle
            coords = list(triangle.exterior.coords)[:-1]

            # Calculer les points médians
            mid1 = get_middle_points(coords[0], coords[1])
            mid2 = get_middle_points(coords[1], coords[2])
            mid3 = get_middle_points(coords[2], coords[0])

            # Créer les trois nouveaux triangles
            t1 = geometry.Polygon([coords[0], mid1, mid3])
            t2 = geometry.Polygon([mid1, coords[1], mid2])
            t3 = geometry.Polygon([mid3, mid2, coords[2]])

            new_triangles.extend([t1, t2, t3])

        triangles = new_triangles

    return triangles


def create_sierpinski_shapefile(iterations, output_file, size=1):
    # Générer le triangle de Sierpinski
    triangles = sierpinski_triangle(iterations, size)

    # Créer un GeoDataFrame
    gdf = gpd.GeoDataFrame(geometry=triangles)

    # Définir le système de coordonnées (ici WGS 84)
    gdf.crs = "EPSG:4326"

    # Sauvegarder en shapefile
    gdf.to_file(output_file)


# Exemple d'utilisation
if __name__ == "__main__":
    create_sierpinski_shapefile(
            iterations=10,
            output_file="sierpinski_triangle.shp",
            size=1
    )

    # plt
    gdf = gpd.read_file("sierpinski_triangle.shp")
    gdf.plot()
    plt.title("Triangle de Sierpinski")
    plt.axis('off')
    plt.show()
