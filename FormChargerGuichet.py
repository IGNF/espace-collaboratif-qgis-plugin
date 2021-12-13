# -*- coding: utf-8 -*-
"""
Created on 25 nov. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""

import os

from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5 import QtCore

from qgis.PyQt import QtGui, uic, QtWidgets

from .ImporterGuichet import ImporterGuichet
from .core import ConstanteRipart as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormChargerGuichet_base.ui'))


class FormChargerGuichet(QtWidgets.QDialog, FORM_CLASS):
    """
    Dialogue pour afficher la liste des couches disponibles pour le profil utilisateur
    et récupération du choix de l'utilisateur
    """
    context = None
    profilUser = None

    # La liste des couches du profil utilisateur
    listLayers = []

    # Balises <ROLE>
    # Role de la couche dans le cadre d'un guichet
    # - visu = couche servant de fond uniquement
    # - ref = couche servant de référence pour la saisie (snapping ou routing)
    # - edit, ref-edit = couche éditable sur le guichet
    # "clé xml":"valeur affichage boite"
    roleCleVal = {"edit": "Edition", "ref-edit": "Edition", "visu": "Visualisation", "ref": "Visualisation"}

    def __init__(self, context, parent=None):
        super(FormChargerGuichet, self).__init__(parent)
        self.setupUi(self)
        self.setFocus()

        self.context = context
        self.listLayers.clear()
        # Tuple contenant Rejected/Accepted pour la connexion Ripart et la liste des layers du groupe utilisateur
        connexionLayers = self.getInfosLayers()

        if connexionLayers[0] == "Rejected":
            raise Exception(u"Vous n'appartenez à aucun groupe, il n'y a pas de données à charger.")

        if connexionLayers[0] == "Accepted":
            self.listLayers = connexionLayers[1]
            # Les couches sont chargées dans l'ordre renvoyé dans geoaut_get.
            # Il faut donc inversé l'ordre pour retrouver le paramétrage de la carte du groupe
            self.listLayers.reverse()

        # Remplissage des différentes tables de couches
        self.setTableWidgetMonGuichet()
        self.setTableWidgetFondsGeoportail()
        self.setTableWidgetFondsGeoportailBis()
        #self.setTableWidgetAutresGeoservices()

        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)

        self.labelGroupeActif.setText("Groupe actif : {}".format(self.profilUser.geogroup.name))
        self.labelGroupeActif.setStyleSheet("QLabel {color : blue}")  ##ff0000

    def getInfosLayers(self):
        infosLayers = []

        if self.context.ripClient is None:
            connResult = self.context.getConnexionRipart()
            if not connResult:
                # la connexion a échoué ou l'utilisateur a cliqué sur Annuler
                return "Rejected", infosLayers

        if self.context.client is None:
            return "Rejected", infosLayers

        self.profilUser = self.context.client.getProfil()
        print("Profil : {0}, {1}".format(self.profilUser.geogroup.id,
                                         self.profilUser.geogroup.name))

        if len(self.profilUser.infosGeogroups) == 0:
            return "Rejected", infosLayers

        for infoGeogroup in self.profilUser.infosGeogroups:
            if infoGeogroup.group.id != self.profilUser.geogroup.id:
                continue

            print("Liste des couches du profil utilisateur")
            for layersAll in infoGeogroup.layers:
                print(layersAll.nom)
                infosLayers.append(layersAll)

        return "Accepted", infosLayers

    def setColonneCharger(self, tableWidget, row, column):
        itemCheckBox = QtWidgets.QTableWidgetItem()
        itemCheckBox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        # itemCheckBox.setCheckState(QtCore.Qt.Checked)
        itemCheckBox.setCheckState(QtCore.Qt.Unchecked)
        tableWidget.setItem(row, column, itemCheckBox)

    def setTableWidgetMonGuichet(self):
        # Entête
        entete = ["Nom de la couche", "Rôle", "Charger"]
        self.tableWidgetMonGuichet.setHorizontalHeaderLabels(entete)
        self.tableWidgetMonGuichet.setHorizontalHeaderLabels(entete)
        self.tableWidgetMonGuichet.setColumnWidth(0, 400)
        self.tableWidgetMonGuichet.setColumnWidth(1, 200)
        self.tableWidgetMonGuichet.setColumnWidth(2, 130)

        # Autres lignes de la table
        for layer in self.listLayers:
            if layer.type != cst.WFS:
                continue

            if layer.url.find(cst.COLLABORATIF) == -1:
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

        #self.tableWidgetMonGuichet.resizeColumnsToContents()

    def setTableWidgetFondsGeoportail(self):
        # Entête
        entete = ["Nom de la couche", "Rôle", "Charger"]
        self.tableWidgetFondsGeoportail.setHorizontalHeaderLabels(entete)
        self.tableWidgetFondsGeoportail.setColumnWidth(0, 400)
        self.tableWidgetFondsGeoportail.setColumnWidth(1, 200)
        self.tableWidgetFondsGeoportail.setColumnWidth(2, 130)

        # Autres lignes de la table
        for layer in self.listLayers:
            if layer.type != cst.GEOPORTAIL:
                continue

            if layer.nom not in self.profilUser.layersCleGeoportail:
                continue

            title = self.profilUser.layersCleGeoportail[layer.nom]
            if title is None:
                continue

            rowPosition = self.tableWidgetFondsGeoportail.rowCount()
            self.tableWidgetFondsGeoportail.insertRow(rowPosition)

            # Colonne "Nom de la couche"
            layerComposed = "{} ({})".format(title, layer.nom)
            item = QtWidgets.QTableWidgetItem(layerComposed)
            self.tableWidgetFondsGeoportail.setItem(rowPosition, 0, item)

            # Colonne "Rôle"
            role = layer.role
            if role in self.roleCleVal:
                item = QtWidgets.QTableWidgetItem(self.roleCleVal[role])
            else:
                item = QtWidgets.QTableWidgetItem("Pas de rôle, bizarre !")
            self.tableWidgetFondsGeoportail.setItem(rowPosition, 1, item)

            # Colonne "Charger"
            self.setColonneCharger(self.tableWidgetFondsGeoportail, rowPosition, 2)

        #self.tableWidgetFondsGeoportail.resizeColumnsToContents()

    def setTableWidgetFondsGeoportailBis(self):
        # Entête
        entete = ["Nom de la couche"]
        self.tableWidgetFondsGeoportailBis.setHorizontalHeaderLabels(entete)
        self.tableWidgetFondsGeoportailBis.setColumnWidth(0, 400)

        # Autres lignes de la table
        for layer in self.listLayers:
            if layer.type != cst.GEOPORTAIL:
                continue

            if layer.nom not in self.profilUser.layersCleGeoportail:
                rowPosition = self.tableWidgetFondsGeoportailBis.rowCount()
                self.tableWidgetFondsGeoportailBis.insertRow(rowPosition)

                # Colonne "Nom de la couche"
                layerComposed = "{} ({})".format(layer.description, layer.nom)
                item = QtWidgets.QTableWidgetItem(layerComposed)
                self.tableWidgetFondsGeoportailBis.setItem(rowPosition, 0, item)
                item.setForeground(QtGui.QColor(89, 89, 89))

        #self.tableWidgetFondsGeoportailBis.resizeColumnsToContents()

    def setTableWidgetAutresGeoservices(self):
        # Entête
        entete = ["Nom de la couche", "Type", "Charger"]
        self.tableWidgetAutresGeoservices.setHorizontalHeaderLabels(entete)

        # Autres lignes de la table
        for layer in self.listLayers:
            if layer.type != cst.WFS and layer.type != cst.WMS:
                continue

            if layer.url.find(cst.COLLABORATIF) != -1:
                continue
            if layer.url.find(cst.WXSIGN) != -1:
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

        self.tableWidgetAutresGeoservices.resizeColumnsToContents()

    def getLayersSelected(self, tableWidget, numCol):
        checked_list = []
        for i in range(tableWidget.rowCount()):
            item = tableWidget.item(i, numCol)
            if item.checkState() == QtCore.Qt.Checked:
                itemCouche = tableWidget.item(i, 0)
                checked_list.append(itemCouche.text())
        return checked_list

    def save(self):
        self.accept()
        layersQGIS = []
        layersChecked = [self.getLayersSelected(self.tableWidgetFondsGeoportail, 2),
                         self.getLayersSelected(self.tableWidgetMonGuichet, 2)]

        # Par exemple[['adresse'], ['GEOGRAPHICALGRIDSYSTEMS.MAPS', 'GEOGRAPHICALGRIDSYSTEMS.PLANIGN'], [], []]
        for layerChecked in layersChecked:
            for tmp in layerChecked:
                for layer in self.listLayers:
                    # tmp est sous la forme 'troncon_de_voie_ferree' ou 'Cartes IGN (GEOGRAPHICALGRIDSYSTEMS.MAPS)'
                    if '(' in tmp:
                        tmpName = tmp.split('(')
                        name = tmpName[1].replace(')', '')
                    else:
                        name = tmp
                    if name == layer.nom:
                        layersQGIS.append(layer)

        importGuichet = ImporterGuichet(self.context)
        importGuichet.doImport(layersQGIS)

    def cancel(self):
        self.reject()
        print("L'utilisateur est sorti de la boite Charger les couches du groupe")
