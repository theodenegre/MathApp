import os
import json
from shapely.geometry import mapping, LineString

def cantor(interval, iterations):
    """
    Génère les segments de l'ensemble de Cantor.

    :param interval: Tuple représentant l'intervalle (x1, x2).
    :param iterations: Nombre d'itérations pour générer l'ensemble.
    :return: Liste des segments de l'ensemble de Cantor sous forme de tuples [(x1, x2), ...].
    """
    x1, x2 = interval
    if iterations == 0:
        return [(x1, x2)]
    else:
        third = (x2 - x1) / 3
        left = (x1, x1 + third)
        right = (x2 - third, x2)
        return cantor(left, iterations - 1) + cantor(right, iterations - 1)

# Vérifier ou créer un dossier simpleGEO
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier Cantor sera sauvegardé
geojson_file = os.path.join(output_folder, "cantor.geojson")

# Générer l'ensemble de Cantor
iterations = 5
initial_interval = (0, 1)
segments = cantor(initial_interval, iterations)

# Construire les entités GeoJSON
features = []
for i, (x1, x2) in enumerate(segments, start=1):
    line = LineString([(x1, 0), (x2, 0)])
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

print(f"GeoJSON représentant l'ensemble de Cantor (itérations={iterations}) créé : {geojson_file}")