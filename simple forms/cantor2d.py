import os
import fiona
from shapely.geometry import mapping, box  # box est utilisé pour créer des rectangles


def cantor(interval, iterations):
    """
    Génère les segments de l'ensemble de Cantor.

    :param interval: Tuple représentant l'intervalle (x1, x2).
    :param iterations: Nombre d'itérations pour générer l'ensemble.
    :return: Liste des segments de l'ensemble de Cantor sous forme de tuples [(x1, x2), ...].
    """
    x1, x2 = interval
    if iterations == 0:
        return [(x1, x2)]
    else:
        # Retirer le tiers central et appeler récursivement sur les deux segments restants
        third = (x2 - x1) / 3
        left = (x1, x1 + third)  # Segment gauche
        right = (x2 - third, x2)  # Segment droit
        return cantor(left, iterations - 1) + cantor(right, iterations - 1)


# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier Cantor sera sauvegardé
shp_file = os.path.join(output_folder, "cantor2d.shp")

# Générer l'ensemble de Cantor
iterations = 14  # Nombre d'itérations
initial_interval = (0, 1)  # Intervalle initial [0, 1]
segments = cantor(initial_interval, iterations)  # Liste des segments sous forme [(x1, x2), ...]

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'Polygon',  # Type de géométrie (polygone pour le rectangle)
    'properties': {'id': 'int'},  # Attribut "id" pour identifier les segments
}

# Écriture dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',  # Système de coordonnées (non critique ici car l'ensemble Cantor est abstrait)
    schema=schema,
) as layer:
    # Ajouter chaque segment comme un rectangle
    for i, (x1, x2) in enumerate(segments, start=1):
        # Créer un rectangle correspondant au segment, avec une hauteur de 1
        rect = box(x1, 0, x2, 1)
        layer.write({
            'geometry': mapping(rect),  # Transformation en format compatible Fiona
            'properties': {'id': i},  # Attribut ID pour identifier le rectangle
        })

print(f"Shapefile représentant l'ensemble de Cantor (itérations={iterations}) créé : {shp_file}")
