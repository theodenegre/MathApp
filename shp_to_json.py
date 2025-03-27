import geopandas as gpd
import os
import shutil


def convert_shp_to_geojson(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".shp"):
                shp_path = os.path.join(root, file)
                geojson_path = os.path.join(root,
                                            file.replace(".shp", ".geojson"))

                try:
                    # Charger le fichier Shapefile
                    gdf = gpd.read_file(shp_path)

                    # Sauvegarder en GeoJSON
                    gdf.to_file(geojson_path, driver="GeoJSON")
                    print(f"Converti : {shp_path} -> {geojson_path}")

                    # Supprimer tous les fichiers liés au Shapefile
                    base_name = file.replace(".shp", "")
                    for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
                        file_to_remove = os.path.join(root, base_name + ext)
                        if os.path.exists(file_to_remove):
                            os.remove(file_to_remove)
                            print(f"Supprimé : {file_to_remove}")
                except Exception as e:
                    print(f"Erreur lors de la conversion de {shp_path} : {e}")


# Spécifiez le répertoire racine
repertoire_racine = "."  # Modifier avec le chemin voulu
convert_shp_to_geojson(repertoire_racine)
