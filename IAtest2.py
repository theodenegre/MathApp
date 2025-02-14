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
# Hyper-paramètres et paramètres de contrôle
#########################################
initial_pays = "FRA" # Code ISO 3166-1 alpha-3 du pays (exemple : "BEL" pour la Belgique ou "GBR" pour le Royaume-Uni)
# URL des données (GADM 4.1 pour la Belgique - shapefile niveau 0)
DATA_URL = f"https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_{initial_pays}_shp.zip"
# Répertoire de sortie pour l'extraction des fichiers
OUTPUT_DIR = f"gadm41_{initial_pays}_shp"
# Nom du shapefile de niveau 0 dans le zip
SHAPEFILE_NAME = f"gadm41_{initial_pays}_0.shp"
# Nombre maximal de tentatives de téléchargement et délai entre tentatives (en secondes)
MAX_RETRIES = 3
RETRY_DELAY = 5

# Tolérance pour la convergence de l'estimation de la dimension fractale,
# en mesurant la différence absolue entre deux étapes successives
ABS_ERR = 1e-3
# Nombre initial d'échelles pour la box-counting
n_scales_initial = 100
# Nombre maximal d'échelles pour éviter des temps de calcul excessifs
n_scales_max = 1000
# Incrément pour les échelles
STEP_SCALES = (n_scales_max - n_scales_initial) // 10

#########################################
# 1. Télécharger et extraire les données GADM uniquement si nécessaire
#########################################
shapefile_path = os.path.join(OUTPUT_DIR, SHAPEFILE_NAME)

# Vérifier si le fichier shapefile existe déjà
if os.path.exists(shapefile_path):
    print(f"Le fichier {SHAPEFILE_NAME} existe déjà. Utilisation des données existantes.")
else:
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
pays_contours = gpd.read_file(shapefile_path)

fig, ax = plt.subplots(figsize=(8, 8))
pays_contours.plot(ax=ax, edgecolor='black', facecolor='lightgray')
ax.set_axis_off()
plt.title(f"Carte du pays associé au code ISO 3166-1 alpha-3 : {initial_pays}")
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
        for poly in geom.geoms:  # Itérer sur les polygones d'un MultiPolygon
            coords.append(np.array(poly.exterior.coords))
        return np.concatenate(coords, axis=0)
    else:
        return np.empty((0, 2))

for geom in pays_contours.geometry:
    pts = extract_exterior_coords(geom)
    if pts.size > 0:
        all_points.append(pts)

if len(all_points) == 0:
    raise Exception("Aucun point extrait pour le calcul de la dimension fractale.")

points = np.concatenate(all_points, axis=0)

#########################################
# 4. Estimation de la dimension fractale par box‐counting
#    avec contrôle de l'erreur absolue entre deux itérations successives
#########################################
def boxcount(points, box_size):
    """
    Retourne le nombre de boîtes de taille box_size contenant au moins un point.
    """
    min_coords = np.min(points, axis=0)
    max_coords = np.max(points, axis=0)
    indices = np.floor((points - min_coords) / box_size).astype(int)
    unique_boxes = np.unique(indices, axis=0)
    return unique_boxes.shape[0]

# Définir l'intervalle de taille de boîte
min_bound = min(pays_contours.total_bounds[2] - pays_contours.total_bounds[0],
                pays_contours.total_bounds[3] - pays_contours.total_bounds[1])
min_box = min_bound / 100.0  # Taille minimale : 1% de l'étendue minimale
max_box = min_bound          # Taille maximale

# Boucle itérative qui s'arrête lorsque la différence absolue entre deux estimations successives
# est inférieure à ABS_ERR
n_scales = n_scales_initial
fractal_dim_prev = None

while n_scales <= n_scales_max:
    # Définir une suite de tailles de boîtes sur une échelle logarithmique
    box_sizes = np.logspace(np.log10(min_box), np.log10(max_box), num=n_scales)

    counts = []
    for size in box_sizes:
        counts.append(boxcount(points, size))

    log_sizes = np.log(box_sizes)
    log_counts = np.log(counts)
    slope, intercept, r_value, p_value, std_err = linregress(log_sizes, log_counts)
    fractal_dim = -slope

    print(f"n_scales = {n_scales}, dimension fractale = {fractal_dim:.6f}")

    # Si une valeur précédente existe, comparer la différence absolue
    if fractal_dim_prev is not None:
        if abs(fractal_dim - fractal_dim_prev) < ABS_ERR:
            print("Convergence atteinte.")
            break

    fractal_dim_prev = fractal_dim
    n_scales += STEP_SCALES  # Incrément (modifiable en fonction de la précision désirée)

if n_scales > n_scales_max:
    print("Attention : nombre maximal d'échelles atteint sans obtenir la tolérance souhaitée.")

#########################################
# Affichage du résultat et de la régression
#########################################
plt.figure(figsize=(8, 6))
plt.scatter(log_sizes, log_counts, color='royalblue', label='Données')
plt.plot(log_sizes, slope*log_sizes + intercept, 'r', label=f'Régression linéaire\npente = {slope:.3f}')
plt.xlabel("log(Taille de la boîte)")
plt.ylabel("log(Nombre de boîtes)")
plt.title(f"Dimension fractale estimée : {fractal_dim:.3f}\n(n_scales = {n_scales})")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.7)
plt.show()

print(f"Dimension fractale estimée de la frontière belge : {fractal_dim:.3f}")
