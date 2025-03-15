# crée un programme pour générer un point en shp

import os
import fiona
from shapely.geometry import Point, mapping

# Vérifier ou créer un dossier simpleSHP
output_folder = "simpleSHP"
os.makedirs(output_folder, exist_ok=True)
