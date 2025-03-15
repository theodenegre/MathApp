import os
import fiona
from shapely.geometry import mapping, Point

# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier sera sauvegardé
shp_file = os.path.join(output_folder, "point.shp")

# Définir un point (Point)
point = Point(0, 0)  # Coordonnées du point

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'Point',  # Type de géométrie (point)
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
    # Ajouter le point au Shapefile
    layer.write({
        'geometry': mapping(point),  # Transformation en format compatible pour Fiona
        'properties': {'id': 1},  # Ajouter un attribut ID
    })

print(f"Shapefile du point créé dans le dossier : {shp_file}")
