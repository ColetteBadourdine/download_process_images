from __future__ import division, print_function, unicode_literals
import sys, os, struct, glob
from glob import glob
import subprocess
import itertools
import re

from pprint import pprint

        
from osgeo import gdal
import osgeo.ogr as ogr
import osgeo.osr as osr

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

gdal.UseExceptions()


###CHEMIN DU REPERTOIRE DE TRAVAIL
os.chdir('your/path')
###CHEMIN DU DOSSIER DES IMAGES DE LA DATE A TRAITER
chemin = 'G:your/path'
liste_fichier =  glob(os.path.join(chemin, "*.tif"))
print(liste_fichier)
liste_warp = []
for img in liste_fichier :
    nom_img = os.path.splitext(os.path.basename(img))[0]
    print(nom_img)
    img_warp = os.path.join(chemin, "ech_%s.tif" % nom_img)
    gdal.Warp(img_warp, img, xRes=10, yRes=10)
    liste_warp.append(img_warp)
###UNE FOIS QUE TOUT A TOURNE BIEN VEILLER A SUPPRIMER LES IMAGES QUI NE SONT PAS
###SURECHANTILLONNEES (LES IMAGES SOURCES) POUR QU'ELLES NE SOIENT PAS PRISES EN COMPTE DANS LES TRAITEMENTS FUTURS
