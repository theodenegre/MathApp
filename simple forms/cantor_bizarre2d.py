import os
import fiona
from shapely.geometry import mapping, box  # box est utilisé pour créer des rectangles


def cantor(interval, height, iterations):
    """
    Génère les segments 2D de l'ensemble de Cantor.

    :param interval: Tuple représentant l'intervalle horizontal (x1, x2).
    :param height: Hauteur (domaine vertical) correspondant à ce niveau.
    :param iterations: Nombre d'itérations pour générer l'ensemble.
    :return: Liste contenant les rectangles de l'ensemble de Cantor sous forme [(x1, x2, y1, y2), ...].
    """
    x1, x2 = interval
    if iterations == 0:
        return [(x1, x2, 0, height)]
    else:
        # Retirer le tiers central
        third = (x2 - x1) / 3
        left = (x1, x1 + third)  # Segment gauche
        right = (x2 - third, x2)  # Segment droit

        # Réduire la hauteur pour la prochaine itération (division par 3)
        new_height = height / 3

        # Récursivement construire les segments restants, avec la nouvelle hauteur
        return (
            cantor(left, new_height, iterations - 1) +
            cantor(right, new_height, iterations - 1)
        )


# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier Cantor sera sauvegardé
shp_file = os.path.join(output_folder, "cantor2d_varied_height.shp")

# Générer l'ensemble de Cantor
iterations = 6  # Nombre d'itérations
initial_interval = (0, 1)  # Intervalle initial [0, 1]
initial_height = 1  # Hauteur initiale
rectangles = cantor(initial_interval, initial_height, iterations)

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
    # Ajouter chaque rectangle comme un polygone
    for i, (x1, x2, y1, y2) in enumerate(rectangles, start=1):
        # Créer un rectangle correspondant au segment avec la hauteur dynamique
        rect = box(x1, y1, x2, y2)
        layer.write({
            'geometry': mapping(rect),  # Transformation en format compatible Fiona
            'properties': {'id': i},  # Attribut ID pour identifier le rectangle
        })

print(f"Shapefile représentant l'ensemble de Cantor (itérations={iterations}) avec hauteurs dynamiques créé : {shp_file}")
