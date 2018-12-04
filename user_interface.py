
# coding: utf-8
"""
@author: colette.badourdine
"""

from __future__ import division, print_function, unicode_literals
import sys, os, struct, glob
from glob import glob
import subprocess
import itertools
import re

from pprint import pprint

from collections import OrderedDict
import pytest
        
from osgeo import gdal
import fiona
from fiona.crs import from_epsg
import rasterio
from rasterio.mask import mask
import rasterstats
import osgeo.ogr as ogr
import osgeo.osr as osr

import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import cv2

import xlsxwriter
import xlrd

import pandas as pd
import pyproj

from shapely.geometry import mapping, Polygon, LinearRing
from shapely.geometry import CAP_STYLE, JOIN_STYLE

import PyQt4
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import cartopy.crs as ccrs
from skimage import exposure

gdal.UseExceptions()
np.seterr(divide='ignore', invalid='ignore')
# Début de l'interface graphique  
class Principal(QMainWindow):

    def __init__(self, parent=None):
        """Initialise la fenêtre"""
        super(Principal, self).__init__(parent)
        
        self.setWindowTitle("Logiciel de traitement d'image satellite et de calcul d'indices")
        self.setGeometry(10, 50, 700, 600)
        self.setCentralWidget(QtGui.QFrame())
        #######################################################################
        ## Création des différents onglets ####################################
                         
        # Début onglet image ######################################################
        self.tabWidget = QtGui.QTabWidget(self.centralWidget())
        self.tabWidget.setGeometry(QtCore.QRect(10, 50, 631, 491))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("Image")
        self.input = QtGui.QPushButton(self.tab)
        self.input.setGeometry(QtCore.QRect(30, 100, 71, 23))
        self.input.setObjectName("input")
        self.satellite = QtGui.QLabel(self.tab)
        self.satellite.setGeometry(QtCore.QRect(30, 330, 111, 20))                            
        self.satellite.setObjectName("satellite")
        self.sentinel = QtGui.QCheckBox(self.tab)
        self.sentinel.setGeometry(QtCore.QRect(150, 330, 70, 17))
        self.sentinel.setObjectName("sentinel")
        self.landsat = QtGui.QCheckBox(self.tab)
        self.landsat.setGeometry(QtCore.QRect(260, 330, 70, 17))
        self.landsat.setObjectName("landsat")                                                                                 
        self.dossier_image = QtGui.QLineEdit(self.tab)
        self.dossier_image.setGeometry(QtCore.QRect(120, 100, 251, 20))
        self.dossier_image.setObjectName("dossier_image")
        self.liste_fichier = QtGui.QListWidget(self.tab)
        self.liste_fichier.setGeometry(QtCore.QRect(140, 140, 211, 141))
        self.liste_fichier.setObjectName("liste_fichier")
        self.listage = QtGui.QPushButton(self.tab)
        self.listage.setGeometry(QtCore.QRect(30, 200, 101, 23))
        self.listage.setObjectName("listage")
        self.instruct_1 = QtGui.QTextEdit(self.tab)
        self.instruct_1.setGeometry(QtCore.QRect(380, 70, 221, 81))
        self.instruct_1.setObjectName("instruc_1")
        self.tabWidget.addTab(self.tab, "")

        #Debut onglet parcelle ####################################################
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("Parcelle")
        #coordonnees parcelle ####################################
        self.shp = QtGui.QPushButton(self.tab_2)
        self.shp.setGeometry(QtCore.QRect(260, 130, 121, 31))
        self.shp.setObjectName("shp")
        self.cd_coord = QtGui.QLineEdit(self.tab_2)
        self.cd_coord.setGeometry(QtCore.QRect(110, 30, 221, 20))
        self.input_coord = QtGui.QPushButton(self.tab_2)
        self.input_coord.setGeometry(QtCore.QRect(10, 30, 91, 23))
        self.input_coord.setObjectName("input_coord")
        self.instruct_3 = QtGui.QTextEdit(self.tab_2)
        self.instruct_3.setGeometry(QtCore.QRect(340, 10, 201, 71))
        self.instruct_3.setObjectName("instruct_3")
        self.decoup = QtGui.QPushButton(self.tab_2)
        self.decoup.setGeometry(QtCore.QRect(260, 270, 321, 31))
        self.decoup.setObjectName("decoup")
        self.liste_image_decoup = QtGui.QListWidget(self.tab_2)
        self.liste_image_decoup.setGeometry(QtCore.QRect(20, 100, 221, 261))
        self.liste_image_decoup.setObjectName("liste_image_decoup")
        self.input_sortie = QtGui.QPushButton(self.tab_2)
        self.input_sortie.setGeometry(QtCore.QRect(260, 180, 91, 23))
        self.input_sortie.setObjectName('input_sortie')
        self.cd_sortie = QtGui.QLineEdit(self.tab_2)
        self.cd_sortie.setGeometry(QtCore.QRect(360, 180, 221, 20))
        self.cd_sortie.setObjectName('cd_sortie')
        self.instruct_5 = QtGui.QTextEdit(self.tab_2)
        self.instruct_5.setGeometry(QtCore.QRect(360, 210, 221, 51))
        self.instruct_5.setObjectName('instruct_5')
        self.tabWidget.addTab(self.tab_2, "")
       
        #Debut onglet indices #####################################################                 
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName("Indices")
        #tableau et bouton ok
        self.tableauindice = QtGui.QListWidget(self.tab_4)
        self.tableauindice.setGeometry(QtCore.QRect(10, 120, 581, 301))
        self.tableauindice.setObjectName("tableauindice")
        self.calc_indice = QtGui.QPushButton(self.tab_4)
        self.calc_indice.setGeometry(QtCore.QRect(370, 10, 121, 31))
        self.calc_indice.setObjectName("calc_indice")
        self.calc_indice_2 = QtGui.QPushButton(self.tab_4)
        self.calc_indice_2.setGeometry(QtCore.QRect(370, 70, 121, 31))
        self.calc_indice_2.setObjectName("calc_indic_2")
        self.liste_fichier_2 = QtGui.QListWidget(self.tab_4)
        self.liste_fichier_2.setGeometry(QtCore.QRect(200, 10, 151, 91))
        self.liste_fichier_2.setObjectName("liste_fichier_2")
        self.selection = QtGui.QLabel(self.tab_4)
        self.selection.setGeometry(QtCore.QRect(50, 40, 141, 20))
        self.selection.setObjectName("selection")
        self.tabWidget.addTab(self.tab_4, "")

        #Debut onglet export #####################################################                 
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName("Export")
        self.dossier_output = QtGui.QLineEdit(self.tab_5)
        self.dossier_output.setGeometry(QtCore.QRect(120, 100, 241, 20))
        self.dossier_output.setObjectName("dossier_output")
        self.output = QtGui.QPushButton(self.tab_5)
        self.output.setGeometry(QtCore.QRect(40, 100, 71, 23))
        self.output.setObjectName("output")
        self.instruct_2 = QtGui.QTextEdit(self.tab_5)
        self.instruct_2.setGeometry(QtCore.QRect(370, 80, 111, 51))
        self.instruct_2.setObjectName("instruct_2")
        self.stat = QtGui.QCheckBox(self.tab_5)
        self.stat.setGeometry(QtCore.QRect(280, 160, 81, 17))
        self.stat.setObjectName("moy")
        self.pix = QtGui.QCheckBox(self.tab_5)
        self.pix.setGeometry(QtCore.QRect(280, 220, 91, 17))
        self.pix.setObjectName("pix")
        self.text = QtGui.QTextBrowser(self.tab_5)
        self.text.setGeometry(QtCore.QRect(40, 150, 221, 71))
        self.text.setObjectName("text")
        self.export_2 = QtGui.QPushButton(self.tab_5)
        self.export_2.setGeometry(QtCore.QRect(400, 170, 81, 31))
        self.export_2.setObjectName("export_2")
        self.tabWidget.addTab(self.tab_5, "")

        #Debut onglet merge ##################################################
        self.tab_6 = QtGui.QWidget()
        self.tab_6.setObjectName("Merge")
        self.text_bandes = QtGui.QTextBrowser(self.tab_6)
        self.text_bandes.setGeometry(QtCore.QRect(130, 70, 351, 51))
        self.text_bandes.setObjectName("text_bandes")
        self.output_rouge = QtGui.QPushButton(self.tab_6)
        self.output_rouge.setGeometry(QtCore.QRect(130, 170, 71, 23))
        self.output_rouge.setObjectName("output_rouge")
        self.dossier_output_rouge = QtGui.QLineEdit(self.tab_6)
        self.dossier_output_rouge.setGeometry(QtCore.QRect(210, 170, 271, 20))
        self.dossier_output_rouge.setObjectName("dossier_output_rouge")
        self.rouge = QtGui.QLabel(self.tab_6)
        self.rouge.setGeometry(QtCore.QRect(50, 170, 61, 20))
        self.rouge.setObjectName("rouge")

        self.vert = QtGui.QLabel(self.tab_6)
        self.vert.setGeometry(QtCore.QRect(50, 200, 61, 20))
        self.vert.setObjectName("vert")
        self.output_vert = QtGui.QPushButton(self.tab_6)
        self.output_vert.setGeometry(QtCore.QRect(130, 200, 71, 23))
        self.output_vert.setObjectName("output_vert")
        self.dossier_output_vert = QtGui.QLineEdit(self.tab_6)
        self.dossier_output_vert.setGeometry(QtCore.QRect(210, 200, 271, 20))

        self.bleue = QtGui.QLabel(self.tab_6)
        self.bleue.setGeometry(QtCore.QRect(50, 230, 61, 20))
        self.bleue.setObjectName("bleue")
        self.output_bleue = QtGui.QPushButton(self.tab_6)
        self.output_bleue.setGeometry(QtCore.QRect(130, 230, 71, 23))
        self.output_bleue.setObjectName("output_bleue")
        self.dossier_output_bleue = QtGui.QLineEdit(self.tab_6)
        self.dossier_output_bleue.setGeometry(QtCore.QRect(210, 230, 271, 20))
        self.dossier_output_bleue.setObjectName("dossier_output_bleue")

        self.dossier = QtGui.QLabel(self.tab_6)
        self.dossier.setGeometry(QtCore.QRect(50, 130, 61, 20))
        self.dossier.setObjectName("dossier")
        self.dossier_output_2 = QtGui.QLineEdit(self.tab_6)
        self.dossier_output_2.setGeometry(QtCore.QRect(210, 130, 271, 20))
        self.dossier_output_2.setObjectName("dossier_output_2")
        self.browse_dossier = QtGui.QPushButton(self.tab_6)
        self.browse_dossier.setGeometry(QtCore.QRect(130, 130, 71, 23))
        self.browse_dossier.setObjectName("browse_dossier")

        self.merge = QtGui.QPushButton(self.tab_6)
        self.merge.setGeometry(QtCore.QRect(410, 270, 71, 23))
        self.merge.setObjectName("merge")
        self.tabWidget.addTab(self.tab_6, "")
        
        #Debut onglet visualisation ##########################################
        self.tab_7 = QtGui.QWidget()
        self.tab_7.setObjectName("Visualisation")
        self.selection_palette = QtGui.QLabel(self.tab_7)
        self.selection_palette.setGeometry(QtCore.QRect(30, 270, 131, 20))
        self.selection_palette.setObjectName("selection_palette")
        self.selection_image = QtGui.QLabel(self.tab_7)
        self.selection_image.setGeometry(QtCore.QRect(30, 150, 131, 20))
        self.selection_image.setObjectName("selection_image")
        self.image_indice = QtGui.QLineEdit(self.tab_7)
        self.image_indice.setGeometry(QtCore.QRect(170, 50, 261, 20))
        self.image_indice.setObjectName("image_indice")
        self.image_input = QtGui.QPushButton(self.tab_7)
        self.image_input.setGeometry(QtCore.QRect(40, 50, 111, 23))
        self.image_input.setObjectName('image_input')
        self.image_merge = QtGui.QLineEdit(self.tab_7)
        self.image_merge.setGeometry(QtCore.QRect(170, 10, 261, 20))
        self.image_merge.setObjectName("image_merge")
        self.image_merge_input = QtGui.QPushButton(self.tab_7)
        self.image_merge_input.setGeometry(QtCore.QRect(40, 10, 111, 23))
        self.image_merge_input.setObjectName('image_merge-input')
        self.instruct_4 = QtGui.QTextEdit(self.tab_7)
        self.instruct_4.setGeometry(QtCore.QRect(450, 10, 111, 51))
        self.instruct_4.setObjectName("instruct_4")
        self.liste_image = QtGui.QListWidget(self.tab_7)
        self.liste_image.setGeometry(QtCore.QRect(170, 90, 261, 151))
        self.liste_image.setObjectName("liste_image")
        self.comboBox_palette = QtGui.QComboBox(self.tab_7)
        self.comboBox_palette.setGeometry(QtCore.QRect(170, 270, 261, 22))
        self.comboBox_palette.setObjectName("comboBox_palette")
        self.comboBox_palette.addItem("Normal")
        self.comboBox_palette.addItem("autumn")
        self.comboBox_palette.addItem("bone")
        self.comboBox_palette.addItem("jet")
        self.comboBox_palette.addItem("winter")
        self.comboBox_palette.addItem("gist_rainbow")
        self.comboBox_palette.addItem("ocean")
        self.comboBox_palette.addItem("summer")
        self.comboBox_palette.addItem("spring")
        self.comboBox_palette.addItem("cool")
        self.comboBox_palette.addItem("hsv")
        self.comboBox_palette.addItem("Greens")
        self.comboBox_palette.addItem("hot")
        self.comboBox_palette.addItem("PiYG")
        self.comboBox_palette.addItem("seismic")
        
        self.ok = QtGui.QPushButton(self.tab_7)
        self.ok.setGeometry(QtCore.QRect(450, 270, 61, 21))
        self.ok.setObjectName("ok")
        self.tabWidget.addTab(self.tab_7, "")
        
        
        ###nom des objets
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab),  "Image")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2),  "Parcelle")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4),  "Indices")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5),  "Export des données")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), "Merge")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7),  "Visualisation")
        self.listage.setText("Listage dossiers")
        self.sentinel.setText("Sentinel")
        self.landsat.setText("Landsat")
        self.input.setText("Browse")
        self.satellite.setText("Type de satellite")
        self.instruct_1.setText("<html><head/><body><p><span style=\" font-size:9pt; font-weight:400;\">Entrez le dossier contenant les images à traiter. ATTENTION : LES DIFFERENTES IMAGES DOIVENT ETRE RANGEES DANS UN DOSSIER NOMME AU FORMAT AAA_MM_DD.</span></p></body></html>")
        self.input_coord.setText("Coordonnées")
        self.shp.setText("Créer le shapefile")
        self.input_sortie.setText("Dossier sortie")
        self.decoup.setText("Découper images et générer un fichier de valeurs pixels")
        self.input_coord.setText("Coordonnées")
        self.instruct_3.setText("<html><head/><body><p><span style=\" font-size:9pt; font-weight:400;\">Entrez le fichier excel contenant les parcelles, les modalités, les coordonnées. Remplir le fichier excel donné en exemple.</span></p></body></html>")    
        self.instruct_5.setText("<html><head/><body><p><span style=\" font-size:9pt; font-weight:400;\">Entrez le dossier dans lequel le fichier excel de valeurs de pixels par bandes et par parcelle sera rangé.</span></p></body></html>")
        self.calc_indice.setText("Calculer les indices")
        self.calc_indice_2.setText("Calculer tout")
        self.selection.setText("Sélection : ")
        self.text.setText("<html><head/><body><p><span style=\" font-size:9pt; font-weight:400;\">Sélectionner les informations que vous voulez exporter : moyenne, médiane et écart-type par parcelle et par indice ou valeurs des pixels par parcelle et par indice.</span></p></body></html>")
        self.stat.setText("Statistiques")
        self.pix.setText("Valeur pixel")
        self.export_2.setText("Exporter")
        self.dossier.setText("Dossier : ")
        self.browse_dossier.setText("Browse")
        self.rouge.setText("Rouge : ")
        self.vert.setText("Vert : ")
        self.bleue.setText("Bleue : ")
        self.output_rouge.setText("Browse")
        self.output_vert.setText("Browse")
        self.output_bleue.setText("Browse")
        self.merge.setText("Merge")
        self.text_bandes.setText("<html><head/><body><p><span style=\" font-size:9pt; font-weight:400;\">Rentrer les bandes rouge (b4 pour sentinel 2, b3 pour landsat), verte (b3 pour sentinel 2, b2 pour landsat) et bleue (b2 pour sentinel 2, b1 pour landsat).</span></p></body></html>")
        self.output.setText("Browse")
        self.instruct_2.setText("<html><head/><body><p><span style=\" font-size:9pt; font-weight:400;\">Entrez le dossier de sauvegarde des résultats. ATTENTION IL DOIT ETRE DIFFERENT DU DOSSIER INPUT.</span></p></body></html>")
        self.selection_palette.setText("Sélectionnez une palette: ")
        self.selection_image.setText("Sélectionnez une image: ")
        self.ok.setText("OK")
        self.image_input.setText("Image")
        self.image_merge_input.setText("Image merge")
        self.instruct_4.setText("<html><head/><body><p><span style=\" font-size:9pt; font-weight:400;\">Entrez le dossier contenant les images à visualiser.</span></p></body></html>")
        
        
        ###Definitions des actions utilisateur####
        self.input.clicked.connect(self.fenetre_ouverture_fichier_input)
        self.listage.clicked.connect(self.listage_des_fichiers_disponibles)
        self.input_coord.clicked.connect(self.fenetre_ouverture_excel_coord)
        self.shp.clicked.connect(self.creer_shp)
        self.decoup.clicked.connect(self.decoup_image_mask)
        self.input_sortie.clicked.connect(self.fenetre_ouverture_dossier_output)
        self.calc_indice.clicked.connect(self.calcul_indice)
        self.calc_indice.clicked.connect(self.reechantillonnage)
        self.calc_indice_2.clicked.connect(self.calcul_tout)
        self.calc_indice_2.clicked.connect(self.reechantillonnage)
        self.export_2.clicked.connect(self.stat_zonale)
        self.output.clicked.connect(self.fenetre_ouverture_fichier_output)
        self.output_rouge.clicked.connect(self.fenetre_ouverture_bande_rouge)
        self.output_vert.clicked.connect(self.fenetre_ouverture_bande_vert)
        self.output_bleue.clicked.connect(self.fenetre_ouverture_bande_bleue)
        self.merge.clicked.connect(self.merge_image)
        self.browse_dossier.clicked.connect(self.fenetre_ouverture_dossier_merge)
        self.image_input.clicked.connect(self.fenetre_ouverture_fichier_image)
        self.image_input.clicked.connect(self.listage_des_images)
        self.image_merge_input.clicked.connect(self.ouverture_fichier_image_merge)
        self.ok.clicked.connect(self.visualisation)
        
        ### sélectionner un dossier ##############
    def fenetre_ouverture_fichier_input(self):
        dossier_input = QFileDialog.getExistingDirectory(self, "Ouvrir un fichier", "\\Users\colette.badourdine\Documents")
        if dossier_input:
            QMessageBox.information(self, "Dossier", self.trUtf8("Vous avez sélectionné :\n") + dossier_input)                          
        self.dossier_image.setText(dossier_input)

    def fenetre_ouverture_excel_coord(self):
        dossier_coord = QFileDialog.getOpenFileName(self, "Ouvrir un fichier excel de coordonnées", "\\Users\colette.badourdine\Documents", "Excel (*.xls *.xlsx)")
        self.cd_coord.setText(dossier_coord)

    def fenetre_ouverture_dossier_output(self):
        dossier_output = QFileDialog.getExistingDirectory(self, "Ouvrir un fichier", "\\Users\colette.badourdine\Documents")
        self.cd_sortie.setText(dossier_output)
        
    def fenetre_ouverture_fichier_output(self):
        dossier_output = QFileDialog.getExistingDirectory(self, "Ouvrir un fichier", "\\Users\colette.badourdine\Documents")           
        self.dossier_output.setText(dossier_output)

    def fenetre_ouverture_fichier_image(self):
        dossier_image = QFileDialog.getExistingDirectory(self, "Ouvrir un fichier", "\\Users\colette.badourdine\Documents")
        self.image_indice.setText(dossier_image)

    def ouverture_fichier_image_merge(self):
        dossier_image = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", "\\Users\colette.badourdine\Documents", "Image (*.tif)")
        self.image_merge.setText(dossier_image)
        
    def fenetre_ouverture_bande_rouge(self):
        fichier_rouge = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", str(self.dossier_output_2.text()+ "\\GRANULE\IMG_DATA"), "Image (*.tif)")
        self.dossier_output_rouge.setText(fichier_rouge)

    def fenetre_ouverture_bande_vert(self):
        fichier_vert = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", str(self.dossier_output_2.text()+ "\\GRANULE\IMG_DATA"), "Image (*.tif)")
        self.dossier_output_vert.setText(fichier_vert)

    def fenetre_ouverture_bande_bleue(self):
        fichier_bleue = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", str(self.dossier_output_2.text()+ "\\GRANULE\IMG_DATA"), "Image (*.tif)")
        self.dossier_output_bleue.setText(fichier_bleue)
        
    def fenetre_ouverture_dossier_merge(self):
        fichier_merge = QFileDialog.getExistingDirectory(self, "Ouvrir un fichier", "\\Users\colette.badourdine\Documents")
        self.dossier_output_2.setText(fichier_merge)
        
        ### liste fichier dispo ##############
    def listage_des_fichiers_disponibles(self):
        dossier = self.dossier_image.text()
        os.chdir(str(dossier))
        self.liste_fichier.clear()
        self.liste_fichier_2.clear()
        for doss in os.listdir('.'):
            self.liste_fichier.addItem(doss)
            self.liste_fichier_2.addItem(doss)
            
    def listage_des_images(self):
        dossier_image = self.image_indice.text()
        os.chdir(str(dossier_image))
        self.liste_image.clear()
        listimage = glob(os.path.join(str(dossier_image), "*.tif"))
        for image in listimage:
            nom_image = os.path.splitext(os.path.basename(image))[0]
            self.liste_image.addItem(nom_image)
            
        ### Utiliser le fichier excel pour recuperer les coordonnees ##################
    def creer_shp(self):
        if self.sentinel.checkState()>0:
            dossier = str(self.dossier_image.text())
            os.chdir(str(dossier))
            for j in os.listdir('.'):
                print("j = " , j)
                rep_s2_data = str(self.dossier_image.text()) +'\\'+ str(j) + '\GRANULE\IMG_DATA'
                print(rep_s2_data)
                rep_s2_pretraitement = str(self.dossier_image.text()) +'\\'+ str(j)  + '\GRANULE\Pretraitement'
                if not os.path.isdir(rep_s2_pretraitement):
                    os.mkdir(rep_s2_pretraitement)
                rep_s2_indice = str(self.dossier_image.text()) +'\\'+ str(j) +'\GRANULE\Indices'
                if not os.path.isdir(rep_s2_indice):
                    os.mkdir(rep_s2_indice)
                rep_s2_indice_1m = rep_s2_indice + '\\indice_1m'
                if not os.path.isdir(rep_s2_indice_1m):
                    os.mkdir(rep_s2_indice_1m)
                dossier_coord = self.cd_coord.text()
                fichier = pd.read_excel(str(dossier_coord))
                liste_fichier = glob(os.path.join(rep_s2_data, "*.tif"))
                print(liste_fichier)
                for img in liste_fichier :
                    image = gdal.Open(img)
                coordonnees = dict()
                point = []
                for i in range(0, len(fichier)):
                    #on recup latitude longitude
                    lat = fichier.Latitude[i]
                    lon = fichier.Longitude[i]
                    #conversion coord decimal
                    deg_lat = float(lat[0:2])
                    min_lat = float(lat [3:5])
                    sec_lat = float(lat[7:10])
                    x = deg_lat + min_lat/60 + sec_lat/(60*60)    
                    deg_lon = float(lon[0])
                    min_lon = float(lon[2:4])
                    sec_lon = float(lon[5:9])
                    if lon[11] == 'O':
                        y = -(deg_lon + min_lon/60 + sec_lon/(60*60))
                    else:
                        y = deg_lon + min_lon/60 + sec_lon/(60*60)
                    lat, lon = x, y
                    proj = image.GetProjection()[588:593]
                    if proj == '32630':
                        epsg_4326 = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs')
                        epsg_32630 = pyproj.Proj('+proj=utm +zone=30 +datum=WGS84 +units=m +no_defs')
                        x, y = pyproj.transform(epsg_4326, epsg_32630, lon, lat)
                        print(i)
                        if i == 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        elif i%4 != 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        elif i%4 == 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point = []
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        print(coordonnees)
                    elif proj == '32631':
                        epsg_4326 = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs  ')
                        epsg_32631 = pyproj.Proj('+proj=utm +zone=31 +datum=WGS84 +units=m +no_defs ')
                        x, y = pyproj.transform(epsg_4326, epsg_32631, lon, lat)
                        if i == 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        elif i%4 != 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        elif i%4 == 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point = []
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                    print(coordonnees)
                schema = {'geometry': 'Polygon', 'properties': OrderedDict([('ID', 'str'), ("Surf", "float:15.2")])}
                shapefile = os.path.join(rep_s2_pretraitement, 'parcelle.shp')
                with fiona.open(shapefile, 'w', driver='ESRI Shapefile', crs=from_epsg(proj), schema=schema) as dst:
                    for i in coordonnees.keys():
                        x1 = coordonnees[i][0][0]
                        y1 = coordonnees[i][0][1]

                        x2 = coordonnees[i][1][0]
                        y2 = coordonnees[i][1][1]

                        x3 = coordonnees[i][2][0]
                        y3 = coordonnees[i][2][1]

                        x4 = coordonnees[i][3][0]
                        y4 = coordonnees[i][3][1]

                        x5 = coordonnees[i][0][0]
                        y5 = coordonnees[i][0][1]

                        poly = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5)])
                        print(poly)
                        print(i)
                        #print(poly.area)
                        buffer = Polygon(poly.buffer(-1.5), LinearRing([(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5)]))
                        #print(buffer.area)
                        #print(" ")
                        dst.write({'geometry': mapping(buffer), 'properties': {'ID': i[1], "Surf": poly.area}})                   
        elif self.landsat.checkState()>0:
            os.chdir(str(self.dossier_image.text()))
            for j in (os.listdir('.')):
                rep_l8_data = str(self.dossier_image.text()) +'\\'+ str(j) +'\\data'
                rep_l8_pretraitement = str(self.dossier_image.text()) +'\\'+ str(j)  + '\\Pretraitement'
                if not os.path.isdir(rep_l8_pretraitement):
                    os.mkdir(rep_l8_pretraitement)
                rep_l8_indice = str(self.dossier_image.text()) +'\\'+ str(j) +'\\Indices'
                if not os.path.isdir(rep_l8_indice):
                    os.mkdir(rep_l8_indice)
                rep_l8_indice_1m = rep_l8_indice + '\\indice_1m'
                if not os.path.isdir(rep_l8_indice_1m):
                    os.mkdir(rep_l8_indice_1m)
                dossier_coord = self.cd_coord.text()
                fichier = pd.read_excel(str(dossier_coord))
                liste_fichier = glob(os.path.join(rep_l8_data, "*.tif"))
                for img in liste_fichier :
                    image = gdal.Open(img)
                coordonnees = dict()
                point = []
                for i in range(0, len(fichier)):
                    #on recup latitude longitude
                    lat = fichier.Latitude[i]
                    lon = fichier.Longitude[i]
                    #conversion coord decimal
                    deg_lat = float(lat[0:2])
                    min_lat = float(lat [3:5])
                    sec_lat = float(lat[6:10])
                    x = deg_lat + min_lat/60 + sec_lat/(60*60)    
                    deg_lon = float(lon[0])
                    min_lon = float(lon[2:4])
                    sec_lon = float(lon[5:9])
                    print(lon)
                    if lon[11] == 'O':
                        y = -(deg_lon + min_lon/60 + sec_lon/(60*60))
                    else:
                        y = deg_lon + min_lon/60 + sec_lon/(60*60)
                    lat, lon = x, y
                    proj = image.GetProjection()[589:594]
                    if (proj == '32630'):
                        epsg_4326 = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs  ')
                        epsg_32630 = pyproj.Proj('+proj=utm +zone=30 +datum=WGS84 +units=m +no_defs ')
                        x, y = pyproj.transform(epsg_4326, epsg_32630, lon, lat)
                        print("SALUT")
                        if i == 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        elif i%4 != 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        elif i%4 == 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point = []
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        print(coordonnees)
                    elif (proj == '32631'):
                        print("je suis la")
                        epsg_4326 = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs')
                        epsg_32631 = pyproj.Proj('+proj=utm +zone=31 +datum=WGS84 +units=m +no_defs')
                        x, y = pyproj.transform(epsg_4326, epsg_32631, lon, lat)
                        print("SALUT")
                        if i == 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        elif i%4 != 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        elif i%4 == 0:
                            #pt = (x, y)
                            pt = (x, y)
                            point = []
                            point.append(pt)
                            coordonnees[(fichier.Parcelle[i][0:13]).encode('utf-8'), (fichier.Modalite[i]).encode('utf-8')]= point
                        print(coordonnees)
                schema = {'geometry': 'Polygon', 'properties': OrderedDict([('ID', 'str'), ("Surf", "float:15.2")])}
                shapefile = os.path.join(rep_l8_pretraitement, 'parcelle.shp')
                with fiona.open(shapefile, 'w', driver='ESRI Shapefile', crs=from_epsg(proj), schema=schema) as dst:
                    for i in coordonnees.keys():
                        print('HELLO')
                        print(i)
                        x1 = coordonnees[i][0][0]
                        y1 = coordonnees[i][0][1]

                        x2 = coordonnees[i][1][0]
                        y2 = coordonnees[i][1][1]

                        x3 = coordonnees[i][2][0]
                        y3 = coordonnees[i][2][1]

                        x4 = coordonnees[i][3][0]
                        y4 = coordonnees[i][3][1]

                        x5 = coordonnees[i][0][0]
                        y5 = coordonnees[i][0][1]

                        poly = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5)])
                        #print(poly.area)
                        buffer = Polygon(poly.buffer(-1.5), LinearRing([(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5)]))
                        #print(buffer.area)
                        #print(" ")
                        dst.write({'geometry': mapping(buffer), 'properties': {'ID': i[1], "Surf": poly.area}})

    def decoup_image_mask(self):
        if self.sentinel.checkState()>0:
            self.liste_image_decoup.clear()
            os.chdir(str(self.dossier_image.text()))
            liste_concat = []
            for i in (os.listdir('.')):
                print(i)
                rep_s2_data = str(self.dossier_image.text()) +'\\'+ str(i) + '\\GRANULE\\IMG_DATA'
                rep_s2_pretraitement = str(self.dossier_image.text()) +'\\'+ str(i)  + '\\GRANULE\\Pretraitement'
                rep_s2_indice = str(self.dossier_image.text()) +'\\'+ str(i) +'\\GRANULE\\Indices'    
                rep_s2_indice_1m = rep_s2_indice + '\\indice_1m'
                #decoupage des rasters a la forme du shapefile
                # Liste de toutes les images de rep_s2_data finissant par jp2
                liste_fichier = glob(os.path.join(rep_s2_data, "*.tif"))
                shapefile = os.path.join(rep_s2_pretraitement, 'parcelle.shp')
                with fiona.open(shapefile, "r") as shapefile:
                    features = [feature["geometry"] for feature in shapefile]
                    liste_mask = []
                for img in liste_fichier:
                    # Nouveau nom de l'image apres decoupe, au format tif, placee dans le bon repertoire
                    #Recuperation du nom de l'image sans l'extension
                    nom_img = os.path.splitext(os.path.basename(img))[0]
                    img_mask = os.path.join(rep_s2_pretraitement, "mask_%s.tif" % nom_img)
                    liste_mask.append(img_mask)
                    with rasterio.open(img) as src:
                        out_image, out_transform = rasterio.mask.mask(src, features, crop=True)
                        out_meta = src.meta.copy()
        
                        out_meta.update({"driver": "GTiff",
                                         "height": out_image.shape[1],
                                         "width": out_image.shape[2],
                                         "transform": out_transform})
                    with rasterio.open(img_mask, "w", **out_meta) as dest:
                        dest.write(out_image)
                    self.liste_image_decoup.addItem(img_mask)
                    
                os.chdir(rep_s2_pretraitement)
                shapefile = "parcelle.shp"
                dico_pixel = {}
                with fiona.open(shapefile) as src:
                    # On traite les géométries du shapefile une par une
                    for parcelle in src:
                        dico_bande_pixel = {}
                        nom_parcelle = parcelle['properties']['ID']
                        for bande in liste_mask:
                            # Nom de bande
                            band = os.path.splitext(os.path.basename(bande))[0]
                            nom_bande = band[-3:]
                            # rasterstats.zonal_stats renvoie une liste mais ici il n'y a qu'un élément (une seule géométrie)
                            # Si tu mets all_touched=True, tu auras des pixels de bordure qui vont se retrouver dans 2 parcelles
                            stats = rasterstats.zonal_stats(parcelle, bande,
                                                            stats= ['mean', 'median', 'std'],
                                                            nodata = -999,  all_touched=False,
                                                            raster_out=True)[0]
                            # Les valeurs des pixels sont mis dans un array à une dimension
                            dico_bande_pixel[nom_bande] =  stats["mini_raster_array"].data.flatten()
                        print(dico_bande_pixel)
                        # On regroupe les données dans un dixtionnaire par indice
                        dico_pixel[nom_parcelle] = dico_bande_pixel

                    # Petite précaution pour le notebook.
                    # On commence par supprimer le DataFrame s'il existe,
                    # sinon on va rajouter des données dans celui qui est déjà en mémoire !
                    try:
                        del df_parc_bande
                    except:
                        pass
                    # Un test facultatif pour vérifier que le DataFrame final contient toutes les lignes.
                    taille_final = 0
                    for parcelle in sorted(dico_pixel.keys()): # tri alphabétique des parcelles facultatif
                        print(len(dico_pixel[parcelle]))
                        df_parc = pd.DataFrame(dico_pixel[parcelle])
                        # On remplace les valeurs -999, 0 et 1 par Nan
                        df_parc.replace([-999, 0, 1], np.nan, inplace=True)
                        # On supprime toutes les lignes ne contenant que des Nan
                        df_parc.dropna(how="all", axis=0, inplace=True)
                        # On rajoute le nom de la parcelle comme colonne
                        df_parc['Parcelle'] = [parcelle]*df_parc.shape[0]
                        # Calcul du nombre de ligne
                        taille_final += df_parc.shape[0]
                        try: # A partir de la deuxième parcelle df_parc_bande existe : on peut lui rajouter des valeurs
                            df_parc_bande = df_parc_bande.append(df_parc)
                        except: # Pour la première parcelle df_parc_indice n'exite pas encore : on le crée
                            df_parc_bande = df_parc
                            
                    ###creation de liste pour la date
                    liste_date = []
                    liste_bande = []
                    for j in range(0, df_parc_bande.shape[0]):
                        liste_bande.append(j)
                        liste_date.append(str(i))
                    ###je cree un dataframe de la date avec liste_date et ensuite je le concatene en ligne avec concat
                    df_parc_bande['Bande'] = liste_bande
                    df_parc_bande2 = df_parc_bande.set_index(['Bande'])
                    
                    df_date = pd.DataFrame({'Date' : liste_date})
                    concat_stat = pd.concat([df_date, df_parc_bande2], axis = 1)
                    cols = concat_stat.columns.tolist()
                    cols = cols[-1:] + cols[:-1]
                    concat_stat = concat_stat[cols]
                    print(concat_stat)
                    print(" ")
                    liste_concat.append(concat_stat)
                       
                chemin = str(self.cd_sortie.text())
                os.chdir(chemin)
                concat_final = pd.concat(liste_concat, ignore_index = True)
                print("concat_final :")
                print(concat_final)
                writer = pd.ExcelWriter('valeur_pixels_bande.xlsx', engine='xlsxwriter')
                concat_final.to_excel(writer)
                writer.save

                  
        elif self.landsat.checkState()>0:
            self.liste_image_decoup.clear()
            os.chdir(str(self.dossier_image.text()))
            os.chdir(str(self.dossier_image.text()))
            liste_concat = []
            for i in (os.listdir('.')):
                print(i)
                rep_l8_data = str(self.dossier_image.text()) +'/'+ str(i)+'\\data'
                rep_l8_pretraitement = str(self.dossier_image.text()) +'/'+ str(i)  + '/Pretraitement'
                rep_l8_indice = str(self.dossier_image.text()) +'/'+ str(i) +'/Indices'
                rep_l8_indice_1m = rep_l8_indice + '/indice_1m'
                #decoupage des rasters a la forme du shapefile
                # Liste de toutes les images de rep_s2_data finissant par jp2
                liste_fichier = glob(os.path.join(rep_l8_data, "*.tif"))
                shapefile = os.path.join(rep_l8_pretraitement, 'parcelle.shp')
                with fiona.open(shapefile, "r") as shapefile:
                    features = [feature["geometry"] for feature in shapefile]
                    liste_mask=[]
                for img in liste_fichier:
                    # Recuperation du nom de l'image sans l'extension 
                    nom_img = os.path.splitext(os.path.basename(img))[0]
                    # Nouveau nom de l'image apres decoupe, au format tif, placee dans le bon repertoire
                    img_mask = os.path.join(rep_l8_pretraitement, "mask_%s.tif" % nom_img)
                    liste_mask.append(img_mask)
                    with rasterio.open(img) as src:
                        out_image, out_transform = rasterio.mask.mask(src, features, crop=True)
                        out_meta = src.meta.copy()
        
                        out_meta.update({"driver": "GTiff",
                                         "height": out_image.shape[1],
                                         "width": out_image.shape[2],
                                         "transform": out_transform})
                    with rasterio.open(img_mask, "w", **out_meta) as dest:
                        dest.write(out_image)
                    self.liste_image_decoup.addItem(img_mask)
            
                os.chdir(rep_l8_pretraitement)
                shapefile = "parcelle.shp"
                dico_pixel = {}
                with fiona.open(shapefile) as src:
                    # On traite les géométries du shapefile une par une
                    for parcelle in src:
                        dico_bande_pixel = {}
                        nom_parcelle = parcelle['properties']['ID']
                        print('liste_mask :')
                        print(liste_mask)
                        for bande in liste_mask:
                            # Nom de bande
                            band = os.path.splitext(os.path.basename(bande))[0]
                            nom_bande = band[-3:]
                            print(nom_bande)
                            # rasterstats.zonal_stats renvoie une liste mais ici il n'y a qu'un élément (une seule géométrie)
                            # Si tu mets all_touched=True, tu auras des pixels de bordure qui vont se retrouver dans 2 parcelles
                            stats = rasterstats.zonal_stats(parcelle, bande,
                                                            stats= ['mean'],
                                                            nodata = -999,  all_touched=False,
                                                            raster_out=True)[0]
                            # Les valeurs des pixels sont mis dans un array à une dimension
                            dico_bande_pixel[nom_bande] =  stats["mini_raster_array"].data.flatten()
                        # On regroupe les données dans un dixtionnaire par indice
                        dico_pixel[nom_parcelle] = dico_bande_pixel
                    # Petite précaution pour le notebook.
                    # On commence par supprimer le DataFrame s'il existe,
                    # sinon on va rajouter des données dans celui qui est déjà en mémoire !
                    try:
                        del df_parc_bande
                    except:
                        pass
                    # Un test facultatif pour vérifier que le DataFrame final contient toutes les lignes.
                    taille_final = 0
                    for parcelle in sorted(dico_pixel.keys()): # tri alphabétique des parcelles facultatif
                        df_parc = pd.DataFrame.from_dict(dico_pixel[parcelle], orient = 'index')
                        df_parc = df_parc.transpose()
                        # On remplace les valeurs -999, 0 et 1 par Nan
                        df_parc.replace([-999, 0, 1], np.nan, inplace=True)
                        # On supprime toutes les lignes ne contenant que des Nan
                        df_parc.dropna(how="all", axis=0, inplace=True)
                        # On rajoute le nom de la parcelle comme colonne
                        df_parc['Parcelle'] = [parcelle]*df_parc.shape[0]
                        # Calcul du nombre de ligne
                        taille_final += df_parc.shape[0]
                        try: # A partir de la deuxième parcelle df_parc_bande existe : on peut lui rajouter des valeurs
                            df_parc_bande = df_parc_bande.append(df_parc)
                        except: # Pour la première parcelle df_parc_indice n'exite pas encore : on le crée
                            df_parc_bande = df_parc
                            
                    ###creation de liste pour la date
                    liste_date = []
                    liste_bande = []
                    for j in range(0, df_parc_bande.shape[0]):
                        liste_bande.append(j)
                        liste_date.append(str(i))
                    ###je cree un dataframe de la date avec liste_date et ensuite je le concatene en ligne avec concat
                    df_parc_bande['Bande'] = liste_bande
                    df_parc_bande2 = df_parc_bande.set_index(['Bande'])
                            
                    df_date = pd.DataFrame({'Date' : liste_date})
                    concat_stat = pd.concat([df_date, df_parc_bande2], axis = 1)
                    cols = concat_stat.columns.tolist()
                    cols = cols[-1:] + cols[:-1]
                    concat_stat = concat_stat[cols]
                    print(concat_stat)
                    print(" ")
                    liste_concat.append(concat_stat)
                   
                chemin = str(self.cd_sortie.text())
                os.chdir(chemin)
                concat_final = pd.concat(liste_concat, ignore_index = True)
                print("concat_final :")
                print(concat_final)
                writer = pd.ExcelWriter('valeur_pixels_bande.xlsx', engine='xlsxwriter')
                concat_final.to_excel(writer)
                writer.save
        
        ### Calcul des indices ##################################
    def calcul_indice(self):
        if self.sentinel.checkState()>0:
            self.tableauindice.clear()
            os.chdir(str(self.dossier_image.text()))
            dossier = self.liste_fichier_2.currentItem().text()
            rep_s2_data = str(self.dossier_image.text()) +'\\'+ str(dossier) + '\\GRANULE\\IMG_DATA'

            rep_s2_pretraitement = str(self.dossier_image.text()) +'\\'+ str(dossier)  + '\\GRANULE\\Pretraitement'
            if not os.path.isdir(rep_s2_pretraitement):
                os.mkdir(rep_s2_pretraitement)

            rep_s2_indice = str(self.dossier_image.text()) +'\\'+ str(dossier) +'\\GRANULE\\Indices'
            if not os.path.isdir(rep_s2_indice):
                os.mkdir(rep_s2_indice)

            rep_s2_indice_1m = rep_s2_indice + '\\indice_1m'
            if not os.path.isdir(rep_s2_indice_1m):
                os.mkdir(rep_s2_indice_1m)

            dictionnaire_indice ={}
            liste_mask = glob(os.path.join(rep_s2_pretraitement, "*.tif"))
            with rasterio.open([val for val in liste_mask if "B02" in val][0]) as src:
                profile = src.profile # On récupère le profile qui servira pour toutes les images
                print(profile)
                blue = src.read(1)
            with rasterio.open([val for val in liste_mask if "B03" in val][0]) as src:
                green = src.read(1)
            with rasterio.open([val for val in liste_mask if "B04" in val][0]) as src:
                red = src.read(1)
            with rasterio.open([val for val in liste_mask if "B05" in val][0]) as src:
                re = src.read(1)
            with rasterio.open([val for val in liste_mask if "B06" in val][0]) as src:
                b6 = src.read(1)
            with rasterio.open([val for val in liste_mask if "B07" in val][0]) as src:
                b7 = src.read(1)
            with rasterio.open([val for val in liste_mask if "B08" in val][0]) as src:
                nir = src.read(1)
            with rasterio.open([val for val in liste_mask if "B11" in val][0]) as src:
                b11 = src.read(1)
            profile["dtype"] = rasterio.dtypes.float32
            # Calcul NDVI
            check = np.logical_and((np.logical_or(red > 0, nir > 0)), red != -999, nir != -999)
            ndvi = np.where(check, (nir - red) / (nir + red), -999)
            dictionnaire_indice["ndvi"] = ndvi
            self.tableauindice.addItem('NDVI - Normalized Difference Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "ndvi.tif"), "w", **profile) as dst:
                dst.write(ndvi, 1)
            # Calcul NDWI
            check = np.logical_and((np.logical_or(green > 0, nir > 0)), green != -999, nir != -999)
            ndwi = np.where(check, (green - nir) / (green + nir), -999)
            dictionnaire_indice["ndwi"] = ndwi
            self.tableauindice.addItem('NDWI - Normalized Difference Water Index')
            with rasterio.open(os.path.join(rep_s2_indice, "ndwi.tif"), "w", **profile) as dst:
                dst.write(ndwi, 1)
            # Calcul du RE-NDWI (red-edge ndwi) on utilise la bande du RE au lieu de la bande du PIR
            check = np.logical_and((np.logical_or(green > 0, re > 0)), green != -999, re != -999)
            re_ndwi = np.where(check, (green - re) / (green + re), -999)
            dictionnaire_indice["re_ndwi"] = re_ndwi
            self.tableauindice.addItem('RE-NDWI - Red-Edge Normalized Difference Water Index')
            with rasterio.open(os.path.join(rep_s2_indice, "re_ndwi.tif"), "w", **profile) as dst:
                dst.write(re_ndwi, 1)
            ## Calcul NDII = detection des stress eventuels
            check = np.logical_and((np.logical_or(nir > 0, b11 > 0)), nir != -999, b11 != -999)
            ndii = np.where(check, (nir - b11) / (nir + b11), -999)
            dictionnaire_indice["ndii"] = ndii
            self.tableauindice.addItem('NDII - Normalized Difference Infrared Index')
            with rasterio.open(os.path.join(rep_s2_indice, "ndii.tif"), "w", **profile) as dst:
                dst.write(ndii, 1)
            ## Calcul MSI
            check = np.logical_and((np.logical_not((nir == 0))), nir != -999, b11 != -999)
            msi = np.where(check, (b11 / nir), -999)
            dictionnaire_indice["msi"] = msi
            self.tableauindice.addItem('MSI - Moisture Stress Index')
            with rasterio.open(os.path.join(rep_s2_indice, "msi.tif"), "w", **profile) as dst:
                dst.write(msi, 1)
            # Calcul de s2rep = red-edge position
            np.seterr(all="ignore");
            verif = np.logical_not((b6 - re)== 0)
            verif2 = np.logical_and(b7 != -999, red != -999, re != -999)
            check = np.logical_and(verif, verif2)
            s2rep = np.where(check, (705 + 35 * (0.5 * (b7 + red) - re)/(b6 - re)), -999)
            dictionnaire_indice["s2rep"] = s2rep
            self.tableauindice.addItem('S2REP - Red-Edge position')
            with rasterio.open(os.path.join(rep_s2_indice, "s2rep.tif"), "w", **profile) as dst:
                dst.write(s2rep, 1)
            # Calcul du PSSR
            check = np.logical_and((np.logical_not((red == 0))), nir != -999, red != -999)
            pssr = np.where(check, (nir/red), -999)
            dictionnaire_indice["pssr"] = pssr
            self.tableauindice.addItem('PSSR - Pigment Specific Simple Ratio')
            with rasterio.open(os.path.join(rep_s2_indice, "pssr.tif"), "w", **profile) as dst:
                dst.write(pssr, 1)
            # Calcul de ARVI = comme ndvi mais plus resistant aux aerosols
            verif = np.logical_not(nir -((2*red)-blue) == 0)
            verif2 = np.logical_and(nir != -999, red != -999, blue != -999)
            check = np.logical_and(verif, verif2)
            arvi = np.where(check, ((nir - (2*red)-blue)/(nir + (2*red)-blue)), -999)
            dictionnaire_indice["arvi"] = arvi
            self.tableauindice.addItem('ARVI - Aerosol Resistant Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "arvi.tif"), "w", **profile) as dst:
                dst.write(arvi, 1)
            # Calcul du PSRI = plant senescence reflectance index
            verif = np.logical_not(re == 0)
            verif2 = np.logical_and(red != -999, re != -999, blue != -999)
            check = np.logical_and(verif, verif2)
            psri = np.where(check, ((red - blue) / re), -999)
            dictionnaire_indice["psri"] = psri
            self.tableauindice.addItem('PSRI - Plant Senescence Reflectance Index')
            with rasterio.open(os.path.join(rep_s2_indice, "psri.tif"), "w", **profile) as dst:
                dst.write(psri, 1)
            # Calcul de CRI2 = carotenoid reflectance index 2
            check = np.logical_and((np.logical_and ((blue !=0), (re != 0))), blue != -999, re != -999)
            cri2 = np.where(check, ((1/blue) - (1/re)), -999)
            dictionnaire_indice["cri2"] = cri2
            self.tableauindice.addItem('CRI2 - Carotenoid Reflectance Index 2')
            with rasterio.open(os.path.join(rep_s2_indice, "cri2.tif"), "w", **profile) as dst:
                dst.write(cri2, 1)
            #Calcul de CRI1
            check = np.logical_and((np.logical_and ((blue > 0), (green > 0))), blue != -999, green != -999)
            cri1 = np.where(check, ((1/blue)-(1/green)), -999)
            dictionnaire_indice["cri1"] = cri1
            self.tableauindice.addItem('CRI1 - Carotenoid Reflectance Index 1')
            with rasterio.open(os.path.join(rep_s2_indice, "cri1.tif"), "w", **profile) as dst:
                dst.write(cri1, 1)
            # Calcul de CHL-RED-EDGE = chlorophylle red edge
            check = np.logical_and((np.logical_not(nir == 0)), re != -999, nir != -999)
            chl_re = np.where(check, (re/nir), -999)
            dictionnaire_indice["chl_re"] = chl_re
            self.tableauindice.addItem('CHL-RE - Chlorophyll Red-Edge')
            with rasterio.open(os.path.join(rep_s2_indice, "chl_re.tif"), "w", **profile) as dst:
                dst.write(chl_re, 1)
            #Calcul ARI2 = anthocyanin reflectance index
            verif = np.logical_and((blue > 0), (green > 0))
            verif2 = np.logical_and(nir != -999, blue != -999, green != -999)    
            check = np.logical_and(verif, verif2)
            ari2 = np.where(check, ((nir/blue)-(nir/green)), -999)
            dictionnaire_indice["ari2"] = ari2
            self.tableauindice.addItem('ARI2 - Anthocyanin Reflectance Index')
            with rasterio.open(os.path.join(rep_s2_indice, "ari2.tif"), "w", **profile) as dst:
                dst.write(ari2, 1)
            #Calcul de EVI = enhanced vegetation index
            check = np.logical_and((np.logical_not((nir + 2.4*red +1)==0)), nir != -999, red != -999)
            evi = np.where(check, (2.5 * (nir - red)/(nir + 2.4*red +1)), -999)
            dictionnaire_indice["evi"] = evi
            self.tableauindice.addItem('EVI - Enhance Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "evi.tif"), "w", **profile) as dst:
                dst.write(evi, 1)
            #Calcul de GNDVI = green normalized vegetation index
            check = np.logical_and((np.logical_not ((nir + green)==0)), nir != -999, green != -999)
            gndvi = np.where(check, ((nir - green)/(nir + green)), -999)
            dictionnaire_indice["gndvi"] = gndvi
            self.tableauindice.addItem('GNDVI - Green Normalized Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "gndvi.tif"), "w", **profile) as dst:
                dst.write(gndvi, 1)
            #Calcul de SAVI (soil adjusted vegetation index)
            check = np.logical_and((np.logical_not((nir + red + 0.5) == 0)), nir != -999, red != -999)
            savi = np.where(check, (((nir - red)/(nir + red + 0.5)*1.5)), -999)
            dictionnaire_indice["savi"] = savi
            self.tableauindice.addItem('SAVI - Soil Adjusted Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "savi.tif"), "w", **profile) as dst:
                dst.write(savi, 1)
            #Calcul de CGI (chlorophyll green index)
            check = np.logical_and((np.logical_not(green == 0)), nir != -999, green != -999)
            chl_green = np.where(check, (nir/green), -999)
            dictionnaire_indice["chl_green"] = chl_green
            self.tableauindice.addItem('CHL_GREEN - Chlorophyll Green Index')
            with rasterio.open(os.path.join(rep_s2_indice, "chl_green"), "w", **profile) as dst:
                dst.write(chl_green, 1)
            #Calcul CVI (chlorophyll vegetation index)
            verif = np.logical_not(green == 0)
            verif2 = np.logical_and(nir != -999, red != -999, green != -999)
            check = np.logical_and(verif, verif2)
            cvi = np.where(check, ((nir*red)/(green* green)), -999)
            dictionnaire_indice['cvi'] = cvi
            self.tableauindice.addItem('CVI - Chlorophyll Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "cvi.tif"), "w", **profile) as dst:
                dst.write(cvi, 1)

        elif self.landsat.checkState()>0:
            self.tableauindice.clear()
            os.chdir(str(self.dossier_image.text()))
            dossier = self.liste_fichier_2.currentItem().text()
            rep_l8_data = str(self.dossier_image.text()) +'\\'+ str(dossier)+'\\data'
            rep_l8_pretraitement = str(self.dossier_image.text()) +'\\'+ str(dossier)  + '\Pretraitement'
            if not os.path.isdir(rep_l8_pretraitement):
                os.mkdir(rep_l8_pretraitement)
                
            rep_l8_indice = str(self.dossier_image.text()) +'\\'+ str(dossier) +'\Indices'
            if not os.path.isdir(rep_l8_indice):
                os.mkdir(rep_l8_indice)
                
            rep_l8_indice_1m = rep_l8_indice + '\\indice_1m'
            if not os.path.isdir(rep_l8_indice_1m):
                os.mkdir(rep_l8_indice_1m)

            dictionnaire_indice ={}
            liste_mask = glob(os.path.join(rep_l8_pretraitement, "*.tif"))    
            with rasterio.open([val for val in liste_mask if "B2" in val][0]) as src:
                profile = src.profile
                print(profile)
                blue = src.read(1)
            with rasterio.open([val for val in liste_mask if "B3" in val][0]) as src:
                green = src.read(1)
            with rasterio.open([val for val in liste_mask if "B4" in val][0]) as src:
                red = src.read(1)
            with rasterio.open([val for val in liste_mask if "B5" in val][0]) as src:
                nir = src.read(1)
            with rasterio.open([val for val in liste_mask if "B6" in val][0]) as src:
                swir1 = src.read(1)
            with rasterio.open([val for val in liste_mask if "B11" in val][0]) as src:
                band11 = src.read(1)
            profile["dtype"] = rasterio.dtypes.float32
            # Calcul NDVI
            check = np.logical_and((np.logical_or(red > 0, nir > 0)), nir != -999, red != -999)
            ndvi = np.where(check, (nir - red) / (nir + red), -999)
            dictionnaire_indice["ndvi"] = ndvi
            self.tableauindice.addItem('NDVI - Normalized Difference Vegetation Index')
            with rasterio.open(os.path.join(rep_l8_indice, "ndvi.tif"), "w", **profile) as dst:
                dst.write(ndvi, 1)
            # Calcul NDWI
            check = np.logical_and((np.logical_or(green > 0, nir > 0)), nir != -999, green != -999)
            ndwi = np.where(check, (green - nir) / (green + nir), -999)
            dictionnaire_indice["ndwi"] = ndwi
            self.tableauindice.addItem('NDWI - Normalized Difference Water Index')
            with rasterio.open(os.path.join(rep_l8_indice, "ndwi.tif"), "w", **profile) as dst:
                dst.write(ndwi, 1)
            # Calcul du PSSR = pigment specific simple ratio
            check = np.logical_and((np.logical_not((red == 0))), nir != -999, red != -999)
            pssr = np.where(check, (nir/red), -999)
            dictionnaire_indice["pssr"] = pssr
            self.tableauindice.addItem('PSSR - Pigment Specific Simple Ratio')
            with rasterio.open(os.path.join(rep_l8_indice, "pssr.tif"), "w", **profile) as dst:
                dst.write(pssr, 1)
            # Calcul de ARVI = comme ndvi mais plus resistant aux aerosols
            verif = np.logical_not(nir -((2*red)-blue))
            verif2 = np.logical_and(nir != -999, red != -999, blue != -999)
            check = np.logical_and(verif, verif2)
            arvi = np.where(check, ((nir - ((2*red)-blue))/(nir + ((2*red)-blue))), -999)
            dictionnaire_indice["arvi"] = arvi
            self.tableauindice.addItem('ARVI - Aerosol Resistant Vegetation Index')
            with rasterio.open(os.path.join(rep_l8_indice, "arvi.tif"), "w", **profile) as dst:
                dst.write(arvi, 1)
            #Calcul CRI1 (carotenoid reflectance index 1)
            check = np.logical_and((np.logical_and((blue != 0), (green != 0))), bleu != -999, green != -999)
            cri1 = np.where(check, ((1/blue)-(1/green)), -999)
            dictionnaire_indice["cri1"] = cri1
            self.tableauindice.addItem('CRI1 - Carotenoid Reflectance Index 1')
            with rasterio.open(os.path.join(rep_l8_indice, "cri1.tif"), "w", **profile) as dst:
                dst.write(cri1, 1)
            #Calcul ARI2 = anthocyanin reflectance index
            verif = np.logical_and((blue != 0), (green != 0))
            verif2 = np.logical_and(red != -999, blue != -999, green != -999)
            check = np.logical_and(verif, verif2)
            ari2= np.where(check, ((red/blue) - (red/green)), -999)
            dictionnaire_indice["ari2"] = ari2
            self.tableauindice.addItem('ARI2 - Anthocyanin Reflectance Index')
            with rasterio.open(os.path.join(rep_l8_indice, "ari2.tif"), "w", **profile) as dst:
                dst.write(ari2, 1)
            # Calcul de EVI = enhanced vegetation index
            verif = np.logical_not((nir + (swir1*red) - (7.5*blue)+1) == 0)
            verif2 = np.logical_and(nir != -999, red != -999, swir != -999)
            verif3 = np.logical_and(verif2,  blue != -999)
            check = np.logical_and(verif, verif3)
            evi = np.where(check, ((2.5*(nir - red))/(nir + (swir1*red) - (7.5*blue)+1)), -999)
            dictionnaire_indice["evi"] = evi
            self.tableauindice.addItem('EVI - Enhance Vegetation Index')
            with rasterio.open(os.path.join(rep_l8_indice, "evi.tif"), "w", **profile) as dst:
                dst.write(evi, 1)
            # Calcul GNDVI (green ndvi)
            check = np.logical_and((np.logical_not (nir + green == 0)), nir != -999, green != -999)
            gndvi = np.where(check, ((nir - green)/(nir + green)), -999)
            dictionnaire_indice["gndvi"] = gndvi
            self.tableauindice.addItem('GNDVI - Green Normalized Vegetation Index')
            with rasterio.open(os.path.join(rep_l8_indice, "gndvi.tif"), "w", **profile) as dst:
                dst.write(gndvi, 1)
            # Calcul de SAVI
            check = np.logical_and((np.logical_and(nir > 0, red > 0)), nir != -999, red != -999)
            savi = np.where(check, (((nir - red)/(nir + red + 0.5))*1.5), -999)
            dictionnaire_indice["savi"] = savi
            self.tableauindice.addItem('SAVI - Soil Adjusted Vegetation Index')
            with rasterio.open(os.path.join(rep_l8_indice, "savi.tif"), "w", **profile) as dst:
                dst.write(savi, 1) 
            # Calcul de NDMI = normalized difference moisture index
            check = np.logical_and((np.logical_not((nir + swir1) == 0)), nir != -999, swir1 != -999)
            ndmi = np.where(check, ((nir - swir1)/(nir + swir1)), -999)
            dictionnaire_indice["ndmi"] = ndmi
            self.tableauindice.addItem('NDMI - Normalized Difference Moisture Index')
            with rasterio.open(os.path.join(rep_l8_indice, "ndmi.tif"), "w", **profile) as dst:
                dst.write(ndmi, 1)
            # Calcul de chlorophyll green index
            check = np.logical_and((np.logical_not(green == 0)) , nir != -999, green != -999)
            chl_green = np.where(check, ((nir/green)-1), -999)
            dictionnaire_indice["chl_green"] = chl_green
            self.tableauindice.addItem('CHL_GREEN - Chlorophyll Green Index')
            with rasterio.open(os.path.join(rep_l8_indice, "chl_green.tif"), "w", **profile) as dst:
                dst.write(chl_green, 1)
            # Calcul CVI = chlorophyll vegetation index
            verif = np.logical_not(green == 0)
            verif2 = np.logical_and(nir != -999, red != -999, green != -999)
            check = np.logical_and(verif, verif2)
            cvi = np.where (check, ((nir*red)/(green*green)), -999)
            dictionnaire_indice["cvi"] = cvi
            self.tableauindice.addItem('CVI - Chlorophyll Vegetation Index')
            with rasterio.open(os.path.join(rep_l8_indice, "cvi.tif"), "w", **profile) as dst:
                dst.write(cvi, 1)

    def calcul_tout(self):
        if self.sentinel.checkState()>0:
            self.tableauindice.clear()
            dossier = self.dossier_image.text()
            os.chdir(str(dossier))
            for doss in os.listdir('.'):
                rep_s2_pretraitement = str(self.dossier_image.text()) +'\\'+ str(doss)  + '\\GRANULE\\Pretraitement'
                rep_s2_indice = str(self.dossier_image.text()) +'\\'+ str(doss) +'\\GRANULE\\Indices'
                dictionnaire_indice ={}
                liste_mask = glob(os.path.join(rep_s2_pretraitement, "*.tif"))
                with rasterio.open([val for val in liste_mask if "B02" in val][0]) as src:
                    profile = src.profile # On récupère le profile qui servira pour toutes les images
                    blue = src.read(1)
                with rasterio.open([val for val in liste_mask if "B03" in val][0]) as src:
                    green = src.read(1)
                with rasterio.open([val for val in liste_mask if "B04" in val][0]) as src:
                    red = src.read(1)
                with rasterio.open([val for val in liste_mask if "B05" in val][0]) as src:
                    re = src.read(1)
                with rasterio.open([val for val in liste_mask if "B06" in val][0]) as src:
                    b6 = src.read(1)
                with rasterio.open([val for val in liste_mask if "B07" in val][0]) as src:
                    b7 = src.read(1)
                with rasterio.open([val for val in liste_mask if "B08" in val][0]) as src:
                    nir = src.read(1)
                with rasterio.open([val for val in liste_mask if "B11" in val][0]) as src:
                    b11 = src.read(1)
                profile["dtype"] = rasterio.dtypes.float32
                # Calcul NDVI
                check = np.logical_and((np.logical_or(red > 0, nir > 0)), red != -999, nir != -999)
                ndvi = np.where(check, (nir - red) / (nir + red), -999)
                dictionnaire_indice["ndvi"] = ndvi
                self.tableauindice.addItem('NDVI - Normalized Difference Vegetation Index')
                with rasterio.open(os.path.join(rep_s2_indice, "ndvi.tif"), "w", **profile) as dst:
                    dst.write(ndvi, 1)
                # Calcul NDWI
                check = np.logical_and((np.logical_or(green > 0, nir > 0)), green != -999, nir != -999)
                ndwi = np.where(check, (green - nir) / (green + nir), -999)
                dictionnaire_indice["ndwi"] = ndwi
                self.tableauindice.addItem('NDWI - Normalized Difference Water Index')
                with rasterio.open(os.path.join(rep_s2_indice, "ndwi.tif"), "w", **profile) as dst:
                    dst.write(ndwi, 1)
                # Calcul du RE-NDWI (red-edge ndwi) on utilise la bande du RE au lieu de la bande du PIR
                check = np.logical_and((np.logical_or(green > 0, re > 0)), green != -999, re != -999)
                re_ndwi = np.where(check, (green - re) / (green + re), -999)
                dictionnaire_indice["re_ndwi"] = re_ndwi
                self.tableauindice.addItem('RE-NDWI - Red-Edge Normalized Difference Water Index')
                with rasterio.open(os.path.join(rep_s2_indice, "re_ndwi.tif"), "w", **profile) as dst:
                    dst.write(re_ndwi, 1)
                ## Calcul NDII = detection des stress eventuels
                check = np.logical_and((np.logical_or(nir > 0, b11 > 0)), nir != -999, b11 != -999)
                ndii = np.where(check, (nir - b11) / (nir + b11), -999)
                dictionnaire_indice["ndii"] = ndii
                self.tableauindice.addItem('NDII - Normalized Difference Infrared Index')
                with rasterio.open(os.path.join(rep_s2_indice, "ndii.tif"), "w", **profile) as dst:
                    dst.write(ndii, 1)
                ## Calcul MSI
                check = np.logical_and((np.logical_not((nir == 0))), nir != -999, b11 != -999)
                msi = np.where(check, (b11 / nir), -999)
                dictionnaire_indice["msi"] = msi
                self.tableauindice.addItem('MSI - Moisture Stress Index')
                with rasterio.open(os.path.join(rep_s2_indice, "msi.tif"), "w", **profile) as dst:
                    dst.write(msi, 1)
                # Calcul de s2rep = red-edge position
                np.seterr(all="ignore");
                verif = np.logical_not((b6 - re)== 0)
                verif2 = np.logical_and(b7 != -999, red != -999, re != -999)
                check = np.logical_and(verif, verif2)
                s2rep = np.where(check, (705 + 35 * (0.5 * (b7 + red) - re)/(b6 - re)), -999)
                dictionnaire_indice["s2rep"] = s2rep
                self.tableauindice.addItem('S2REP - Red-Edge position')
                with rasterio.open(os.path.join(rep_s2_indice, "s2rep.tif"), "w", **profile) as dst:
                    dst.write(s2rep, 1)
                # Calcul du PSSR
                check = np.logical_and((np.logical_not((red == 0))), nir != -999, red != -999)
                pssr = np.where(check, (nir/red), -999)
                dictionnaire_indice["pssr"] = pssr
                self.tableauindice.addItem('PSSR - Pigment Specific Simple Ratio')
                with rasterio.open(os.path.join(rep_s2_indice, "pssr.tif"), "w", **profile) as dst:
                    dst.write(pssr, 1)
                # Calcul de ARVI = comme ndvi mais plus resistant aux aerosols
                verif = np.logical_not(nir -((2*red)-blue) == 0)
                verif2 = np.logical_and(nir != -999, red != -999, blue != -999)
                check = np.logical_and(verif, verif2)
                arvi = np.where(check, ((nir - (2*red)-blue)/(nir + (2*red)-blue)), -999)
                dictionnaire_indice["arvi"] = arvi
                self.tableauindice.addItem('ARVI - Aerosol Resistant Vegetation Index')
                with rasterio.open(os.path.join(rep_s2_indice, "arvi.tif"), "w", **profile) as dst:
                    dst.write(arvi, 1)
                # Calcul du PSRI = plant senescence reflectance index
                verif = np.logical_not(re == 0)
                verif2 = np.logical_and(red != -999, re != -999, blue != -999)
                check = np.logical_and(verif, verif2)
                psri = np.where(check, ((red - blue) / re), -999)
                dictionnaire_indice["psri"] = psri
                self.tableauindice.addItem('PSRI - Plant Senescence Reflectance Index')
                with rasterio.open(os.path.join(rep_s2_indice, "psri.tif"), "w", **profile) as dst:
                    dst.write(psri, 1)
                # Calcul de CRI2 = carotenoid reflectance index 2
                check = np.logical_and((np.logical_and ((blue !=0), (re != 0))), blue != -999, re != -999)
                cri2 = np.where(check, ((1/blue) - (1/re)), -999)
                dictionnaire_indice["cri2"] = cri2
                self.tableauindice.addItem('CRI2 - Carotenoid Reflectance Index 2')
                with rasterio.open(os.path.join(rep_s2_indice, "cri2.tif"), "w", **profile) as dst:
                    dst.write(cri2, 1)
                #Calcul de CRI1
                check = np.logical_and((np.logical_and ((blue > 0), (green > 0))), blue != -999, green != -999)
                cri1 = np.where(check, ((1/blue)-(1/green)), -999)
                dictionnaire_indice["cri1"] = cri1
                self.tableauindice.addItem('CRI1 - Carotenoid Reflectance Index 1')
                with rasterio.open(os.path.join(rep_s2_indice, "cri1.tif"), "w", **profile) as dst:
                    dst.write(cri1, 1)
                # Calcul de CHL-RED-EDGE = chlorophylle red edge
                check = np.logical_and((np.logical_not(nir == 0)), re != -999, nir != -999)
                chl_re = np.where(check, (re/nir), -999)
                dictionnaire_indice["chl_re"] = chl_re
                self.tableauindice.addItem('CHL-RE - Chlorophyll Red-Edge')
                with rasterio.open(os.path.join(rep_s2_indice, "chl_re.tif"), "w", **profile) as dst:
                    dst.write(chl_re, 1)
                #Calcul ARI2 = anthocyanin reflectance index
                verif = np.logical_and((blue > 0), (green > 0))
                verif2 = np.logical_and(nir != -999, blue != -999, green != -999)    
                check = np.logical_and(verif, verif2)
                ari2 = np.where(check, ((nir/blue)-(nir/green)), -999)
                dictionnaire_indice["ari2"] = ari2
                self.tableauindice.addItem('ARI2 - Anthocyanin Reflectance Index')
                with rasterio.open(os.path.join(rep_s2_indice, "ari2.tif"), "w", **profile) as dst:
                    dst.write(ari2, 1)
                #Calcul de EVI = enhanced vegetation index
                check = np.logical_and((np.logical_not((nir + 2.4*red +1)==0)), nir != -999, red != -999)
                evi = np.where(check, (2.5 * (nir - red)/(nir + 2.4*red +1)), -999)
                dictionnaire_indice["evi"] = evi
                self.tableauindice.addItem('EVI - Enhance Vegetation Index')
                with rasterio.open(os.path.join(rep_s2_indice, "evi.tif"), "w", **profile) as dst:
                    dst.write(evi, 1)
                #Calcul de GNDVI = green normalized vegetation index
                check = np.logical_and((np.logical_not ((nir + green)==0)), nir != -999, green != -999)
                gndvi = np.where(check, ((nir - green)/(nir + green)), -999)
                dictionnaire_indice["gndvi"] = gndvi
                self.tableauindice.addItem('GNDVI - Green Normalized Vegetation Index')
                with rasterio.open(os.path.join(rep_s2_indice, "gndvi.tif"), "w", **profile) as dst:
                    dst.write(gndvi, 1)
                #Calcul de SAVI (soil adjusted vegetation index)
                check = np.logical_and((np.logical_not((nir + red + 0.5) == 0)), nir != -999, red != -999)
                savi = np.where(check, (((nir - red)/(nir + red + 0.5)*1.5)), -999)
                dictionnaire_indice["savi"] = savi
                self.tableauindice.addItem('SAVI - Soil Adjusted Vegetation Index')
                with rasterio.open(os.path.join(rep_s2_indice, "savi.tif"), "w", **profile) as dst:
                    dst.write(savi, 1)
                #Calcul de CGI (chlorophyll green index)
                check = np.logical_and((np.logical_not(green == 0)), nir != -999, green != -999)
                chl_green = np.where(check, (nir/green), -999)
                dictionnaire_indice["chl_green"] = chl_green
                self.tableauindice.addItem('CHL_GREEN - Chlorophyll Green Index')
                with rasterio.open(os.path.join(rep_s2_indice, "chl_green"), "w", **profile) as dst:
                    dst.write(chl_green, 1)
                #Calcul CVI (chlorophyll vegetation index)
                verif = np.logical_not(green == 0)
                verif2 = np.logical_and(nir != -999, red != -999, green != -999)
                check = np.logical_and(verif, verif2)
                cvi = np.where(check, ((nir*red)/(green* green)), -999)
                dictionnaire_indice['cvi'] = cvi
                self.tableauindice.addItem('CVI - Chlorophyll Vegetation Index')
                with rasterio.open(os.path.join(rep_s2_indice, "cvi.tif"), "w", **profile) as dst:
                    dst.write(cvi, 1)

        elif self.landsat.checkState()>0:
            self.tableauindice.clear()
            dossier = str(self.dossier_image.text())
            os.chdir(str(dossier))
            for doss in os.listdir('.'):
                rep_l8_pretraitement = str(self.dossier_image.text()) +'\\'+ str(doss)  + '\Pretraitement'
                rep_l8_indice = str(self.dossier_image.text()) +'\\'+ str(doss) +'\Indices'
                dictionnaire_indice ={}
                liste_mask = glob(os.path.join(rep_l8_pretraitement, "*.tif"))
                with rasterio.open([val for val in liste_mask if "B2" in val][0]) as src:
                    profile = src.profile
                    blue = src.read(1)
                with rasterio.open([val for val in liste_mask if "B3" in val][0]) as src:
                    green = src.read(1)
                with rasterio.open([val for val in liste_mask if "B4" in val][0]) as src:
                    red = src.read(1)
                with rasterio.open([val for val in liste_mask if "B5" in val][0]) as src:
                    nir = src.read(1)
                with rasterio.open([val for val in liste_mask if "B6" in val][0]) as src:
                    swir1 = src.read(1)
                with rasterio.open([val for val in liste_mask if "B11" in val][0]) as src:
                    band11 = src.read(1)
                profile["dtype"] = rasterio.dtypes.float32
                # Calcul NDVI
                check = np.logical_and((np.logical_or(red > 0, nir > 0)), nir != -999, red != -999)
                ndvi = np.where(check, (nir - red) / (nir + red), -999)
                dictionnaire_indice["ndvi"] = ndvi
                self.tableauindice.addItem('NDVI - Normalized Difference Vegetation Index')
                with rasterio.open(os.path.join(rep_l8_indice, "ndvi.tif"), "w", **profile) as dst:
                    dst.write(ndvi, 1)
                # Calcul NDWI
                check = np.logical_and((np.logical_or(green > 0, nir > 0)), nir != -999, green != -999)
                ndwi = np.where(check, (green - nir) / (green + nir), -999)
                dictionnaire_indice["ndwi"] = ndwi
                self.tableauindice.addItem('NDWI - Normalized Difference Water Index')
                with rasterio.open(os.path.join(rep_l8_indice, "ndwi.tif"), "w", **profile) as dst:
                    dst.write(ndwi, 1)
                # Calcul du PSSR = pigment specific simple ratio
                check = np.logical_and((np.logical_not((red == 0))), nir != -999, red != -999)
                pssr = np.where(check, (nir/red), -999)
                dictionnaire_indice["pssr"] = pssr
                self.tableauindice.addItem('PSSR - Pigment Specific Simple Ratio')
                with rasterio.open(os.path.join(rep_l8_indice, "pssr.tif"), "w", **profile) as dst:
                    dst.write(pssr, 1)
                #Calcul CRI1 (carotenoid reflectance index 1)
                check = np.logical_and((np.logical_and((blue != 0), (green != 0))), blue != -999, green != -999)
                cri1 = np.where(check, ((1/blue)-(1/green)), -999)
                dictionnaire_indice["cri1"] = cri1
                self.tableauindice.addItem('CRI1 - Carotenoid Reflectance Index 1')
                with rasterio.open(os.path.join(rep_l8_indice, "cri1.tif"), "w", **profile) as dst:
                    dst.write(cri1, 1)
                #Calcul ARI2 = anthocyanin reflectance index
                verif = np.logical_and((blue != 0), (green != 0))
                verif2 = np.logical_and(red != -999, blue != -999, green != -999)
                check = np.logical_and(verif, verif2)
                ari2= np.where(check, ((red/blue) - (red/green)), -999)
                dictionnaire_indice["ari2"] = ari2
                self.tableauindice.addItem('ARI2 - Anthocyanin Reflectance Index')
                with rasterio.open(os.path.join(rep_l8_indice, "ari2.tif"), "w", **profile) as dst:
                    dst.write(ari2, 1)
                # Calcul de EVI = enhanced vegetation index
                verif = np.logical_not((nir + (swir1*red) - (7.5*blue)+1) == 0)
                verif2 = np.logical_and(nir != -999, red != -999, swir1 != -999)
                verif3 = np.logical_and(verif2,  blue != -999)
                check = np.logical_and(verif, verif3)
                evi = np.where(check, ((2.5*(nir - red))/(nir + (swir1*red) - (7.5*blue)+1)), -999)
                dictionnaire_indice["evi"] = evi
                self.tableauindice.addItem('EVI - Enhance Vegetation Index')
                with rasterio.open(os.path.join(rep_l8_indice, "evi.tif"), "w", **profile) as dst:
                    dst.write(evi, 1)
                # Calcul GNDVI (green ndvi)
                check = np.logical_and((np.logical_not (nir + green == 0)), nir != -999, green != -999)
                gndvi = np.where(check, ((nir - green)/(nir + green)), -999)
                dictionnaire_indice["gndvi"] = gndvi
                self.tableauindice.addItem('GNDVI - Green Normalized Vegetation Index')
                with rasterio.open(os.path.join(rep_l8_indice, "gndvi.tif"), "w", **profile) as dst:
                    dst.write(gndvi, 1)
                # Calcul de SAVI
                check = np.logical_and((np.logical_and(nir > 0, red > 0)), nir != -999, red != -999)
                savi = np.where(check, (((nir - red)/(nir + red + 0.5))*1.5), -999)
                dictionnaire_indice["savi"] = savi
                self.tableauindice.addItem('SAVI - Soil Adjusted Vegetation Index')
                with rasterio.open(os.path.join(rep_l8_indice, "savi.tif"), "w", **profile) as dst:
                    dst.write(savi, 1) 
                # Calcul de NDMI = normalized difference moisture index
                check = np.logical_and((np.logical_not((nir + swir1) == 0)), nir != -999, swir1 != -999)
                ndmi = np.where(check, ((nir - swir1)/(nir + swir1)), -999)
                dictionnaire_indice["ndmi"] = ndmi
                self.tableauindice.addItem('NDMI - Normalized Difference Moisture Index')
                with rasterio.open(os.path.join(rep_l8_indice, "ndmi.tif"), "w", **profile) as dst:
                    dst.write(ndmi, 1)
                # Calcul de chlorophyll green index
                check = np.logical_and((np.logical_not(green == 0)) , nir != -999, green != -999)
                chl_green = np.where(check, ((nir/green)-1), -999)
                dictionnaire_indice["chl_green"] = chl_green
                self.tableauindice.addItem('CHL_GREEN - Chlorophyll Green Index')
                with rasterio.open(os.path.join(rep_l8_indice, "chl_green.tif"), "w", **profile) as dst:
                    dst.write(chl_green, 1)
                # Calcul CVI = chlorophyll vegetation index
                verif = np.logical_not(green == 0)
                verif2 = np.logical_and(nir != -999, red != -999, green != -999)
                check = np.logical_and(verif, verif2)
                cvi = np.where (check, ((nir*red)/(green*green)), -999)
                dictionnaire_indice["cvi"] = cvi
                self.tableauindice.addItem('CVI - Chlorophyll Vegetation Index')
                with rasterio.open(os.path.join(rep_l8_indice, "cvi.tif"), "w", **profile) as dst:
                    dst.write(cvi, 1)

                        
    def reechantillonnage(self):
        if self.sentinel.checkState()>0:
            dossier = self.dossier_image.text()
            os.chdir(str(dossier))
            for doss in os.listdir('.'):
                rep_s2_indice = str(self.dossier_image.text()) +'\\'+ str(doss) +'\\GRANULE\\Indices'
                rep_s2_indice_1m = str(rep_s2_indice) + "/indice_1m"
                # Liste de toutes les images d'indice finissant par tif
                liste_fichier = glob(os.path.join(rep_s2_indice, "*.tif"))
                liste_indice_1m = []
                for img in liste_fichier:
                    nom_img = os.path.splitext(os.path.basename(img))[0]
                    img_indice = os.path.join(rep_s2_indice_1m, "%s_1m.tif" % nom_img)    
                    gdal.Warp(img_indice, img, xRes=1, yRes=1) # Réchantillonage à 1m, méthode nearest
                    liste_indice_1m.append(img_indice)

        elif self.landsat.checkState()>0:
            dossier = self.dossier_image.text()
            os.chdir(str(dossier))
            for doss in os.listdir('.'):
                rep_l8_indice = str(self.dossier_image.text()) +'\\'+ str(doss) +'\Indices'
                rep_l8_indice_1m = rep_l8_indice + '\\indice_1m'
                # Liste de toutes les images d'indice finissant par tif
                liste_fichier = glob(os.path.join(rep_l8_indice, "*.tif"))
                liste_indice_1m = []
                for img in liste_fichier:
                    nom_img = os.path.splitext(os.path.basename(img))[0]
                    img_indice = os.path.join(rep_l8_indice_1m, "%s_1m.tif" % nom_img)    
                    gdal.Warp(img_indice, img, xRes=1, yRes=1) # Réchantillonage à 1m, méthode nearest
                    liste_indice_1m.append(img_indice)
            

    def stat_zonale(self):
        if self.stat.checkState()>0:
            if self.sentinel.checkState()>0:
                dossier = self.dossier_image.text()
                os.chdir(str(dossier))
                liste_concat = []
                for doss in os.listdir('.'):
                    rep_s2_pretraitement = str(self.dossier_image.text()) + '\\' + str(doss) + '\\GRANULE\\Pretraitement'
                    rep_s2_indice = str(self.dossier_image.text()) +'\\'+ str(doss) +'\\GRANULE\\Indices'
                    rep_s2_indice_1m = str(rep_s2_indice) + "/indice_1m"

                    liste_image_indice = glob(os.path.join(rep_s2_indice, "*.tif"))
                    os.chdir(str(rep_s2_pretraitement))
                    shapefile = "parcelle.shp"
                    with fiona.open(shapefile) as src:
                        ID_dict = dict()
                        c = 1
                        nom_ligne = []
                        for i in src:
                            ID_dict[c] = i['properties']['ID']
                            c = c + 1
                            nom_ligne.append(i['properties']['ID'])
                    stat = dict()
                    for index in liste_image_indice:
                        #on récupére le nom de l'indice sans l'extension\
                        indice = os.path.splitext(os.path.basename(index))
                        stats = rasterstats.zonal_stats(shapefile, index, stats= ['mean', 'median', 'std'], nodata = -999,  all_touched=False)
                        stat[indice[0]]=stats
                    #on récupère le nom des parcelles
                    with fiona.open(shapefile) as src:
                        ID_list = []
                        for i in src:
                            c = i['properties']['ID']
                            ID_list.append(i['properties']['ID'])
                    moyenne = dict()
                    std = dict()
                    mediane = dict()
                    for key in stat.keys():
                        for i in range (0, len(ID_list)):
                            parcelle = ID_list[i]
                            moyenne[parcelle, key] = stat[key][i]['mean']
                            std[parcelle, key] = stat[key][i]['std']
                            mediane[parcelle, key] = stat[key][i]['median']
                    df_mean = pd.Series(moyenne)
                    df_std = pd.Series(std)
                    df_mediane = pd.Series(mediane)
                    df_mean = df_mean.unstack()
                    df_std = df_std.unstack()
                    df_mediane = df_mediane.unstack()
                    
                    ###creation de liste pour attribue une colonne selon le type de stat //moy, std, med
                    liste_mean = []
                    liste_std = []
                    liste_med = []
                    liste_date = []
                    for i in range(0, df_mean.shape[0]):
                        liste_mean.append('moyenne')
                        liste_date.append(doss)
                    for i in range(0, df_std.shape[0]):
                        liste_std.append('ecart-type')
                        liste_date.append(doss)
                    for i in range (0, df_mediane.shape[0]):
                        liste_med.append('mediane')
                        liste_date.append(doss)
                    ##on les convertit en dataframe
                    col_mean = pd.DataFrame({'Data' : liste_mean})
                    col_std = pd.DataFrame({'Data' : liste_std})
                    col_med = pd.DataFrame({'Data' : liste_med})
                    col = pd.concat([col_mean, col_std, col_med], ignore_index = True)
                    #print(col)
                    #print(" ")
                    ###on les concat pas à la suite en ligne mais à la suite en colonne
                    df_mean['Parcelle'] = df_mean.index
                    df_std['Parcelle'] = df_std.index
                    df_mediane['Parcelle'] = df_mediane.index
                    df_stat = pd.concat([df_mean, df_std, df_mediane], ignore_index = True)
                    cols = df_stat.columns.tolist()
                    cols = cols[-1:] + cols[:-1]
                    df_stat = df_stat[cols]
                    #print(df_stat)
                    #print(" ")
                    ###je concatene en ligne les trois df
                    concat = pd.concat([col, df_stat], axis = 1)
                    #print(concat)
                    #print(" ")
                    ###je cree un dataframe de la date avec liste_date et ensuite je le concatene en ligne avec concat
                    df_date = pd.DataFrame({'Date' : liste_date})
                    concat_stat = pd.concat([df_date, concat], axis = 1)
                    #print(concat_stat)
                    #print(" ")
                    liste_concat.append(concat_stat)
                    
                dossier = self.dossier_output.text()
                os.chdir(str(dossier))
                concat_final = pd.concat(liste_concat, ignore_index = True)
                print(concat_final)
                writer = pd.ExcelWriter('statistique_zonal.xlsx', engine='xlsxwriter')
                concat_final.to_excel(writer)
                writer.save()
                
            elif self.landsat.checkState()>0:
                dossier = self.dossier_image.text()
                os.chdir(str(dossier))
                liste_concat = []
                for doss in os.listdir('.'):
                    rep_l8_pretraitement = str(self.dossier_image.text()) +'\\'+ str(doss)  + '\Pretraitement'
                    rep_l8_indice = str(self.dossier_image.text()) +'\\'+ str(doss) +'\Indices'
                    rep_l8_indice_1m = str(rep_l8_indice) + "\indice_1m"
                    os.chdir(str(rep_l8_pretraitement))
                    shapefile = 'parcelle.shp'
                    liste_image_indice = glob(os.path.join(str(rep_l8_indice_1m), "*.tif"))
                    with fiona.open(shapefile) as src:
                        ID_dict = dict()
                        c = 1
                        nom_ligne = []
                        for i in src:
                            ID_dict[c] = i['properties']['ID']
                            c = c + 1
                            nom_ligne.append(i['properties']['ID'])
                    stat = dict()
                    for index in liste_image_indice:
                        #on récupére le nom de l'indice sans l'extension\
                        indice = os.path.splitext(os.path.basename(index))
                        stats = rasterstats.zonal_stats(shapefile, index, stats= ['mean', 'median', 'std'], nodata = -999,  all_touched=False)
                        stat[indice[0]]=stats
                    #on récupère le nom des parcelles
                    with fiona.open(shapefile) as src:
                        ID_list = []
                        for i in src:
                            c = i['properties']['ID']
                            ID_list.append(i['properties']['ID'])
                    moyenne = dict()
                    std = dict()
                    mediane = dict()
                    for key in stat.keys():
                        for i in range (0, len(ID_list)):
                            parcelle = ID_list[i]
                            moyenne[parcelle, key] = stat[key][i]['mean']
                            std[parcelle, key] = stat[key][i]['std']
                            mediane[parcelle, key] = stat[key][i]['median']
                    df_mean = pd.Series(moyenne)
                    df_std = pd.Series(std)
                    df_mediane = pd.Series(mediane)
                    df_mean = df_mean.unstack()
                    df_std = df_std.unstack()
                    df_mediane = df_mediane.unstack()
        
                    ###creation de liste pour attribue une colonne selon le type de stat //moy, std, med
                    liste_mean = []
                    liste_std = []
                    liste_med = []
                    liste_date = []
                    for i in range(0, df_mean.shape[0]):
                        liste_mean.append('moyenne')
                        liste_date.append(doss)
                    for i in range(0, df_std.shape[0]):
                        liste_std.append('ecart-type')
                        liste_date.append(doss)
                    for i in range (0, df_mediane.shape[0]):
                        liste_med.append('mediane')
                        liste_date.append(doss)
                    ##on les convertit en dataframe
                    col_mean = pd.DataFrame({'Data' : liste_mean})
                    col_std = pd.DataFrame({'Data' : liste_std})
                    col_med = pd.DataFrame({'Data' : liste_med})
                    col = pd.concat([col_mean, col_std, col_med], ignore_index = True)
                    #print(col)
                    #print(" ")
                    ###on les concat pas à la suite en ligne mais à la suite en colonne
                    df_mean['Parcelle'] = df_mean.index
                    df_std['Parcelle'] = df_std.index
                    df_mediane['Parcelle'] = df_mediane.index
                    df_stat = pd.concat([df_mean, df_std, df_mediane], ignore_index = True)
                    cols = df_stat.columns.tolist()
                    cols = cols[-1:] + cols[:-1]
                    df_stat = df_stat[cols]
                    #print(df_stat)
                    #print(" ")
                    ###je concatene en ligne les trois df
                    concat = pd.concat([col, df_stat], axis = 1)
                    #print(concat)
                    #print(" ")
                    ###je cree un dataframe de la date avec liste_date et ensuite je le concatene en ligne avec concat
                    df_date = pd.DataFrame({'Date' : liste_date})
                    concat_stat = pd.concat([df_date, concat], axis = 1)
                    #print(concat_stat)
                    #print(" ")
                    liste_concat.append(concat_stat)
                    
                dossier = self.dossier_output.text()
                os.chdir(str(dossier))
                concat_final = pd.concat(liste_concat, ignore_index = True)
                print(concat_final)
                writer = pd.ExcelWriter('statistique_zonal.xlsx', engine='xlsxwriter')
                concat_final.to_excel(writer)
                writer.save()
                
        elif self.pix.checkState()>0:
            if self.sentinel.checkState()>0:
                dossier = self.dossier_image.text()
                os.chdir(str(dossier))
                liste_concat = []
                for doss in os.listdir('.'):
                    rep_s2_pretraitement = str(self.dossier_image.text()) + '\\' + str(doss) + '\\GRANULE\\Pretraitement'
                    rep_s2_indice = str(self.dossier_image.text()) +'\\'+ str(doss) +'\\GRANULE\\Indices'
                    rep_s2_indice_1m = str(rep_s2_indice) + "/indice_1m"
                    os.chdir(rep_s2_pretraitement)
                    shapefile = "parcelle.shp"
                    liste_image_indice = glob(os.path.join(rep_s2_indice, "*.tif"))
                    dico_pixel = {}
                    with fiona.open(shapefile) as src:
                        # On traite les géométries du shapefile une par une
                        for parcelle in src:
                            dico_indice_pixel = {}
                            nom_parcelle = parcelle['properties']['ID']
                            for index in liste_image_indice:
                                # Nom de l'indice
                                indice = os.path.splitext(os.path.basename(index))[0]
                                # rasterstats.zonal_stats renvoie une liste mais ici il n'y a qu'un élément (une seule géométrie)
                                # Si tu mets all_touched=True, tu auras des pixels de bordure qui vont se retrouver dans 2 parcelles
                                stats = rasterstats.zonal_stats(parcelle, index,
                                                                stats= ['mean'],
                                                                nodata = -999,  all_touched=False,
                                                                raster_out=True)[0]
                                # Les valeurs des pixels sont mis dans un array à une dimension
                                dico_indice_pixel[indice] =  stats["mini_raster_array"].data.flatten()
                            # On regroupe les données dans un dixtionnaire par indice
                            dico_pixel[nom_parcelle] = dico_indice_pixel

                    # Petite précaution pour le notebook.
                    # On commence par supprimer le DataFrame s'il existe,
                    # sinon on va rajouter des données dans celui qui est déjà en mémoire !
                    try:
                        del df_parc_indice
                    except:
                        pass
                    # Un test facultatif pour vérifier que le DataFrame final contient toutes les lignes.
                    taille_final = 0
                    for parcelle in sorted(dico_pixel.keys()): # tri alphabétique des parcelles facultatif
                        df_parc = pd.DataFrame(dico_pixel[parcelle])
                        # On remplace les valeurs -999 par Nan
                        df_parc.replace([-999], np.nan, inplace=True)
                        # On supprime toutes les lignes ne contenant que des Nan
                        df_parc.dropna(how="all", axis=0, inplace=True)
                        # On rajoute le nom de la parcelle comme colonne
                        df_parc['Parcelle'] = [parcelle]*df_parc.shape[0]
                        # Calcul du nombre de ligne
                        taille_final += df_parc.shape[0]
                        try: # A partir de la deuxième parcelle df_parc_indice existe : on peut lui rajouter des valeurs
                            df_parc_indice = df_parc_indice.append(df_parc)
                        except: # Pour la première parcelle df_parc_indice n'exite pas encore : on le crée
                            df_parc_indice = df_parc
                            
                    ###creation de liste pour la date
                    liste_date = []
                    liste_index = []
                    for i in range(0, df_parc_indice.shape[0]):
                        liste_index.append(i)
                        liste_date.append(doss)
                    ###je cree un dataframe de la date avec liste_date et ensuite je le concatene en ligne avec concat
                    df_parc_indice['Index'] = liste_index
                    df_parc_indice2 = df_parc_indice.set_index(['Index'])
                    print(df_parc_indice2)
                    print(" ")
                            
                    df_date = pd.DataFrame({'Date' : liste_date})
                    print(df_date)
                    concat_stat = pd.concat([df_date, df_parc_indice2], axis = 1)
                    cols = concat_stat.columns.tolist()
                    cols = cols[-1:] + cols[:-1]
                    concat_stat = concat_stat[cols]
                    print(concat_stat)
                    print(" ")
                    liste_concat.append(concat_stat)
                    
                dossier = self.dossier_output.text()
                os.chdir(str(dossier))
                concat_final = pd.concat(liste_concat, ignore_index = True)
                print(concat_final)
                writer = pd.ExcelWriter('valeur_pixels.xlsx', engine='xlsxwriter')
                concat_final.to_excel(writer)
                writer.save

            elif self.landsat.checkState()>0:
                dossier = self.dossier_image.text()
                os.chdir(str(dossier))
                liste_concat = []
                for doss in os.listdir('.'):
                    rep_l8_pretraitement = str(self.dossier_image.text()) +'\\'+ str(doss)  + '\Pretraitement'
                    os.chdir(str(rep_l8_pretraitement))
                    shapefile = 'parcelle.shp'
                    rep_l8_indice = str(self.dossier_image.text()) +'\\'+ str(doss) +'\Indices'
                    liste_image_indice = glob(os.path.join(rep_l8_indice, "*.tif"))
                    dico_pixel = {}
                    with fiona.open(shapefile) as src:
                        # On traite les géométries du shapefile une par une
                        for parcelle in src:
                            dico_indice_pixel = {}
                            nom_parcelle = parcelle['properties']['ID']
                            for index in liste_image_indice:
                                # Nom de l'indice
                                indice = os.path.splitext(os.path.basename(index))[0]
                                # rasterstats.zonal_stats renvoie une liste mais ici il n'y a qu'un élément (une seule géométrie)
                                # Si tu mets all_touched=True, tu auras des pixels de bordure qui vont se retrouver dans 2 parcelles
                                stats = rasterstats.zonal_stats(parcelle, index,
                                                                stats= ['mean'],
                                                                nodata = -999,  all_touched=False,
                                                                raster_out=True)[0]
                                # Les valeurs des pixels sont mis dans un array à une dimension
                                dico_indice_pixel[indice] =  stats["mini_raster_array"].data.flatten()
                            # On regroupe les données dans un dixtionnaire par indice
                            dico_pixel[nom_parcelle] = dico_indice_pixel

                    # Petite précaution pour le notebook.
                    # On commence par supprimer le DataFrame s'il existe,
                    # sinon on va rajouter des données dans celui qui est déjà en mémoire !
                    try:
                        del df_parc_indice
                    except:
                        pass
                    # Un test facultatif pour vérifier que le DataFrame final contient toutes les lignes.
                    taille_final = 0
                    for parcelle in sorted(dico_pixel.keys()): # tri alphabétique des parcelles facultatif
                        df_parc = pd.DataFrame(dico_pixel[parcelle])
                        # On remplace les valeurs -999 par Nan
                        df_parc.replace([-999], np.nan, inplace=True)
                        # On supprime toutes les lignes ne contenant que des Nan
                        df_parc.dropna(how="all", axis=0, inplace=True)
                        # On rajoute le nom de la parcelle comme colonne
                        df_parc['Parcelle'] = [parcelle]*df_parc.shape[0]
                        # Calcul du nombre de ligne
                        taille_final += df_parc.shape[0]
                        try: # A partir de la deuxième parcelle df_parc_indice existe : on peut lui rajouter des valeurs
                            df_parc_indice = df_parc_indice.append(df_parc)
                        except: # Pour la première parcelle df_parc_indice n'exite pas encore : on le crée
                            df_parc_indice = df_parc
                            
                    ###creation de liste pour la date
                    liste_date = []
                    liste_index = []
                    for i in range(0, df_parc_indice.shape[0]):
                        liste_index.append(i)
                        liste_date.append(doss)
                    ###je cree un dataframe de la date avec liste_date et ensuite je le concatene en ligne avec concat
                    df_parc_indice['Index'] = liste_index
                    df_parc_indice2 = df_parc_indice.set_index(['Index'])
                    print(df_parc_indice2)
                    print(" ")
                            
                    df_date = pd.DataFrame({'Date' : liste_date})
                    print(df_date)
                    concat_stat = pd.concat([df_date, df_parc_indice2], axis = 1)
                    cols = concat_stat.columns.tolist()
                    cols = cols[-1:] + cols[:-1]
                    concat_stat = concat_stat[cols]
                    print(concat_stat)
                    print(" ")
                    liste_concat.append(concat_stat)
                    
                dossier = self.dossier_output.text()
                os.chdir(str(dossier))
                concat_final = pd.concat(liste_concat, ignore_index = True)
                print(concat_final)
                writer = pd.ExcelWriter('valeur_pixels.xlsx', engine='xlsxwriter')
                concat_final.to_excel(writer)
                writer.save
                                                        
    def merge_image(self):
        dossier_output = self.dossier_output_2.text()
        rep_s2_pretraitement = str(dossier_output) + '\\GRANULE\\Pretraitement'                                            
        dossier_coord = self.cd_coord.text()
        fichier = pd.read_excel(str(dossier_coord))
        #on recup latitude longitude
        lat = fichier.Latitude[0]
        lon = fichier.Longitude[0]
        #conversion coord decimal
        deg_lat = float(lat[0:2])
        min_lat = float(lat [3:5])
        sec_lat = float(lat[6:10])
        min_lat_mini = min_lat - 1
        min_lat_maxi = min_lat + 1
        xmin = deg_lat + min_lat_mini/60 + sec_lat/(60*60)
        xmax = deg_lat + min_lat_maxi/60 + sec_lat/(60*60)
        deg_lon = float(lon[0])
        min_lon = float(lon[2:4])
        sec_lon = float(lon[5:9])
        min_lon_mini = min_lon - 1
        min_lon_maxi = min_lon + 1
        if lon[11] == 'O':
            ymin = deg_lon + min_lon_mini/60 + sec_lon/(60*60)
            ymax = -(deg_lon + min_lon_maxi/60 + sec_lon/(60*60))
        else:
            ymin = deg_lon + min_lon_mini/60 + sec_lon/(60*60)
            ymax = deg_lon + min_lon_maxi/60 + sec_lon/(60*60)   
        lat1, lon1 = xmin, ymin
        lat2, lon2 = xmax, ymax
        rouge = str(self.dossier_output_rouge.text())
        image = gdal.Open(rouge)
        vert = str(self.dossier_output_vert.text())
        bleue = str(self.dossier_output_bleue.text())
        print(image.GetProjection()[588:593])
        if (image.GetProjection()[588:593]) == '32630':
            epsg_4326 = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs  ')
            epsg_32630 = pyproj.Proj('+proj=utm +zone=30 +datum=WGS84 +units=m +no_defs ')
            xmax, ymax = pyproj.transform(epsg_4326, epsg_32630, lon2, lat2)
            xmin, ymin = pyproj.transform(epsg_4326, epsg_32630, lon1, lat1)
            xmax, ymax, xmin, ymin = int(xmax), int(ymax), int(xmin), int(ymin)
            print(xmax, ymax, xmin, ymin)
        elif (image.GetProjection()[588:593]) == '32631':
            epsg_4326 = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs  ')
            epsg_32631 = pyproj.Proj('+proj=utm +zone=31 +datum=WGS84 +units=m +no_defs ')
            xmax, ymax = pyproj.transform(epsg_4326, epsg_32631, lon2, lat2)
            xmin, ymin = pyproj.transform(epsg_4326, epsg_32631, lon1, lat1)
            xmax, ymax, xmin, ymin = int(xmax), int(ymax), int(xmin), int(ymin)
            print(xmax, ymax, xmin, ymin)
        liste_fichier = [rouge, vert, bleue]
        liste_decoupe = []
        for img in liste_fichier:
            #Recuperation du nom de l'image sans l'extension
            nom_img = os.path.splitext(os.path.basename(img))[0]
            #Nouveau nom de l'image apres decoupe, au format tif, placee dans le bon repertoire
            img_pretraitement = os.path.join(str(str(dossier_output) + '\\GRANULE'), "decoup_%s.tif" % nom_img)
            liste_decoupe.append(img_pretraitement)
            # Decoupage de l'image selon l'emprise
            res = subprocess.Popen(["gdalwarp",
                                    "-te", str(xmin), str(ymin), str(xmax), str(ymax),
                                    "-tr", "10", "10",
                                    "-overwrite",
                                    img, img_pretraitement],
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE).communicate()
            #print("Résultat de la commande : ", res[0])
            #print("Erreur éventuelle de la commande : ", res[1])
            #print("")
        rouge = liste_decoupe[0]
        vert = liste_decoupe[1]
        bleue = liste_decoupe[2]
        output = os.path.join(str(str(dossier_output) + '\\GRANULE'), "merge.tif")
        gm = "C:/Users/colette.badourdine/Documents/STAGE/telechargements/WinPython-64bit-2.7.10.3/python-2.7.10.amd64/Scripts/gdal_merge.py"
        res2 = subprocess.Popen(['python', gm, '-separate', '-co', 'PHOTOMETRIC=RGB', '-o', output, rouge, vert, bleue],
                                stdin=None, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE, shell=True).communicate()
        print("Résultat de la commande : ", res[0])
        print("Erreur éventuelle de la commande : ", res[1])
        print("")
        ####alternative opencv
##        liste = [rouge, vert, bleu]
##        bandes = []
##        np.seterr(divide='ignore', invalid='ignore')
##        for img in liste:
##            with rasterio.open(img) as src:
##                band = src.read()
##                maxi = band.max()
##                mini = band.min()
##                band = ((band-mini)*255)/(maxi - mini)
##                band = band[0]
##                band = band.astype(np.uint8)
##                bandes.append(band)
##        img = cv2.merge((bandes[2], bandes[1], bandes[0]))###attention à bien mettre dans l'ordre bgr
##        cv2.imwrite('merge.png', img)
##        cv2.imshow('image', img)
##        cv2.waitKey(0)
##        cv2.destroyAllWindows()

    def visualisation(self):
        dossier_image = self.image_indice.text()
        os.chdir(str(dossier_image))
        image = self.liste_image.currentItem().text()
        nom_image = "%s.tif" % image
        bg = str(self.image_merge.text()) ###bg c'est l'image merge

        indice = gdal.Open(bg)
        print(indice.GetProjection()[588:593])
        if (indice.GetProjection()[588:593]) == '32630':
            # Définition de la projection
            projection = ccrs.UTM(30)
        elif (indice.GetProjection()[588:593]) == '32631':
            projection = ccrs.UTM(31)
        print(projection)

        with rasterio.open(bg) as src:
            meta = src.meta
            left_bg, bottom_bg, right_bg, top_bg = src.bounds
            # Normalisation (entre 0 et 1) des 3 bandes de l'image RGB
            im_bg = np.empty([meta['height'], meta['width'], meta['count']], dtype=meta['dtype'])
            for band in range(meta['count']):
                b = src.read(band+1)
                b_norm = (b - np.min(b)) / (np.max(b) - np.min(b))
                im_bg[:, :, band] = b_norm
        with rasterio.open(nom_image) as src:
            left_i, bottom_i, right_i, top_i = src.bounds
            ####on trouve le max
            band = src.read()
            #print(band[0])
            band = band[0]
            maxi = band.max()
            #print(maxi)
            ####on trouve le min
            band_list = band.tolist() #on transforme le ndarray initial en liste de liste
            liste_temp = []
            for j in band_list:
                for i in j:
                    if (i != -999):
                        liste_temp.append(i)
            mini = min(liste_temp)       
            #print(mini)
            band_255 = np.where((band[:, :] != -999), ((band[:,:]-mini)*255)/(maxi-mini), mini)
            #print(band_255)
            band_255 = band_255.astype(np.uint8)
            #print(band_255)
            
        item = self.comboBox_palette.currentText()
        print(item)
        # Une figure avec 3 sous-figures
        fig, (axe1) = plt.subplots(ncols=1, subplot_kw={'projection': projection})
        fig.set_figwidth(10)
        if item == "Normal":
            axe1.set_title('cmap = Normal'+ '\nIndice :' +str(image))
            axe1.set_extent([left_bg, right_bg, bottom_bg, top_bg], projection)
            axe1.imshow(exposure.adjust_log(im_bg, 2), origin='upper',
                        extent=[left_bg, right_bg, bottom_bg, top_bg])
            axe1.imshow(band_255, origin='upper',
                        extent=(left_i, right_i, bottom_i, top_i),
                        cmap='gray')
        else :
            axe1.set_title('cmap =' + str(item) + '\nIndice :'+ str(image))
            axe1.set_extent([left_bg, right_bg, bottom_bg, top_bg], projection)
            axe1.imshow(exposure.adjust_log(im_bg, 2), origin='upper',
                        extent=[left_bg, right_bg, bottom_bg, top_bg])
            axe1.imshow(band_255, origin='upper',
                        extent=(left_i, right_i, bottom_i, top_i),
                        cmap=str(item))

        # plt.savefig('cartopy.png', dpi=300)          
        item = self.comboBox_palette.currentText()
        figure, axe = plt.subplots(ncols = 1, subplot_kw={'projection': projection})
        figure.set_figwidth(10)
        if item == "Normal":
            axe.set_title('cmap = Normal'+ '\nIndice :' +str(image))
            axe.imshow(band_255, origin='upper',
                        extent=(left_i, right_i, bottom_i, top_i),
                        cmap='gray')
        else:
            axe.set_title('cmap = '+ str(item) + '\nIndice :' +str(image))
            axe.imshow(band_255, origin='upper',
                        extent=(left_i, right_i, bottom_i, top_i),
                        cmap=str(item))
        plt.show()
        
###############################################################################
################## Lancemennt du programme ####################################
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('toto'))
    main = Principal()
    main.show()
    sys.exit(app.exec_())
                         
                         
        

            
        

