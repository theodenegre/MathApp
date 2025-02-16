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
    ax.set_title(f'Box Counting Level {level}\nNumber of boxes: {len(boxes)}, Box size: {width:.2f} x {height:.2f}\nApprx dim : {np.log(len(boxes)) / np.log(1 / width):.2f}')
    return ax


def box_counting_method(shapefile_path, num_levels):
    # Charger et préparer les données
    gdf = load_shapefile(shapefile_path)
    geometry = gdf.union_all()
    coastline = extract_coastline(geometry)
    bounds = coastline.bounds

    counter = GridCounter(bounds)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    initial_box_size = max(width, height)

    box_sizes = []
    box_counts = []

    # Créer une figure avec des sous-graphiques pour chaque niveau
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.ravel()

    for level in range(min(num_levels, 6)):  # Limiter à 6 visualisations
        box_size = initial_box_size / (2 ** level)
        count = counter.count_boxes_recursive(coastline, box_size, level)

        box_sizes.append(box_size)
        box_counts.append(count)

        # Visualiser le comptage des boîtes pour ce niveau
        visualize_box_counting(coastline, counter, level, axes[level])

    plt.tight_layout()
    plt.show()

    return box_sizes, box_counts


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


# Exemple d'utilisation
pays = "BEL"
shapefile_path = f'gadm41_{pays}_shp/gadm41_{pays}_0.shp'
num_levels = 6

# Appliquer la méthode de comptage et visualiser
box_sizes, box_counts = box_counting_method(shapefile_path, num_levels)
fractal_dimension = calculate_fractal_dimension(box_sizes, box_counts)
print(f'Fractal Dimension: {fractal_dimension:.4f}')

# Afficher le graphique de régression
plot_box_counting_regression(box_sizes, box_counts, fractal_dimension)