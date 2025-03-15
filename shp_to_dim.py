import numpy as np
import trimesh
import geopandas as gpd
from shapely.geometry import box


def box_counting_dimension(input_file, is_3d=False, min_box_size=0.01, max_box_size=10, num_scales=10):
    """
    Calcul de la dimension fractale (box-counting) pour des objets 2D et 3D.

    Args:
        input_file (str): Chemin vers le fichier (Shapefile pour objets 2D / fichiers 3D comme OBJ, STL pour objets 3D).
        is_3d (bool): Indique si l'objet est en 3D.
        min_box_size (float): Taille minimale des boîtes.
        max_box_size (float): Taille maximale des boîtes.
        num_scales (int): Nombre d'échelles pour le comptage (entre min_box_size et max_box_size).

    Returns:
        float: La dimension fractale estimée.
    """
    if is_3d:
        # Cas 3D : Chargez l'objet avec Trimesh
        mesh = trimesh.load(input_file)
        if not isinstance(mesh, trimesh.Trimesh):
            raise ValueError("Fichier 3D non valide ou format non pris en charge.")

        # Extraire les bornes (bounding box) de l'objet
        bounds = mesh.bounds  # [[xmin, ymin, zmin], [xmax, ymax, zmax]]
        xmin, ymin, zmin = bounds[0]
        xmax, ymax, zmax = bounds[1]

        # Calculer la dimension fractale 3D
        return _calculate_box_counting_3d(mesh, (xmin, ymin, zmin, xmax, ymax, zmax), min_box_size, max_box_size, num_scales)

    else:
        # Cas 2D : Charger un shapefile (ou autre fichier compatible Geopandas)
        gdf = gpd.read_file(input_file)

        # Combiner toutes les géométries en une seule (via union)
        geometry_total = gdf.unary_union

        # Extraire les bornes (bounding box) de la géométrie
        xmin, ymin, xmax, ymax = geometry_total.bounds

        # Calculer la dimension fractale 2D
        return _calculate_box_counting_2d(geometry_total, (xmin, ymin, xmax, ymax), min_box_size, max_box_size, num_scales)


def _calculate_box_counting_2d(geometry, bounds, min_box_size, max_box_size, num_scales):
    """
    Calcul du comptage par boîte pour un objet 2D.

    Args:
        geometry (shapely.geometry.base.BaseGeometry): Géométrie 2D (polygone, ligne).
        bounds (tuple): Limites (xmin, ymin, xmax, ymax) de l'objet.
        min_box_size (float): Taille minimale des boîtes.
        max_box_size (float): Taille maximale des boîtes.
        num_scales (int): Nombre d'échelles pour le comptage.

    Returns:
        float: La dimension fractale estimée.
    """
    xmin, ymin, xmax, ymax = bounds

    # Générer les tailles de boîte sur une échelle logarithmique
    box_sizes = np.logspace(np.log10(min_box_size), np.log10(max_box_size), num_scales)

    box_counts = []

    for box_size in box_sizes:
        count = 0  # Nombre de boîtes occupées
        x = xmin
        while x < xmax:
            y = ymin
            while y < ymax:
                # Créez une boîte carrée dans la grille
                b = box(x, y, x + box_size, y + box_size)
                # Vérifiez si elle intersecte la géométrie
                if b.intersects(geometry):
                    count += 1
                y += box_size
            x += box_size
        box_counts.append(count)
        print(f"Taille boîte: {box_size:.4f}, Nb boîtes occupées: {count}")

    # Régression log-log (calcul de la pente)
    log_box_sizes = np.log(1 / np.array(box_sizes))
    log_box_counts = np.log(box_counts)
    slope, _ = np.polyfit(log_box_sizes, log_box_counts, 1)

    print(f"Dimension fractale estimée (2D) : {slope}")
    return slope


def _calculate_box_counting_3d(mesh, bounds, min_box_size, max_box_size, num_scales):
    """
    Calcul du comptage par boîte pour un objet 3D.

    Args:
        mesh (trimesh.Trimesh): Maillage 3D.
        bounds (tuple): Limites (xmin, ymin, zmin, xmax, ymax, zmax) de l'objet.
        min_box_size (float): Taille minimale des boîtes.
        max_box_size (float): Taille maximale des boîtes.
        num_scales (int): Nombre d'échelles pour le comptage.

    Returns:
        float: La dimension fractale estimée.
    """
    xmin, ymin, zmin, xmax, ymax, zmax = bounds

    # Générer les tailles de boîte sur une échelle logarithmique
    box_sizes = np.logspace(np.log10(min_box_size), np.log10(max_box_size), num_scales)

    box_counts = []

    for box_size in box_sizes:
        count = 0  # Nombre de boîtes occupées
        nx = int(np.ceil((xmax - xmin) / box_size))
        ny = int(np.ceil((ymax - ymin) / box_size))
        nz = int(np.ceil((zmax - zmin) / box_size))

        # Créer une grille 3D de boîtes
        for ix in range(nx):
            for iy in range(ny):
                for iz in range(nz):
                    # Coordonnées de la boîte
                    x = xmin + ix * box_size
                    y = ymin + iy * box_size
                    z = zmin + iz * box_size
                    # Créez une boîte cubique
                    cube = trimesh.primitives.Box(extents=(box_size, box_size, box_size)).apply_translation([x + box_size / 2, y + box_size / 2, z + box_size / 2])
                    # Vérifiez si cette boîte intersecte le maillage
                    if mesh.intersects_bbox(cube.bounds):
                        count += 1
        box_counts.append(count)
        print(f"Taille boîte: {box_size:.4f}, Nb boîtes occupées: {count}")

    # Régression log-log (calcul de la pente)
    log_box_sizes = np.log(1 / np.array(box_sizes))
    log_box_counts = np.log(box_counts)
    slope, _ = np.polyfit(log_box_sizes, log_box_counts, 1)

    print(f"Dimension fractale estimée (3D) : {slope}")
    return slope


# Exemple d'utilisation
if __name__ == "__main__":
    # Chemin du fichier
    input_file = input("Entrez le chemin du fichier (Shapefile pour 2D ou OBJ/STL pour 3D) : ")
    is_3d = input("L'objet est-il 3D ? (oui/non) : ").strip().lower() == "oui"

    # Paramètres
    min_box_size = float(input("Taille minimale des boîtes (ex: 0.01) : ") or 0.01)
    max_box_size = float(input("Taille maximale des boîtes (ex: 10) : ") or 10)
    num_scales = int(input("Nombre d'échelles (par défaut 10) : ") or 10)

    # Calculer la dimension fractale
    dimension = box_counting_dimension(input_file, is_3d, min_box_size, max_box_size, num_scales)
    print(f"La dimension fractale calculée est : {dimension}")
