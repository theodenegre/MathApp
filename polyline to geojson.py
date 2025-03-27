import matplotlib.pyplot as plt
import re
import numpy as np
from shapely.geometry import LineString, mapping
import json
import os

# Convert all files in the 'coastlines/polylines' folder
polyline_folder = 'coastlines/polylines'
output_folder = 'coastlines/specials'

for filename in os.listdir(polyline_folder):
    if filename.endswith('.txt'):
        with open(os.path.join(polyline_folder, filename), 'r') as file:
            polyline_str = file.read()
        
        # Extract points from the polyline string
        points_str = re.search(r'points="([^"]+)"', polyline_str).group(1)
        points = [tuple(map(float, point.split(','))) for point in points_str.split()]

        # Create a list of x and y coordinates
        x, y = zip(*points)
        y = -np.array(y)

        points = zip(x, y)
        line = LineString(points)

        # Create a FeatureCollection with a MultiLineString
        feature_collection = {
            "type": "FeatureCollection",
            "name": "Polyline",
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
                        "stroke": "#ff0000",
                        "stroke-width": 2
                    },
                    "geometry": {
                        "type": "MultiLineString",
                        "coordinates": [list(line.coords)]
                    }
                }
            ]
        }

        output_filename = f'poly_{filename.replace(".txt", ".geojson")}'
        with open(os.path.join(output_folder, output_filename), 'w') as f:
            json.dump(feature_collection, f)

        print(f"Fichier enregistré dans '{output_folder}/{output_filename}'")
