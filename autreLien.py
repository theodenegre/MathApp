#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os

def download_file(url, output_path):
    """
    Télécharge un fichier depuis une URL et l'enregistre localement.
    Affiche la progression (si le header 'content-length' est présent)
    ou simplement une confirmation du téléchargement.
    """
    try:
        print(f"\nTéléchargement de {url} ...")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Vérifie que la requête s'est bien déroulée

        # Récupérer la taille totale (si disponible)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Ko
        wrote = 0

        # Si le fichier est volumineux et que content-length est donné, on affiche une progression.
        with open(output_path, 'wb') as file:
            if total_size > 0:
                for data in response.iter_content(block_size):
                    file.write(data)
                    wrote += len(data)
                    print(f"\rTéléchargé {wrote / 1024:.2f} Ko sur {total_size/1024:.2f} Ko", end="")
            else:  # Sinon, on télécharge sans progression
                file.write(response.content)

        print(f"\nFichier enregistré : {output_path}")
    except requests.exceptions.HTTPError as e:
        print(f"Erreur HTTP lors du téléchargement de {url} : {e}")
        print("La ressource demandée n'a pas été trouvée ou n'est pas accessible (par exemple, 404).")
    except Exception as e:
        print(f"Erreur lors du téléchargement de {url} : {e}")

def main():
    # Crée un dossier pour stocker les fichiers téléchargés
    output_dir = "donnees_vectors"
    os.makedirs(output_dir, exist_ok=True)

    ressources = {
        "Natural_Earth_Coastline": {
            # Téléchargement du fichier ZIP de côtes en 10m de Natural Earth Data
            "url": "http://www.naturalearthdata.com/download/10m/physical/ne_10m_coastline.zip",
            "filename": "ne_10m_coastline.zip"
        },
        "GSHHS": {
            # Téléchargement de la version shapefile de GSHHS
            "url": "https://www.soest.hawaii.edu/pwessel/gshhg/gshhg-shp-2.3.7.zip",
            "filename": "gshhg-shp-2.3.7.zip"
        },
        "OSM_Great_Britain": {
            # Téléchargement des données shapefile d'OpenStreetMap pour la Grande‑Bretagne via Geofabrik
            "url": "https://download.geofabrik.de/europe/great-britain-latest-free.shp.zip",
            "filename": "great_britain-latest-free.shp.zip"
        },
        "GADM_Download_Page": {
            # Téléchargement de la page HTML de GADM (une page listant les pays et liens)
            "url": "https://gadm.org/download_country.html",
            "filename": "gadm_download_country.html"
        },
        "MapsVG": {
            # Exemple avec une URL qui génère une erreur 404 (à adapter ou supprimer)
            "url": "https://mapsvg.com/maps/united-kingdom.json",
            "filename": "united-kingdom.json"
        },
        "Autre_Exemple": {
            # Exemple d'une autre ressource, ici vous pouvez ajouter n'importe quelle URL valide pour vos besoins.
            "url": "https://example.com/autre_resource.zip",
            "filename": "autre_resource.zip"
        }
    }

    print("Début du téléchargement des ressources...\n")
    for nom, info in ressources.items():
        print(f"Démarrage du téléchargement pour {nom}...")
        output_path = os.path.join(output_dir, info["filename"])
        download_file(info["url"], output_path)

    print("\nTéléchargement terminé.")

if __name__ == "__main__":
    main()
