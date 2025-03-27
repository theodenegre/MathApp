import json
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import unary_union
import numpy as np


def is_closed(line):
    """Vérifie si une ligne est fermée (début et fin identiques)."""
    return np.allclose(line.coords[0], line.coords[-1])


def find_closest_line(target, lines):
    """Trouve la ligne la plus proche de l'extrémité d'une autre ligne."""
    target_end = target.coords[-1]  # Dernier point de la ligne cible
    min_distance = float('inf')
    closest_line = None
    closest_index = None

    for i, line in enumerate(lines):
        start_distance = np.linalg.norm(np.array(line.coords[0]) - np.array(target_end))
        end_distance = np.linalg.norm(np.array(line.coords[-1]) - np.array(target_end))

        if start_distance < min_distance:
            min_distance = start_distance
            closest_line = line
            closest_index = i

        if end_distance < min_distance:
            min_distance = end_distance
            closest_line = LineString(list(reversed(line.coords)))  # Inverser la ligne
            closest_index = i

    return closest_line, closest_index


def close_contour(line, remaining_lines):
    """Ferme un contour ouvert en fusionnant récursivement les lignes les plus proches."""
    while not is_closed(line) and remaining_lines:
        closest, index = find_closest_line(line, remaining_lines)
        if closest is None:
            break  # Impossible de fermer

        # Fusionner la ligne trouvée
        line = LineString(list(line.coords) + list(closest.coords))

        # Retirer la ligne utilisée
        remaining_lines.pop(index)

    return line


def process_geojson(input_filepath, output_filepath, country_code):
    with open(input_filepath) as f:
        geojson_dict = json.load(f)

    feature = geojson_dict['features'][0]
    geometry = shape(feature['geometry'])

    # Fusionner les polygones pour obtenir le contour extérieur
    contour = unary_union(geometry)

    # Extraire uniquement les contours extérieurs
    if isinstance(contour, Polygon):
        exterior_contours = [contour.exterior]
    elif isinstance(contour, MultiPolygon):
        exterior_contours = [geom.exterior for geom in contour.geoms]
    elif isinstance(contour, MultiLineString):
        exterior_contours = list(contour.geoms)
    else:
        raise ValueError("La géométrie fournie n'est ni un Polygon ni un MultiPolygon.")

    # Sélectionner la plus longue ligne comme point de départ
    longest_contour = sorted(exterior_contours, key=lambda c: c.length, reverse=True)[0]

    # Vérifier et fermer le contour si nécessaire
    remaining_lines = [line for line in exterior_contours if line != longest_contour]
    closed_contour = close_contour(longest_contour, remaining_lines)

    # Conversion en GeoJSON
    contour_geojson = {
        "type": "FeatureCollection",
        "name": f"{country_code}_contour",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": [
            {
                "type": "Feature",
                "properties": {"GID_0": country_code},
                "geometry": {
                    "type": "LineString",
                    "coordinates": list(closed_contour.coords)
                }
            }
        ]
    }

    # Sauvegarder dans un fichier GeoJSON
    with open(output_filepath, 'w') as f:
        json.dump(contour_geojson, f, indent=2)


# Exemple d'utilisation
if __name__ == "__main__":
    country_code = "GBR"
    input_filepath = f'coastlines/contour/{country_code}.geojson'
    output_filepath = f'coastlines/specials/{country_code}_contour.geojson'

    process_geojson(input_filepath, output_filepath, country_code)
