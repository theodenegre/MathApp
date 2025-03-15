import os
import fiona
from shapely.geometry import Polygon, LineString, mapping
import numpy as np


def koch_snowflake(iterations):
    """
    Génère les segments de la courbe du flocon de Koch après un certain nombre d'itérations.

    :param iterations: Nombre d'itérations pour raffiner la courbe.
    :return: Liste de segments sous forme de tuples ((x1, y1), (x2, y2)).
    """
    # Triangle équilatéral initial
    sqrt3 = np.sqrt(3) / 2
    points = [
        (0, 0),
        (0.5, sqrt3),
        (1, 0),
        (0, 0)  # Retour au point initial
    ]

    for _ in range(iterations):
        new_points = []
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]

            # Calcul des sous-segments
            dx, dy = (p2[0] - p1[0]) / 3, (p2[1] - p1[1]) / 3
            pA = (p1[0] + dx, p1[1] + dy)
            pB = (p1[0] + 2 * dx, p1[1] + 2 * dy)

            # Point sommet du triangle
            angle = np.pi / 3  # 60°
            pC = (
                (pA[0] + np.cos(angle) * (pB[0] - pA[0]) - np.sin(angle) * (
                            pB[1] - pA[1])),
                (pA[1] + np.sin(angle) * (pB[0] - pA[0]) + np.cos(angle) * (
                            pB[1] - pA[1]))
            )

            # Ajout des nouveaux segments
            new_points.extend([p1, pA, pC, pB])
        new_points.append(points[-1])  # Fin du segment
        points = new_points

    return points


# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin pour le fichier généré
shp_file = os.path.join(output_folder, "koch_snowflake.shp")

# Paramètre d'itérations
iterations = 7  # Augmenter pour un flocon plus détaillé

# Générer les points de la courbe
snowflake_points = koch_snowflake(iterations)

# Définir le schéma pour écrire dans le fichier Shapefile
schema = {
    'geometry': 'LineString',  # Type de géométrie représentée
    'properties': {'id': 'int'},
}

# Écriture dans un fichier Shapefile
with fiona.open(
        shp_file,
        mode='w',
        driver='ESRI Shapefile',
        crs='EPSG:4326',
        schema=schema,
) as layer:
    line = LineString(snowflake_points)
    layer.write({
        'geometry': mapping(line),
        'properties': {'id': 1},
    })

print(
    f"Shapefile du flocon de Koch en 2D (itérations={iterations}) créé : {shp_file}")