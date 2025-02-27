import os
import geopandas as gpd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    pays = "BEL"
    # dir = f"gadm41_{pays}_shp"
    # filename = f"gadm41_{pays}_0.shp"
    dir = ""
    filename = "peano_curve.shp"
    final_filename = os.path.join(dir, filename)
    try:
        gdf = gpd.read_file(final_filename)
    except Exception as e:
        print(f"Erreur lors du chargement du fichier shapefile : {e}")
        exit()

    geometry = gdf.union_all()
    coastline = geometry.boundary
    gdf_coastline = gpd.GeoDataFrame(geometry=[coastline], crs=gdf.crs)

    output_filename = f"coastlines/{filename}"
    output_dir = "coastlines"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Enrigiste le fichier shapefile (shp) de la côte et aucun autre fichier (shx, dbf, ...)
        gdf_coastline.to_file(output_filename, driver='ESRI Shapefile')

        print(f"Fichier shapefile de la côte enregistré : {output_filename}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du fichier shapefile de la côte : {e}")
        exit()

    gdf_coastline.plot()
    plt.title("Côte du pays")
    plt.axis('off')
    plt.show()