import os
import json
from shapely.geometry import mapping, Polygon
from math import sqrt


def sierpinski_carpet(x, y, size, iterations):
    """
    Génère les carrés du tapis de Sierpiński.

    :param x: Coordonnée x du coin inférieur gauche du carré de base.
    :param y: Coordonnée y du coin inférieur gauche du carré de base.
    :param size: Taille du côté du carré de base.
    :param iterations: Nombre d'itérations pour générer le tapis de Sierpiński.
    :return: Liste des carrés restants sous forme de listes de sommets [[(x1, y1), (x2, y2), (x3, y3), (x4, y4)], ...].
    """
    if iterations == 0:
        return [[(x, y), (x + size, y), (x + size, y + size), (x, y + size)]]

    new_size = size / 3
    carpets = []

    for dx in range(3):
        for dy in range(3):
            if dx != 1 or dy != 1:  # Ne pas remplir le carré central
                carpets.extend(sierpinski_carpet(x + dx * new_size, y + dy * new_size, new_size, iterations - 1))

    return carpets


# Vérifier ou créer un dossier simpleGEO
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier de Sierpiński sera sauvegardé
geojson_file = os.path.join(output_folder, "sierpinski_carpet.geojson")

# Générer le tapis de Sierpiński
iterations = 4  # Nombre d'itérations
initial_x, initial_y, initial_size = 0, 0, 1  # Carré de base

carpets = sierpinski_carpet(initial_x, initial_y, initial_size, iterations)  # Liste des carrés restants

# Écriture dans un fichier GeoJSON
features = [{"type": "Feature", "geometry": mapping(Polygon(carpet)), "properties": {"id": i}} for i, carpet in enumerate(carpets, start=1)]
geojson_obj = {"type": "FeatureCollection", "features": features}  # PAS de json.dumps() ici !

with open(geojson_file, 'w', encoding="utf-8") as f:
    json.dump(geojson_obj, f, indent=2)

print(f"GeoJSON représentant le tapis de Sierpiński (itérations={iterations}) créé : {geojson_file}")