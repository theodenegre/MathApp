import os
import subprocess
import pandas as pd
from time import time_ns, sleep


def clean():
    sleep(1)
    for filename in os.listdir(coastlines_dir):
        if filename.endswith(".xml") or filename.endswith(".txt"):
            os.remove(os.path.join(coastlines_dir, filename))
    sleep(1)

fractalyse_jar = "fractalyse-3.0-0.9.1.jar"
coastlines_dir = "coastlines/contour"

# Boxcounting parameters
min_value = "1E-1"
max_value = "1.0"

specials = ["ATA"]

clean()

pays = []
dim = []
durations = []

# Première boucle pour traiter les fichiers .geojson
for filename in os.listdir(coastlines_dir):
    if filename[:3] in specials:
        continue
    elif filename.endswith(".geojson"):
        start = time_ns()
        filepath = os.path.join(coastlines_dir, filename)
        command = ["java", "-jar", fractalyse_jar, "--boxcounting",
                   f"min={min_value}", f"max={max_value}", filepath]
        subprocess.run(command)
        durations.append(round((time_ns() - start) / 1e9))

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

sleep(1)

# Crée le classement et l'enregistre dans un fichier CSV
df = pd.DataFrame(
    {"Pays": pays, "Dimension fractale": dim, "durée": durations}
).sort_values("Dimension fractale", ascending=False).to_csv(
    "fractal_dimensions.csv", index=False)

clean()
