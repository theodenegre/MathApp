import os
import subprocess
import pandas as pd
from time import time_ns, sleep
import geopandas as gpd


def clean_files():
    sleep(1)
    for filename in os.listdir(coastlines_dir):
        if filename.endswith(".xml") or filename.endswith(".txt"):
            os.remove(os.path.join(coastlines_dir, filename))
    sleep(1)
    for filename in os.listdir("."):
        if filename.startswith("box_glid"):
            os.remove(os.path.join(".", filename))
    sleep(1)


def calculate_box_size(belgium_bounds, country_bounds):
    bel_width = belgium_bounds['x_max'] - belgium_bounds['x_min']
    bel_height = belgium_bounds['y_max'] - belgium_bounds['y_min']

    country_width = country_bounds['x_max'] - country_bounds['x_min']
    country_height = country_bounds['y_max'] - country_bounds['y_min']

    scale_factor = max(country_width / bel_width, country_height / bel_height)
    min_size = min(max(belgium_min_box_size * (scale_factor ** 2), MIN_MIN),
                   MAX_MIN)
    return min_size, min_size * (2 ** NBR_BOXES_APPROX)


def get_country_bounds(filepath):
    gdf = gpd.read_file(filepath)
    bounds = gdf.total_bounds  # [x_min, y_min, x_max, y_max]
    return {
        'x_min': bounds[0],
        'y_min': bounds[1],
        'x_max': bounds[2],
        'y_max': bounds[3]
    }


fractalyse_jar = "fractalyse-3.0-0.9.1.jar"
coastlines_dir = "coastlines/contour"

# We take the Belgium box size as a reference and scale the others accordingly
belgium_min_box_size = 5E-3  # PRECISION PARAMETER TO MODIFY
MIN_MIN = 1E-5
MAX_MIN = 1E-1
NBR_BOXES_APPROX = 3
# Calculate Belgium bounds
belgium_filepath = os.path.join(coastlines_dir, "BEL_contour.geojson")
belgium_bounds = get_country_bounds(belgium_filepath)

specials = ["ATA"]

pays = []
dim = []
durations = []
box_min = []
box_max = []

clean_files()
# Première boucle pour traiter les fichiers .geojson
for filename in os.listdir(coastlines_dir):
    if filename[:3] in specials:
        continue
    elif filename.endswith(".geojson"):
        start = time_ns()
        filepath = os.path.join(coastlines_dir, filename)

        if filename[:3] == "BEL":
            min_value = str(belgium_min_box_size)
            max_value = str(belgium_min_box_size * (2 ** NBR_BOXES_APPROX))
        else:
            country_bounds = get_country_bounds(filepath)
            box_size = calculate_box_size(belgium_bounds, country_bounds)
            min_value = str(box_size[0])
            max_value = str(box_size[1])

        command = ["java", "-jar", fractalyse_jar, "--boxcounting",
                   f"min={min_value}", f"max={max_value}", filepath]
        print(
            f"Calcul pour : {filename[:3]} avec min_value={float(min_value):.2e} et max_value={float(max_value):.2e}")
        subprocess.run(command, stdout=subprocess.DEVNULL)
        durations.append(round((time_ns() - start) / 1e9))
        box_min.append(min_value)
        box_max.append(max_value)

sleep(1)

# Deuxième boucle pour traiter les fichiers .txt
for filename in os.listdir(coastlines_dir):
    if filename[:3] in specials:
        continue
    elif filename.endswith(".txt"):
        filepath = os.path.join(coastlines_dir, filename)
        with open(filepath) as f:
            # La dimension fractale est la 6e ligne du fichier
            fractal_dim = float(f.readlines()[5].split()[2].replace(",", "."))
        pays.append(filename[:3])
        dim.append(fractal_dim)
        print(f"Pays: {filename[:3]}, Dimension fractale: {fractal_dim}")

print(f"{len(pays) = }, {len(dim) = }, {len(durations) = } {len(box_min) = }, {len(box_max) = }")
print("Durée totale :", sum(durations), "secondes")
print("Durée moyenne :", sum(durations) / len(durations), "secondes")

sleep(1)

# Crée le classement et l'enregistre dans un fichier CSV
df = pd.DataFrame(
        {"Pays"   : pays, "Dimension fractale": dim, "durée": durations,
         "box_min": box_min, "box_max": box_max}).sort_values(
    "Dimension fractale", ascending=False).to_csv(
        "fractal_dimensions_adaptative.csv", index=False)

print("Résultats enregistrés dans fractal_dimensions_adaptative.csv")

clean_files()
