import os
import json
from shapely.geometry import mapping, Polygon


def create_cube_shp(output_geojson):
    """
    Crée un fichier GeoJSON représentant un cube "rempli" en 3D avec des polygones 3D.
    Chaque face du cube est représentée comme un polygone avec des coordonnées Z.

    Args:
        output_geojson (str): Chemin où le fichier GeoJSON sera sauvé.
    """

    # Définition des 6 faces du cube avec des coordonnées 3D (X, Y, Z)
    cube_faces = [
        # Face avant
        Polygon([
            (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 0)
        ]),
        # Face arrière
        Polygon([
            (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1), (0, 0, 1)
        ]),
        # Face gauche
        Polygon([
            (0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)
        ]),
        # Face droite
        Polygon([
            (1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1), (1, 0, 0)
        ]),
        # Face du dessous
        Polygon([
            (0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1), (0, 0, 0)
        ]),
        # Face du dessus
        Polygon([
            (0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1), (0, 1, 0)
        ]),
    ]

    # Construire les entités GeoJSON
    features = []
    for i, face in enumerate(cube_faces, start=1):
        features.append({
            "type": "Feature",
            "geometry": mapping(face),
            "properties": {"id": i}
        })

    # Structure GeoJSON
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    # Écriture dans un fichier GeoJSON
    with open(output_geojson, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=4)

    print(f"Cube 3D rempli sauvegardé ! Fichier : {output_geojson}")


# Exemple d'utilisation
if __name__ == "__main__":
    # Nom du fichier de sortie
    output_file = "simpleGEO/cube_filled.geojson"

    # Appeler la fonction pour créer le cube
    create_cube_shp(output_geojson=output_file)
