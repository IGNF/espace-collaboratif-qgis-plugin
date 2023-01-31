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
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes
from .RipartHelper import RipartHelper
from .core.SQLiteManager import SQLiteManager
from .core.Layer import Layer

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
        self.infosgeogroups = self.profile.infosGeogroups
        for igg in self.infosgeogroups:
            self.comboBoxGroup.addItem(igg.group.name)
        if self.activeGroup is not None and self.activeGroup != "":
            self.comboBoxGroup.setCurrentText(self.activeGroup)

    def setComboBoxWorkZone(self):
        index = -1
        polyLayers = self.context.getMapPolygonLayers()
        polyList = [val for key, val in polyLayers.items() if val != RipartHelper.nom_Calque_Croquis_Polygone]
        self.comboBoxWorkZone.clear()
        self.comboBoxWorkZone.addItem("")
        self.comboBoxWorkZone.addItems(polyList)
        zone = RipartHelper.load_ripartXmlTag(self.context.projectDir, RipartHelper.xml_Zone_extraction, "Map").text
        if zone is None:
            self.comboBoxWorkZone.setCurrentIndex(0)
        else:
            index = self.comboBoxWorkZone.findText(zone, Qt.MatchFlag.MatchCaseSensitive)
            # si le nom de la couche stockée dans le xml n'est pas dans la liste des couches existantes
            # dans le projet alors on affiche une zone vide
            if index == -1:
                self.comboBoxWorkZone.setCurrentIndex(0)
        if index > 0:
            self.comboBoxWorkZone.setCurrentIndex(index)

    def setButtonsTextAndConnect(self):
        self.buttonBox.button(QDialogButtonBox.Save).setText("Continuer")
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.toolButtonShapeFile.clicked.connect(self.openShapeFile)

    def openShapeFile(self):
        self.newShapefilesDict.clear()
        formats = ["shp", "SHP"]
        filters = u"ESRI Shapefile (*.shp; *.SHP);;"
        shapefilePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Nouvelle zone de travail Shapefile', '.',
                                                                 filters)
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

                # On vérifie que le shapefile n'est pas déjà dans la liste des zones
                bAddItem = True
                allItems = [self.comboBoxWorkZone.itemText(i) for i in range(self.comboBoxWorkZone.count())]
                index = 0
                for item in allItems:
                    if item == shapefileLayerName:
                        bAddItem = False
                        self.comboBoxWorkZone.setCurrentIndex(index)
                        message = "La zone de travail [{}] existe déjà dans la carte. Voulez-vous la supprimer ?\n" \
                                  "Le nouveau fichier shape sera importé.".format(shapefileLayerName)
                        reply = QMessageBox.question(self, 'IGN Espace Collaboratif', message, QMessageBox.Yes,
                                                     QMessageBox.No)
                        if reply == QMessageBox.Yes:
                            removeLayers = QgsProject.instance().mapLayersByName(shapefileLayerName)
                            if len(removeLayers) == 1:
                                QgsProject.instance().removeMapLayer(removeLayers[0].id())
                                QgsProject.instance().write()
                                bAddItem = True
                        break
                    index += 1

                if bAddItem:
                    self.newShapefilesDict[shapefileLayerName] = shapefilePath
                    self.comboBoxWorkZone.addItem(shapefileLayerName)
                    self.comboBoxWorkZone.setCurrentText(shapefileLayerName)
        else:
            self.comboBoxWorkZone.setCurrentIndex(0)

    def importShapefile(self, shapefileLayerName):
        shapefilePath = self.newShapefilesDict[shapefileLayerName]
        if shapefilePath is None:
            return "Impossible d'importer le fichier {0}".format(shapefilePath)

        vlayer = QgsVectorLayer(shapefilePath, shapefileLayerName, "ogr")
        if not vlayer.isValid():
            return "Layer {0} failed to load!".format(shapefileLayerName)

        root = QgsProject.instance().layerTreeRoot()
        # False pour que la couche ne soit pas immédiatement ajoutée au gestionnaire de couches
        QgsProject.instance().addMapLayer(vlayer, False)
        root.insertLayer(-1, vlayer)
        # Il faut sauvegarder le projet
        QgsProject.instance().write()
        # si le système de coordonnées de référence assigné (SCR) est vide, il faut le signaler à l'utilisateur
        sourcecrs = vlayer.sourceCrs()
        if sourcecrs.isValid() is False:
            message = "Le système de coordonnées de référence (SCR) n'est pas assigné pour la couche [{0}]. Veuillez " \
                      "le renseigner dans [Propriétés...][Couche][Système de Coordonnées de Référence " \
                      "assigné]".format(vlayer.name())
            RipartHelper.showMessageBox(message)
        return ""

    # Bouton Continuer comme le nom de la fonction l'indique ;-)
    def save(self):
        # Si le nom de la zone de travail est vide --> extraction complete
        spatialFilterLayerName = self.comboBoxWorkZone.currentText()
        if spatialFilterLayerName == '':
            message = "Vous n'avez pas spécifié de zone de travail. Lorsque vous importerez les signalements ou les " \
                      "données de votre groupe, le chargement se fera sur la totalité du territoire et sera " \
                      "probablement long. Voulez-vous continuer ?"
            reply = QMessageBox.question(self, 'IGN Espace Collaboratif', message, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            self.bCancel = False

        # Récupération du nom du groupe que l'utilisateur a choisi
        index = self.comboBoxGroup.currentIndex()
        self.idChosenGroup = self.infosgeogroups[index].group.id
        self.nameChosenGroup = self.infosgeogroups[index].group.name
        self.accept()
        self.bCancel = False

        # Est-ce qu'un changement de groupe ou de zone de travail est intervenu au moment de la sauvegarde ?
        # Si oui, il faut supprimer l'ensemble des couches et le groupe
        self.deleteLayersAndGroup(spatialFilterLayerName)

        # Création d'une nouvelle zone de travail si le dictionnaire est rempli avec un shape
        # que l'utilisateur a chargé avec le bouton 'Parcourir'
        message = ""
        if spatialFilterLayerName in self.newShapefilesDict:
            message = self.importShapefile(spatialFilterLayerName)
            # Sauvegarde du nom de la nouvelle zone de travail
            RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_Zone_extraction,
                                        spatialFilterLayerName,
                                        "Map")

        # si l'import s'est mal passé, envoi d'une exception
        if message != "":
            print(message)
            raise Exception(message)

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

    def deleteLayersAndGroup(self, userWorkZone):
        # Le nom de la zone stockée dans le xml .../xxx_espaceco.xml
        storedWorkZone = RipartHelper.load_ripartXmlTag(self.context.projectDir,
                                                        RipartHelper.xml_Zone_extraction,
                                                        "Map").text

        # Si rien n'a changé, on sort
        if self.activeGroup == self.nameChosenGroup and storedWorkZone == userWorkZone:
            return

        # Si l'utilisateur a changé de groupe, on supprime l'ancien
        if self.activeGroup != self.nameChosenGroup:
            RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_GroupeActif, self.nameChosenGroup,
                                        "Serveur")
            # Quels sont les groupes du project ?
            root = QgsProject.instance().layerTreeRoot()
            nodesGroup = root.findGroups()
            for ng in nodesGroup:
                if ng.name() == self.activeGroup:
                    message = "Le groupe [{0}] va être supprimé du projet ainsi que toutes ses couches liées, " \
                              "voulez-vous continuez ?".format(self.activeGroup)
                    reply = QMessageBox.question(self, 'IGN Espace Collaboratif', message, QMessageBox.Yes, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        root.removeChildNode(ng)
                        QgsProject.instance().write()
                    break

        # Si l'utilisateur a changé de zone de travail, il faut supprimer les couches
        if storedWorkZone != userWorkZone:
            # Récupération de l'ensemble des noms des couches chargées dans le projet QGIS
            projectLayers = self.context.getAllMapLayers()
            # Récupération de l'ensemble des noms des couches chargées dans la table des tables ?
            layersFromTableOfTables = SQLiteManager.selectLayersFromTableOfTables()
            layersInTT = []
            for lftot in layersFromTableOfTables:
                layersInTT.append(lftot[0])
            layersInProject = []
            for lp in projectLayers:
                tmp = Layer()
                tmp.nom = lp
                layersInProject.append(tmp)
            self.context.removeLayersFromProject(layersInProject, layersInTT)
            RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_Zone_extraction, userWorkZone, "Map")
