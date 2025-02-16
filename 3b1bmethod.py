import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import box

def load_shapefile(shapefile_path):
    return gpd.read_file(shapefile_path)

def extract_coastline(geometry):
    """
    Extrait uniquement la 'coastline' d'une géométrie.
    Cela revient à utiliser uniquement le contour extérieur (boundary).
    """
    # Extraire les limites (boundary) des géométries fusionnées.
    return geometry.boundary

def create_grid(bounds, box_size):
    minx, miny, maxx, maxy = bounds
    x_coords = np.arange(minx, maxx, box_size)
    y_coords = np.arange(miny, maxy, box_size)
    grid = [box(x, y, x + box_size, y + box_size) for x in x_coords for y in y_coords]
    return grid

def count_boxes_touched(geometry, grid):
    count = 0
    for box_geom in grid:
        if box_geom.intersects(geometry):
            count += 1
    return count

def box_counting_method(shapefile_path, box_sizes):
    gdf = load_shapefile(shapefile_path)
    geometry = gdf.union_all()  # Fusionner toutes les géométries du shapefile

    # Extraire uniquement la limite (coastline)
    coastline = extract_coastline(geometry)
    bounds = coastline.bounds

    box_counts = []
    for box_size in box_sizes:
        grid = create_grid(bounds, box_size)
        count = count_boxes_touched(coastline, grid)  # Utiliser uniquement la côte
        box_counts.append(count)

    return box_sizes, box_counts

def calculate_fractal_dimension(box_sizes, box_counts):
    log_sizes = np.log(box_sizes)
    log_counts = np.log(box_counts)
    slope, intercept = np.polyfit(log_sizes, log_counts, 1)
    return -slope

def plot_box_counting(box_sizes, box_counts, fractal_dimension):
    plt.scatter(np.log(box_sizes), np.log(box_counts), label='Box Counting Data')
    plt.xlabel('Log of Box Size')
    plt.ylabel('Log of Box Count')
    plt.title(f'Box Counting Method\nFractal Dimension: {fractal_dimension:.2f}')
    plt.legend()
    plt.show()

# Exemple d'utilisation
pays = "BEL"  # Code ISO pour votre pays
shapefile_path = f'gadm41_{pays}_shp/gadm41_{pays}_0.shp'  # Chemin vers votre shapefile
start_size = 0.1  # Taille initiale de la boîte
box_sizes = [start_size/(2 ** i) for i in range(4)]  # Versions successives des tailles de boîte

# Appliquer la méthode de comptage
box_sizes, box_counts = box_counting_method(shapefile_path, box_sizes)
fractal_dimension = calculate_fractal_dimension(box_sizes, box_counts)
print(f'Fractal Dimension: {fractal_dimension:.4f}')

# Afficher le graphique
plot_box_counting(box_sizes, box_counts, fractal_dimension)
