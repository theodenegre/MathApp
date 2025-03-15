import os
import fiona
from shapely.geometry import mapping, Point

# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier sera sauvegardé
shp_file = os.path.join(output_folder, "points_fraction.shp")

# Définir une liste de points pour 1/n
points = [Point(1/n, 0) for n in range(1, 1001)]

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'Point',  # Type de géométrie (point)
    'properties': {'id': 'int', 'value': 'float'},  # Champs : un entier "id" et un flottant "value"
}

# Écriture dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',  # Système de coordonnées (WGS84)
    schema=schema,
) as layer:
    # Ajouter chaque point dans le Shapefile
    for i, point in enumerate(points, start=1):  # i est l'ID unique pour chaque point
        layer.write({
            'geometry': mapping(point),  # Transformation en format compatible Fiona
            'properties': {'id': i, 'value': 1 / i},  # Ajouter les attributs ID et valeur 1/n
        })

print(f"Shapefile contenant les points 1/n (0 <= n <= 1000) créé : {shp_file}")
