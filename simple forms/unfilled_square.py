import os
import json
from shapely.geometry import mapping, LineString

# Vérifier ou créer le dossier simpleGEO
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin où le fichier sera sauvegardé
geojson_file = os.path.join(output_folder, "square_borders.geojson")

# Définition des bordures d'un carré (4 côtés comme des segments de ligne)
# Carré de côté 10, défini par ses sommets : (0, 0), (0, 10), (10, 10), (10, 0)
borders = [
    LineString([(0, 0), (0, 10)]),  # Bordure de gauche
    LineString([(0, 10), (10, 10)]),  # Bordure du haut
    LineString([(10, 10), (10, 0)]),  # Bordure de droite
    LineString([(10, 0), (0, 0)])  # Bordure du bas
]

# Écriture des bordures dans un fichier GeoJSON
features = [json.dumps({"type": "Feature", "geometry": mapping(border), "properties": {"id": i}}) for i, border in enumerate(borders, start=1)]
geojson_obj = {"type": "FeatureCollection", "features": features}

with open(geojson_file, 'w') as f:
    json.dump(geojson_obj, f)

print(f"GeoJSON des bordures du carré créé dans : {geojson_file}")
