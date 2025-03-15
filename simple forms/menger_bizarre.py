import os
import fiona
from shapely.geometry import Polygon, mapping
from itertools import product


def menger_sponge_2d(coords, width, height, iterations):
    """
    Génère les rectangles restants de l'éponge de Menger en 2D.

    :param coords: Tuple (x, y) des coordonnées du coin inférieur-gauche de la forme initiale.
    :param width: Largeur de la forme initiale.
    :param height: Hauteur de la forme initiale.
    :param iterations: Nombre d'itérations pour la génération de l'éponge.
    :return: Liste de rectangles restants sous la forme [(x, y, width, height), ...].
    """
    if iterations == 0:
        return [(*coords, width, height)]

    x, y = coords
    next_width = width / 3   # Largeur des sous-rectangles
    next_height = height / 5  # Hauteur des sous-rectangles
    rectangles = []

    # Parcourir chaque sous-rectangle dans une grille 3x5
    for dx, dy in product(range(3), [0, 5]):
        sub_x, sub_y = x + dx * next_width, y + dy * next_height

        # Exclure le rectangle central dans une disposition 3x5
        if dx == 1 and dy == 2:  # Le "centre" de la grille 3x5
            continue

        # Répéter pour les itérations restantes
        rectangles.extend(menger_sponge_2d((sub_x, sub_y), next_width, next_height, iterations - 1))
    return rectangles


def rectangle_to_polygon(x, y, width, height):
    """
    Convertit un rectangle en sa représentation polygonale.

    :param x: Coordonnée X du coin inférieur-gauche.
    :param y: Coordonnée Y du coin inférieur-gauche.
    :param width: Largeur du rectangle.
    :param height: Hauteur du rectangle.
    :return: Un objet `Polygon` représentant le rectangle.
    """
    return Polygon([
        (x, y),  # Coin inférieur-gauche
        (x + width, y),  # Coin inférieur-droit
        (x + width, y + height),  # Coin supérieur-droit
        (x, y + height),  # Coin supérieur-gauche
        (x, y),  # Retour au point initial pour fermer le polygone
    ])


# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin pour le fichier généré
shp_file = os.path.join(output_folder, "menger_sponge_rectangular.shp")

# Paramètres initiaux : taille, itérations, coordonnées de départ
iterations = 1  # Attention, la croissance est exponentielle !
initial_width = 1  # Largeur initiale
initial_height = 1  # Hauteur initiale
initial_coords = (0, 0)  # Coordonnées du coin inférieur-gauche initial

# Générer les rectangles de l'éponge de Menger adaptée
rectangles = menger_sponge_2d(initial_coords, initial_width, initial_height, iterations)

# Définir le schéma pour écrire dans le fichier Shapefile
schema = {
    'geometry': 'Polygon',  # Type de géométrie représentée (polygone en 2D)
    'properties': {'id': 'int'},  # Ajouter une propriété ID pour chaque élément
}

# Écriture dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',  # Système de projection (abstrait ici)
    schema=schema,
) as layer:
    polygon_id = 0
    for rectangle in rectangles:
        x, y, width, height = rectangle

        # Créer un polygone pour ce rectangle
        poly = rectangle_to_polygon(x, y, width, height)
        polygon_id += 1
        layer.write({
            'geometry': mapping(poly),  # Transformation en format compatible Fiona
            'properties': {'id': polygon_id},  # Un ID unique pour chaque rectangle
        })

print(f"Shapefile représentant l'éponge de Menger en 2D avec division 3x5 (itérations={iterations}) créé : {shp_file}")
