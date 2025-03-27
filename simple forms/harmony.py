import os
import json
from shapely.geometry import mapping, Point

# Vérifier ou créer un dossier simpleGEO
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier sera sauvegardé
geojson_file = os.path.join(output_folder, "points_fraction.geojson")

# Définir une liste de points pour 1/n
points = [Point(1/n, 0) for n in range(1, 1001)]

# Définir les features pour le GeoJSON
features = []
for i, point in enumerate(points, start=1):
    features.append({
        'type': 'Feature',
        'geometry': mapping(point),
        'properties': {'id': i, 'value': 1 / i},
    })

# Définir la structure GeoJSON
geojson = {
    'type': 'FeatureCollection',
    'features': features,
}

# Écriture dans un fichier GeoJSON
with open(geojson_file, 'w') as f:
    json.dump(geojson, f)

print(f"GeoJSON contenant les points 1/n (0 <= n <= 1000) créé : {geojson_file}")
