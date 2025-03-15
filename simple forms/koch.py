import os
import fiona
from shapely.geometry import mapping, LineString
from math import sqrt


def koch(segment, iterations):
    """
    Génère les segments de la courbe de Koch.

    :param segment: Tuple représentant le segment (Point1, Point2) comme ((x1, y1), (x2, y2)).
    :param iterations: Nombre d'itérations pour générer la courbe de Koch.
    :return: Liste des segments de la courbe de Koch sous forme de tuples [((x1, y1), (x2, y2)), ...].
    """
    if iterations == 0:
        return [segment]
    else:
        (x1, y1), (x2, y2) = segment

        # Points définissant les divisions du segment
        dx, dy = x2 - x1, y2 - y1

        # Premier tiers
        p1 = (x1, y1)
        p2 = (x1 + dx / 3, y1 + dy / 3)

        # Point du "pic" du triangle équilatéral
        px = (x1 + dx / 2 - sqrt(3) * dy / 6)
        py = (y1 + dy / 2 + sqrt(3) * dx / 6)
        p3 = (px, py)

        # Dernier tiers
        p4 = (x1 + 2 * dx / 3, y1 + 2 * dy / 3)
        p5 = (x2, y2)

        # Répéter la construction pour chaque segment
        return (
            koch((p1, p2), iterations - 1)
            + koch((p2, p3), iterations - 1)
            + koch((p3, p4), iterations - 1)
            + koch((p4, p5), iterations - 1)
        )


# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier Koch sera sauvegardé
shp_file = os.path.join(output_folder, "koch.shp")

# Générer la courbe de Koch
iterations = 4  # Nombre d'itérations
initial_segment = ((0, 0), (1, 0))  # Segment initial entre les points (0, 0) et (1, 0)
segments = koch(initial_segment, iterations)  # Liste des segments sous forme [((x1, y1), (x2, y2)), ...]

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'LineString',  # Type de géométrie (ligne)
    'properties': {'id': 'int'},  # Attribut "id" pour identifier les segments
}

# Écriture dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',  # Système de coordonnées (non critique ici car la courbe de Koch est abstraite)
    schema=schema,
) as layer:
    # Ajouter chaque segment comme une ligne
    for i, ((x1, y1), (x2, y2)) in enumerate(segments, start=1):
        line = LineString([(x1, y1), (x2, y2)])  # Créer un segment
        layer.write({
            'geometry': mapping(line),  # Transformation en format compatible Fiona
            'properties': {'id': i},  # Attribut ID pour identifier le segment
        })

print(f"Shapefile représentant la courbe de Koch (itérations={iterations}) créé : {shp_file}")
