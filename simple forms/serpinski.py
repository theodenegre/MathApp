import os
import fiona
from shapely.geometry import mapping, Polygon
from math import sqrt


def sierpinski(vertices, iterations):
    """
    Génère les triangles du triangle de Sierpiński.

    :param vertices: Liste des sommets du triangle de base [(x1, y1), (x2, y2), (x3, y3)].
    :param iterations: Nombre d'itérations pour générer le triangle de Sierpiński.
    :return: Liste des triangles restants sous forme de listes de sommets [[(x1, y1), (x2, y2), (x3, y3)], ...].
    """
    if iterations == 0:
        return [vertices]

    # Points des sommets du triangle initial
    (x1, y1), (x2, y2), (x3, y3) = vertices

    # Calcul des milieux des trois côtés du triangle
    mid1 = ((x1 + x2) / 2, (y1 + y2) / 2)
    mid2 = ((x2 + x3) / 2, (y2 + y3) / 2)
    mid3 = ((x3 + x1) / 2, (y3 + y1) / 2)

    # Récursion sur les trois triangles restants
    return (
        sierpinski([vertices[0], mid1, mid3], iterations - 1) +   # Triangle en bas à gauche
        sierpinski([mid1, vertices[1], mid2], iterations - 1) +   # Triangle en bas à droite
        sierpinski([mid3, mid2, vertices[2]], iterations - 1)     # Triangle en haut
    )


# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où le fichier de Sierpiński sera sauvegardé
shp_file = os.path.join(output_folder, "sierpinski.shp")

# Générer le triangle de Sierpiński
iterations = 11  # Nombre d'itérations
initial_triangle = [(0, 0), (1, 0), (.5, sqrt(3) / 2)]  # Triangle équilatéral de base

triangles = sierpinski(initial_triangle, iterations)  # Liste des triangles restants

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'Polygon',  # Type de géométrie (polygone pour les triangles)
    'properties': {'id': 'int'},  # Attribut "id" pour identifier les polygones
}

# Écriture dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',  # Système de coordonnées (non critique ici car abstrait)
    schema=schema,
) as layer:
    # Ajouter chaque triangle comme un polygone
    for i, triangle in enumerate(triangles, start=1):
        # Créer un polygone à partir des sommets, boucle fermée
        polygon = Polygon(triangle)
        layer.write({
            'geometry': mapping(polygon),  # Transformation en format compatible Fiona
            'properties': {'id': i},  # Attribut ID pour identifier le polygone
        })

print(f"Shapefile représentant le triangle de Sierpiński (itérations={iterations}) créé : {shp_file}")
