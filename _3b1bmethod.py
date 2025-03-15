import time

import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import box
from matplotlib.patches import Rectangle


def load_shapefile(shapefile_path):
    return gpd.read_file(shapefile_path)


def extract_coastline(geometry):
    return geometry.boundary


class GridCounter:
    def __init__(self, bounds):
        self.bounds = bounds
        self.selected_boxes = {}

    def create_subboxes(self, parent_box):
        minx, miny, maxx, maxy = parent_box.bounds
        midx = (minx + maxx) / 2
        midy = (miny + maxy) / 2

        return [
            box(minx, miny, midx, midy),
            box(midx, miny, maxx, midy),
            box(minx, midy, midx, maxy),
            box(midx, midy, maxx, maxy)
        ]

    def count_boxes_recursive(self, geometry, box_size, level=0):
        if level == 0:
            minx, miny, maxx, maxy = self.bounds
            x_coords = np.arange(minx, maxx, box_size)
            y_coords = np.arange(miny, maxy, box_size)
            boxes = [box(x, y, x + box_size, y + box_size)
                     for x in x_coords for y in y_coords]

            self.selected_boxes[level] = [b for b in boxes if
                                          geometry.intersects(b)]

        else:
            parent_boxes = self.selected_boxes[level - 1]
            current_boxes = []

            for parent_box in parent_boxes:
                subboxes = self.create_subboxes(parent_box)
                current_boxes.extend(
                        [b for b in subboxes if geometry.intersects(b)])

            self.selected_boxes[level] = current_boxes

        return len(self.selected_boxes[level])


def visualize_box_counting(geometry, counter, level, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 8))

    # Tracer la côte
    if hasattr(geometry, 'geoms'):
        for geom in geometry.geoms:
            x, y = geom.xy
            ax.plot(x, y, 'k-', linewidth=0.5)
    else:
        x, y = geometry.xy
        ax.plot(x, y, 'k-', linewidth=0.5)

    # Tracer les boîtes sélectionnées
    boxes = counter.selected_boxes[level]
    for box_geom in boxes:
        minx, miny, maxx, maxy = box_geom.bounds
        width = maxx - minx
        height = maxy - miny
        rect = Rectangle((minx, miny), width, height,
                         fill=False, edgecolor='r', alpha=0.5)
        ax.add_patch(rect)

    # Configurer les axes
    ax.set_aspect('equal')
    ax.set_title(f'Box Counting Level {level}\nNumber of boxes: {len(boxes)}, Box size: {width:.2f} x {height:.2f}')
    return ax


def calculate_box_counting_unoptimized(shapefile_path, num_levels):
    """
    Complexité exponentielle en num_levels (temps et mémoire)
    """
    # Charger et préparer les données
    gdf = load_shapefile(shapefile_path)
    geometry = gdf.union_all()
    coastline = extract_coastline(geometry)
    bounds = coastline.bounds

    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    initial_box_size = max(width, height)

    box_sizes = []
    box_counts = []

    # Pour chaque niveau
    for level in range(num_levels):
        box_size = initial_box_size / (2 ** level)

        # Créer une grille de boîtes pour ce niveau
        minx, miny, maxx, maxy = bounds
        x_coords = np.arange(minx, maxx, box_size)
        y_coords = np.arange(miny, maxy, box_size)

        # Créer toutes les boîtes possibles
        boxes = [box(x, y, x + box_size, y + box_size)
                 for x in x_coords for y in y_coords]

        # Compter les boîtes qui intersectent la côte
        intersecting_boxes = [b for b in boxes if coastline.intersects(b)]

        box_sizes.append(box_size)
        box_counts.append(len(intersecting_boxes))

    return coastline, None, box_sizes, box_counts


def calculate_box_counting(shapefile_path, num_levels):
    # Charger et préparer les données
    gdf = load_shapefile(shapefile_path)
    geometry = gdf.union_all()
    coastline = extract_coastline(geometry)
    bounds = coastline.bounds

    counter = GridCounter(bounds)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    initial_box_size = max(width, height) / 2

    box_sizes = []
    box_counts = []

    # Calculer tous les niveaux
    for level in range(num_levels):
        box_size = initial_box_size / (2 ** level)
        count = counter.count_boxes_recursive(coastline, box_size, level)
        box_sizes.append(box_size)
        box_counts.append(count)

    return coastline, counter, box_sizes, box_counts

