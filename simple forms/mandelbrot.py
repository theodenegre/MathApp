import os
import fiona
from shapely.geometry import mapping, Point
from tqdm import tqdm


def mandelbrot(c, max_iterations):
    """
    Calcule si un point c appartient à l'ensemble de Mandelbrot à l'aide d'une itération.

    :param c: Nombre complexe représentant le point c (dans le plan complexe).
    :param max_iterations: Nombre maximal d'itérations pour déterminer si c reste borné.
    :return: Le nombre d'itérations avant que c échappe (ou max_iterations si c est dans l'ensemble).
    """
    z = 0  # Initialisation de z à 0
    for n in range(max_iterations):
        z = z * z + c
        if abs(z) > 2:  # Si la valeur de |z| dépasse 2, c n'est pas dans l'ensemble
            return n
    return max_iterations  # Si la valeur est restée bornée pendant toutes les itérations, c est considéré dans l'ensemble


# Créer un dossier pour le fichier de sortie
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin où le fichier de Mandelbrot sera sauvegardé
shp_file = os.path.join(output_folder, "mandelbrot.shp")

# Définir les limites du plan complexe à explorer et la résolution
x_min, x_max = -3, 2.0  # Limites pour les parties réelles
y_min, y_max = -1.25, 1.25  # Limites pour les parties imaginaires
resolution = 1_000  # Nombre de points par axe (plus grand = plus de détails)

# Définir le nombre maximal d'itérations
max_iterations = 100

# Créer une grille de points dans le plan complexe
x_values = [x_min + (x_max - x_min) * i / resolution for i in range(resolution)]
y_values = [y_min + (y_max - y_min) * i / resolution for i in range(resolution)]

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'Point',  # Type de géométrie (point)
    'properties': {'iterations': 'int'},  # Attribut représentant le nombre d'itérations avant échappement
}

# Écriture dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',  # Système de coordonnées fictif pour les besoins de visualisation
    schema=schema,
) as layer:
    # Itérer sur chaque point de la grille
    for x in tqdm(x_values, desc="Calcul de l'ensemble de Mandelbrot"):
        for y in y_values:
            c = complex(x, y)  # Les coordonnées dans le plan complexe
            iterations = mandelbrot(c, max_iterations)  # Calculer le nombre d'itérations
            if iterations == max_iterations:
                # Ajouter le point uniquement s'il appartient (approximativement) à l'ensemble de Mandelbrot
                point = Point(x, y)
                layer.write({
                    'geometry': mapping(point),  # Transformation en format compatible Fiona
                    'properties': {'iterations': iterations},  # Ajout du niveau d'échappement
                })

print(f"Shapefile représentant l'ensemble de Mandelbrot créé : {shp_file}")
