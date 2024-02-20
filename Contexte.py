# -*- coding: utf-8 -*-
"""
Created on 29 sept. 2015
Updated on 30 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import spatialite_connect
from qgis.core import QgsCoordinateReferenceSystem, QgsFeatureRequest, QgsCoordinateTransform, QgsGeometry,\
    QgsVectorLayer, QgsRasterLayer, QgsProject, QgsWkbTypes, QgsLayerTreeGroup, QgsDataSourceUri

import os.path
import shutil
import ntpath
import configparser

from .core.Community import Community
from .PluginHelper import PluginHelper
from .core.RipartLoggerCl import RipartLogger
from .core.ClientHelper import ClientHelper
from .core.SketchAttributes import SketchAttributes
from .core.Point import Point
from .core.Sketch import Sketch
from .FormConnection import FormConnectionDialog
from .core import Constantes as cst
from .Import_WMTS import importWMTS
from .core.GuichetVectorLayer import GuichetVectorLayer
from .core.EditFormFieldFromAttributes import EditFormFieldFromAttributes
from .core.WfsGet import WfsGet
from .core.SQLiteManager import SQLiteManager
from .core.ProgressBar import ProgressBar


class Contexte(object):
    """
    Contexte et initialisation de la "session"
    """
    # instance du Contexte
    instance = None

    # identifiants de connexion
    login = ""
    pwd = ""
    urlHostEspaceCo = ""
    profil = None


    # client pour le service RIPart
    client = None

    # fenêtre de connexion
    loginWindow = None

    # le répertoire du projet qgis
    projectDir = ""

    # le nom du fichier (projet qgis)
    projectFileName = ""

    # chemin vers la base de donnée sqlite
    dbPath = ""

    # répertoire du plugin
    plugin_path = os.path.dirname(os.path.realpath(__file__))

    # fichier xml de configuration
    ripartXmlFile = ""

    # objets QGis
    QObject = None
    QgsProject = None
    iface = None

    # map canvas,la carte courante
    mapCan = None

    # Le système géodésique employé par le service Ripart (WGS84; EPSG:2154)
    spatialRef = None

    # connexion à la base de données
    conn = None

    # proxy
    proxy = None

    # le logger
    logger = None

    # les statistiques
    guichetLayers = []

    # extension sqlite
    sqlite_ext = ".sqlite"

    def __init__(self, QObject, QgsProject):
        """
        Constructor

        Initialisation du contexte
        """
        self.QObject = QObject
        self.QgsProject = QgsProject
        self.mapCan = QObject.iface.mapCanvas()
        self.iface = QObject.iface
        self.login = ""
        self.pwd = ""
        self.auth = {'login': self.login, 'password': self.pwd}
        self.urlHostEspaceCo = ""
        self.profil = None
        self.logger = RipartLogger("Contexte").getRipartLogger()
        self.spatialRef = QgsCoordinateReferenceSystem(cst.EPSGCRS4326, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
        self.dbPath = SQLiteManager.getBaseSqlitePath()
        # version in metadata
        cst.RIPART_CLIENT_VERSION = self.getMetadata()
        self.__userCommunity = None
        self.__activeCommunityName = ''

        try:
            # set du répertoire et fichier du projet qgis
            self.setProjectParams()

            # contrôle l'existence du fichier de configuration
            self.checkConfigFile()

            # set de la base de données
            self.createDatabaseSQLite()

            # Création des tables de signalements et de croquis
            # self.createTablesReportsAndSketchs()

            # set des fichiers de style
            self.copyRipartStyleFiles()

            # retrouve les formats de fichiers joints acceptés à partir du fichier formats.txt.
            formatFile = open(os.path.join(self.plugin_path, 'files', 'formats.txt'), 'r')
            lines = formatFile.readlines()
            self.formats = [x.split("\n")[0] for x in lines]

        except Exception as e:
            self.logger.error("init contexte:" + format(e))
            raise

    def getUserCommunity(self) -> Community:
        return self.__userCommunity

    def setUserCommunity(self, community) -> None:
        self.__userCommunity = community

    def setActiveCommunityName(self, name) -> None:
        self.__activeCommunityName = name

    def getActiveCommunityName(self) -> str:
        return self.__activeCommunityName

    def getMetadata(self):
        config = configparser.RawConfigParser()
        config.read(self.plugin_path + '\\metadata.txt')
        return config.get('general', 'version')

    @staticmethod
    def IsLayerInMap(layerName):
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == layerName:
                return True
        return False

    @staticmethod
    def getInstance(QObject=None, QgsProject=None):
        """
        Retourne l'instance du Contexte
        """
        if not Contexte.instance or (Contexte.instance.projectDir != QgsProject.instance().homePath() or
                                     ntpath.basename(QgsProject.instance().fileName()) not in [
                                         Contexte.instance.projectFileName + ".qgs",
                                         Contexte.instance.projectFileName + ".qgz"]):
            Contexte.instance = Contexte._createInstance(QObject, QgsProject)
        return Contexte.instance

    @staticmethod
    def _createInstance(QObject, QgsProject):
        """
        Création de l'instance du contexte
        """
        try:
            Contexte.instance = Contexte(QObject, QgsProject)
            Contexte.instance.logger.debug("Nouvelle instance de contexte créée")
        except Exception as e:
            Contexte.instance = None
            return None
        return Contexte.instance

    def setProjectParams(self):
        """set des paramètres du projet
        """
        self.projectDir = QgsProject.instance().homePath()
        if self.projectDir == "":
            PluginHelper.showMessageBox(
                u"Votre projet QGIS doit être enregistré avant de pouvoir utiliser le plugin de l'espace collaboratif")
            raise Exception(u"Projet QGIS non enregistré")

        # nom du fichier du projet enregistré
        fname = ntpath.basename(QgsProject.instance().fileName())

        nbPoints = fname.count(".")
        if nbPoints != 1:
            PluginHelper.showMessageBox(
                u"Le nom de votre projet QGIS ne doit pas contenir de point en dehors de son extension (.qgz). Merci "
                u"de le renommer.")
            raise Exception(u"Nom de projet QGIS non valide")

        self.projectFileName = fname[:fname.find(".")]

    def checkConfigFile(self):
        """
        Contrôle de l'existence du fichier de configuration
        """
        ripartxml = self.projectDir + os.path.sep + PluginHelper.getConfigFile()
        if not os.path.isfile(ripartxml):
            try:
                shutil.copy(self.plugin_path + os.path.sep + PluginHelper.ripart_files_dir + os.path.sep +
                            PluginHelper.nom_Fichier_Parametres_Ripart, ripartxml)
                self.logger.debug("Copy {}".format(PluginHelper.nom_Fichier_Parametres_Ripart))
                new_file = os.path.join(self.projectDir, PluginHelper.getConfigFile())
                os.rename(ripartxml, new_file)
            except Exception as e:
                self.logger.error(
                    "No {} found in plugin directory".format(PluginHelper.nom_Fichier_Parametres_Ripart) + format(e))
                raise Exception("Le fichier de configuration " + PluginHelper.nom_Fichier_Parametres_Ripart +
                                " n'a pas été trouvé.")

    def copyRipartStyleFiles(self):
        """
        Copie les fichiers de styles (pour les remarques et croquis ripart)
        """
        styleFilesDir = self.projectDir + os.path.sep + PluginHelper.qmlStylesDir

        PluginHelper.copy(self.plugin_path + os.path.sep + PluginHelper.ripart_files_dir + os.path.sep +
                          PluginHelper.qmlStylesDir, styleFilesDir)

    def getVisibilityLayersFromGroupeActif(self):
        """
        Retourne True si au moins une couche est éditable
        False sinon
        """
        if self.__activeCommunityName is None or self.__activeCommunityName == "":
            return False

        if self.profil is None:
            return False

        for infoGeogroup in self.profil.infosGeogroups:
            if infoGeogroup.getName() != self.__activeCommunityName:
                continue

            for layer in infoGeogroup.layers:
                if layer.role == "edit" or layer.role == "ref-edit":
                    return True
        return False

    def getConnexionEspaceCollaboratif(self, newLogin=False):
        """Connexion à l'espace collaboratif

        :param newLogin: booléen indiquant si on fait un nouveau login (fonctionnalité "Connexion à l'espace collaboratif")
        :type newLogin: boolean

        :return 1 si la connexion a réussie, 0 si elle a échouée, -1 s'il y a eu une erreur (Exception)
        :rtype int
        """
        self.logger.debug("getConnexionEspaceCollaboratif")
        try:
            self.urlHostEspaceCo = PluginHelper.load_ripartXmlTag(self.projectDir, PluginHelper.xml_UrlHost,
                                                                  "Serveur").text
            self.logger.debug("this.urlHostEspaceCo " + self.urlHostEspaceCo)

        except Exception as e:
            self.logger.error("URLHOST inexistant dans fichier configuration")
            PluginHelper.showMessageBox(u"L'url du serveur doit être renseignée dans la configuration avant de "
                                        u"pouvoir se connecter.\n(Aide>Configurer le plugin>Adresse de connexion "
                                        u"...)")
            return

        self.loginWindow = FormConnectionDialog(self)
        self.loginWindow.setWindowTitle("Connexion à {0}".format(self.urlHostEspaceCo))
        loginXmlNode = PluginHelper.load_ripartXmlTag(self.projectDir, PluginHelper.xml_Login, "Serveur")
        if loginXmlNode is None:
            self.login = ""
        else:
            self.login = PluginHelper.load_ripartXmlTag(self.projectDir, PluginHelper.xml_Login, "Serveur").text

        xmlproxy = PluginHelper.load_ripartXmlTag(self.projectDir, PluginHelper.xml_proxy, "Serveur").text
        if xmlproxy is not None and str(xmlproxy).strip() != '':
            self.proxy = {'https': str(xmlproxy).strip()}
        else:
            self.proxy = None

        xmlgroupeactif = PluginHelper.load_ripartXmlTag(self.projectDir, PluginHelper.xml_GroupeActif, "Serveur")
        if xmlgroupeactif is not None:
            self.__activeCommunityName = PluginHelper.load_ripartXmlTag(self.projectDir, PluginHelper.xml_GroupeActif,
                                                              "Serveur").text
            if self.__activeCommunityName is not None:
                self.logger.debug("Contexte.__activeCommunityName " + self.__activeCommunityName)

        if self.login == "" or self.pwd == "" or newLogin:
            self.loginWindow.setLineEditLogin(self.login)

        # Le résultat de la connexion est initialisé à -1.
        # Tant qu'il reste à -1, c'est que le formulaire de connexion a renvoyé une exception (mauvais mot de passe, pb
        # de proxy etc.). Dans ce cas-là, on rouvre le formulaire pour que l'utilisateur essaie de se reconnecter.
        connectionResult = -1
        while connectionResult < 0:
            self.loginWindow.exec_()
            connectionResult = self.loginWindow.getConnectionResult()
            self.auth = self.loginWindow.getAuthentification()
        return connectionResult

    # Création de la base de données spatialite si elle n'existe pas
    def createDatabaseSQLite(self):
        if not os.path.isfile(self.dbPath):
            try:
                shutil.copy(self.plugin_path + os.path.sep + PluginHelper.ripart_files_dir + os.path.sep +
                            PluginHelper.ripart_db, self.dbPath)
                self.logger.debug("copy espaceco.sqlite")
            except Exception as e:
                self.logger.error("no espaceco.sqlite found in plugin directory" + format(e))
                raise e

    # Création des tables de signalements et de croquis
    def createTablesReportsAndSketchs(self):
        # Création de la table des signalements et de croquis
        for table in PluginHelper.reportSketchLayersName:
            if SQLiteManager.isTableExist(table):
                SQLiteManager.emptyTable(table)
                SQLiteManager.deleteTable(table)
            if table == PluginHelper.nom_Calque_Signalement:
                SQLiteManager.createReportTable()
            elif table in PluginHelper.sketchLayers:
                SQLiteManager.createSketchTable(table, PluginHelper.sketchLayers[table])
        SQLiteManager.vacuumDatabase()

    def importWFS(self, layer):
        # Création éventuelle de la table SQLite liée à la couche
        sqliteManager = SQLiteManager()

        # Si la table du nom de la couche existe,
        # elle est vidée, détruite et recréée
        if SQLiteManager.isTableExist(layer.name):
            SQLiteManager.emptyTable(layer.name)
            SQLiteManager.deleteTable(layer.name)
        bColumnDetruitExist = sqliteManager.createTableFromLayer(layer)

        # Création de la source pour la couche dans la carte liée à la table SQLite
        uri = self.getUriDatabaseSqlite()
        self.logger.debug(uri.uri())
        uri.setDataSource('', layer.name, layer.geometryName)
        uri.setSrid(str(cst.EPSGCRS4326))
        geomDim = ""
        geomType = ""
        for attribute in layer.attributes:
            if attribute['name'] != layer.geometryName:
                continue
            geomDim = attribute['is3d']
            geomType = attribute['type']
        parameters = {'uri': uri.uri(), 'name': layer.name, 'genre': 'spatialite', 'databasename': layer.databasename,
                      'sqliteManager': sqliteManager, 'idName': layer.idName,
                      'geometryName': layer.geometryName, 'geometryDimension': geomDim,
                      'geometryType': geomType}

        vlayer = GuichetVectorLayer(parameters)
        # vlayer = QgsVectorLayer(uri.uri(), layer.name, 'spatialite')
        vlayer.setCrs(QgsCoordinateReferenceSystem(cst.EPSGCRS4326, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId))
        return vlayer, bColumnDetruitExist

    def addGuichetLayersToMap(self, guichet_layers, bbox, nameGroup):
        """
        Add guichet layers to the current map
        """
        global progress
        try:
            # Quelles sont les cartes chargées dans le projet QGIS courant
            maplayers = self.getAllMapLayers()
            root = self.QgsProject.instance().layerTreeRoot()

            # Le groupe existe t-il dans le projet
            nodeGroup = None
            nodesGroup = root.findGroups()
            for ng in nodesGroup:
                # Si le groupe existe déjà, on sort
                tmp = ng.name().removeprefix(cst.ESPACECO)
                if tmp == nameGroup:
                    nodeGroup = ng
                    break

            # Si le groupe n'existe pas et que des couches doivent être chargées
            # alors il y a création du groupe dans le projet
            nbLayersWFS = 0
            for layer in guichet_layers:
                if layer.type == cst.WFS:
                    nbLayersWFS += 1
            if nodeGroup is None and nbLayersWFS != 0:
                newNode = QgsLayerTreeGroup(nameGroup)
                # Ajout d'un préfixe pour distinguer les groupes collaboratifs
                newNode.setName("{0}{1}".format(cst.ESPACECO, newNode.name()))
                root.insertChildNode(0, newNode)
                nodeGroup = root.findGroup("{0}{1}".format(cst.ESPACECO, nameGroup))

            # Destruction de toutes les couches existantes si ce n'est pas fait manuellement par l'utilisateur
            # sauf celui-ci à cliqué sur Non à la demande de destruction dans ce cas la fonction retourne False
            if not self.removeLayersFromProject(guichet_layers, maplayers):
                return

            endMessage = ''
            if len(guichet_layers) == 0:
                endMessage = 'Pas de couches sélectionnées, fin du chargement.\n'

            progress = ProgressBar(len(guichet_layers), cst.LOADINGTEXTPROGRESS)
            i = 0
            for layer in guichet_layers:
                i += 1
                progress.setValue(i)
                '''
                Ajout des couches WFS selectionnées dans "Mon guichet"
                '''
                if layer.type == cst.WFS:
                    sourceLayer = self.importWFS(layer)
                    if not sourceLayer[0].isValid():
                        endMessage += "Layer {} failed to load !\n".format(layer.name)
                        continue
                    endMessage += self.formatLayer(layer, sourceLayer[0], nodeGroup, bbox, sourceLayer[1])
                    endMessage += "\n"

                '''
                Ajout des couches WMTS selectionnées dans "Mon guichet"
                '''
                if layer.type == cst.WMTS:
                    importWmts = importWMTS(self, layer)
                    titleLayer_uri = importWmts.getWtmsUrlParams(layer.geoservice['layers'])
                    if 'Exception' in titleLayer_uri[0]:
                        endMessage += "{0} : {1}\n\n".format(layer.name, titleLayer_uri[1])
                        continue
                    rlayer = QgsRasterLayer(titleLayer_uri[1], titleLayer_uri[0], 'wms')
                    if not rlayer.isValid():
                        endMessage = "Layer {} failed to load !".format(rlayer.name())
                        continue

                    self.QgsProject.instance().addMapLayer(rlayer, False)
                    # Insertion à la fin avec -1
                    root.insertLayer(-1, rlayer)
                    self.logger.debug("Layer {} added to map".format(rlayer.name()))
                    message = "Couche {0} ajoutée à la carte.\n\n".format(rlayer.name())
                    print(message)
                    endMessage += message
            progress.close()

            # Rafraichissement de la carte
            self.mapCan.refresh()
            QMessageBox.information(self.iface.mainWindow(), cst.IGNESPACECO, endMessage)

        except Exception as e:
            progress.close()
            self.logger.error(format(e))
            self.iface.messageBar(). \
                pushMessage("Remarque",
                            str(e),
                            level=1, duration=3)
            print(str(e))

    def hideColumn(self, layer, columnName):
        config = layer.attributeTableConfig()
        columns = config.columns()
        for column in columns:
            if column.name == columnName:
                column.hidden = True
                break
        config.setColumns(columns)
        layer.setAttributeTableConfig(config)

    def removeLayersFromProject(self, guichet_layers, maplayers, bAskForConfirmation=True):
        tmp = ''
        removeLayers = []
        for layer in guichet_layers:
            if layer.name in maplayers:
                removeLayers.append(layer.name)
                tmp += "{}, ".format(layer.name)
        return self.removeLayersById(removeLayers, tmp, bAskForConfirmation)

    def removeLayersById(self, removeLayers, tmp, bAskForConfirmation):
        if len(removeLayers) == 0:
            return True

        if bAskForConfirmation:
            if len(removeLayers) == 1:
                message = "La couche [{}] existe déjà, elle va être mise à jour.\nVoulez-vous continuer ?".format(
                    tmp[:-2])
            else:
                message = "Les couches [{}] existent déjà, elles vont être mises à jour.\nVoulez-vous continuer ?".format(
                    tmp[:-2])
            reply = QMessageBox.question(self.iface.mainWindow(), cst.IGNESPACECO, message, QMessageBox.Yes,
                                         QMessageBox.No)
            if reply == QMessageBox.No:
                return False

        layerIds = []
        for removeLayer in removeLayers:
            listLayers = self.QgsProject.instance().mapLayersByName(removeLayer)
            for lLayer in listLayers:
                layerIds.append(lLayer.id())

        self.QgsProject.instance().removeMapLayers(layerIds)
        return True

    def formatLayer(self, layer, newVectorLayer, nodeGroup, bbox, bColumnDetruitExist):
        geometryName = layer.geometryName
        newVectorLayer.isStandard = layer.isStandard
        idNameForDatabase = layer.idName
        newVectorLayer.idNameForDatabase = idNameForDatabase
        newVectorLayer.geometryNameForDatabase = geometryName
        newVectorLayer.databasename = layer.databasename
        newVectorLayer.srid = layer.srid
        newVectorLayer.geometryDimensionForDatabase = layer.is3d
        newVectorLayer.geometryTypeForDatabase = layer.geometryType

        # Remplissage de la table SQLite liée à la couche
        parameters = {'databasename': layer.databasename, 'layerName': layer.name,
                      'sridLayer': layer.srid, 'role': layer.role, 'isStandard': layer.isStandard,
                      'is3D': layer.is3d, 'geometryName': geometryName, 'sridProject': cst.EPSGCRS4326,
                      'bbox': bbox, 'detruit': bColumnDetruitExist, 'numrec': "0",
                      'urlHostEspaceCo': self.urlHostEspaceCo, 'authentification': self.auth,
                      'proxy': self.proxy, 'databaseid': layer.databaseId, 'tableid': layer.table
                      }
        wfsGet = WfsGet(parameters)
        maxNumrecMessage = wfsGet.gcms_get(True)

        # Stockage des données utiles à la synchronisation d'une couche après fermeture/ouverture de QGIS
        valStandard = 1
        if not layer.isStandard:
            valStandard = 0
        dim = 0
        if layer.is3d:
            dim = 1

        parametersForTableOfTables = {'layer': layer.name, 'idName': idNameForDatabase, 'standard': valStandard,
                                      'database': layer.databasename, 'srid': layer.srid,
                                      'geometryName': geometryName, 'geometryDimension': dim,
                                      'geometryType': layer.geometryType,
                                      'numrec': maxNumrecMessage[0]}
        SQLiteManager.InsertIntoTableOfTables(parametersForTableOfTables)

        # On stocke le srid de la layer pour pouvoir traiter le post
        newVectorLayer.srid = parameters['sridLayer']

        # Modification du formulaire d'attributs
        efffa = EditFormFieldFromAttributes(newVectorLayer, layer.attributes)
        newVectorLayer.correspondanceChampType = efffa.readData()

        # Modification de la symbologie de la couche
        listOfValuesFromItemStyle = layer.getListOfValuesFromItemStyle()
        newVectorLayer.setModifySymbols(listOfValuesFromItemStyle)

        # Affichage des données en fonction de l'échelle
        newVectorLayer.setDisplayScale(layer.minzoom, layer.maxzoom)

        # Une couche en visualisation est non modifiable
        if layer.role == 'visu' or layer.role == 'ref':
            newVectorLayer.setReadOnly()

        # Ajout de la couche dans la carte
        self.QgsProject.instance().addMapLayer(newVectorLayer, False)
        nodeGroup.addLayer(newVectorLayer)
        self.guichetLayers.append(newVectorLayer)

        # On masque les champs de travail et champs internes
        # fields = newVectorLayer.fields()
        # for i in range(0, fields.count()):
        #     f = fields.field(i)
        #     if f.name() == cst.ID_SQLITE or f.name() == cst.IS_FINGERPRINT or f.name() == cst.FINGERPRINT:
        #         self.hideColumn(newVectorLayer, f.name())
        #         hidden_setup = QgsEditorWidgetSetup('Hidden', f.editorWidgetSetup().config())
        #         newVectorLayer.setEditorWidgetSetup(i, hidden_setup)

        self.logger.debug("Layer {} added to map".format(newVectorLayer.name()))
        message = "Couche {0} ajoutée à la carte.\n{1}\n".format(newVectorLayer.name(), maxNumrecMessage[1])
        print(message)
        return message

    def getAllMapLayers(self):
        """
        Return the list of layer names which are loaded in the map
        :return dictionnaire des couches chargées sur la carte (key: layer name, value: layer id)
        :rtype dictionary
        """
        layers = self.QgsProject.instance().mapLayers()
        maplayers = {}
        for key in layers:
            layer = layers[key]
            maplayers[layer.name()] = layer
        return maplayers

    def getMapPolygonLayers(self):
        """
        Retourne les calques qui sont de type polygon ou multipolygon
        :return dictionnaire des couches de type polygon(key: layer id, value: layer name)
        :rtype dictionary
        """
        polylayers = {}
        layers = self.QgsProject.instance().mapLayers()
        for key in layers:
            layer = layers[key]
            layerType = type(layer)
            if layerType is not QgsVectorLayer:
                continue
            geometryType = layer.geometryType()
            if geometryType is not None and geometryType != QgsWkbTypes.GeometryType.PolygonGeometry:
                continue
            print("{0} {1}".format(layer.name(), geometryType))
            polylayers[layer.id()] = layer.name()
        return polylayers

    def getLayerByName(self, layName):
        """
        Retourne le calque donné par son nom
        :param layName: le nom du calque
        :type layName: string

        :return: le premier calque ayant pour nom celui donné en paramètre
        :rtype: QgsVectorLayer
        """
        mapByName = self.QgsProject.instance().mapLayersByName(layName)
        if len(mapByName) > 0:
            return mapByName[0]
        else:
            return None

    def refresh_layers(self):
        """
        Rafraichissement de la carte
        """
        for layer in self.mapCan.layers():
            layer.triggerRepaint()

    def updateRemarqueInSqlite(self, rem):
        """
        Met à jour une remarque (après l'ajout d'une réponse)
        :param rem : la remarque à mettre à jour
        :type rem: Remarque
        """
        curs = None
        try:
            # self.conn= sqlite3.connect(self.__dbPath)
            self.conn = spatialite_connect(self.dbPath)

            sql = "UPDATE " + PluginHelper.nom_Calque_Signalement + " SET "
            sql += " Date_MAJ= '" + rem.getAttribut("dateMiseAJour") + "',"
            sql += " Date_validation= '" + rem.getAttribut("dateValidation") + "',"
            sql += " Réponses= '" + ClientHelper.getValForDB(rem.concatenateResponse()) + "', "
            sql += " Statut='" + rem.statut + "' "
            sql += " WHERE NoSignalement = " + rem.id

            curs = self.conn.cursor()
            curs.execute(sql)
            self.conn.commit()

        except Exception as e:
            self.logger.error(format(e))
            raise
        finally:
            curs.close()
            self.conn.close()

    def countRemarqueByStatut(self, statut):
        """
        Retourne le nombre de remarques ayant le statut donné en paramètre
        :param statut: le statut de la remarque (=code renvoyé par le service)
        :type statut: string
        """
        remLay = self.getLayerByName(PluginHelper.nom_Calque_Signalement)
        expression = '"Statut" = \'' + statut + '\''
        filtFeatures = remLay.getFeatures(QgsFeatureRequest().setFilterExpression(expression))
        return len(list(filtFeatures))

    def hasMapSelectedFeatures(self):
        """
        Vérifie s'il y a des objets sélectionnés
        :return true si de objets sont sélectionnés, false sinon
        :rtype boolean
        """
        mapLayers = self.mapCan.layers()
        for layer in mapLayers:
            if type(layer) is QgsVectorLayer and len(layer.selectedFeatures()) > 0:
                return True
        return False

    def makeCroquisFromSelection(self):
        """
        Transforme en croquis Ripart les object sélectionnés dans la carte en cours.
        Le système de référence spatial doit être celui du service Ripart(i.e. 4326), donc il faut transformer les
        coordonnées si la carte est dans un autre système de réf.
        """

        # dictionnaire : key: nom calque, value: liste des attributs
        attCroquis = PluginHelper.load_attCroquis(self.projectDir)

        # Recherche tous les features sélectionnés sur la carte (pour les transformer en croquis)
        listCroquis = []
        mapLayers = self.mapCan.layers()
        for lay in mapLayers:
            if type(lay) is not QgsVectorLayer:
                continue

            # Si le CRS de la couche n'est pas défini, on prévient l'utilisateur et on sort
            if len(lay.selectedFeatures()) > 0 and not lay.sourceCrs().isValid():
                nom = lay.name()
                message = "La couche {0} ne peut pas être utilisée pour créer un signalement car son système " \
                          "de projection n'est pas défini. Veuillez le définir avant de créer " \
                          "un signalement.".format(nom)
                PluginHelper.showMessageBox(message)
                return []

            for f in lay.selectedFeatures():
                # la liste des croquis
                croquiss = []
                # le type du feature
                ftype = f.geometry().type()
                geom = f.geometry()
                isMultipart = geom.isMultipart()
                # if geom.isMultipart() => explode to single parts
                if isMultipart and ftype == QgsWkbTypes.GeometryType.PolygonGeometry:
                    for poly in geom.asMultiPolygon():
                        croquiss.append(
                            self.makeCroquis(QgsGeometry.fromPolygonXY(poly), ftype, lay.crs(),
                                             f[0]))
                elif isMultipart and ftype == QgsWkbTypes.GeometryType.LineGeometry:
                    for line in geom.asMultiPolyline():
                        croquiss.append(
                            self.makeCroquis(QgsGeometry.fromPolylineXY(line), ftype, lay.crs(),
                                             f[0]))
                elif isMultipart and ftype == QgsWkbTypes.GeometryType.PointGeometry:
                    for pt in geom.asMultiPoint():
                        croquiss.append(
                            self.makeCroquis(QgsGeometry.fromPointXY(pt), ftype, lay.crs(), f[0]))
                else:
                    croquiss.append(self.makeCroquis(geom, ftype, lay.crs(), f[0]))

                if len(croquiss) == 0:
                    continue

                for croquisTemp in croquiss:
                    if lay.name() in attCroquis:
                        for att in attCroquis[lay.name()]:
                            idx = lay.fields().lookupField(att)
                            attribut = SketchAttributes(att, f.attributes()[idx])
                            croquisTemp.addAttribut(attribut)
                    listCroquis.append(croquisTemp)

        return listCroquis

    def makeCroquis(self, geom, ftype, layerCrs, fId):
        """
        Génère un croquis Ripart à partir d'une géométrie
        Les coordonnées des points du croquis doivent être transformées dans le crs de Ripart (4326)

        :param geom: la géométrie à transformer en croquis
        :type geom: QgsGeometry

        :param ftype: le type de l'objet géométrique
        :param type ftype: QGis.WkbType

        :param layerCrs: le syst de coordonnées de référence du calque dont provient le feature
        :type layerCrs: QgsCoordinateReferenceSystem

        :param fId: l'id de l'objet géométrique (valeur du premier attribut du feature)
        :type fId: int

        :return le croquis créé
        :rtype Croquis ou None s'il y a eu une erreur
        """
        newCroquis = Sketch()
        geomPoints = []

        try:
            destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS4326)
            transformer = QgsCoordinateTransform(layerCrs, destCrs, self.QgsProject.instance())
            if ftype == QgsWkbTypes.GeometryType.PolygonGeometry:
                geomPoints = geom.asPolygon()
                if len(geomPoints) > 0:
                    geomPoints = geomPoints[0]  # les points du polygone
                else:
                    self.logger.debug(u"geomPoints problem " + str(fId))
                newCroquis.type = newCroquis.sketchType.Polygone
            elif ftype == QgsWkbTypes.GeometryType.LineGeometry:
                geomPoints = geom.asPolyline()
                newCroquis.type = newCroquis.sketchType.Ligne
            elif ftype == QgsWkbTypes.GeometryType.PointGeometry:
                geomPoints = [geom.asPoint()]
                newCroquis.type = newCroquis.sketchType.Point
            else:
                newCroquis.type = newCroquis.sketchType.Vide

            for pt in geomPoints:
                pt = transformer.transform(pt)
                newCroquis.addPoint(Point(pt.x(), pt.y()))

        except Exception as e:
            self.logger.error(u"in makeCroquis:" + format(e))
            return None

        return newCroquis

    def getPositionRemarque(self, listCroquis):
        """
        Recherche et retourne la position de la remarque (point).
        La position est calculée à partir des croquis associés à la remarque

        :param listCroquis: la liste des croquis
        :type listCroquis: list de Croquis

        :return la position de la remarque
        :rtype Point
        """
        # crée la table temporaire dans spatialite et calcule les centroides de chaque croquis
        res = self._createTempCroquisTable(listCroquis)

        # trouve le barycentre de l'ensemble des centroïdes
        if type(res) == list:
            barycentre = self._getBarycentre()
            return barycentre
        else:
            return None

    def _createTempCroquisTable(self, listCroquis):
        """
        Crée une table temporaire dans sqlite pour les nouveaux croquis
        La table contient la géométrie des croquis au format texte (WKT).
        Retourne la liste des points des croquis

        :param listCroquis : la liste des nouveaux croquis
        :type listCroquis: list

        :return une liste contenant tous les points des croquis
        :rtype: list de Point
        """
        cur = None
        tmpTable = "tmpTable"
        allCroquisPoints = []
        if len(listCroquis) == 0:
            return None

        cr = listCroquis[0]
        try:
            self.conn = spatialite_connect(self.dbPath)
            print(self.dbPath)
            cur = self.conn.cursor()

            sql = u"Drop table if Exists " + tmpTable
            print(sql)
            cur.execute(sql)

            sql = u"CREATE TABLE " + tmpTable + " (" + \
                  u"id INTEGER NOT NULL PRIMARY KEY, textGeom TEXT, centroid TEXT)"
            print(sql)
            cur.execute(sql)

            i = 0
            textGeom = ""
            textGeomEnd = ""
            for cr in listCroquis:
                i += 1
                if cr.type == cr.sketchType.Ligne:
                    textGeom = "LINESTRING("
                    textGeomEnd = ")"
                elif cr.type == cr.sketchType.Polygone:
                    textGeom = "POLYGON(("
                    textGeomEnd = "))"
                elif cr.type == cr.sketchType.Point:
                    textGeom = "POINT("
                    textGeomEnd = ")"

                for pt in cr.points:
                    textGeom += str(pt.longitude) + " " + str(pt.latitude) + ","
                    allCroquisPoints.append(pt)

                textGeom = textGeom[:-1] + textGeomEnd
                sql = "INSERT INTO " + tmpTable + "(id,textGeom,centroid) VALUES (" + str(i) + ",'" + textGeom + "'," + \
                      "AsText(centroid( ST_GeomFromText('" + textGeom + "'))))"
                print(sql)
                cur.execute(sql)

            self.conn.commit()

        except Exception as e:
            self.logger.error("_createTempCroquisTable " + format(e))
            return False
        finally:
            cur.close()
            self.conn.close()

        return allCroquisPoints

    def _getBarycentre(self):
        """
        Calcul du barycentre de l'ensemble des croquis à partir des centroides de chaque croquis;
        ces centroides sont stockés dans la table temporaire "tmpTable"

        :return: le barycentre
        :rtype: Point
        """
        barycentre = None
        tmpTable = "tmpTable"
        try:
            self.conn = spatialite_connect(self.dbPath)
            cur = self.conn.cursor()

            sql = "SELECT X(ST_GeomFromText(centroid)) as x, Y(ST_GeomFromText(centroid)) as y  from " + tmpTable
            cur.execute(sql)

            rows = cur.fetchall()
            sumX = 0
            sumY = 0
            for row in rows:
                sumX += row[0]
                sumY += row[1]
            ptX = sumX / float(len(rows))
            ptY = sumY / float(len(rows))
            barycentre = Point(ptX, ptY)

        except Exception as e:
            self.logger.error("getBarycentre " + format(e))

        return barycentre

    '''magicwand'''

    def selectRemarkByNo(self, noSignalements):
        """
        Sélection des remarques données par leur no
        :param noSignalements : les no de signalements à sélectionner
        :type noSignalements: list de string
        """
        self.conn = spatialite_connect(self.dbPath)
        cur = self.conn.cursor()
        table = PluginHelper.nom_Calque_Signalement
        lay = self.getLayerByName(table)
        sql = "SELECT * FROM " + table + "  WHERE noSignalement in (" + noSignalements + ")"
        rows = cur.execute(sql)
        featIds = []
        for row in rows:
            print(row[0])
            featIds.append(row[0])
        lay.selectByIds(featIds)

    def getCroquisForRemark(self, noSignalement, croquisSelFeats):
        """
        Retourne les croquis associés à une remarque

        :param noSignalement: le no de la remarque
        :type noSignalement: int

        :param croquisSelFeats: dictionnaire contenant les croquis
                                 (key: le nom de la table du croquis, value: liste des identifiants de croquis)
        :type croquisSelFeats: dictionnary

        :return: dictionnaire contenant les croquis
        :rtype: dictionnary
        """
        crlayers = PluginHelper.sketchLayers
        self.conn = spatialite_connect(self.dbPath)
        cur = self.conn.cursor()

        for table in crlayers:
            sql = "SELECT * FROM " + table + "  WHERE noSignalement= " + str(noSignalement)
            rows = cur.execute(sql)
            featIds = []
            for row in rows:
                featIds.append(row[0])
                if table not in croquisSelFeats:
                    croquisSelFeats[table] = []
                croquisSelFeats[table].append(row[0])

        return croquisSelFeats

    def checkProfilServeurClient(self):
        # Le profil a t'il pu être changé sur le serveur ?
        if self.client is not None:
            nomProfilServeur = self.client.getNomProfil()
            if self.profil.title != nomProfilServeur:
                message = "Votre groupe actif ({} versus {}) semble avoir été modifié par une autre application cliente " \
                          "de l'Espace collaboratif.\nMerci de vous reconnecter via le bouton 'Se connecter à l'Espace " \
                          "collaboratif' pour confirmer dans quel groupe vous souhaitez travailler.\nAttention : si vous " \
                          "avez déjà chargé les couches d'un autre groupe, vous devez les supprimer au préalable ou " \
                          "créer un autre projet QGIS.".format(self.profil.title, nomProfilServeur)
                PluginHelper.showMessageBox(message)
                raise Exception(u"Les projets actifs diffèrent entre le serveur et le client")

    def getLayers(self) -> (str, [], object):
        # La liste des couches et non la liste de courses ;-)
        infosLayers = []
        # Si le client n'existe pas, il faut demander à l'utilisateur de se connecter
        if self.client is None:
            connResult = self.getConnexionEspaceCollaboratif()
            if not connResult or connResult == -1:
                # la connexion a échoué ou l'utilisateur a cliqué sur Annuler
                return "Rejected", infosLayers
        # Si malgré la demande de connexion le client n'est toujours pas déterminé
        if self.client is None:
            return "Rejected", infosLayers
        # Récupération du profil lié à l'utilisateur
        profilUser = self.client.getProfil()
        print("Profil : {0}, {1}".format(profilUser.geogroup.getId(),
                                         profilUser.geogroup.getName))

        if len(profilUser.infosGeogroups) == 0:
            return "Rejected", infosLayers, profilUser
        # https://espacecollaboratif.ign.fr/gcms/api/communities/375/layers
        return "Accepted", infosLayers, profilUser

    def getInfosLayers(self):
        infosLayers = []

        if self.client is None:
            connResult = self.getConnexionEspaceCollaboratif()
            if not connResult or connResult == -1:
                # la connexion a échoué ou l'utilisateur a cliqué sur Annuler
                return "Rejected", infosLayers

        if self.client is None:
            return "Rejected", infosLayers

        profilUser = self.client.getProfil()
        print("Profil : {0}, {1}".format(profilUser.geogroup.getId(),
                                         profilUser.geogroup.getName))

        if len(profilUser.infosGeogroups) == 0:
            return "Rejected", infosLayers

        for infoGeogroup in profilUser.infosGeogroups:
            if infoGeogroup.group.getId() != profilUser.geogroup.getId():
                continue

            print("Liste des couches du profil utilisateur")
            for layersAll in infoGeogroup.layers:
                print(layersAll.nom)
                infosLayers.append(layersAll)

        return "Accepted", infosLayers, profilUser

    def getUriDatabaseSqlite(self):
        uri = QgsDataSourceUri(cst.EPSG4326)
        uri.setDatabase(SQLiteManager.getBaseSqlitePath())
        return uri