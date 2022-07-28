# -*- coding: utf-8 -*-
"""
Created on 25 nov. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""
import os

from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox
from qgis.PyQt import uic, QtWidgets
from PyQt5.QtCore import Qt
from qgis._core import QgsWkbTypes
from qgis.core import QgsProject, QgsVectorLayer
from .RipartHelper import RipartHelper

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormChoixGroupe_base.ui'))


class FormChoixGroupe(QtWidgets.QDialog, FORM_CLASS):
    """
    Dialogue pour le choix du groupe après la connexion au serveur
    et récupération du profil utilisateur
    """
    infosgeogroups = None
    bCancel = True
    context = None
    profile = None
    activeGroup = None
    newShapefilesDict = {}
    idChosenGroup = None
    nameChosenGroup = None

    def __init__(self, context, profile, activeGroup, parent=None):
        super(FormChoixGroupe, self).__init__(parent)
        print("init")
        self.setupUi(self)
        self.setFocus()
        self.setFixedSize(self.width(), self.height())
        self.context = context
        self.profile = profile
        self.activeGroup = activeGroup

        # Ajout des noms de groupes trouvés pour l'utilisateur
        self.setComboBoxGroup()

        # Ajout des zones de travail de type "polygone" susceptibles d'être utilisées comme zone d'extraction
        self.setComboBoxWorkZone()

        # Modification des intitulés des boutons
        self.setButtonsTextAndConnect()

    def setComboBoxGroup(self):
        print("setComboBoxGroup")
        self.infosgeogroups = self.profile.infosGeogroups
        for igg in self.infosgeogroups:
            self.comboBoxGroup.addItem(igg.group.name)
        if self.activeGroup is not None and self.activeGroup != "":
            self.comboBoxGroup.setCurrentText(self.activeGroup)

    def setComboBoxWorkZone(self):
        polyLayers = self.context.getMapPolygonLayers()
        polyList = [val for key, val in polyLayers.items() if val != RipartHelper.nom_Calque_Croquis_Polygone]
        self.comboBoxWorkZone.clear()
        self.comboBoxWorkZone.addItem("")
        self.comboBoxWorkZone.addItems(polyList)
        zone = RipartHelper.load_ripartXmlTag(self.context.projectDir, RipartHelper.xml_Zone_extraction, "Map").text
        index = self.comboBoxWorkZone.findText(zone, Qt.MatchFlag.MatchCaseSensitive)
        # si la couche servant de zone de travail a été supprimée dans la carte
        # alors on affiche une zone vide
        if index == -1:
            self.comboBoxWorkZone.setCurrentIndex(0)
        self.comboBoxWorkZone.setCurrentIndex(index)

    def setButtonsTextAndConnect(self):
        self.buttonBox.button(QDialogButtonBox.Save).setText("Continuer")
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.toolButtonShapeFile.clicked.connect(self.openShapeFile)

    def openShapeFile(self):
        formats = ["shp", "SHP"]
        filters = u"ESRI Shapefile (*.shp; *.SHP);;"
        shapefilePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Nouvelle zone de travail Shapefile', '.', filters)
        if shapefilePath != "":
            extension = os.path.splitext(shapefilePath)[1]
            if extension[1:] not in formats:
                message = u"Le fichier de type '" + extension + u"' n'est pas un fichier Shapefile."
                RipartHelper.showMessageBox(message)
            else:
                parts = shapefilePath.split('/')
                shapefileName = parts[len(parts)-1]
                # Nom du shapefile sans extension
                shapefileLayerName = shapefileName[0:len(shapefileName)-4]

                # On vérifie que le shapefile est surfacique
                vlayer = QgsVectorLayer(shapefilePath, shapefileLayerName, "ogr")
                if vlayer.geometryType() != QgsWkbTypes.GeometryType.PolygonGeometry:
                    QMessageBox.warning(self, "IGN Espace collaboratif", "La zone de travail ne peut être définie "
                                                                         "qu'à partir d'une couche d'objets "
                                                                         "surfaciques.")
                    return

                self.newShapefilesDict[shapefileLayerName] = shapefilePath
                self.comboBoxWorkZone.addItem(shapefileLayerName)
                self.comboBoxWorkZone.setCurrentText(shapefileLayerName)
        else:
            self.comboBoxWorkZone.setCurrentIndex(0)

    def importShapefile(self, shapefileLayerName):
        shapefilePath = self.newShapefilesDict[shapefileLayerName]
        if shapefilePath is not None:
            vlayer = QgsVectorLayer(shapefilePath, shapefileLayerName, "ogr")
            if not vlayer.isValid():
                print("Layer {0} failed to load!".format(shapefileLayerName))
            QgsProject.instance().addMapLayer(vlayer)

    # Bouton Continuer comme le nom de la fonction l'indique ;-)
    def save(self):
        # Sauvegarde du nom de la zone de travail
        spatialFilterLayerName = self.comboBoxWorkZone.currentText()
        RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_Zone_extraction, spatialFilterLayerName, "Map")

        # Création de la nouvelle couche shapefile
        if spatialFilterLayerName in self.newShapefilesDict:
            self.importShapefile(spatialFilterLayerName)

        index = self.comboBoxGroup.currentIndex()
        self.idChosenGroup = self.infosgeogroups[index].group.id
        self.nameChosenGroup = self.infosgeogroups[index].group.name

        self.accept()
        self.bCancel = False

    """
    Retourne l'identifiant du groupe de l'utilisateur
    en fonction de son choix
    """
    def getChosenGroupInfo(self):
        return self.idChosenGroup, self.nameChosenGroup

    # bouton Annuler
    def cancel(self):
        self.bCancel = True
        self.reject()
