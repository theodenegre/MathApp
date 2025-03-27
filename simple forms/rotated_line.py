import os
import json
from shapely.geometry import mapping, LineString
from math import sqrt

# Vérifier ou créer un dossier simpleGEO
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier sera sauvegardé
geojson_file = os.path.join(output_folder, "line_rotated.geojson")

# Définir une ligne (LineString)
line = LineString([
    (0, 0), (sqrt(2)/2, sqrt(2)/2)  # Points qui définissent la ligne
])

# Définir la structure GeoJSON
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": mapping(line),  # Transformation en format compatible GeoJSON
            "properties": {"id": 1}  # Ajouter un attribut ID
        }
    ]
}

# Écriture dans un fichier GeoJSON
with open(geojson_file, 'w') as f:
    json.dump(geojson_data, f)

print(f"GeoJSON de la ligne créé dans le dossier : {geojson_file}")
