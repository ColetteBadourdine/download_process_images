
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

import urllib3
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import certifi
import time
import datetime
from datetime import date
import json
from pprint import pprint
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

import zipfile

from PyQt4.QtGui import QApplication

from lib.gui import *

os = __import__('os')
gdal.UseExceptions()
np.seterr(divide='ignore', invalid='ignore')
# Début de l'interface graphique
class Principal(QWidget, Ui_Main):
    def __init__(self, parent=None):
        """Initialise la fenêtre"""
        super(QWidget, self).__init__(parent)
        self.setupUi(parent)

        ### sélectionner un dossier ##############
    def fenetre_ouverture_fichier_input(self):
        dossier_input = QFileDialog.getExistingDirectory(self, "Ouvrir un fichier", "\\Users\colette.badourdine\Documents")
        self.dossier_image.setText(dossier_input)
        os.chdir(str(dossier_input))
        self.liste_fichier.clear()
        self.liste_fichier_2.clear()
        for doss in os.listdir('.'):
            self.liste_fichier.addItem(doss)
            self.liste_fichier_2.addItem(doss)        

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
        fichier_rouge = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", str(self.dossier_output_2.text()+ "\\DATA"), "Image (*.tif)")
        self.dossier_output_rouge.setText(fichier_rouge)

    def fenetre_ouverture_bande_vert(self):
        fichier_vert = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", str(self.dossier_output_2.text()+ "\\DATA"), "Image (*.tif)")
        self.dossier_output_vert.setText(fichier_vert)

    def fenetre_ouverture_bande_bleue(self):
        fichier_bleue = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", str(self.dossier_output_2.text()+ "\\DATA"), "Image (*.tif)")
        self.dossier_output_bleue.setText(fichier_bleue)

    def fenetre_ouverture_dossier_merge(self):
        fichier_merge = QFileDialog.getExistingDirectory(self, "Ouvrir un fichier", "\\Users\colette.badourdine\Documents")
        self.dossier_output_2.setText(fichier_merge)

        ### liste fichier dispo ##############
    def listage_des_images(self):
        dossier_image = self.image_indice.text()
        os.chdir(str(dossier_image))
        self.liste_image.clear()
        listimage = glob(os.path.join(str(dossier_image), "*.tif"))
        for image in listimage:
            nom_image = os.path.splitext(os.path.basename(image))[0]
            self.liste_image.addItem(nom_image)
    
        ### Utiliser le fichier excel pour recuperer les coordonnees ##################
    def telechargement(self):
        global features_images
        global token
        global params
        login = str(self.login_2.text())
        password = str(self.password_2.text())
        print(login), print(password)
        #on recupere le token qui permet ensuite de s'authentifier sur le serveur 
        token =  requests.post("https://theia.cnes.fr/atdistrib/services/authenticate/",
                               data ={"ident": login,
                                      "pass": password},
                               verify = False).text
        print(token)
            
        #on cree une requete
        now = datetime.date.today()
        today = str(now.strftime("%Y-%m-%d"))
        print(today), print(type(today))
        lieu = str(self.localite.text())
        print(lieu), print(type(lieu))
        jour = self.jour.text()
        print(len(jour))
        if len(jour) == 1:
            jour = "0" + str(jour)
            print("jour : ", jour)
        mois = self.mois.text()
        if len(mois) ==  1:
            mois = "0" + str(mois)
            print("mois: ", mois)
        annee = self.annee.text()
        date = str(str(annee)+ "-" + str(mois) + "-" + str(jour))
        print(date), print(type(date))
        params = {"collection": "SENTINEL2",
                  "q": lieu,
                  #"lon": "-1.6",
                  #"lat":"48.11",
                  "startDate": date,
                  "completionDate": "%s" % today}
        print(params)
        #on lance la requete
        url = "https://theia.cnes.fr/atdistrib/resto2/api/collections/SENTINEL2/search.json"
        req = requests.get(url,
                           verify = False,
                           params=params)
        print(req)
        print(req.ok)
        if req.ok:
            list_images = json.loads(req.text)
            #pprint(list_images)
        else:
            print("Problème avec la requête.")
            QMessageBox.information(self, "Avertissement", self.trUtf8("Problème avec la requête"))

        #sauvegarde du fichier json en local
        with open('datas.json', 'w') as f:
            f.write(req.text)
        #affichage de quelques infos par image contenues dans le fichier json
        print("Nombre d'images correpondant à la requête : %d" % len(list_images["features"]))
        self.nb_total_image = len(list_images["features"])
        self.tableWidget.setRowCount(len(list_images["features"]))
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['NOM IMAGE', 'DATE ACQUISITION', 'CLOUD COVER', 'LIEN TELECHARGEMENT'])
        features_images = list_images["features"]
        #print("features_images :", features_images)
        i = 0
        for f in features_images:
            prod = f["properties"]["productIdentifier"]
            self.tableWidget.setItem(i, 0, QtGui.QTableWidgetItem(prod))
            cloudCover = f["properties"]["cloudCover"]
            nuage = str(cloudCover) + "%"
            self.tableWidget.setItem(i, 2, QtGui.QTableWidgetItem(nuage))
            feature_id = f["id"]
            completionDate = f["properties"]["completionDate"]
            self.tableWidget.setItem(i, 1, QtGui.QTableWidgetItem(completionDate))
            download = f["properties"]["services"]["download"]["url"]
            link = str(download)
            self.tableWidget.setItem(i, 3, QtGui.QTableWidgetItem(link))
            print("Pourcentage de nuages : %s %%" %cloudCover)
            print("Date : %s" % completionDate)
            print("Lien : %s" % download)
            print("")
            i = i + 1
    def clic_ok(self):
        global nom_dossier_saving
        numberImage, ask_user = QtGui.QInputDialog.getInt(self, "Quelle image voulez-vous télécharger?",
                                                          "Entrez le numéro de l'image :", value = self.variable_clic,
                                                          min = 1, max = self.nb_total_image,
                                                          step = 1)
        nom_dossier_saving = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier d'enregistrement de l'image", "\\Users\colette.badourdine\Documents")
        os.chdir(str(nom_dossier_saving))
        self.variable_clic = numberImage
        print("dans clic_ok: ", self.variable_clic)
        ###telechargement d'une image
        # Lien de l'image à télécharger
        lien = features_images[(self.variable_clic - 1)]["properties"]["services"]["download"]["url"]
        prod = str(features_images[(self.variable_clic - 1)]["properties"]["productIdentifier"])
        completionDate = features_images[(self.variable_clic - 1)]["properties"]["completionDate"]
        date_img_chargee = completionDate[:10]
        headers = {'Authorization': 'Bearer %s' % token,}
        params = (('issuerId', 'theia'),)
        img = requests.get(lien,
                           headers=headers,
                           params=params,
                           verify = False,
                           stream = True)
        if img.ok:
            total_size = int(img.headers.get('content-length', 0))
            print("Taille de l'image : %d" % total_size)
            QMessageBox.information(self, "image sélectionnée", self.trUtf8("Taille de l'image: %d" %total_size))
            nom_img = (date_img_chargee + ".zip")
            with open(nom_img, 'wb') as fd:
                start = time.clock()
                if total_size is None:
                    fd.write(img.content)
                else:
                    dl = 0
                    self.progressbar.setValue(dl)
                    for data in img.iter_content(32*1024):
                        #print("data : ", len(data))
                        dl += len(data)
                        #print("dl : ", dl)
                        fd.write(data)
                        done = int(100 * dl / int(total_size))
                        #print("done : ", done)
                        self.progressbar.setValue(done)
                        QApplication.processEvents() 
        else:
            print("Problème avec la requête.")
            QMessageBox.information(self, "Information", self.trUtf8("Problème avec la requête"))

        nom_zip = os.path.join(str(nom_dossier_saving), date_img_chargee + ".zip")
        print("nom zip : ", nom_zip)
        nom_dezip = os.path.join(str(nom_dossier_saving), date_img_chargee)
        print("nom_dezip :", nom_dezip)
        zip_ref = zipfile.ZipFile(nom_zip, 'r')
        zip_ref.extractall(nom_dezip)
        zip_ref.close()
        data = os.path.join(nom_dezip,"DATA")
        print("dossier data: ", data)
        if not os.path.isdir(data):
            os.mkdir(data)
        liste_dossier = os.listdir(nom_dezip)
        print("liste_dossier dezip: ", liste_dossier)
        liste_fichier = glob(os.path.join(os.path.join(nom_dezip, liste_dossier[1]), "*.tif"))
        for i in liste_fichier:
            if "FRE" in i:
                nom = os.path.basename(i)
                print(nom)
                nouveau_chemin = os.path.join(data, nom)
                print(nouveau_chemin)
                #print(nouveau_chemin)
                os.rename(i, nouveau_chemin)
                
    def reech_image(self):
        print("\n###Réechantillonage des images à 10 m###")
        dossier = str(nom_dossier_saving)
        os.chdir(dossier)
        print("dossier : ", dossier)
        print(os.listdir('.'))
        for i in (os.listdir('.')):
            rep_s2_data = os.path.join(dossier, str(i), "DATA")
            liste_fichier =  glob(os.path.join(rep_s2_data, "*.tif"))
            liste_warp = []
            for img in liste_fichier:
                nom_img = os.path.splitext(os.path.basename(img))[0]
                print(nom_img)
                img_warp = os.path.join(rep_s2_data, "ech_%s.tif" % nom_img)
                gdal.Warp(img_warp, img, xRes=10, yRes=10)
                liste_warp.append(img_warp)
                os.remove(img)
            liste_nan = []
            for img in liste_warp:
                nom_img = os.path.splitext(os.path.basename(img))[0]
                img_nan = os.path.join(rep_s2_data, "nan_%s.tif" % nom_img)
                with rasterio.open(img) as src:
                    array = src.read()
                    profile = src.profile
                    profile['dtype'] = 'float64'
                    print(profile)
                    array = array.astype(float)
                    pprint(array)
                    array[array == -10000] = np.nan
                    pprint(array)
                    with rasterio.open(img_nan, 'w', **profile) as dst:
                        dst.write(array)
                liste_nan.append(img_nan)
                os.remove(img)
        
        
    def creer_shp(self):
        dossier = str(self.dossier_image.text())
        for j in os.listdir('.'):
            print("j = " , j)
            rep_s2_data = os.path.join(dossier, str(j),'DATA')
            print("rep_s2_data : ", rep_s2_data)
            rep_s2_pretraitement = os.path.join(dossier, str(j), "Pretraitement")
            print("rep_s2_pretraitement : ", rep_s2_pretraitement)
            if not os.path.isdir(rep_s2_pretraitement):
                os.mkdir(rep_s2_pretraitement)
            rep_s2_indice = os.path.join(dossier, str(j), "Indices")
            if not os.path.isdir(rep_s2_indice):
                os.mkdir(rep_s2_indice)
            rep_s2_indice_1m = os.path.join(rep_s2_indice, "indice_1m")
            if not os.path.isdir(rep_s2_indice_1m):
                os.mkdir(rep_s2_indice_1m)
            dossier_coord = self.cd_coord.text()
            fichier = pd.read_excel(str(dossier_coord))
            print("fichier excel : ", fichier)
            liste_fichier = glob(os.path.join(rep_s2_data, "*.tif"))
            print("liste_fichier : " , liste_fichier)
            # for img in liste_fichier :
            #     image = gdal.Open(img)
            image = gdal.Open(liste_fichier[0])
            with rasterio.open(liste_fichier[0]) as src:
                img_proj = src.crs.data["init"].split(":")[1]
                print("Code epsg = ", img_proj)

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
                if lon[11] == 'O':
                    y = -(deg_lon + min_lon/60 + sec_lon/(60*60))
                else:
                    y = deg_lon + min_lon/60 + sec_lon/(60*60)
                lat, lon = x, y
                print(lat, lon)
                with rasterio.open(liste_fichier[0]) as src:
                    img_proj = src.crs.data["init"].split(":")[1]
                #print("Code epsg = ", img_proj)
                if (img_proj) == '32630':
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
                elif (img_proj) == '32631':
                    epsg_4326 = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs  ')
                    epsg_32631 = pyproj.Proj('+proj=utm +zone=31 +datum=WGS84 +units=m +no_defs ')
                    x, y = pyproj.transform(epsg_4326, epsg_32631, lon, lat)
                    print(fichier.Modalite[i])
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
            with fiona.open(shapefile, 'w', driver='ESRI Shapefile', crs=from_epsg(img_proj), schema=schema) as dst:
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
                    #print(poly.area)
                    buffer = Polygon(poly.buffer(-1.5), LinearRing([(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5)]))
                    #print(buffer.area)
                    #print(" ")
                    dst.write({'geometry': mapping(buffer), 'properties': {'ID': str(i[1]), "Surf": poly.area}})
        QMessageBox.information(self, "Information", self.trUtf8("Le shapefile est créer ! CLIQUEZ SUR DECOUPER LES IMAGES !"))

    def decoup_image_mask(self):
        print("\n### Découpage image ###")
        self.liste_image_decoup.clear()
        dossier = str(self.dossier_image.text())
        os.chdir(dossier)
        liste_concat = []
        print("dossier : ", dossier)
        print(os.listdir('.'))
        for i in (os.listdir('.')):
            rep_s2_data = os.path.join(dossier, str(i), "DATA")
            print("rep_s2_data : ", rep_s2_data)
            rep_s2_pretraitement = os.path.join(dossier, str(i), "Pretraitement")
            print("rep_s2_pretraitement : ", rep_s2_pretraitement)
            if not os.path.isdir(rep_s2_pretraitement):
                os.mkdir(rep_s2_pretraitement)
            rep_s2_indice = os.path.join(dossier, str(i), "Indices")
            if not os.path.isdir(rep_s2_indice):
                os.mkdir(rep_s2_indice)
            rep_s2_indice_1m = os.path.join(rep_s2_indice, "indice_1m")
            print("rep_s2_indice_1m : ", rep_s2_indice_1m)
            if not os.path.isdir(rep_s2_indice_1m):
                os.mkdir(rep_s2_indice_1m)
            #decoupage des rasters a la forme du shapefile
            # Liste de toutes les images de rep_s2_data finissant par jp2
            liste_fichier = glob(os.path.join(rep_s2_data, "*.tif"))
            print("liste_fichier : ", liste_fichier)
            shapefile = os.path.join(rep_s2_pretraitement, 'parcelle.shp')
            with fiona.open(shapefile, "r") as shapefile:
                features = [feature["geometry"] for feature in shapefile]
                liste_mask = []
                liste_decoup = []
            for img in liste_fichier:
                # Nouveau nom de l'image apres decoupe, au format tif, placee dans le bon repertoire
                #Recuperation du nom de l'image sans l'extension
                nom_img = os.path.splitext(os.path.basename(img))[0]
                img_mask = os.path.join(rep_s2_pretraitement, "mask_%s.tif" % nom_img)
                img_decoup = os.path.join(rep_s2_pretraitement, "decoup_%s.tif" % nom_img)
                liste_mask.append(img_mask)
                liste_decoup.append(img_decoup)
                with rasterio.open(img) as src:
                    out_image, out_transform = rasterio.mask.mask(src, features, nodata = -999, crop = True)
                    out_meta = src.meta.copy()

                    out_meta.update({"driver": "GTiff",
                                     "height": out_image.shape[1],
                                     "width": out_image.shape[2],
                                     "transform": out_transform})
                with rasterio.open(img_mask, "w", **out_meta) as dest:
                    dest.write(out_image)
                print('##### LISTE IMAGE MASK#####')
                print(liste_mask)        
                for img_mask in liste_mask:
                    print("####image mask####")
                    print(img_mask)
                    with rasterio.open(img_mask) as src:
                        array = src.read()
                        profile = src.profile
                        print(profile)
                        profile['dtype'] = 'float32'
                        array = array.astype('float32')
                        print(profile)
                        pprint(array)
                        array[array == -999] = np.nan
                    with rasterio.open(img_decoup, 'w', **profile) as dst:
                        dst.write(array)
                    self.liste_image_decoup.addItem(img_decoup)
                print('##### LISTE IMAGE DECOUPEES#####')
                print(liste_decoup)
            for img in liste_mask:
                os.remove(img)
            os.chdir(rep_s2_pretraitement)
            shapefile = "parcelle.shp"
            dico_pixel = {}
            with fiona.open(shapefile) as src:
                # On traite les géométries du shapefile une par une
                for parcelle in src:
                    dico_bande_pixel = {}
                    nom_parcelle = parcelle['properties']['ID']
                    for bande in liste_decoup:
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
                    # On regroupe les données dans un dictionnaire par indice
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
                    # On remplace les valeurs -999 par Nan
                    df_parc.replace(-999, np.nan, inplace=True)
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
        QMessageBox.information(self, "Information", self.trUtf8("Toutes images ont été découpées"))  
        QMessageBox.information(self, "Information", self.trUtf8("Le fichier excel a été généré. PASSEZ A L'ONGLET SUIVANT !"))
          
        
        ### Calcul des indices ##################################
    def calcul_indice(self):
        self.tableauindice.clear()
        dossier = str(self.dossier_image.text())
        print("dossier_image : ", self.dossier_image.text())
        print("liste_fichier_2 : ", self.liste_fichier_2.currentItem().text())
        ssdossier = str(self.liste_fichier_2.currentItem().text())
        rep_s2_data = os.path.join(dossier, ssdossier, "DATA")

        rep_s2_pretraitement = os.path.join(dossier, ssdossier, "Pretraitement")
        if not os.path.isdir(rep_s2_pretraitement):
            os.mkdir(rep_s2_pretraitement)

        rep_s2_indice = os.path.join(dossier, ssdossier, "Indices")
        if not os.path.isdir(rep_s2_indice):
            os.mkdir(rep_s2_indice)

        rep_s2_indice_1m = os.path.join(rep_s2_indice, "indice_1m")
        if not os.path.isdir(rep_s2_indice_1m):
            os.mkdir(rep_s2_indice_1m)

        dictionnaire_indice ={}
        liste_mask = glob(os.path.join(rep_s2_pretraitement, "*.tif"))
        print("liste_mask : ", liste_mask)
        with rasterio.open([val for val in liste_mask if "B2" in val][0]) as src:
            profile = src.profile # On récupère le profile qui servira pour toutes les images
            print(profile)
            blue = src.read(1)
        with rasterio.open([val for val in liste_mask if "B3" in val][0]) as src:
            green = src.read(1)
        with rasterio.open([val for val in liste_mask if "B4" in val][0]) as src:
            red = src.read(1)
        with rasterio.open([val for val in liste_mask if "B5" in val][0]) as src:
            re = src.read(1)
        with rasterio.open([val for val in liste_mask if "B6" in val][0]) as src:
            b6 = src.read(1)
        with rasterio.open([val for val in liste_mask if "B7" in val][0]) as src:
            b7 = src.read(1)
        with rasterio.open([val for val in liste_mask if "B8" in val][0]) as src:
            nir = src.read(1)
        with rasterio.open([val for val in liste_mask if "B8A" in val][0]) as src:
            narrow_nir = src.read(1)
        with rasterio.open([val for val in liste_mask if "B11" in val][0]) as src:
            b11 = src.read(1)
        profile["dtype"] = rasterio.dtypes.float32
        # Calcul NDVI
        check = np.logical_and((np.logical_or(red > 0, nir > 0)), red != -999, nir != -999)
        ndvi = np.where(check, (nir - red) / (nir + red), -999)
        ndvi[ndvi == -999] = np.nan
        dictionnaire_indice["ndvi"] = ndvi
        self.tableauindice.addItem('NDVI - Normalized Difference Vegetation Index')
        with rasterio.open(os.path.join(rep_s2_indice, "ndvi.tif"), "w", **profile) as dst:
            dst.write(ndvi, 1)
        # Calcul NDWI
        check = np.logical_and((np.logical_or(narrow_nir > 0, b11 > 0)), narrow_nir != -999, b11 != -999)
        ndwi = np.where(check, (narrow_nir - b11) / (narrow_nir + b11), -999)
        ndwi[ndwi == -999] = np.nan
        dictionnaire_indice["ndwi"] = ndwi
        self.tableauindice.addItem('NDWI - Normalized Difference Water Index')
        with rasterio.open(os.path.join(rep_s2_indice, "ndwi.tif"), "w", **profile) as dst:
            dst.write(ndwi, 1)
        # Calcul du RE-NDWI (red-edge ndwi) on utilise la bande du RE au lieu de la bande du PIR
        check = np.logical_and((np.logical_or(green > 0, re > 0)), green != -999, re != -999)
        re_ndwi = np.where(check, (green - re) / (green + re), -999)
        re_ndwi[re_ndwi == -999] = np.nan
        dictionnaire_indice["re_ndwi"] = re_ndwi
        self.tableauindice.addItem('RE-NDWI - Red-Edge Normalized Difference Water Index')
        with rasterio.open(os.path.join(rep_s2_indice, "re_ndwi.tif"), "w", **profile) as dst:
            dst.write(re_ndwi, 1)
        ## Calcul NDII = detection des stress eventuels
        check = np.logical_and((np.logical_or(nir > 0, b11 > 0)), nir != -999, b11 != -999)
        ndii = np.where(check, (nir - b11) / (nir + b11), -999)
        ndii[ndii == -999] = np.nan
        dictionnaire_indice["ndii"] = ndii
        self.tableauindice.addItem('NDII - Normalized Difference Infrared Index')
        with rasterio.open(os.path.join(rep_s2_indice, "ndii.tif"), "w", **profile) as dst:
            dst.write(ndii, 1)
        ## Calcul MSI
        check = np.logical_and((np.logical_not((nir == 0))), nir != -999, b11 != -999)
        msi = np.where(check, (b11 / nir), -999)
        msi[msi == -999] = np.nan
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
        s2rep[s2rep == -999] = np.nan
        dictionnaire_indice["s2rep"] = s2rep
        self.tableauindice.addItem('S2REP - Red-Edge position')
        with rasterio.open(os.path.join(rep_s2_indice, "s2rep.tif"), "w", **profile) as dst:
            dst.write(s2rep, 1)
        # Calcul du PSSR
        check = np.logical_and((np.logical_not((red == 0))), nir != -999, red != -999)
        pssr = np.where(check, (nir/red), -999)
        pssr[pssr == -999] = np.nan
        dictionnaire_indice["pssr"] = pssr
        self.tableauindice.addItem('PSSR - Pigment Specific Simple Ratio')
        with rasterio.open(os.path.join(rep_s2_indice, "pssr.tif"), "w", **profile) as dst:
            dst.write(pssr, 1)
        # Calcul de ARVI = comme ndvi mais plus resistant aux aerosols
        verif = np.logical_not(nir -((2*red)-blue) == 0)
        verif2 = np.logical_and(nir != -999, red != -999, blue != -999)
        check = np.logical_and(verif, verif2)
        arvi = np.where(check, ((nir - (2*red)-blue)/(nir + (2*red)-blue)), -999)
        arvi[arvi == -999] = np.nan
        dictionnaire_indice["arvi"] = arvi
        self.tableauindice.addItem('ARVI - Aerosol Resistant Vegetation Index')
        with rasterio.open(os.path.join(rep_s2_indice, "arvi.tif"), "w", **profile) as dst:
            dst.write(arvi, 1)
        # Calcul du PSRI = plant senescence reflectance index
        verif = np.logical_not(re == 0)
        verif2 = np.logical_and(red != -999, re != -999, blue != -999)
        check = np.logical_and(verif, verif2)
        psri = np.where(check, ((red - blue) / re), -999)
        psri[psri == -999] = np.nan
        dictionnaire_indice["psri"] = psri
        self.tableauindice.addItem('PSRI - Plant Senescence Reflectance Index')
        with rasterio.open(os.path.join(rep_s2_indice, "psri.tif"), "w", **profile) as dst:
            dst.write(psri, 1)
        # Calcul de CRI2 = carotenoid reflectance index 2
        check = np.logical_and((np.logical_and ((blue !=0), (re != 0))), blue != -999, re != -999)
        cri2 = np.where(check, ((1/blue) - (1/re)), -999)
        cri2[cri2 == -999] = np.nan
        dictionnaire_indice["cri2"] = cri2
        self.tableauindice.addItem('CRI2 - Carotenoid Reflectance Index 2')
        with rasterio.open(os.path.join(rep_s2_indice, "cri2.tif"), "w", **profile) as dst:
            dst.write(cri2, 1)
        #Calcul de CRI1
        check = np.logical_and((np.logical_and ((blue > 0), (green > 0))), blue != -999, green != -999)
        cri1 = np.where(check, ((1/blue)-(1/green)), -999)
        cri1[cri1 == -999] = np.nan
        dictionnaire_indice["cri1"] = cri1
        self.tableauindice.addItem('CRI1 - Carotenoid Reflectance Index 1')
        with rasterio.open(os.path.join(rep_s2_indice, "cri1.tif"), "w", **profile) as dst:
            dst.write(cri1, 1)
        # Calcul de CHL-RED-EDGE = chlorophylle red edge
        check = np.logical_and((np.logical_not(nir == 0)), re != -999, nir != -999)
        chl_re = np.where(check, (nir/re)-1, -999)
        chl_re[chl_re == -999] = np.nan
        dictionnaire_indice["chl_re"] = chl_re
        self.tableauindice.addItem('CHL-RE - Chlorophyll Red-Edge')
        with rasterio.open(os.path.join(rep_s2_indice, "chl_re.tif"), "w", **profile) as dst:
            dst.write(chl_re, 1)
        #Calcul ARI2 = anthocyanin reflectance index
        verif = np.logical_and((blue > 0), (green > 0))
        verif2 = np.logical_and(nir != -999, blue != -999, green != -999)
        check = np.logical_and(verif, verif2)
        ari2 = np.where(check, ((nir/blue)-(nir/green)), -999)
        ari2[ari2 == -999] = np.nan
        dictionnaire_indice["ari2"] = ari2
        self.tableauindice.addItem('ARI2 - Anthocyanin Reflectance Index')
        with rasterio.open(os.path.join(rep_s2_indice, "ari2.tif"), "w", **profile) as dst:
            dst.write(ari2, 1)
        #Calcul de EVI = enhanced vegetation index
        check = np.logical_and((np.logical_not((nir + 2.4*red +1)==0)), nir != -999, red != -999)
        evi = np.where(check, (2.5 * (nir - red)/(nir + 2.4*red +1)), -999)
        evi[evi == -999] = np.nan
        dictionnaire_indice["evi"] = evi
        self.tableauindice.addItem('EVI - Enhance Vegetation Index')
        with rasterio.open(os.path.join(rep_s2_indice, "evi.tif"), "w", **profile) as dst:
            dst.write(evi, 1)
        #Calcul de GNDVI = green normalized vegetation index
        check = np.logical_and((np.logical_not ((nir + green)==0)), nir != -999, green != -999)
        gndvi = np.where(check, ((nir - green)/(nir + green)), -999)
        gndvi[gndvi == -999] = np.nan
        dictionnaire_indice["gndvi"] = gndvi
        self.tableauindice.addItem('GNDVI - Green Normalized Vegetation Index')
        with rasterio.open(os.path.join(rep_s2_indice, "gndvi.tif"), "w", **profile) as dst:
            dst.write(gndvi, 1)
        #Calcul de SAVI (soil adjusted vegetation index)
        check = np.logical_and((np.logical_not((nir + red + 0.5) == 0)), nir != -999, red != -999)
        savi = np.where(check, (((nir - red)/(nir + red + 0.5))*1.5), -999)
        savi[savi == -999] = np.nan
        dictionnaire_indice["savi"] = savi
        self.tableauindice.addItem('SAVI - Soil Adjusted Vegetation Index')
        with rasterio.open(os.path.join(rep_s2_indice, "savi.tif"), "w", **profile) as dst:
            dst.write(savi, 1)
        #Calcul de CGI (chlorophyll green index)
        check = np.logical_and((np.logical_not(green == 0)), nir != -999, green != -999)
        chl_green = np.where(check, (green/nir)-1, -999)
        chl_green[chl_green == -999] = np.nan
        dictionnaire_indice["chl_green"] = chl_green
        self.tableauindice.addItem('CHL_GREEN - Chlorophyll Green Index')
        with rasterio.open(os.path.join(rep_s2_indice, "chl_green.tif"), "w", **profile) as dst:
            dst.write(chl_green, 1)
        #Calcul CVI (chlorophyll vegetation index)
        verif = np.logical_not(green == 0)
        verif2 = np.logical_and(nir != -999, red != -999, green != -999)
        check = np.logical_and(verif, verif2)
        cvi = np.where(check, ((nir*red)/(green* green)), -999)
        cvi[cvi == -999] = np.nan
        dictionnaire_indice['cvi'] = cvi
        self.tableauindice.addItem('CVI - Chlorophyll Vegetation Index')
        with rasterio.open(os.path.join(rep_s2_indice, "cvi.tif"), "w", **profile) as dst:
            dst.write(cvi, 1)

    def calcul_tout(self):
        print("\n### Calcul tout ###")
        self.tableauindice.clear()
        dossier = str(self.dossier_image.text())
        print("dossier_image : ", self.dossier_image.text())
        os.chdir(dossier)
        for doss in os.listdir('.'):
            print(doss)
            rep_s2_pretraitement = os.path.join(dossier, doss, "Pretraitement")
            print(rep_s2_pretraitement)
            rep_s2_indice = os.path.join(dossier, doss, "Indices")
            print(rep_s2_indice)
            dictionnaire_indice ={}
            liste_mask = glob(os.path.join(rep_s2_pretraitement, "*.tif"))
            print(liste_mask)
            with rasterio.open([val for val in liste_mask if "B2" in val][0]) as src:
                profile = src.profile # On récupère le profile qui servira pour toutes les images
                blue = src.read(1)
            with rasterio.open([val for val in liste_mask if "B3" in val][0]) as src:
                green = src.read(1)
            with rasterio.open([val for val in liste_mask if "B4" in val][0]) as src:
                red = src.read(1)
            with rasterio.open([val for val in liste_mask if "B5" in val][0]) as src:
                re = src.read(1)
            with rasterio.open([val for val in liste_mask if "B6" in val][0]) as src:
                b6 = src.read(1)
            with rasterio.open([val for val in liste_mask if "B7" in val][0]) as src:
                b7 = src.read(1)
            with rasterio.open([val for val in liste_mask if "B8" in val][0]) as src:
                nir = src.read(1)
            with rasterio.open([val for val in liste_mask if "B8A" in val][0]) as src:
                narrow_nir = src.read(1)
            with rasterio.open([val for val in liste_mask if "B11" in val][0]) as src:
                b11 = src.read(1)
            profile["dtype"] = rasterio.dtypes.float32
            # Calcul NDVI
            check = np.logical_and((np.logical_or(red > 0, nir > 0)), red != -999, nir != -999)
            ndvi = np.where(check, (nir - red) / (nir + red), -999)
            ndvi[ndvi == -999] = np.nan
            dictionnaire_indice["ndvi"] = ndvi
            self.tableauindice.addItem('NDVI - Normalized Difference Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "ndvi.tif"), "w", **profile) as dst:
                dst.write(ndvi, 1)
            # Calcul NDWI
            check = np.logical_and((np.logical_or(narrow_nir > 0, b11 > 0)), narrow_nir != -999, b11 != -999)
            ndwi = np.where(check, (narrow_nir - b11) / (narrow_nir + b11), -999)
            ndwi[ndwi == -999] = np.nan
            dictionnaire_indice["ndwi"] = ndwi
            self.tableauindice.addItem('NDWI - Normalized Difference Water Index')
            with rasterio.open(os.path.join(rep_s2_indice, "ndwi.tif"), "w", **profile) as dst:
                dst.write(ndwi, 1)
            # Calcul du RE-NDWI (red-edge ndwi) on utilise la bande du RE au lieu de la bande du PIR
            check = np.logical_and((np.logical_or(green > 0, re > 0)), green != -999, re != -999)
            re_ndwi = np.where(check, (green - re) / (green + re), -999)
            re_ndwi[re_ndwi == -999] = np.nan
            dictionnaire_indice["re_ndwi"] = re_ndwi
            self.tableauindice.addItem('RE-NDWI - Red-Edge Normalized Difference Water Index')
            with rasterio.open(os.path.join(rep_s2_indice, "re_ndwi.tif"), "w", **profile) as dst:
                dst.write(re_ndwi, 1)
            ## Calcul NDII = detection des stress eventuels
            check = np.logical_and((np.logical_or(nir > 0, b11 > 0)), nir != -999, b11 != -999)
            ndii = np.where(check, (nir - b11) / (nir + b11), -999)
            ndii[ndii == -999] = np.nan
            dictionnaire_indice["ndii"] = ndii
            self.tableauindice.addItem('NDII - Normalized Difference Infrared Index')
            with rasterio.open(os.path.join(rep_s2_indice, "ndii.tif"), "w", **profile) as dst:
                dst.write(ndii, 1)
            ## Calcul MSI
            check = np.logical_and((np.logical_not((nir == 0))), nir != -999, b11 != -999)
            msi = np.where(check, (b11 / nir), -999)
            msi[msi == -999] = np.nan
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
            s2rep[s2rep == -999] = np.nan
            dictionnaire_indice["s2rep"] = s2rep
            self.tableauindice.addItem('S2REP - Red-Edge position')
            with rasterio.open(os.path.join(rep_s2_indice, "s2rep.tif"), "w", **profile) as dst:
                dst.write(s2rep, 1)
            # Calcul du PSSR
            check = np.logical_and((np.logical_not((red == 0))), nir != -999, red != -999)
            pssr = np.where(check, (nir/red), -999)
            pssr[pssr == -999] = np.nan
            dictionnaire_indice["pssr"] = pssr
            self.tableauindice.addItem('PSSR - Pigment Specific Simple Ratio')
            with rasterio.open(os.path.join(rep_s2_indice, "pssr.tif"), "w", **profile) as dst:
                dst.write(pssr, 1)
            # Calcul de ARVI = comme ndvi mais plus resistant aux aerosols
            verif = np.logical_not(nir -((2*red)-blue) == 0)
            verif2 = np.logical_and(nir != -999, red != -999, blue != -999)
            check = np.logical_and(verif, verif2)
            arvi = np.where(check, ((nir - (2*red)-blue)/(nir + (2*red)-blue)), -999)
            arvi[arvi == -999] = np.nan
            dictionnaire_indice["arvi"] = arvi
            self.tableauindice.addItem('ARVI - Aerosol Resistant Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "arvi.tif"), "w", **profile) as dst:
                dst.write(arvi, 1)
            # Calcul du PSRI = plant senescence reflectance index
            verif = np.logical_not(re == 0)
            verif2 = np.logical_and(red != -999, re != -999, blue != -999)
            check = np.logical_and(verif, verif2)
            psri = np.where(check, ((red - blue) / re), -999)
            psri[psri == -999] = np.nan
            dictionnaire_indice["psri"] = psri
            self.tableauindice.addItem('PSRI - Plant Senescence Reflectance Index')
            with rasterio.open(os.path.join(rep_s2_indice, "psri.tif"), "w", **profile) as dst:
                    dst.write(psri, 1)
            # Calcul de CRI2 = carotenoid reflectance index 2
            check = np.logical_and((np.logical_and ((blue !=0), (re != 0))), blue != -999, re != -999)
            cri2 = np.where(check, ((1/blue) - (1/re)), -999)
            cri2[cri2 == -999] = np.nan
            dictionnaire_indice["cri2"] = cri2
            self.tableauindice.addItem('CRI2 - Carotenoid Reflectance Index 2')
            with rasterio.open(os.path.join(rep_s2_indice, "cri2.tif"), "w", **profile) as dst:
                dst.write(cri2, 1)
            #Calcul de CRI1
            check = np.logical_and((np.logical_and ((blue > 0), (green > 0))), blue != -999, green != -999)
            cri1 = np.where(check, ((1/blue)-(1/green)), -999)
            cri1[cri1 == -999] = np.nan
            dictionnaire_indice["cri1"] = cri1
            self.tableauindice.addItem('CRI1 - Carotenoid Reflectance Index 1')
            with rasterio.open(os.path.join(rep_s2_indice, "cri1.tif"), "w", **profile) as dst:
                dst.write(cri1, 1)
            # Calcul de CHL-RED-EDGE = chlorophylle red edge
            check = np.logical_and((np.logical_not(nir == 0)), re != -999, nir != -999)
            chl_re = np.where(check, (nir/re)-1, -999)
            chl_re[chl_re == -999] = np.nan
            dictionnaire_indice["chl_re"] = chl_re
            self.tableauindice.addItem('CHL-RE - Chlorophyll Red-Edge')
            with rasterio.open(os.path.join(rep_s2_indice, "chl_re.tif"), "w", **profile) as dst:
                dst.write(chl_re, 1)
            #Calcul ARI2 = anthocyanin reflectance index
            verif = np.logical_and((blue > 0), (green > 0))
            verif2 = np.logical_and(nir != -999, blue != -999, green != -999)
            check = np.logical_and(verif, verif2)
            ari2 = np.where(check, ((nir/blue)-(nir/green)), -999)
            ari2[ari2 == -999] = np.nan
            dictionnaire_indice["ari2"] = ari2
            self.tableauindice.addItem('ARI2 - Anthocyanin Reflectance Index')
            with rasterio.open(os.path.join(rep_s2_indice, "ari2.tif"), "w", **profile) as dst:
                dst.write(ari2, 1)
            #Calcul de EVI = enhanced vegetation index
            check = np.logical_and((np.logical_not((nir + 2.4*red +1)==0)), nir != -999, red != -999)
            evi = np.where(check, (2.5 * (nir - red)/(nir + 2.4*red +1)), -999)
            evi[evi == -999] = np.nan
            dictionnaire_indice["evi"] = evi
            self.tableauindice.addItem('EVI - Enhance Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "evi.tif"), "w", **profile) as dst:
                dst.write(evi, 1)
            #Calcul de GNDVI = green normalized vegetation index
            check = np.logical_and((np.logical_not ((nir + green)==0)), nir != -999, green != -999)
            gndvi = np.where(check, ((nir - green)/(nir + green)), -999)
            gndvi[gndvi == -999] = np.nan
            dictionnaire_indice["gndvi"] = gndvi
            self.tableauindice.addItem('GNDVI - Green Normalized Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "gndvi.tif"), "w", **profile) as dst:
                dst.write(gndvi, 1)
            #Calcul de SAVI (soil adjusted vegetation index)
            check = np.logical_and((np.logical_not((nir + red + 0.5) == 0)), nir != -999, red != -999)
            savi = np.where(check, (((nir - red)/(nir + red + 0.5)*1.5)), -999)
            savi[savi == -999] = np.nan
            dictionnaire_indice["savi"] = savi
            self.tableauindice.addItem('SAVI - Soil Adjusted Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "savi.tif"), "w", **profile) as dst:
                dst.write(savi, 1)
            #Calcul de CGI (chlorophyll green index)
            check = np.logical_and((np.logical_not(green == 0)), nir != -999, green != -999)
            chl_green = np.where(check, (green/nir)-1, -999)
            chl_green[chl_green == -999] = np.nan
            dictionnaire_indice["chl_green"] = chl_green
            self.tableauindice.addItem('CHL_GREEN - Chlorophyll Green Index')
            with rasterio.open(os.path.join(rep_s2_indice, "chl_green.tif"), "w", **profile) as dst:
                dst.write(chl_green, 1)
            #Calcul CVI (chlorophyll vegetation index)
            verif = np.logical_not(green == 0)
            verif2 = np.logical_and(nir != -999, red != -999, green != -999)
            check = np.logical_and(verif, verif2)
            cvi = np.where(check, ((nir*red)/(green* green)), -999)
            cvi[cvi == -999] = np.nan
            dictionnaire_indice['cvi'] = cvi
            self.tableauindice.addItem('CVI - Chlorophyll Vegetation Index')
            with rasterio.open(os.path.join(rep_s2_indice, "cvi.tif"), "w", **profile) as dst:
                dst.write(cvi, 1)

    def reechantillonnage(self):
        print("\n### reechantillonnage ###")
        dossier = str(self.dossier_image.text())
        print("dossier : ", dossier)
        for doss in os.listdir('.'):
            print("doss : ", doss)
            rep_s2_indice = os.path.join(dossier, doss, "Indices")
            print("rep_s2_indice : ", rep_s2_indice)
            rep_s2_indice_1m = os.path.join(rep_s2_indice, "indice_1m")
            print("rep_s2_indice_1m : ", rep_s2_indice_1m)
            # Liste de toutes les images d'indice finissant par tif
            liste_fichier = glob(os.path.join(rep_s2_indice, "*.tif"))
            liste_indice_1m = []
            for img in liste_fichier:
                nom_img = os.path.splitext(os.path.basename(img))[0]
                print("nom_img : ", nom_img)
                img_indice = os.path.join(rep_s2_indice_1m, "%s_1m.tif" % nom_img)
                print("img_indice : ", img_indice)
                gdal.Warp(img_indice, img, xRes=1, yRes=1) # Réchantillonage à 1m, méthode nearest
                liste_indice_1m.append(img_indice)
        QMessageBox.information(self, "Information", self.trUtf8("Les indices ont été calculés. PASSEZ A L'ONGLET SUIVANT !"))

        
    def stat_zonale(self):
        print("\n### stat_zonale ###")
        if self.stat.checkState()>0:
            liste_concat = []
            dossier = str(self.dossier_image.text())
            os.chdir(dossier)
            for doss in os.listdir('.'):
                rep_s2_pretraitement = os.path.join(dossier, doss, "Pretraitement")
                rep_s2_indice = os.path.join(dossier, doss, "Indices")
                rep_s2_indice_1m = os.path.join(rep_s2_indice, "indice_1m")

                liste_image_indice = glob(os.path.join(rep_s2_indice_1m, "*.tif"))
                os.chdir(str(rep_s2_pretraitement))
                shapefile = "parcelle.shp"
                with fiona.open(shapefile) as src:
                    # ID_dict = dict()
                    # c = 1
                    # nom_ligne = []
                    # for i in src:
                    #     ID_dict[c] = i['properties']['ID']
                    #     c = c + 1
                    #     nom_ligne.append(i['properties']['ID'])
                    ID_dict = {k+1: v['properties']['ID'] for k, v in enumerate(src)}
                    nom_ligne = [val['properties']['ID'] for val in src]
                stat = dict()
                for index in liste_image_indice:
                    #on récupére le nom de l'indice sans l'extension\
                    indice = os.path.splitext(os.path.basename(index))
                    stats = rasterstats.zonal_stats(shapefile, index, stats= ['mean', 'median', 'std'], nodata = -999,  all_touched=True)
                    stat[indice[0]]=stats
                #on récupère le nom des parcelles
                with fiona.open(shapefile) as src:
                    print("src.bounds : ", src.bounds)
                    ID_list = []
                    for i in src:
                        c = i['properties']['ID']
                        ID_list.append(i['properties']['ID'])
                moyenne = dict()
                std = dict()
                mediane = dict()
                print("ID_list : ", ID_list)
                for key in stat.keys():
                    for i in range (0, len(ID_list)):
                        parcelle = ID_list[i]
                        moyenne[parcelle, key] = stat[key][i]['mean']
                        std[parcelle, key] = stat[key][i]['std']
                        mediane[parcelle, key] = stat[key][i]['median']
                df_mean = pd.Series(moyenne)
                print("\ndf_mean : ", df_mean.head())
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
            QMessageBox.information(self, "Information", self.trUtf8("Le fichier excel de statistiques a été généré."))    
        if self.pix.checkState()>0:
            liste_concat = []
            dossier = str(self.dossier_image.text())
            os.chdir(dossier)
            for doss in os.listdir('.'):
                rep_s2_pretraitement = os.path.join(str(self.dossier_image.text()), doss, "Pretraitement")
                rep_s2_indice = os.path.join(str(self.dossier_image.text()), doss, "Indices")
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
                                                            stats= ['mean', 'median', 'std'],
                                                            nodata = -999,  all_touched=True,
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
                print("dico_pixel.keys : ", dico_pixel.keys())
                for parcelle in sorted(dico_pixel.keys()): # tri alphabétique des parcelles facultatif
                    df_parc = pd.DataFrame(dico_pixel[parcelle])
                    # On remplace les valeurs -999, 0 et 1 par Nan
                    df_parc.replace(-999, np.nan, inplace=True)
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

            dossier = str(self.dossier_output.text())
            os.chdir(dossier)
            concat_final = pd.concat(liste_concat, ignore_index = True)
            print(concat_final)
            writer = pd.ExcelWriter('valeur_pixels.xlsx', engine='xlsxwriter')
            concat_final.to_excel(writer)
            writer.save
            QMessageBox.information(self, "Information", self.trUtf8("Le fichier excel des valeurs des pixels par indices a été généré."))

    def merge_image(self):
        print("\n### merge_image ###")
        global dossier_output
        dossier_output = str(self.dossier_output_2.text())
        rep_s2_pretraitement = os.path.join(str(dossier_output), "Pretraitement")
        if not os.path.isdir(rep_s2_pretraitement):
            os.mkdir(rep_s2_pretraitement)
        print("rep_s2_pretraitement : ", rep_s2_pretraitement)
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
        print(min_lat_mini, min_lat_maxi)
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
        vert = str(self.dossier_output_vert.text())
        bleue = str(self.dossier_output_bleue.text())
        with rasterio.open(rouge) as src:
            img_proj = src.crs.data["init"].split(":")[1]
            print("Code epsg = ", img_proj)
        if (img_proj) == '32630':
            epsg_4326 = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs  ')
            epsg_32630 = pyproj.Proj('+proj=utm +zone=30 +datum=WGS84 +units=m +no_defs ')
            xmax, ymax = pyproj.transform(epsg_4326, epsg_32630, lon2, lat2)
            xmin, ymin = pyproj.transform(epsg_4326, epsg_32630, lon1, lat1)
            xmax, ymax, xmin, ymin = int(xmax), int(ymax), int(xmin), int(ymin)
            print("bounds : ", xmax, ymax, xmin, ymin)
        elif (img_proj) == '32631':
            epsg_4326 = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs  ')
            epsg_32631 = pyproj.Proj('+proj=utm +zone=31 +datum=WGS84 +units=m +no_defs ')
            xmax, ymax = pyproj.transform(epsg_4326, epsg_32631, lon2, lat2)
            xmin, ymin = pyproj.transform(epsg_4326, epsg_32631, lon1, lat1)
            xmax, ymax, xmin, ymin = int(xmax), int(ymax), int(xmin), int(ymin)
            print(xmax, ymax, xmin, ymin)
        liste_fichier = [rouge, vert, bleue]
        liste_decoupe = []
        for img in liste_fichier:
            print("img : ", img)
            #Recuperation du nom de l'image sans l'extension
            nom_img = os.path.splitext(os.path.basename(img))[0]
            #Nouveau nom de l'image apres decoupe, au format tif, placee dans le bon repertoire
            img_pretraitement = os.path.join(rep_s2_pretraitement, "merge_%s.tif" % nom_img)
            print("img_pretraitement : ", img_pretraitement)
            liste_decoupe.append(img_pretraitement)
            # Decoupage de l'image selon l'emprise
            res = subprocess.Popen(["gdalwarp",
                                    "-te", str(xmin), str(ymin), str(xmax), str(ymax),
                                    "-tr", "10", "10",
                                    "-overwrite",
                                    img, img_pretraitement],
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE).communicate()
            print("Résultat de la commande : ", res[0])
            print("Erreur éventuelle de la commande : ", res[1])
            print("")
        print("liste_decoupe : ", liste_decoupe)
        rouge = liste_decoupe[0]
        vert = liste_decoupe[1]
        bleue = liste_decoupe[2]
        output = os.path.join(rep_s2_pretraitement, "merge.tif")
        print("output : ", output)
        gm = "C:/Users/colette.badourdine/Documents/STAGE/script/SCRIPTSFINAUX/Final/lib/gdal_merge.py"
        res2 = subprocess.Popen(['python', gm, '-separate', '-co', 'PHOTOMETRIC=RGB', '-o', output, rouge, vert, bleue],
                                 stdin=None, stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE, shell=True).communicate()
        print("Résultat de la commande : ", res[0])
        print("Erreur éventuelle de la commande : ", res[1])
        print("")

    def visualisation(self):
        print("\n### visualisation ###")
        dossier_image = self.image_indice.text()
        os.chdir(str(dossier_image))
        image = self.liste_image.currentItem().text()
        nom_image = "%s.tif" % image
        bg = str(self.image_merge.text()) ###bg c'est l'image merge

        with rasterio.open(bg) as src:
            img_proj = src.crs.data["init"].split(":")[1]
            print("Code epsg = ", img_proj)
        if img_proj == '32630':
            # Définition de la projection
            projection = ccrs.UTM(30)
        elif img_proj == '32631':
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
            print("####BAND ARRAY %s #####" % nom_image)
            print(band[0])
            band = band[0]
            maxi = np.nanmax(band)
            mini = np.nanmin(band)
            print("MAXI")
            print(maxi)
            print("MINI")
            print(mini)
            band_255 = np.where((band[:, :] != -999), ((band[:,:]-mini)*255)/(maxi-mini), np.nan)
            print("band_255")
            print(band_255)
            #band_255 = band_255.astype(np.uint8)
            #print(band_255)

        item = self.comboBox_palette.currentText()
        print(item)
        # Une figure avec 3 sous-figures
        fig, (axe1) = plt.subplots(ncols=1, subplot_kw={'projection': projection})
        fig.set_figwidth(10)
        if item == "Normal":
            axe1.set_title('cmap = Normal'+ '\nIndice :' + str(image))
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
def main(args):
    app = QApplication(args)
    f = QWidget()
    c = Principal(f)
    f.show()
    return app.exec_()

if __name__=="__main__":
    main(sys.argv)
