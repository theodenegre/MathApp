import os
import fiona
from shapely.geometry import mapping, LineString

# Vérifier ou créer le dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin où le fichier sera sauvegardé
shp_file = os.path.join(output_folder, "square_borders.shp")

# Définition des bordures d'un carré (4 côtés comme des segments de ligne)
# Carré de côté 10, défini par ses sommets : (0, 0), (0, 10), (10, 10), (10, 0)
borders = [
    LineString([(0, 0), (0, 10)]),  # Bordure de gauche
    LineString([(0, 10), (10, 10)]),  # Bordure du haut
    LineString([(10, 10), (10, 0)]),  # Bordure de droite
    LineString([(10, 0), (0, 0)])  # Bordure du bas
]

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'LineString',  # Type de géométrie (ici, polylignes)
    'properties': {'id': 'int'},  # Attributs (champs) : un champ "id" entier
}

# Écriture des bordures dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',  # Système de coordonnées (WGS84)
    schema=schema,
) as layer:
    # Ajouter chaque bordure de ligne dans le Shapefile
    for i, border in enumerate(borders, start=1):  # Itération sur les lignes avec un ID
        layer.write({
            'geometry': mapping(border),  # Convertir la géométrie en un format supporté par Fiona
            'properties': {'id': i},  # Ajouter un ID unique pour chaque bordure
        })

print(f"Shapefile des bordures du carré créé dans : {shp_file}")
