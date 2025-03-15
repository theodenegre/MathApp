import os
import fiona
from shapely.geometry import mapping, Polygon


def create_cube_shp(output_shp):
    """
    Crée un Shapefile représentant un cube "rempli" en 3D avec des polygones 3D.
    Chaque face du cube est représentée comme un polygone avec des coordonnées Z.

    Args:
        output_shp (str): Chemin où le fichier Shapefile sera sauvé.
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

    # Schéma pour le Shapefile avec des polygones 3D
    schema = {
        'geometry': 'Polygon',  # Polygones (avec Z possible grâce au .shp)
        'properties': {'id': 'int'},  # Un champ d'identifiant (id entier)
    }

    # Système de coordonnées (arbitraire, ici c'est en mètres, sans CRS spécifique)
    crs = "EPSG:4326"

    # Écriture de chaque face dans un Shapefile
    with fiona.open(output_shp, 'w',
                    driver='ESRI Shapefile',
                    schema=schema,
                    crs=crs) as layer:
        print(f"Création d'un cube 3D rempli dans {output_shp}...")

        for i, face in enumerate(cube_faces,
                                 start=1):  # Face numérotée de 1 à 6
            # Ajouter la face actuelle au fichier
            layer.write({
                'geometry': mapping(face),
                # Convertir en format acceptable pour Fiona
                'properties': {'id': i},  # Identifiant unique pour chaque face
            })

    print(f"Cube 3D rempli sauvegardé ! Fichier : {output_shp}")


# Exemple d'utilisation
if __name__ == "__main__":
    # Nom du fichier de sortie
    output_file = "simpleSHP/cube_filled.shp"

    # Appeler la fonction pour créer le cube
    create_cube_shp(output_shp=output_file)
