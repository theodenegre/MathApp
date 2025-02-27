import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import zipfile
import io
import os
import time
import numpy as np
from scipy.stats import linregress
from matplotlib.animation import FuncAnimation

#########################################
# Hyper-paramètres et paramètres de contrôle
#########################################
initial_pays = "BEL"
DATA_URL = f"https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_{initial_pays}_shp.zip"
OUTPUT_DIR = f"gadm41_{initial_pays}_shp"
SHAPEFILE_NAME = f"gadm41_{initial_pays}_0.shp"
MAX_RETRIES = 3
RETRY_DELAY = 5
ABS_ERR = 1e-3
n_scales_initial = 100
n_scales_max = 1000
STEP_SCALES = (n_scales_max - n_scales_initial) // 10


#########################################
# Fonctions optimisées
#########################################
def optimized_boxcount(points, box_size):
    """
    Version optimisée du box counting utilisant numpy pour les calculs vectoriels
    """
    min_coords = points.min(axis=0)
    indices = np.floor((points - min_coords) / box_size).astype(int)
    unique_boxes = set(map(tuple, indices))
    return len(unique_boxes)


def calculate_fractal_dimension(points, n_scales_initial=100, max_scales=1000,
                                abs_err=1e-3, step_scales=100):
    """
    Calcul optimisé de la dimension fractale avec contrôle de convergence
    """
    min_coords = points.min(axis=0)
    max_coords = points.max(axis=0)
    min_bound = min(max_coords - min_coords)

    min_box = min_bound / 100.0
    max_box = min_bound

    n_scales = n_scales_initial
    fractal_dim_prev = None
    results = []

    while n_scales <= max_scales:
        box_sizes = np.logspace(np.log10(min_box), np.log10(max_box),
                                num=n_scales)
        counts = [optimized_boxcount(points, size) for size in box_sizes]

        log_sizes = np.log(box_sizes)
        log_counts = np.log(counts)

        slope, intercept, r_value, p_value, std_err = linregress(log_sizes,
                                                                 log_counts)
        fractal_dim = -slope

        results.append((box_sizes, counts, fractal_dim))
        print(f"n_scales = {n_scales}, dimension fractale = {fractal_dim:.6f}")

        if fractal_dim_prev is not None and abs(
                fractal_dim - fractal_dim_prev) < abs_err:
            print("Convergence atteinte.")
            break

        fractal_dim_prev = fractal_dim
        n_scales += step_scales

    if n_scales > max_scales:
        print(
            "Attention : nombre maximal d'échelles atteint sans obtenir la tolérance souhaitée.")

    return results[-1], n_scales


def plot_results(results, n_scales):
    """
    Fonction d'affichage des résultats
    """
    box_sizes, counts, fractal_dim = results

    log_sizes = np.log(box_sizes)
    log_counts = np.log(counts)
    slope = -fractal_dim
    intercept = log_counts[0] + slope * log_sizes[0]

    plt.figure(figsize=(8, 6))
    plt.scatter(log_sizes, log_counts, color='royalblue', label='Données')
    plt.plot(log_sizes, slope * log_sizes + intercept, 'r',
             label=f'Régression linéaire\npente = {slope:.3f}')
    plt.xlabel("log(Taille de la boîte)")
    plt.ylabel("log(Nombre de boîtes)")
    plt.title(
        f"Dimension fractale estimée : {fractal_dim:.3f}\n(n_scales = {n_scales})")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.7)
    plt.show()

    return fractal_dim


def extract_exterior_coords(geom):
    """
    Extrait les coordonnées du contour extérieur d'un Polygone ou MultiPolygon.
    """
    if geom.geom_type == "Polygon":
        return np.array(geom.exterior.coords)
    elif geom.geom_type == "MultiPolygon":
        coords = []
        for poly in geom.geoms:
            coords.append(np.array(poly.exterior.coords))
        return np.concatenate(coords, axis=0)
    else:
        return np.empty((0, 2))


