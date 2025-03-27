import os
import json
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


# Vérifier ou créer un dossier simpleGEO
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier Koch sera sauvegardé
geojson_file = os.path.join(output_folder, "koch.geojson")

# Générer la courbe de Koch
iterations = 4  # Nombre d'itérations
initial_segment = ((0, 0), (1, 0))  # Segment initial entre les points (0, 0) et (1, 0)
segments = koch(initial_segment, iterations)  # Liste des segments sous forme [((x1, y1), (x2, y2)), ...]

# Construire les entités GeoJSON
features = []
for i, ((x1, y1), (x2, y2)) in enumerate(segments, start=1):
    line = LineString([(x1, y1), (x2, y2)])  # Créer un segment
    features.append({
        "type": "Feature",
        "geometry": mapping(line),
        "properties": {"id": i}
    })

# Structure GeoJSON
geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

# Écriture dans un fichier GeoJSON
with open(geojson_file, "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, ensure_ascii=False, indent=4)

print(f"GeoJSON représentant la courbe de Koch (itérations={iterations}) créé : {geojson_file}")
