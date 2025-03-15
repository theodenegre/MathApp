import os
import fiona
from shapely.geometry import mapping, LineString

# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier sera sauvegardé
shp_file = os.path.join(output_folder, "line.shp")

# Définir une ligne (LineString)
line = LineString([
    (0, 0), (0.999, 0)  # Points qui définissent la ligne
])

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'LineString',  # Type de géométrie (ligne)
    'properties': {'id': 'int'},  # Attributs (un champ "id" de type entier)
}

# Écriture dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',  # Système de coordonnées (WGS84 standard)
    schema=schema,
) as layer:
    # Ajouter la ligne au Shapefile
    layer.write({
        'geometry': mapping(line),  # Transformation en format compatible pour Fiona
        'properties': {'id': 1},  # Ajouter un attribut ID
    })

print(f"Shapefile de la ligne créé dans le dossier : {shp_file}")