def plot_box_counting_step_with_fill(points, box_size, ax):
    """
    Visualise une étape du box-counting avec les boîtes colorées.
    """
    min_coords = np.min(points, axis=0)
    max_coords = np.max(points, axis=0)
    indices = np.floor((points - min_coords) / box_size).astype(int)
    unique_boxes = np.unique(indices, axis=0)

    for box in unique_boxes:
        box_x = min_coords[0] + box[0] * box_size
        box_y = min_coords[1] + box[1] * box_size
        rect = plt.Rectangle((box_x, box_y), box_size, box_size,
                             facecolor='lightblue', alpha=0.5,
                             edgecolor='gray')
        ax.add_patch(rect)

    x_grid = np.arange(min_coords[0], max_coords[0] + box_size, box_size)
    y_grid = np.arange(min_coords[1], max_coords[1] + box_size, box_size)

    for x in x_grid:
        ax.axvline(x=x, color='gray', alpha=0.3, linestyle=':')
    for y in y_grid:
        ax.axhline(y=y, color='gray', alpha=0.3, linestyle=':')

    ax.plot(points[:, 0], points[:, 1], 'k.', markersize=1)

    box_count = unique_boxes.shape[0]
    total_boxes = (len(x_grid) - 1) * (len(y_grid) - 1)

    ax.set_title(f'Taille de boîte: {box_size:.2f}\n'
                 f'Boîtes occupées: {box_count}/{total_boxes}\n'
                 f'({(box_count / total_boxes * 100):.1f}% de couverture)')

    blue_patch = plt.Rectangle((0, 0), 1, 1, facecolor='lightblue', alpha=0.5)
    white_patch = plt.Rectangle((0, 0), 1, 1, facecolor='white',
                                edgecolor='gray')
    ax.legend([blue_patch, white_patch], ['Boîte occupée', 'Boîte vide'],
              loc='upper right')

    ax.set_aspect('equal')


def create_box_counting_animation_with_fill(points, viz_box_sizes):
    fig, ax = plt.subplots(figsize=(10, 10))

    def update(frame):
        ax.clear()
        box_size = viz_box_sizes[frame]
        plot_box_counting_step_with_fill(points, box_size, ax)
        return ax,

    anim = FuncAnimation(fig, update, frames=len(viz_box_sizes),
                         interval=1500, blit=False)
    plt.show()


#########################################
# Programme principal
#########################################
# 1. Téléchargement et extraction des données
shapefile_path = os.path.join(OUTPUT_DIR, SHAPEFILE_NAME)

if os.path.exists(shapefile_path):
    print(
        f"Le fichier {SHAPEFILE_NAME} existe déjà. Utilisation des données existantes.")
else:
    print("Téléchargement des données...")
    response = None
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Tentative {attempt + 1}/{MAX_RETRIES}...")
            response = requests.get(DATA_URL, timeout=10)
            response.raise_for_status()
            print("Téléchargement réussi.")
            break
        except requests.exceptions.RequestException as e:
            print(f"Tentative {attempt + 1}/{MAX_RETRIES} échouée : {e}")
            time.sleep(RETRY_DELAY)

    if response is None or response.status_code != 200:
        raise Exception("Toutes les tentatives de téléchargement ont échoué.")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(OUTPUT_DIR)
    print("Extraction terminée.")

# 2. Chargement et affichage de la carte
pays_contours = gpd.read_file(shapefile_path)

fig, ax = plt.subplots(figsize=(8, 8))
pays_contours.plot(ax=ax, edgecolor='black', facecolor='lightgray')
ax.set_axis_off()
plt.title(f"Carte du pays : {initial_pays}")
plt.show()

# 3. Extraction des points du contour
all_points = []
for geom in pays_contours.geometry:
    pts = extract_exterior_coords(geom)
    if pts.size > 0:
        all_points.append(pts)

if len(all_points) == 0:
    raise Exception(
        "Aucun point extrait pour le calcul de la dimension fractale.")

points = np.concatenate(all_points, axis=0)

# 4. Calcul de la dimension fractale
results, n_scales = calculate_fractal_dimension(points,
                                                n_scales_initial=n_scales_initial,
                                                max_scales=n_scales_max,
                                                abs_err=ABS_ERR,
                                                step_scales=STEP_SCALES)

fractal_dim = plot_results(results, n_scales)
print(f"Dimension fractale estimée : {fractal_dim:.3f}")

# 5. Visualisation du box-counting
min_bound = min(pays_contours.total_bounds[2] - pays_contours.total_bounds[0],
                pays_contours.total_bounds[3] - pays_contours.total_bounds[1])
min_box = min_bound / 100.0
max_box = min_bound

n_viz = 4
viz_box_sizes = np.logspace(np.log10(min_box), np.log10(max_box), num=n_viz)

fig, axes = plt.subplots(2, 2, figsize=(15, 15))
axes = axes.ravel()

for i, box_size in enumerate(viz_box_sizes):
    plot_box_counting_step_with_fill(points, box_size, axes[i])

plt.tight_layout()
plt.show()

# 6. Animation (optionnelle)
create_box_counting_animation_with_fill(points, viz_box_sizes)
