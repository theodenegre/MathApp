import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from matplotlib.animation import FuncAnimation

def get_segments(geom):
    segments = []
    if geom.geom_type == "LineString":
        coords = np.array(geom.coords)
        for i in range(len(coords) - 1):
            segments.append((coords[i], coords[i + 1]))
    elif geom.geom_type == "MultiLineString":
        for line in geom.geoms:
            coords = np.array(line.coords)
            for i in range(len(coords) - 1):
                segments.append((coords[i], coords[i + 1]))
    return segments

def segment_grid_indices(start, end, box_size, min_coords):
    x0, y0 = start
    x1, y1 = end
    cell_x = int(np.floor((x0 - min_coords[0]) / box_size))
    cell_y = int(np.floor((y0 - min_coords[1]) / box_size))
    end_cell_x = int(np.floor((x1 - min_coords[0]) / box_size))
    end_cell_y = int(np.floor((y1 - min_coords[1]) / box_size))

    indices = set()
    indices.add((cell_x, cell_y))

    if (cell_x, cell_y) == (end_cell_x, end_cell_y):
        return indices

    dx = x1 - x0
    dy = y1 - y0

    step_x = 1 if dx > 0 else -1
    step_y = 1 if dy > 0 else -1

    tDeltaX = box_size / abs(dx) if dx != 0 else float('inf')
    tDeltaY = box_size / abs(dy) if dy != 0 else float('inf')

    if dx > 0:
        next_boundary_x = min_coords[0] + (cell_x + 1) * box_size
    else:
        next_boundary_x = min_coords[0] + cell_x * box_size
    if dy > 0:
        next_boundary_y = min_coords[1] + (cell_y + 1) * box_size
    else:
        next_boundary_y = min_coords[1] + cell_y * box_size

    tMaxX = (next_boundary_x - x0) / dx if dx != 0 else float('inf')
    tMaxY = (next_boundary_y - y0) / dy if dy != 0 else float('inf')

    while (cell_x, cell_y) != (end_cell_x, end_cell_y):
        if tMaxX < tMaxY:
            cell_x += step_x
            tMaxX += tDeltaX
        else:
            cell_y += step_y
            tMaxY += tDeltaY
        indices.add((cell_x, cell_y))

    return indices

def get_occupied_boxes(geom, box_size):
    minx, miny, maxx, maxy = geom.bounds
    min_coords = np.array([minx, miny])
    indices_set = set()
    segments = get_segments(geom)

    for seg in segments:
        indices_set |= segment_grid_indices(seg[0], seg[1], box_size, min_coords)

    return indices_set

def boxcount_segments(geom, box_size):
    occupied_boxes = get_occupied_boxes(geom, box_size)
    return len(occupied_boxes)

def calculate_fractal_dimension(geom, min_iterations=4, max_iterations=12, abs_err=1e-3):
    box_sizes = []
    box_counts = []

    minx, miny, maxx, maxy = geom.bounds
    max_dim = max(maxx - minx, maxy - miny)

    for i in range(min_iterations, max_iterations + 1):
        box_size = max_dim / (2 ** i)
        count = boxcount_segments(geom, box_size)
        box_sizes.append(box_size)
        box_counts.append(count)

        if i > min_iterations:
            prev_slope = np.log(box_counts[-2]) / np.log(box_sizes[-2])
            curr_slope = np.log(box_counts[-1]) / np.log(box_sizes[-1])
            if abs(curr_slope - prev_slope) < abs_err:
                break

    fractal_dim = -np.polyfit(np.log(box_sizes), np.log(box_counts), 1)[0]
    return (box_sizes, box_counts, fractal_dim), i


