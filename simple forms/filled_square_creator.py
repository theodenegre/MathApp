import os
import fiona
from shapely.geometry import mapping, Polygon

# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier sera sauvegardé
shp_file = os.path.join(output_folder, "squares.shp")

# Définir un carré rempli (Polygon plein)
square_filled = Polygon([
    (0, 0), (0, 10), (10, 10), (10, 0), (0, 0)  # Contour du carré
])

# Définir un carré vide (Polygon avec un trou)
outer_square = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]  # Contour externe
inner_square = [(3, 3), (3, 7), (7, 7), (7, 3), (3, 3)]  # Trou à l'intérieur
square_empty = Polygon(shell=outer_square, holes=[inner_square])

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'Polygon',  # Type de géométrie (polygone)
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
    # Ajouter le carré rempli
    layer.write({
        'geometry': mapping(square_filled),  # Transformation en format compatible
        'properties': {'id': 1},  # Ajouter un attribut ID
    })
    # Ajouter le carré vide
    layer.write({
        'geometry': mapping(square_empty),  # Transformation en format compatible
        'properties': {'id': 2},  # Ajouter un autre ID
    })

print(f"Shapefile créé dans le dossier : {shp_file}")
