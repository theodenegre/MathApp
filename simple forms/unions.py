import os
import fiona
from shapely.geometry import shape, mapping, MultiPolygon, Polygon, MultiLineString, LineString, GeometryCollection

def union_shapefile(inputs_shp, output_shp):
    """Combine les géométries de plusieurs fichiers Shapefile en une seule
    et sauvegarde le résultat dans un nouveau Shapefile.

    Args:
        inputs_shp (list): Liste des chemins vers les fichiers Shapefile d'entrée.
        output_shp (str): Chemin vers le fichier Shapefile de sortie.
    """
    # Vérifier si les fichiers sources existent
    for input_shp in inputs_shp:
        if not os.path.exists(input_shp):
            print(f"Le fichier {input_shp} n'existe pas.")
            return

    # Initialiser les listes de géométries
    polygon_geometries = []
    line_geometries = []

    # Lire les Shapefiles sources
    for input_shp in inputs_shp:
        with fiona.open(input_shp, 'r') as source:
            for feature in source:
                geom = shape(feature['geometry'])

                # Vérifier si c'est une GeometryCollection
                if isinstance(geom, GeometryCollection):
                    for sub_geom in geom.geoms:
                        if isinstance(sub_geom, (Polygon, MultiPolygon)):
                            polygon_geometries.append(sub_geom)
                        elif isinstance(sub_geom, (LineString, MultiLineString)):
                            line_geometries.append(sub_geom)
                elif isinstance(geom, (Polygon, MultiPolygon)):
                    polygon_geometries.append(geom)
                elif isinstance(geom, (LineString, MultiLineString)):
                    line_geometries.append(geom)

    # Gérer l'union des Polygones
    if polygon_geometries:
        union_polygon = polygon_geometries[0]
        for geom in polygon_geometries[1:]:
            union_polygon = union_polygon.union(geom)

        # Vérifier que l'union produit un MultiPolygon
        if isinstance(union_polygon, Polygon):
            union_polygon = MultiPolygon([union_polygon])

        # Écrire les polygones résultants dans un fichier
        with fiona.open(output_shp, 'w',
                        driver='ESRI Shapefile',
                        schema={'geometry': 'MultiPolygon', 'properties': {'id': 'int'}},
                        crs='EPSG:4326') as output:
            print(f"Écriture des polygones fusionnés dans {output_shp}...")
            output.write({'geometry': mapping(union_polygon), 'properties': {'id': 1}})

        print(f"Fichier de polygones sauvegardé dans {output_shp}.")

    # Gérer les lignes si elles existent
    if line_geometries:
        output_line_shp = output_shp.replace(".shp", "_lines.shp")

        with fiona.open(output_line_shp, 'w',
                        driver='ESRI Shapefile',
                        schema={'geometry': 'MultiLineString', 'properties': {'id': 'int'}},
                        crs='EPSG:4326') as output:
            print(f"Écriture des lignes dans {output_line_shp}...")
            for i, geom in enumerate(line_geometries, start=1):
                output.write({'geometry': mapping(geom), 'properties': {'id': i}})

        print(f"Fichier de lignes sauvegardé dans {output_line_shp}.")


if __name__ == "__main__":
    # Demander les chemins des fichiers Shapefile d'entrée
    input_files = input("Entrez les chemins des fichiers Shapefile d'entrée (séparés par des espaces) : ")
    input_files = input_files.split()

    # Définir un fichier de sortie basé sur les fichiers d'entrée
    output_file = "simpleSHP/union.shp"

    # Appliquer l'union des géométries
    union_shapefile(input_files, output_file)
