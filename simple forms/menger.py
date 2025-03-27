import os
import json
from shapely.geometry import Polygon, mapping
from itertools import product


def menger_sponge_2d(coords, size, iterations):
    """
    Génère les carrés restants de l'éponge de Menger dans une structure 2D.

    :param coords: Tuple (x, y) des coordonnées du coin inférieur-gauche du carré.
    :param size: Taille (longueur d'un côté) du carré.
    :param iterations: Nombre d'itérations pour la génération de l'éponge.
    :return: Liste de carrés restants sous forme de [(x, y, size), ...].
    """
    if iterations == 0:
        return [(*coords, size)]

    x, y = coords
    next_size = size / 3  # Taille des sous-carrés dans cette étape
    squares = []

    # Parcourir chaque sous-carré dans une grille 3x3
    for dx, dy in product(range(3), repeat=2):
        sub_x, sub_y = x + dx * next_size, y + dy * next_size

        # Exclure le carré central (1,1) dans la grille 3x3
        if dx == 1 and dy == 1:
            continue

        # Répéter pour les itérations restantes
        squares.extend(menger_sponge_2d((sub_x, sub_y), next_size, iterations - 1))
    return squares


def square_to_polygon(x, y, size):
    """
    Convertit un carré en sa représentation polygonale.

    :param x: Coordonnée X du coin inférieur gauche.
    :param y: Coordonnée Y du coin inférieur gauche.
    :param size: Taille d'un côté du carré.
    :return: Un objet `Polygon` représentant le carré.
    """
    return Polygon([
        (x, y),  # Coin inférieur-gauche
        (x + size, y),  # Coin inférieur-droit
        (x + size, y + size),  # Coin supérieur-droit
        (x, y + size),  # Coin supérieur-gauche
        (x, y),  # Retour au point initial pour fermer le polygone
    ])


# Vérifier ou créer un dossier simpleGEO
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin pour le fichier généré
geojson_file = os.path.join(output_folder, "menger_sponge.geojson")

# Paramètres initiaux : taille, itérations, coordonnées de départ
iterations = 6  # Attention, la croissance est exponentielle !
initial_size = 1  # Taille initiale du carré
initial_square = (0, 0)  # Coordonnées du coin inférieur-gauche initial

# Générer les carrés de l'éponge de Menger
squares = menger_sponge_2d(initial_square, initial_size, iterations)

# Préparer les données GeoJSON
features = []
polygon_id = 0
for square in squares:
    x, y, size = square

    # Créer un polygone pour ce carré
    poly = square_to_polygon(x, y, size)
    polygon_id += 1
    features.append({
        'type': 'Feature',
        'geometry': mapping(poly),  # Transformation en format compatible GeoJSON
        'properties': {'id': polygon_id},  # Un ID unique pour chaque carré
    })

geojson_data = {
    'type': 'FeatureCollection',
    'features': features,
}

# Écriture dans un fichier GeoJSON
with open(geojson_file, 'w') as f:
    json.dump(geojson_data, f)

print(f"GeoJSON représentant l'éponge de Menger en 2D (itérations={iterations}) créé : {geojson_file}")