def plot_box_counting_levels(coastline, counter, num_levels):
    # Créer une figure avec des sous-graphiques pour chaque niveau
    fig, axes = plt.subplots(2, 2, figsize=(15, 15))
    axes = axes.ravel()

    # Sélectionner les niveaux à visualiser
    levels_to_show = [0]
    if num_levels > 2:
        levels_to_show.append((num_levels-1) // 3)
    if num_levels > 3:
        levels_to_show.append(2 * (num_levels-1) // 3)
    if num_levels > 1:
        levels_to_show.append(num_levels-1)

    # Visualiser les niveaux sélectionnés
    for i, level in enumerate(levels_to_show):
        if i < 4:  # Limiter à 4 visualisations
            ax = visualize_box_counting(coastline, counter, level, ax=axes[i])

    # plt.tight_layout()
    plt.show()


def calculate_fractal_dimension(box_sizes, box_counts):
    log_sizes = np.log(box_sizes)
    log_counts = np.log(box_counts)
    slope, intercept = np.polyfit(log_sizes, log_counts, 1)
    return -slope


def plot_box_counting_regression(box_sizes, box_counts, fractal_dimension):
    plt.figure(figsize=(10, 6))
    plt.scatter(np.log(box_sizes), np.log(box_counts),
                label='Box Counting Data')

    log_sizes = np.log(box_sizes)
    log_counts = np.log(box_counts)
    slope, intercept = np.polyfit(log_sizes, log_counts, 1)
    plt.plot(log_sizes, slope * log_sizes + intercept, 'r-',
             label=f'Regression (D = {-slope:.2f})')

    plt.xlabel('Log of Box Size')
    plt.ylabel('Log of Box Count')
    plt.title(
        f'Box Counting Method\nFractal Dimension: {fractal_dimension:.2f}')
    plt.legend()
    plt.grid(True)
    plt.show()


def compare_speed(shapefile_path, num_levels):
    # Exécuter la version optimisée
    start_optimized = time.time()
    coastline, counter, box_sizes, box_counts = calculate_box_counting(shapefile_path, num_levels)
    time_optimized = time.time() - start_optimized
    fractal_dimension = calculate_fractal_dimension(box_sizes, box_counts)

    # Exécuter la version non optimisée
    start_unoptimized = time.time()
    coastline, _, box_sizes_unopt, box_counts_unopt = calculate_box_counting_unoptimized(shapefile_path, num_levels)
    time_unoptimized = time.time() - start_unoptimized
    fractal_dimension_unopt = calculate_fractal_dimension(box_sizes_unopt, box_counts_unopt)

    # Calculer le facteur d'accélération
    speedup = time_unoptimized/time_optimized

    # Créer le tableau avec des strings formatés
    print("\nPerformance Comparison:")
    print("-" * 65)
    print(f"{'Metric':<20} {'Optimized':<15} {'Unoptimized':<15} {'Difference':<15}")
    print("-" * 65)
    print(f"{'Execution Time (s)':<20} {time_optimized:.<15.4f} {time_unoptimized:.<15.4f} {speedup:.2f}x faster")
    print(f"{'Fractal Dimension':<20} {fractal_dimension:.<15.4f} {fractal_dimension_unopt:.<15.4f} {abs(fractal_dimension - fractal_dimension_unopt):.4f}")
    print("-" * 65)


def print_and_plot(shapefile_path, num_levels):
    print("Calculating fractal dimension using Box Counting Method...")
    coastline, counter, box_sizes, box_counts = calculate_box_counting(
        shapefile_path, num_levels)
    fractal_dimension = calculate_fractal_dimension(box_sizes, box_counts)

    print(f"Fractal dimension of {shapefile_path} : {fractal_dimension}")

    print("Plotting box counting levels...")
    plot_box_counting_levels(coastline, counter, num_levels)
    print("Plotting regression line...")
    plot_box_counting_regression(box_sizes, box_counts, fractal_dimension)


if __name__ == "__main__":
    pays = "NOR"
    shapefile_path = f'gadm41_{pays}_shp/gadm41_{pays}_0.shp'
    shapefile_path = f'peano_curve.shp'
    num_levels = 4

    # compare_speed(shapefile_path, num_levels)
    print_and_plot(shapefile_path, num_levels)