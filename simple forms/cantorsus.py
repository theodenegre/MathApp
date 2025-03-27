import os
import json
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
        return [(x1, x2, y, None)]

    fraction_to_remove = 1 / 3
    for i in range(len(k_values) - 1):
        if k_values[i] < iterations <= k_values[i + 1]:
            fraction_to_remove = 3 / 5 if i % 2 == 0 else 1 / 3
            break

    fraction = (x2 - x1) * fraction_to_remove
    left = (x1, x1 + fraction / 2)
    right = (x2 - fraction / 2, x2)

    return (
            cantor_custom(left, iterations - 1, k_values, y * 1) +
            cantor_custom(right, iterations - 1, k_values, y * 1)
    )

# Vérifier ou créer un dossier simpleGEO
output_folder = "simpleGEO"
os.makedirs(output_folder, exist_ok=True)

# Chemin complet où sauvegarder le fichier
geojson_file = os.path.join(output_folder, "cantor_modifie.geojson")

# Générer les k_n pour délimiter les étapes
n_max = 5
k_values = [2**n for n in range(n_max + 1)]

# Générer l'ensemble modifié
iterations = 8
initial_interval = (0, .99)
segments = cantor_custom(initial_interval, iterations, k_values)

# Construire les entités GeoJSON
features = []
for i, (x1, x2, y, _) in enumerate(segments, start=1):
    line = LineString([(x1, y), (x2, y)])
    features.append({
        "type": "Feature",
        "geometry": mapping(line),
        "properties": {
            "id": i,
            "height": y
        }
    })

# Structure GeoJSON
geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

# Écriture dans un fichier GeoJSON
with open(geojson_file, "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, ensure_ascii=False, indent=4)

print(f"GeoJSON représentant l'ensemble modifié créé : {geojson_file}")