# -*- coding: utf-8 -*-


import os

from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5 import QtCore

from qgis.PyQt import QtGui, uic, QtWidgets
from qgis.core import *

from .core.Layer import Layer
from .Contexte import Contexte

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormChargerGuichet_base.ui'))

class FormChargerGuichet(QtWidgets.QDialog, FORM_CLASS):

    """
    Dialogue pour afficher la liste des couches disponibles pour le profil utilisateur
    et récupération du choix de l'utilisateur
    """
    cancel = True
    context = None
    profilUser = None

    # La liste des couches du profil utilisateur
    listLayers = []

    # Types de couches, balise <TYPE>
    wms = "WMS"
    wfs = "WFS"
    geoportail = "GeoPortail"

    # Balises <ROLE>
    # clé xml:valeur affichage boite
    roleCleVal = {"edit":"Edition", "ref-edit":"Référence-Edition", "visu":"Visualisation"}


    def __init__(self, context, parent=None):
        super(FormChargerGuichet, self).__init__(parent)
        self.setupUi(self)
        self.setFocus()
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Valider")
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")

        self.context = context
        self.listLayers = self.getInfosLayers()

        # Remplissage des différentes tables de couches
        self.setTableWidgetMonGuichet()
        self.setTableWidgetFondsGeoportail()
        self.setTableWidgetFondsGeoportailBis()
        self.setTableWidgetAutresGeoservices()

        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.save)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)


    def getInfosLayers(self):
        infosLayers = []

        if self.context.ripClient == None:
            connResult =self.context.getConnexionRipart()
            if not connResult:
                #la connexion a échoué, on ne fait rien
                self.context.iface.messageBar().pushMessage("",u"Un problème de connexion avec le service est survenu. Veuillez rééssayer", level=2, duration=5)
                return infosLayers

        self.profilUser = self.context.client.getProfil()

        print("Liste des couches du profil utilisateur")
        for layersAll in self.profilUser.infosGeogroupes[0].layers:
            print(layersAll.nom)
            infosLayers.append(layersAll)

        return infosLayers



    def setColonneCharger(self, tableWidget, row, column):
        itemCheckBox = QtWidgets.QTableWidgetItem()
        itemCheckBox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        itemCheckBox.setCheckState(QtCore.Qt.Checked)
        tableWidget.setItem(row, column, itemCheckBox)



    def setTableWidgetMonGuichet(self):

        # Entête
        entete = ["Nom de la couche", "Rôle", "Charger"]
        self.tableWidgetMonGuichet.setHorizontalHeaderLabels(entete)

        # Autres lignes de la table
        for layer in self.listLayers:
            if layer.type != self.wfs:
                continue

            if layer.url.find("collaboratif.ign.fr") == -1:
                continue

            rowPosition = self.tableWidgetMonGuichet.rowCount()
            self.tableWidgetMonGuichet.insertRow(rowPosition)

            # Colonne "Nom de la couche"
            item = QtWidgets.QTableWidgetItem(layer.nom)
            self.tableWidgetMonGuichet.setItem(rowPosition, 0, item)

            # Colonne "Rôle"
            role = layer.role
            if role in self.roleCleVal:
                item = QtWidgets.QTableWidgetItem(self.roleCleVal[role])
            else:
                item = QtWidgets.QTableWidgetItem("Pas de rôle, bizarre !")
            self.tableWidgetMonGuichet.setItem(rowPosition, 1, item)

            # Colonne "Charger"
            self.setColonneCharger(self.tableWidgetMonGuichet, rowPosition, 2)



    def setTableWidgetFondsGeoportail(self):

        # Entête
        entete = ["Nom de la couche", "Charger"]
        self.tableWidgetFondsGeoportail.setHorizontalHeaderLabels(entete)

        # Autres lignes de la table
        for layer in self.listLayers:
            if layer.type != self.geoportail:
                continue

            if layer.nom in self.profilUser.layersCleGeoportail:

                rowPosition = self.tableWidgetFondsGeoportail.rowCount()
                self.tableWidgetFondsGeoportail.insertRow(rowPosition)

                # Colonne "Nom de la couche"
                item = QtWidgets.QTableWidgetItem(layer.nom)
                self.tableWidgetFondsGeoportail.setItem(rowPosition, 0, item)

                # Colonne "Charger"
                self.setColonneCharger(self.tableWidgetFondsGeoportail, rowPosition, 1)



    def setTableWidgetFondsGeoportailBis(self):

        # Entête
        entete = ["Nom de la couche", "Charger"]
        self.tableWidgetFondsGeoportailBis.setHorizontalHeaderLabels(entete)

        # Autres lignes de la table
        for layer in self.listLayers:
            if layer.type != self.geoportail:
                continue

            if layer.nom not in self.profilUser.layersCleGeoportail:

                rowPosition = self.tableWidgetFondsGeoportailBis.rowCount()
                self.tableWidgetFondsGeoportailBis.insertRow(rowPosition)

                # Colonne "Nom de la couche"
                item = QtWidgets.QTableWidgetItem(layer.nom)
                self.tableWidgetFondsGeoportailBis.setItem(rowPosition, 0, item)

                # Colonne "Charger"
                self.setColonneCharger(self.tableWidgetFondsGeoportailBis, rowPosition, 1)



    def setTableWidgetAutresGeoservices(self):

        # Entête
        entete = ["Nom de la couche", "Type", "Charger"]
        self.tableWidgetAutresGeoservices.setHorizontalHeaderLabels(entete)

        # Autres lignes de la table
        for layer in self.listLayers:
            if layer.type != self.wfs and layer.type != self.wms:
                continue

            if layer.url.find("collaboratif.ign.fr"):
                continue

            rowPosition = self.tableWidgetAutresGeoservices.rowCount()
            self.tableWidgetAutresGeoservices.insertRow(rowPosition)

            # Colonne "Nom de la couche"
            item = QtWidgets.QTableWidgetItem(layer.nom)
            self.tableWidgetAutresGeoservices.setItem(rowPosition, 0, item)

            # Colonne "Type"
            item = QtWidgets.QTableWidgetItem(layer.type)
            self.tableWidgetAutresGeoservices.setItem(rowPosition, 1, item)

            # Colonne "Charger"
            self.setColonneCharger(self.tableWidgetAutresGeoservices, rowPosition, 2)



    def save(self):
        print("Affichage des couches dans QGIS : sauvegarde du choix utilisateur.")
        self.cancel = False
        self.close()


    def cancel(self):
        print ("L'utilisateur est sorti de la boite Charger le guichet")
        self.cancel=True
        self.close()
