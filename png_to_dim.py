#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Python pour estimer la dimension fractale d'une image (exemple : côte de l'Angleterre)
en utilisant la méthode du box-counting.
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


def boxcount(Z, box_size):
    """
    Compte le nombre de boîtes de taille box_size qui contiennent une partie non nulle (c'est-à-dire
    une partie de l'objet).

    Paramètres :
      Z : tableau 2D (image binaire)
      box_size : taille de la boîte

    Retourne :
      nombre_de_boites : Nombre de boîtes contenant une partie de l'objet.
    """
    # On découpe l'image en sous-tableaux de taille box_size x box_size
    S = np.add.reduceat(
            np.add.reduceat(Z, np.arange(0, Z.shape[0], box_size), axis=0),
            np.arange(0, Z.shape[1], box_size), axis=1)

    # Une boîte compte si elle n'est ni complètement vide (0) ni complètement pleine (box_size*box_size)
    return np.sum((S > 0) & (S < box_size * box_size))


def fractal_dimension(Z, threshold=128):
    """
    Calcule la dimension fractale d'une image 2D (tableau numpy) en utilisant la méthode du box-counting.

    Paramètres :
      Z : image 2D (tableau numpy, par exemple en niveaux de gris)
      threshold : seuil pour convertir l'image en binaire (0-255)

    Retourne :
      D : dimension fractale estimée
      sizes : liste des tailles de boîte utilisées
      counts: liste des comptes de boîtes correspondants
    """
    # Conversion de l'image en binaire (0,1)
    Z = np.asarray(Z)
    # On considère les pixels inférieurs au seuil comme faisant partie de l'objet (par exemple, la côte)
    Z = (Z < threshold).astype(np.uint8)

    # Détermine la taille minimale (la dimension la plus petite de l'image)
    p = min(Z.shape)
    # On utilise la plus grande puissance de 2 inférieure à p pour avoir des boîtes de taille exactement puissance de 2
    n = 2 ** np.floor(np.log2(p))
    n = int(n)

    # Prépare la liste des tailles de boîte (puissances de 2)
    sizes = 2 ** np.arange(int(np.log2(n)), 1, -1)
    counts = []

    for size in sizes:
        counts.append(boxcount(Z, size))

    # Calcul de la pente de la droite dans le diagramme log-log :
    # log(N(box)) = -D * log(box_size) + constant
    coeffs = np.polyfit(np.log(sizes), np.log(counts), 1)
    D = - coeffs[0]

    return D, sizes, counts


if __name__ == "__main__":
    # Chargement de l'image représentant la côte (par exemple "coastline.png")
    # Vous pouvez utiliser une image en niveaux de gris où la côte est représentée en noir sur fond blanc.
    filename = "coastline.png"
    try:
        image = Image.open(filename).convert(
            'L')  # conversion en niveaux de gris
    except Exception as e:
        print(f"Erreur lors de l'ouverture de l'image : {e}")
        exit()

    image_data = np.array(image)

    # Vous pouvez ajuster le seuil en fonction de votre image
    D, sizes, counts = fractal_dimension(image_data, threshold=128)
    print("Dimension fractale estimée : ", D)

    # Affichage du diagramme log-log
    plt.figure()
    plt.plot(np.log(sizes), np.log(counts), 'o-',
             label=f"Pente = {-np.polyfit(np.log(sizes), np.log(counts), 1)[0]:.3f}")
    plt.xlabel("log(taille de boîte)")
    plt.ylabel("log(nombre de boîtes)")
    plt.title("Diagramme Log-Log pour l'estimation de la dimension fractale")
    plt.legend()
    plt.grid(True)
    plt.show()