def plot_results(results, iterations, geom):
    box_sizes, counts, fractal_dim = results

    log_sizes = np.log(box_sizes)
    log_counts = np.log(counts)

    slope, intercept, r_value, p_value, std_err = linregress(log_sizes, log_counts)

    plt.figure(figsize=(8, 6))
    plt.scatter(log_sizes, log_counts, color='royalblue', label='Données')
    plt.plot(log_sizes, slope * log_sizes + intercept, 'r', label=f'Régression linéaire\npente = {slope:.3f}')
    plt.xlabel("log(Taille de la boîte)")
    plt.ylabel("log(Nombre de boîtes)")
    plt.title(f"Dimension fractale estimée : {fractal_dim:.3f}\n(iterations = {iterations})")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.7)
    plt.show()

    segments = get_segments(geom)
    plt.figure(figsize=(8, 8))
    for seg in segments:
        seg = np.array(seg)
        plt.plot(seg[:, 0], seg[:, 1], 'k-', lw=1)
    plt.title("Géométrie utilisée pour le calcul (segments)")
    plt.axis('equal')
    plt.show()

    return fractal_dim

def plot_box_counting_step_with_fill(geom, box_size, ax):
    minx, miny, maxx, maxy = geom.bounds
    min_coords = np.array([minx, miny])

    occupied_boxes = get_occupied_boxes(geom, box_size)

    for box in occupied_boxes:
        box_x = min_coords[0] + box[0] * box_size
        box_y = min_coords[1] + box[1] * box_size
        rect = plt.Rectangle((box_x, box_y), box_size, box_size, facecolor='lightblue', alpha=0.5, edgecolor='gray')
        ax.add_patch(rect)

    x_grid = np.arange(min_coords[0], maxx + box_size, box_size)
    y_grid = np.arange(min_coords[1], maxy + box_size, box_size)
    for x in x_grid:
        ax.axvline(x=x, color='gray', alpha=0.3, linestyle=':')
    for y in y_grid:
        ax.axhline(y=y, color='gray', alpha=0.3, linestyle=':')

    segments = get_segments(geom)
    for seg in segments:
        seg = np.array(seg)
        ax.plot(seg[:, 0], seg[:, 1], 'k-', lw=1)

    box_count = len(occupied_boxes)
    total_boxes = (len(x_grid) - 1) * (len(y_grid) - 1)
    ax.set_title(f'Taille de boîte: {box_size:.2f}\nCases occupées: {box_count}/{total_boxes}')

    blue_patch = plt.Rectangle((0, 0), 1, 1, facecolor='lightblue', alpha=0.5)
    white_patch = plt.Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='gray')
    ax.legend([blue_patch, white_patch], ['Case occupée', 'Case vide'], loc='upper right')

    ax.set_aspect('equal')

def create_box_counting_animation_with_fill(geom, viz_box_sizes):
    fig, ax = plt.subplots(figsize=(10, 10))

    def update(frame):
        ax.clear()
        box_size = viz_box_sizes[frame]
        plot_box_counting_step_with_fill(geom, box_size, ax)
        return ax,

    anim = FuncAnimation(fig, update, frames=len(viz_box_sizes), interval=1500, blit=False)
    plt.show()

if __name__ == "__main__":
    initial_pays = input("Entrez le code du pays (ex : GBR pour le Royaume-Uni) : ")
    path = f"coastlines/contour/{initial_pays}_contour.geojson"
    ABS_ERR = 1e-2
    MAX_ITERATIONS = 20 # Bonne valeur : 20
    MIN_ITERATIONS = 4 # Bonne valeur : 4

    pays_contours = gpd.read_file(path)

    multi_line = pays_contours.union_all()
    if multi_line.is_empty:
        raise Exception("Aucune géométrie extraite pour le calcul de la dimension fractale.")

    results, iterations = calculate_fractal_dimension(multi_line, min_iterations=MIN_ITERATIONS, max_iterations=MAX_ITERATIONS, abs_err=ABS_ERR)
    fractal_dim = plot_results(results, iterations, multi_line)
    print(f"Dimension fractale estimée : {fractal_dim:.3f}")

    # Get sizes for visualization
    box_sizes = results[0]
    # Select a few representative box sizes for visualization
    viz_indices = np.linspace(0, len(box_sizes)-1, 4, dtype=int)
    viz_box_sizes = [box_sizes[i] for i in viz_indices]

    fig, axes = plt.subplots(2, 2, figsize=(15, 15))
    axes = axes.ravel()
    for i, box_size in enumerate(viz_box_sizes):
        plot_box_counting_step_with_fill(multi_line, box_size, axes[i])
    plt.tight_layout()
    plt.show()

    create_box_counting_animation_with_fill(multi_line, viz_box_sizes)