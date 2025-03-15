import os
import fiona
from shapely.geometry import mapping, Polygon
from math import cos, sin, pi


def scale_and_translate(vertices, center, scale_factor):
    """
    Réduit la taille d'un pentagone (ou tout polygone) et le déplace au nouveau centre.

    :param vertices: Liste des sommets du polygone [(x1, y1), (x2, y2), ...].
    :param center: Tuple (xc, yc) représentant le nouveau centre du pentagone.
    :param scale_factor: Facteur de réduction de la taille.
    :return: Liste des nouveaux sommets transformés [(x1', y1'), (x2', y2'), ...].
    """
    return [
        (
            center[0] + scale_factor * (x - center[0]),
            center[1] + scale_factor * (y - center[1]),
        )
        for x, y in vertices
    ]


def sierpinski_pentagon(vertices, iterations):
    """
    Génère la structure fractale du pentagone de Sierpiński de manière récursive.

    :param vertices: Liste des sommets du pentagone initial.
    :param iterations: Nombre d'itérations pour générer la fractale.
    :return: Liste des pentagones restants sous forme de listes de sommets.
    """
    if iterations == 0:
        return [vertices]  # Retourne le pentagone de cette branch recursionnelle.

    # Liste pour stocker les subdivisions générées à cette étape.
    new_pentagons = []

    # Traite chaque sommet comme le centre du nouveau petit pentagone
    for i in range(len(vertices)):
        # Centre du petit pentagone = un sommet du pentagone parent
        center = vertices[i]

        # Réduire et décaler un nouveau pentagone centré à "center"
        sub_pentagon = scale_and_translate(vertices, center, scale_factor=0.38)

        # Appel récursif sur le petit pentagone
        new_pentagons += sierpinski_pentagon(sub_pentagon, iterations - 1)

    return new_pentagons


# ----- Génération et exportation -----

# Vérifier ou créer un dossier pour sauvegarder le fichier
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin où le fichier sera sauvegardé
shp_file = os.path.join(output_folder, "sierpinski_pentagon.shp")

# Nombre d'itérations (profondeur fractale)
iterations = 6

# Construire un pentagone initial équilatéral (inscrit dans un cercle)
radius = 1  # Rayon du cercle support
initial_pentagon = [
    (cos(2 * pi * i / 5) * radius, sin(2 * pi * i / 5) * radius)
    for i in range(5)
]

# Générer les pentagones restants
pentagons = sierpinski_pentagon(initial_pentagon, iterations)

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'Polygon',  # Type de géométrie
    'properties': {'id': 'int'},  # Attribut ID
}

# Sauvegarder les pentagones dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',
    schema=schema,
) as layer:
    # Ajouter chaque pentagone comme polygone distinct
    for i, pentagon in enumerate(pentagons, start=1):
        # Créer un polygone avec une boucle fermée
        polygon = Polygon(pentagon)
        layer.write({
            'geometry': mapping(polygon),
            'properties': {'id': i},
        })

print(f"Shapefile représentant le pentagone de Sierpiński (itérations={iterations}) créé : {shp_file}")
