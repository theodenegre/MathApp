import json

def lire_fichier_json(chemin):
    with open(chemin, 'r', encoding='utf-8') as f:
        return json.load(f)

def sauvegarder_fichier_json(data, chemin):
    with open(chemin, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def combiner_fichiers_json(fichier1, fichier2):
    # Lire les fichiers json
    data1 = lire_fichier_json(fichier1)
    data2 = lire_fichier_json(fichier2)

    # Vérifier que les deux fichiers sont des FeatureCollection
    if data1['type'] != 'FeatureCollection' or data2['type'] != 'FeatureCollection':
        raise ValueError("Les deux fichiers doivent être des FeatureCollection.")

    # Combiner les entités des deux fichiers
    features_combinees = data1['features'] + data2['features']

    # Créer une nouvelle FeatureCollection avec les entités combinées
    feature_collection_combinee = {
        "type": "FeatureCollection",
        "features": features_combinees
    }

    return feature_collection_combinee

# Chemins des fichiers geojson en entrée
chemin_fichier1 = 'simpleGEO/sierpinski.geojson'
chemin_fichier2 = 'simpleGEO/sierpinski_carpet.geojson'

# Combiner les fichiers json
fichier_combine = combiner_fichiers_json(chemin_fichier1, chemin_fichier2)

# Chemin du fichier json en sortie
chemin_sortie_fichier_combine = 'simpleGEO/sierpinski_combined.geojson'

# Sauvegarder le fichier geojson combiné
sauvegarder_fichier_json(fichier_combine, chemin_sortie_fichier_combine)

print(f"Fichier combiné sauvegardé à {chemin_sortie_fichier_combine}")
