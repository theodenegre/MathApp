import os
import json
from shapely.geometry import mapping, LineString

# Vérifier ou créer un dossier simpleGEO
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier sera sauvegardé
geojson_file = os.path.join(output_folder, "line.geojson")

# Définir une ligne (LineString)
line = LineString([
    (0, 0), (0.999, 0)  # Points qui définissent la ligne
])

# Construire l'entité GeoJSON
feature = {
    "type": "Feature",
    "geometry": mapping(line),
    "properties": {"id": 1}
}

# Structure GeoJSON
geojson_data = {
    "type": "FeatureCollection",
    "features": [feature]
}

# Écriture dans un fichier GeoJSON
with open(geojson_file, "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, ensure_ascii=False, indent=4)

print(f"GeoJSON de la ligne créé dans le dossier : {geojson_file}")
