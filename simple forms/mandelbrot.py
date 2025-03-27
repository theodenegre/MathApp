import os
import json
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
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin où le fichier de Mandelbrot sera sauvegardé
geojson_file = os.path.join(output_folder, "mandelbrot.geojson")

# Définir les limites du plan complexe à explorer et la résolution
x_min, x_max = -3, 2.0  # Limites pour les parties réelles
y_min, y_max = -1.25, 1.25  # Limites pour les parties imaginaires
resolution = 1_000  # Nombre de points par axe (plus grand = plus de détails)

# Définir le nombre maximal d'itérations
max_iterations = 100

# Créer une grille de points dans le plan complexe
x_values = [x_min + (x_max - x_min) * i / resolution for i in range(resolution)]
y_values = [y_min + (y_max - y_min) * i / resolution for i in range(resolution)]

# Construire les entités GeoJSON
features = []
for x in tqdm(x_values, desc="Calcul de l'ensemble de Mandelbrot"):
    for y in y_values:
        c = complex(x, y)  # Les coordonnées dans le plan complexe
        iterations = mandelbrot(c, max_iterations)  # Calculer le nombre d'itérations
        if iterations == max_iterations:
            # Ajouter le point uniquement s'il appartient (approximativement) à l'ensemble de Mandelbrot
            point = Point(x, y)
            features.append({
                "type": "Feature",
                "geometry": mapping(point),
                "properties": {"iterations": iterations}
            })

# Structure GeoJSON
geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

# Écriture dans un fichier GeoJSON
with open(geojson_file, "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, ensure_ascii=False, indent=4)

print(f"GeoJSON représentant l'ensemble de Mandelbrot créé : {geojson_file}")
