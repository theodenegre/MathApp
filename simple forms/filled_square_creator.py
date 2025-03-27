import os
import json
from shapely.geometry import mapping, Polygon

# Vérifier ou créer un dossier simpleGEO
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier sera sauvegardé
geojson_file = os.path.join(output_folder, "squares.geojson")

# Définir un carré rempli (Polygon plein)
square_filled = Polygon([
    (0, 0), (0, 10), (10, 10), (10, 0), (0, 0)  # Contour du carré
])

# Définir un carré vide (Polygon avec un trou)
outer_square = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]  # Contour externe
square_empty = Polygon(shell=outer_square)

# Créer une collection de fonctionnalités GeoJSON
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": mapping(square_filled),
            "properties": {"id": 1}
        },
        {
            "type": "Feature",
            "geometry": mapping(square_empty),
            "properties": {"id": 2}
        }
    ]
}

# Écriture dans un fichier GeoJSON
with open(geojson_file, 'w') as f:
    json.dump(geojson_data, f)

print(f"GeoJSON créé dans le dossier : {geojson_file}")
