# MathApp – Calcul de dimension fractales de côtes de différents pays.

## Présentation Générale

Ce projet Python permet de générer, manipuler et exporter des objets mathématiques (ensembles fractales) au format GeoJSON, principalement pour la visualisation ou le calcul dimensionnel.

## Organisation des Dossiers et Fichiers

- **simple forms/**  
  Contient des scripts pour générer des figures mathématiques simples ou classiques :
  - `cantor.py`, `cantor2d.py`, `cantorsus.py` : Ensembles de Cantor et variantes.
  - `koch.py`, `koch2d.py` : Flocons et courbes de Koch.
  - `sierpinski.py`, `sierpinski_carpet.py` : Triangles et tapis de Sierpiński.
  - `menger.py`, `menger_bizarre.py` : Éponges de Menger (2D ou variantes).
  - `mandelbrot.py` : Ensemble de Mandelbrot.
  - `peano.py` : Courbe de Peano.
  - `filled_square_creator.py`, `unfilled_square.py`, `filled_circle.py`, `cube.py` : Création de formes géométriques simples (carrés, cercles, cubes).
  - `line_creator.py`, `long_line.py`, `rotated_line.py`, `point.py`, `harmony.py` : Création de lignes, points, suites particulières.

- **tools/**  
  Outils utilitaires pour la conversion ou le traitement de fichiers :
  - `polyline_to_geojson.py` : Convertit des fichiers de polylignes en GeoJSON. Ce qui a servi pour utiliser les cartes de la base de donnée Wolfram.

- **simpleGEO/**  
  Dossier de sortie où sont générés les fichiers GeoJSON représentant les fractales simples.

- **Fichiers d'analyse fractale :**
  - `run_fractalyse.py` : Script pour lancer automatiquement le calcul de la dimension fractale (méthode du box-counting) sur tous les fichiers de contours de pays présents dans `coastlines/contour`. Il utilise le logiciel Fractalyse (Java) et génère un classement des dimensions fractales dans `results/fractal_dimensions.csv`.
  - `run_fractalyse_adaptative.py` : Variante avancée qui adapte automatiquement la taille des boîtes de comptage en fonction de la taille du pays analysé. Les résultats sont enregistrés dans `results/fractal_dimensions_adaptative.csv`.

## Utilité des Fichiers

Chaque script Python génère une ou plusieurs figures mathématiques et exporte le résultat dans un fichier GeoJSON (ou Shapefile pour certains scripts).  
Les scripts sont indépendants : il suffit de lancer un script pour générer la figure correspondante dans le dossier `simpleGEO`.

## Guide d'Utilisation

### Prérequis

- Python 3.7+
- Installer les dépendances nécessaires :
```bash
pip install -r requirements.txt
```

### Générer une figure

1. **Exécuter un script**  
   Par exemple, pour générer un triangle de Sierpiński :
   ```
   python simple forms/sierpinski.py
   ```
   Le fichier `simpleGEO/sierpinski.geojson` sera créé.

2. **Modifier les paramètres**  
   Pour changer la taille, le nombre d'itérations ou d'autres paramètres, éditez les variables en début de script (ex : `iterations`, `initial_size`, etc.).

3. **Visualiser les résultats**  
   Les fichiers GeoJSON générés peuvent être ouverts avec QGIS, geojson ou d'autres outils compatibles.

### Combiner ou convertir des fichiers

- Utilisez `simple forms/unions.py` pour fusionner deux fichiers GeoJSON de type FeatureCollection.
- Utilisez `tools/polyline_to_geojson.py` pour convertir des polylignes en GeoJSON.

## Personnalisation

Chaque script peut être adapté pour générer d'autres variantes de figures, changer les couleurs, ajouter des propriétés, etc.

