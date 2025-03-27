import json
import os
import geopandas as gpd
import requests
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.ops import unary_union


def download_coastlines(country_code, path):
    response = None
    try:
        response = requests.get(f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{country_code}_0.json", timeout=10)
        response.raise_for_status()
        print(f"Téléchargement réussi pour {country_code}.")
    except requests.exceptions.RequestException as e:
        print(f"Le pays {country_code} n'a pas pu être téléchargé.")

    if response is None or response.status_code != 200:
        raise Exception("Toutes les tentatives de téléchargement ont échoué.")

    with open(path, "wb") as f:
        f.write(response.content)

    pays_contours = gpd.read_file(path)
    return pays_contours

def process_geojson(input_filepath, output_filepath, country_code):
    with open(input_filepath) as f:
        geojson_dict = json.load(f)

    # Convertir le MultiPolygon en Polygon
    feature = geojson_dict['features'][0]
    geometry = shape(feature['geometry'])

    # Fusionner les polygones pour obtenir le contour extérieur
    contour = unary_union(geometry)

    # Extraire uniquement les contours extérieurs
    if isinstance(contour, Polygon):
        exterior_contours = [contour.exterior]
    elif isinstance(contour, MultiPolygon):
        exterior_contours = [geom.exterior for geom in contour.geoms]

    contour_geojson = {
        "type": "FeatureCollection",
        "name": f"{country_code}_contour",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "GID_0": country_code
                },
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [list(contour.coords) for contour in exterior_contours]
                }
            }
        ]
    }

    with open(output_filepath, 'w') as f:
        json.dump(contour_geojson, f, indent=2)


# Télécharger les contours de tous les pays dans la base de données
import string

existing = os.listdir("coastlines/contour")
existing = [a.split("_")[0] for a in existing]
existing = [a for a in existing if len(a) == 3]
existing.sort()
start = existing[-1]
code_to_pass = ["CON"] # car bug bizarrement pour le code "CON", alors qu'il n'existe pas de pays avec ce code
country_codes = [a + b + c for a in string.ascii_uppercase for b in string.ascii_uppercase for c in string.ascii_uppercase if a + b + c not in code_to_pass and a + b + c > start]
for country_code in country_codes:
    full_path = f"coastlines/full/{country_code}.geojson"
    contour_path = f"coastlines/contour/{country_code}_contour.geojson"

    try:
        if not os.path.exists(full_path):
            download_coastlines(country_code, full_path)
        process_geojson(full_path, contour_path, country_code)
        print(f'Téléchargement réussi pour {country_code}.')
    except Exception as e:
        pass
