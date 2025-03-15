import os
import fiona
from shapely.geometry import mapping, LineString


def cantor_custom(interval, iterations, k_values, y=0):
    """
    Génère les segments de l'ensemble modifié avec une hauteur différente à chaque étape d'itération.

    :param interval: Tuple représentant l'intervalle (x1, x2).
    :param iterations: Nombre total d'itérations restantes.
    :param k_values: Liste des k_n = 10^n (limites des étapes).
    :param y: Hauteur actuelle du segment (augmente de 1 à chaque itération).
    :return: Liste des segments de l'ensemble sous forme de tuples [(x1, x2, y, fraction), ...].
    """
    x1, x2 = interval

    if iterations == 0:
        # Terminaison : retourner le segment complet
        return [(x1, x2, y, None)]

    # Identifier la fraction à enlever en fonction de l'itération actuelle
    fraction_to_remove = 1 / 3  # Valeur par défaut
    for i in range(len(k_values) - 1):
        if k_values[i] < iterations <= k_values[i + 1]:
            # Alterner entre 3/5 et 1/3 en fonction de la plage
            fraction_to_remove = 3 / 5 if i % 2 == 0 else 1 / 3
            break

    # Supprimer la fraction centrale et appeler récursivement sur les deux segments restants
    fraction = (x2 - x1) * fraction_to_remove
    left = (x1, x1 + fraction / 2)  # Segment gauche
    right = (x2 - fraction / 2, x2)  # Segment droit

    # Ajouter l'information sur la hauteur avec une augmentation de +1
    return (
            cantor_custom(left, iterations - 1, k_values, y * 1) +
            cantor_custom(right, iterations - 1, k_values, y * 1)
    )


# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où sauvegarder le fichier
shp_file = os.path.join(output_folder, "cantor_modifie.shp")

# Générer les k_n pour délimiter les étapes (ici k_n = 10^n)
n_max = 5  # Nombre de niveaux (définir en fonction des besoins)
k_values = [2**n for n in range(n_max + 1)]

# Générer l'ensemble modifié
iterations = 8  # Nombre d'itérations (peut être ajusté selon les besoins)
initial_interval = (0, .99)  # Intervalle initial [0, 1]
segments = cantor_custom(initial_interval, iterations, k_values)

# Définir le schéma pour le Shapefile
schema = {
    'geometry': 'LineString',  # Type de géométrie (ligne)
    'properties': {
        'id': 'int',           # Attribut "id" pour identifier les segments
        'height': 'int',       # Hauteur (profondeur de l'itération)
    },
}

# Écrire dans un fichier Shapefile
with fiona.open(
    shp_file,
    mode='w',
    driver='ESRI Shapefile',
    crs='EPSG:4326',  # Système de coordonnées arbitraire
    schema=schema,
) as layer:
    # Ajouter chaque segment comme une ligne
    for i, (x1, x2, y, _) in enumerate(segments, start=1):
        line = LineString([(x1, y), (x2, y)])  # Segment horizontal positionné à la hauteur y
        layer.write({
            'geometry': mapping(line),  # Transformation en format compatible Fiona
            'properties': {
                'id': i,       # ID unique pour chaque segment
                'height': y,   # Hauteur correspondant à la profondeur de l'itération
            },
        })

print(f"Shapefile représentant l'ensemble modifié créé : {shp_file}")
