import os
from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox
from qgis.PyQt import uic, QtWidgets, QtCore
from PyQt5.QtCore import Qt
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes
from .PluginHelper import PluginHelper
from .Contexte import Contexte
from .core.SQLiteManager import SQLiteManager
from .core.Layer import Layer
from .core import Constantes as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormChoixGroupe_base.ui'))


class FormChoixGroupe(QtWidgets.QDialog, FORM_CLASS):
    """
    Classe du dialogue pour le choix du groupe après la connexion au serveur
    et récupération du profil utilisateur.
    """

    def __init__(self, context, parent=None) -> None:
        """
        Constructeur de la boite de dialogue intitulée "Paramètres de travail"
        Initialisation des paramètres connus à partir du projet ou du fichier xml de configuration.

        NB : appeler dans Contexte.py, fonction : __connectToService

        :param context: le contexte du projet
        :type context: Contexte
        """
        super(FormChoixGroupe, self).__init__(parent)
        self.setupUi(self)
        self.setFocus()
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.__context = context
        self.__listNamesIdsCommunities = context.getListNameOfCommunities()
        self.__nameActiveCommunity = context.getActiveCommunityName()
        self.__newShapefilesDict = {}
        self.__bCancel = True
        self.__idSelectedCommunity = ''
        self.__nameSelectedCommunity = ''

        # Ajout des noms de groupes trouvés pour l'utilisateur
        self.setComboBoxGroup()

        # Ajout des zones de travail de type "polygone" susceptibles d'être utilisées comme zone d'extraction
        self.setComboBoxWorkZone()

        # Modification des intitulés des boutons
        self.setButtonsTextAndConnect()

    def getCancel(self) -> int:
        """
        Clic de l'utilisateur sur le bouton Annuler ou sur la croix de fermeture de la boite de dialogue.

        :return: 1 si l'utilisateur a fermé le dialogue, 0 sinon.
        """
        return self.__bCancel

    def setComboBoxGroup(self) -> None:
        """
        Remplissage de la liste déroulante "Groupe" avec les noms des groupes appartenant à l'utilisateur.
        """
        for nameid in self.__listNamesIdsCommunities:
            self.comboBoxGroup.addItem(nameid['name'])
        if self.__nameActiveCommunity is not None and self.__nameActiveCommunity != "":
            self.comboBoxGroup.setCurrentText(self.__nameActiveCommunity)

    def setComboBoxWorkZone(self) -> None:
        """
        Remplissage de la liste déroulante "Zone de travail" avec les noms des couches de type polygone présentes
        dans le projet. Le nom de la couche issue du fichier xml de configuration est mis en premier dans la liste
        si elle existe dans la carte, vide sinon.
        """
        index = -1
        polyLayers = self.__context.getMapPolygonLayers()
        polyList = [val for key, val in polyLayers.items() if val != cst.nom_Calque_Croquis_Polygone]
        self.comboBoxWorkZone.clear()
        self.comboBoxWorkZone.addItem("")
        self.comboBoxWorkZone.addItems(polyList)
        zone = PluginHelper.load_ripartXmlTag(self.__context.projectDir, PluginHelper.xml_Zone_extraction, "Map").text
        if zone is None:
            self.comboBoxWorkZone.setCurrentIndex(0)
        else:
            index = self.comboBoxWorkZone.findText(zone, Qt.MatchFlag.MatchCaseSensitive)
            # si le nom de la couche n'est pas dans la liste des couches existantes
            # dans le projet alors on affiche une zone vide
            if index == -1:
                self.comboBoxWorkZone.setCurrentIndex(0)
        if index > 0:
            self.comboBoxWorkZone.setCurrentIndex(index)

    def setButtonsTextAndConnect(self) -> None:
        """
        Modification de l'intitulé des boutons Save et Cancel.
        Connexion des signaux en réaction au clic sur un des boutons :
        - save, l'utilisateur veut continuer
        - cancel, l'utilisateur stoppe la procédure
        - shapeFile, l'utilisateur veut importer une couche shapefile comme zone de travail
        """
        self.buttonBox.button(QDialogButtonBox.Save).setText("Continuer")
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.toolButtonShapeFile.clicked.connect(self.openShapeFile)

    def openShapeFile(self) -> None:
        """
        L'utilisateur veut importer sa zone de travail à partir d'un fichier shapefile.
        L'outil propose l'import et vérifie si les conditions d'import d'une nouvelle zone sont respectées :
         - si c'est un fichier .shp
         - si la zone contenue dan sle fichier est de type polygone
         - si la zone existe déjà dans le projet
        """
        self.__newShapefilesDict.clear()
        formats = ["shp", "SHP"]
        filters = u"ESRI Shapefile (*.shp; *.SHP);;"
        shapefilePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Nouvelle zone de travail Shapefile', '.',
                                                                 filters)
        if shapefilePath != "":
            extension = os.path.splitext(shapefilePath)[1]
            if extension[1:] not in formats:
                message = u"Le fichier de type '" + extension + u"' n'est pas un fichier Shapefile."
                PluginHelper.showMessageBox(message)
            else:
                parts = shapefilePath.split('/')
                shapefileName = parts[len(parts) - 1]
                # Nom du shapefile sans extension
                shapefileLayerName = shapefileName[0:len(shapefileName) - 4]

                # On vérifie que le shapefile est surfacique
                vlayer = QgsVectorLayer(shapefilePath, shapefileLayerName, "ogr")
                if vlayer.geometryType() != QgsWkbTypes.GeometryType.PolygonGeometry:
                    QMessageBox.warning(self, cst.IGNESPACECO, "La zone de travail ne peut être définie "
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
                        reply = QMessageBox.question(self, cst.IGNESPACECO, message, QMessageBox.Yes,
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
                    self.__newShapefilesDict[shapefileLayerName] = shapefilePath
                    self.comboBoxWorkZone.addItem(shapefileLayerName)
                    self.comboBoxWorkZone.setCurrentText(shapefileLayerName)
        else:
            self.comboBoxWorkZone.setCurrentIndex(0)

    def importShapefile(self, shapefileLayerName) -> str:
        """
        Import du fichier shapefile avec quelques vérifications :
        - est-ce que le fichier existe ?
        - est ce que QGIS arrive à créer la couche QgsVectorLayer ?
        - est-ce que le système de coordonnées est renseigné ?

        :return: un message d'erreur correspondant aux vérifications, vide si l'import s'est bien passé
        """
        shapefilePath = self.__newShapefilesDict[shapefileLayerName]
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
            PluginHelper.showMessageBox(message)
        return ""

    def save(self) -> None:
        """
        Bouton Continuer de la boite de dialogue comme le nom de la fonction l'indique ;-)
        Remarques :
         - Si le nom de la zone de travail est vide → extraction complete
         - Si changement de groupe ou de zone de travail, suppression du groupe et de ses couches associées
         - Si import d'un shapefile, sauvegarde du nom de la zone de travail dans le fichier xml de configuration
          - Si l'import s'est mal passé, envoi d'une exception
        """
        # Si le nom de la zone de travail est vide → extraction complete
        spatialFilterLayerName = self.comboBoxWorkZone.currentText()
        if spatialFilterLayerName == '':
            message = "Vous n'avez pas spécifié de zone de travail. Lorsque vous importerez les signalements ou les " \
                      "données de votre groupe, le chargement se fera sur la totalité du territoire et sera " \
                      "probablement long. Voulez-vous continuer ?"
            reply = QMessageBox.question(self, cst.IGNESPACECO, message, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            self.__bCancel = False

        # Récupération du nom du groupe que l'utilisateur a choisi
        for nameid in self.__listNamesIdsCommunities:
            if nameid['name'] == self.comboBoxGroup.currentText():
                self.__idSelectedCommunity = nameid['id']
                break
        self.__nameSelectedCommunity = self.comboBoxGroup.currentText()
        self.accept()
        self.__bCancel = False

        # Est-ce qu'un changement de groupe ou de zone de travail est intervenu au moment de la sauvegarde ?
        # Si oui, il faut supprimer l'ensemble des couches et le groupe
        self.deleteLayersAndGroup(spatialFilterLayerName)

        # Création d'une nouvelle zone de travail si le dictionnaire est rempli avec un shape
        # que l'utilisateur a chargé avec le bouton 'Parcourir'
        message = ""
        if spatialFilterLayerName in self.__newShapefilesDict:
            message = self.importShapefile(spatialFilterLayerName)
            # Sauvegarde du nom de la nouvelle zone de travail
            PluginHelper.setXmlTagValue(self.__context.projectDir, PluginHelper.xml_Zone_extraction,
                                        spatialFilterLayerName,
                                        "Map")
        # si spatialFilterLayerName est rempli, la zone existe déjà
        elif spatialFilterLayerName != '':
            PluginHelper.setXmlTagValue(self.__context.projectDir, PluginHelper.xml_Zone_extraction,
                                        spatialFilterLayerName,
                                        "Map")

        # si l'import s'est mal passé, envoi d'une exception
        if message != "":
            print(message)
            raise Exception(message)

    def getIdAndNameFromSelectedCommunity(self) -> ():
        """
        :return: l'identifiant et le nom du groupe de l'utilisateur en fonction de son choix
        """
        return self.__idSelectedCommunity, self.__nameSelectedCommunity

    def cancel(self) -> None:
        """
        En réaction au clic sur le bouton Annuler
        """
        self.__bCancel = True
        self.reject()

    def deleteLayersAndGroup(self, userWorkZone) -> None:
        """
        Suppression du groupe et de ses couches associées, si nouvelle zone de travail ou nouveau groupe.
        NB : les couches d'un projet sont rassemblées sous un groupe dont le nom est préfixé par "[ESPACE CO] xxxx"
        NB : mise à jour du xml de configuration si nouvelle zone ou nouveau groupe

        :param userWorkZone: la zone de travail de l'utilisateur (un surfacique permettant de limiter
                             une extraction de données
        :type userWorkZone: str
        """
        # Si c'est un projet nouvellement créé, il faut vérifier si la table des tables existe
        if not SQLiteManager.isTableExist(cst.TABLEOFTABLES):
            return

        # Le nom de la zone stockée dans le xml .../xxx_espaceco.xml
        storedWorkZone = PluginHelper.load_ripartXmlTag(self.__context.projectDir,
                                                        PluginHelper.xml_Zone_extraction,
                                                        "Map").text

        bNewGroup = self.__nameActiveCommunity != self.__nameSelectedCommunity
        bNewZone = storedWorkZone != userWorkZone
        # Si rien n'a changé, on sort
        if not bNewGroup and not bNewZone:
            return

        # Récupération de l'ensemble des noms des couches chargées dans le projet QGIS
        projectLayers = self.__context.getAllMapLayers()
        layersInProject = []
        for c, v in projectLayers.items():
            tmp = Layer()
            tmp.setName(c)
            layersInProject.append(tmp)

        # On regarde si le projet QGIS contient des couches Espace co
        bEspaceCoLayersInProject = False
        root = QgsProject.instance().layerTreeRoot()
        nodesGroup = root.findGroups()
        newGroup = None
        for ng in nodesGroup:
            # Dans le cas ou le nom du groupe actif, du groupe dans la carte et celui stocké dans le xml sont tous
            # les trois différents et qu'il n'y a qu'un seul groupe [ESPACE CO] par construction, le plus simple
            # est de chercher le prefixe
            if ng.name().find(cst.ESPACECO) != -1:
                bEspaceCoLayersInProject = True
                newGroup = ng
                break

        # Si l'utilisateur a changé de groupe, on supprime l'ancien (s'il existe dans le projet)
        # et toutes les couches associées. On supprime la base SQLite et on la recrée
        if bNewGroup:
            if newGroup is not None:
                message = "Vous avez choisi un nouveau groupe. Toutes les données du groupe {0} vont être " \
                      "supprimées. Voulez-vous continuer ?".format(newGroup.name())
                reply = QMessageBox.question(self, cst.IGNESPACECO, message, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    root.removeChildNode(newGroup)
                    self.removeTablesSQLite(layersInProject)
                    QgsProject.instance().write()
                else:
                    self.__bCancel = True
                PluginHelper.setXmlTagValue(self.__context.projectDir, PluginHelper.xml_GroupeActif,
                                            self.__nameSelectedCommunity, "Serveur")

        # Si l'utilisateur a changé de zone de travail, il faut supprimer les couches
        if bNewZone:
            # Récupération de l'ensemble des noms des couches chargées dans la table des tables
            layersFromTableOfTables = SQLiteManager.selectLayersFromTableOfTables()
            layersInTT = []
            for lftot in layersFromTableOfTables:
                layersInTT.append(lftot[0])

            # Si l'utilisateur n'a pas été déjà averti de la suppression des données via le changement de groupe,
            # on l'informe
            if not bNewGroup and bEspaceCoLayersInProject:
                message = "Vous avez choisi une nouvelle zone de travail. Les couches Espace collaboratif " \
                          " déjà chargées dans votre projet vont être supprimées. Voulez-vous continuer ?"
                reply = QMessageBox.question(self, cst.IGNESPACECO, message, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.__context.removeLayersFromProject(layersInProject, layersInTT, False)
                    PluginHelper.setXmlTagValue(self.__context.projectDir, PluginHelper.xml_Zone_extraction,
                                                userWorkZone, "Map")
                    self.removeTablesSQLite(layersInProject)
                else:
                    self.__bCancel = True

    def removeTablesSQLite(self, layers) -> None:
        """
        Vide et supprime une (ou plusieurs) table(s) de la base SQLite du projet.
        NB : les tables portent le nom des couches par simplification.

        :param layers: liste des tables à supprimer
        :type layers: list
        """
        for layer in layers:
            SQLiteManager.emptyTable(layer.name())
            SQLiteManager.deleteTable(layer.name())
        SQLiteManager.emptyTable(cst.TABLEOFTABLES)
        SQLiteManager.vacuumDatabase()
