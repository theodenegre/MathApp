import os
import fiona
from shapely.geometry import mapping, Polygon, LineString
from math import sqrt


def koch_snowflake(start, end, iterations):
    """
    Génère les segments du flocon de Koch récursivement à partir d'un segment initial.

    :param start: Point de départ de la ligne (x1, y1).
    :param end: Point d'arrivée de la ligne (x2, y2).
    :param iterations: Nombre d'itérations pour générer le flocon.
    :return: Liste ordonnée des points qui décrivent la courbe du flocon de Koch.
    """
    if iterations == 0:
        return [start, end]

    x1, y1 = start
    x2, y2 = end

    # Diviser le segment initial en trois parties
    third1 = ((2 * x1 + x2) / 3, (2 * y1 + y2) / 3)  # Point à 1/3
    third2 = ((x1 + 2 * x2) / 3, (y1 + 2 * y2) / 3)  # Point à 2/3

    # Calcul de l'apex (sommet) du triangle équilatéral
    # Utilisation de la rotation d'un vecteur autour de son milieu pour construire le triangle
    midX = (x1 + x2) / 2
    midY = (y1 + y2) / 2

    dx = third2[0] - third1[0]
    dy = third2[1] - third1[1]

    # Appliquer une rotation de +60° sur le vecteur [dx, dy] pour créer le sommet
    # cos(60°) = 0.5, sin(60°) = sqrt(3)/2
    apex = (
        third1[0] + dx * 0.5 - dy * (3**0.5) / 2,
        third1[1] + dy * 0.5 + dx * (3**0.5) / 2
    )

    # Récursion sur les quatre segments
    return (
        koch_snowflake(start, third1, iterations - 1) +
        koch_snowflake(third1, apex, iterations - 1) +
        koch_snowflake(apex, third2, iterations - 1) +
        koch_snowflake(third2, end, iterations - 1)
    )


def close_snowflake(points):
    """Ferme le flocon en ajoutant le premier point à la fin pour former un polygone complet."""
    if points[-1] != points[0]:
        points.append(points[0])
    return points


# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier du flocon de Koch sera sauvegardé
shp_file = os.path.join(output_folder, "koch_snowflake2.shp")

# Paramètres initiaux pour le flocon de Koch
iterations = 5  # Nombre d'itérations
triangle = [(0, 0), (1, 0), (0.5, sqrt(3) / 2)]  # Triangle équilatéral de base

# Construction du flocon en connectant les côtés du triangle de départ
points = (
    koch_snowflake(triangle[0], triangle[1], iterations)[:-1] +  # Premier segment
    koch_snowflake(triangle[1], triangle[2], iterations)[:-1] +  # Deuxième segment
    koch_snowflake(triangle[2], triangle[0], iterations)         # Troisième segment
)
points = close_snowflake(points)  # Ferme le flocon pour former un polygone complet

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'Polygon',  # Type de géométrie (polygone pour le flocon)
    'properties': {'id': 'int'},  # Attribut "id" pour identifier le polygone
}

# Écriture dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',  # Système de coordonnées (non critique ici car abstrait)
    schema=schema,
) as layer:
    # Créer un polygone à partir des points et ajouter dans la couche
    polygon = Polygon(points)
    layer.write({
        'geometry': mapping(polygon),  # Transformation en format compatible Fiona
        'properties': {'id': 1},  # Identifiant unique
    })

print(f"Shapefile représentant le flocon de Koch (itérations={iterations}) créé : {shp_file}")
