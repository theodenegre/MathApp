import geopandas as gpd
import os

# converti tout les fichiers shp en geojson, le nom du fichier est le meme que le fichier shp
# tout les fichiers annexes sont ignorés, sauf sauf qui servent à format shp (shx, dbf, etc) qui sont alors suppimés
def shp_to_json():
    # liste des fichiers dans le dossier
    files = os.listdir()
    # pour chaque fichier
    for file in files:
        # si c'est un fichier shp
        if file.endswith(".shp"):
            # on ouvre le fichier
            gdf = gpd.read_file(file)
            # on converti le fichier en geojson
            gdf.to_file(file.replace(".shp", ".geojson"), driver='GeoJSON')
            # on supprime les fichiers annexes
            for ext in [".shx", ".dbf", ".prj", ".cpg"]:
                try:
                    os.remove(file.replace(".shp", ext))
                except:
                    pass