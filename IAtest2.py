import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import zipfile
import io
import os
import time
import numpy as np
from scipy.stats import linregress

#########################################
# Hyper-paramètres
#########################################
# URL des données (GADM 4.1 pour la Belgique - shapefile niveau 0)
DATA_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_BEL_shp.zip"
# Répertoire de sortie pour l'extraction des fichiers
OUTPUT_DIR = "gadm41_BEL_shp"
# Nom du shapefile de niveau 0 dans le zip
SHAPEFILE_NAME = "gadm41_BEL_0.shp"
# Nombre maximal de tentatives de téléchargement et délai entre tentatives (en secondes)
MAX_RETRIES = 3
RETRY_DELAY = 5
# Paramètres pour l'estimation de la dimension fractale par box-counting
N_SCALES = 20

#########################################
# 1. Télécharger et extraire les données GADM Belgique (shapefile - gadm41_BEL_0)
#########################################
print("Téléchargement des données...")
response = None
for attempt in range(MAX_RETRIES):
    try:
        print(f"Tentative {attempt+1}/{MAX_RETRIES}...")
        response = requests.get(DATA_URL, timeout=10)
        response.raise_for_status()
        print("Téléchargement réussi.")
        break
    except requests.exceptions.RequestException as e:
        print(f"Tentative {attempt+1}/{MAX_RETRIES} échouée : {e}")
        time.sleep(RETRY_DELAY)

if response is None or response.status_code != 200:
    raise Exception("Toutes les tentatives de téléchargement ont échoué. Veuillez vérifier votre connexion ou télécharger les données manuellement.")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    z.extractall(OUTPUT_DIR)
print("Extraction terminée.")

#########################################
# 2. Chargement du shapefile et affichage de la carte
#########################################
shapefile_path = os.path.join(OUTPUT_DIR, SHAPEFILE_NAME)
belgique = gpd.read_file(shapefile_path)

fig, ax = plt.subplots(figsize=(8, 8))
belgique.plot(ax=ax, edgecolor='black', facecolor='lightgray')
ax.set_axis_off()
plt.title("Carte de la Belgique (GADM 4.1, niveau 0)")
plt.show()

#########################################
# 3. Extraction des points du contour pour estimation de la dimension fractale
#########################################
all_points = []

def extract_exterior_coords(geom):
    """
    Extrait les coordonnées du contour extérieur d'un Polygone ou MultiPolygon.
    """
    if geom.geom_type == "Polygon":
        return np.array(geom.exterior.coords)
    elif geom.geom_type == "MultiPolygon":
        coords = []
        for poly in geom.geoms:  # Itérer sur geom.geoms pour MultiPolygon
            coords.append(np.array(poly.exterior.coords))
        return np.concatenate(coords, axis=0)
    else:
        return np.empty((0, 2))

for geom in belgique.geometry:
    pts = extract_exterior_coords(geom)
    if pts.size > 0:
        all_points.append(pts)

if len(all_points) == 0:
    raise Exception("Aucun point extrait pour le calcul de la dimension fractale.")

points = np.concatenate(all_points, axis=0)

#########################################
# 4. Estimation de la dimension fractale par box‐counting
#########################################
def boxcount(points, box_size):
    """
    Retourne le nombre de boîtes de taille box_size contenant au moins un point.
    """
    min_coords = np.min(points, axis=0)
    max_coords = np.max(points, axis=0)
    nx = int(np.ceil((max_coords[0] - min_coords[0]) / box_size))
    ny = int(np.ceil((max_coords[1] - min_coords[1]) / box_size))
    indices = np.floor((points - min_coords) / box_size).astype(int)
    unique_boxes = np.unique(indices, axis=0)
    return unique_boxes.shape[0]

# Définition des échelles (tailles de boîtes)
min_bound = min(belgique.total_bounds[2] - belgique.total_bounds[0],
                belgique.total_bounds[3] - belgique.total_bounds[1])
min_box = min_bound / 100.0  # Taille minimale : 1% de l'étendue minimale
max_box = min_bound          # Taille maximale
box_sizes = np.logspace(np.log10(min_box), np.log10(max_box), num=N_SCALES)

counts = []
for size in box_sizes:
    N = boxcount(points, size)
    counts.append(N)

log_sizes = np.log(box_sizes)
log_counts = np.log(counts)
slope, intercept, r_value, p_value, std_err = linregress(log_sizes, log_counts)
fractal_dim = -slope

plt.figure(figsize=(8, 6))
plt.scatter(log_sizes, log_counts, color='royalblue', label='Données')
plt.plot(log_sizes, slope * log_sizes + intercept, 'r', label=f'Régression linéaire\npente = {slope:.3f}')
plt.xlabel("log(Taille de la boîte)")
plt.ylabel("log(Nombre de boîtes)")
plt.title(f"Dimension fractale estimée : {fractal_dim:.3f}")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.7)
plt.show()

print(f"Dimension fractale estimée de la frontière belge : {fractal_dim:.3f}")
