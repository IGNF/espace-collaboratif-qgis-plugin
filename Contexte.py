# -*- coding: utf-8 -*-
"""
Created on 29 sept. 2015
Updated on 30 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""

from PyQt5 import QtGui
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import spatialite_connect
from qgis.core import QgsCoordinateReferenceSystem, QgsFeatureRequest, QgsCoordinateTransform, \
    QgsGeometry, QgsDataSourceUri, QgsVectorLayer, QgsRasterLayer, QgsProject, \
    QgsWkbTypes, QgsLayerTreeGroup

import os.path
import shutil
import ntpath
import configparser

from .RipartException import RipartException
from .RipartHelper import RipartHelper
from .core.RipartLoggerCl import RipartLogger
from .core.Client import Client
from .core.ClientHelper import ClientHelper
from .core.SketchAttributes import SketchAttributes
from .core.Point import Point
from .core.Sketch import Sketch
from .FormConnexion_dialog import FormConnexionDialog
from .FormInfo import FormInfo
from .FormChoixGroupe import FormChoixGroupe
from .core import ConstanteRipart as cst
from .Import_WMTS import importWMTS
from .core.GuichetVectorLayer import GuichetVectorLayer
from .core.EditFormFieldFromAttributes import EditFormFieldFromAttributes
from .core.WfsGet import WfsGet
from .core.SQLiteManager import SQLiteManager


class Contexte(object):
    """
    Contexte et initialisation de la "session"
    """
    # instance du Contexte
    instance = None

    # identifiants de connexion
    login = ""
    pwd = ""
    urlHostRipart = ""
    profil = None

    # groupe actif
    groupeactif = ""

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
        self.urlHostRipart = ""
        self.groupeactif = ""
        self.profil = None
        self.ripClient = None
        self.logger = RipartLogger("Contexte").getRipartLogger()
        self.spatialRef = QgsCoordinateReferenceSystem(cst.EPSGCRS, QgsCoordinateReferenceSystem.EpsgCrsId)

        # version in metadata
        cst.RIPART_CLIENT_VERSION = self.getMetadata('general', 'version')

        try:
            # set du répertoire et fichier du projet qgis
            self.setProjectParams(QgsProject)

            # contrôle l'existence du fichier de configuration
            self.checkConfigFile()

            # set de la base de données
            self.getOrCreateDatabase()

            # set des fichiers de style
            self.copyRipartStyleFiles()

            # retrouve les formats de fichiers joints acceptés à partir du fichier formats.txt.
            formatFile = open(os.path.join(self.plugin_path, 'files', 'formats.txt'), 'r')
            lines = formatFile.readlines()
            self.formats = [x.split("\n")[0] for x in lines]

        except Exception as e:
            self.logger.error("init contexte:" + format(e))
            raise

    def getMetadata(self, category, param):
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

    def setProjectParams(self, QgsProject):
        """set des paramètres du projet
        """
        self.projectDir = QgsProject.instance().homePath()
        if self.projectDir == "":
            RipartHelper.showMessageBox(
                u"Votre projet QGIS doit être enregistré avant de pouvoir utiliser le plugin de l'espace collaboratif")
            raise Exception(u"Projet QGIS non enregistré")

        # nom du fichier du projet enregistré
        fname = ntpath.basename(QgsProject.instance().fileName())

        nbPoints = fname.count(".")
        if nbPoints != 1:
            RipartHelper.showMessageBox(
                u"Le nom de votre projet QGIS ne doit pas contenir de point en dehors de son extension (.qgz). Merci "
                u"de le renommer.")
            raise Exception(u"Nom de projet QGIS non valide")

        self.projectFileName = fname[:fname.find(".")]

    def checkConfigFile(self):
        """
        Contrôle de l'existence du fichier de configuration
        """
        ripartxml = self.projectDir + os.path.sep + RipartHelper.nom_Fichier_Parametres_Ripart
        if not os.path.isfile(ripartxml):
            try:
                shutil.copy(self.plugin_path + os.path.sep + RipartHelper.ripart_files_dir + os.path.sep +
                            RipartHelper.nom_Fichier_Parametres_Ripart, ripartxml)
                self.logger.debug("Copy espaceco.xml")
            except Exception as e:
                self.logger.error("No espaceco.xml found in plugin directory" + format(e))
                raise Exception("Le fichier de configuration " + RipartHelper.nom_Fichier_Parametres_Ripart +
                                " n'a pas été trouvé.")

    def copyRipartStyleFiles(self):
        """
        Copie les fichiers de styles (pour les remarques et croquis ripart)
        """
        styleFilesDir = self.projectDir + os.path.sep + RipartHelper.qmlStylesDir

        RipartHelper.copy(self.plugin_path + os.path.sep + RipartHelper.ripart_files_dir + os.path.sep +
                          RipartHelper.qmlStylesDir, styleFilesDir)

    def getVisibilityLayersFromGroupeActif(self):
        """
        Retourne True si au moins une couche est éditable
        False sinon
        """
        if self.groupeactif is None or self.groupeactif == "":
            return False

        if self.profil is None:
            return False

        for infoGeogroup in self.profil.infosGeogroups:
            if infoGeogroup.group.name != self.groupeactif:
                continue

            for layer in infoGeogroup.layers:
                if layer.role == "edit" or layer.role == "ref-edit":
                    return True
        return False

    def getConnexionRipart(self, newLogin=False):
        """Connexion au service ripart

        :param newLogin: booléen indiquant si on fait un nouveau login (fonctionnalité "Connexion au service Ripart")
        :type newLogin: boolean

        :return 1 si la connexion a réussie, 0 si elle a échouée, -1 s'il y a eu une erreur (Exception)
        :rtype int
        """
        client = None
        self.logger.debug("GetConnexionRipart ")
        result = -1

        try:
            self.urlHostRipart = RipartHelper.load_ripartXmlTag(self.projectDir, RipartHelper.xml_UrlHost,
                                                                "Serveur").text
            self.logger.debug("this.URLHostRipart " + self.urlHostRipart)
        except Exception as e:
            self.logger.error("URLHOST inexistant dans fichier configuration")
            RipartHelper.showMessageBox(u"L'url du serveur doit être renseignée dans la configuration avant de "
                                        u"pouvoir se connecter.\n(Aide>Configurer le plugin>Adresse de connexion "
                                        u"...)")
            return

        self.loginWindow = FormConnexionDialog()
        self.loginWindow.setWindowTitle("Connexion à {0}".format(self.urlHostRipart))
        loginXmlNode = RipartHelper.load_ripartXmlTag(self.projectDir, RipartHelper.xml_Login, "Serveur")
        if loginXmlNode is None:
            self.login = ""
        else:
            self.login = RipartHelper.load_ripartXmlTag(self.projectDir, RipartHelper.xml_Login, "Serveur").text

        xmlproxy = RipartHelper.load_ripartXmlTag(self.projectDir, RipartHelper.xml_proxy, "Serveur").text
        if xmlproxy is not None and str(xmlproxy).strip() != '':
            self.proxy = {'https': str(xmlproxy).strip()}
        else:
            self.proxy = None

        xmlgroupeactif = RipartHelper.load_ripartXmlTag(self.projectDir, RipartHelper.xml_GroupeActif, "Serveur")
        if xmlgroupeactif is not None:
            self.groupeactif = RipartHelper.load_ripartXmlTag(self.projectDir, RipartHelper.xml_GroupeActif,
                                                              "Serveur").text
            if self.groupeactif is not None:
                self.logger.debug("this.groupeactif " + self.groupeactif)

        if self.login == "" or self.pwd == "" or newLogin:
            self.loginWindow.setLogin(self.login)
            self.loginWindow.exec_()

            while result < 0:
                if self.loginWindow.cancel:
                    # fix_print_with_import
                    print("rejected")
                    self.loginWindow = None
                    result = 0
                elif self.loginWindow.connect:
                    # fix_print_with_import
                    print("connect")
                    self.login = self.loginWindow.getLogin()
                    self.pwd = self.loginWindow.getPwd()
                    print("login " + self.login)
                    try:
                        client = Client(self.urlHostRipart, self.login, self.pwd, self.proxy)
                        profil = client.getProfil()

                        if profil is not None:
                            dlgInfoToScreen = True
                            self.saveLogin(self.login)

                            # si l'utilisateur appartient à 1 seul groupe, celui-ci est déjà actif
                            # si l'utilisateur n'appartient à aucun groupe, un profil par défaut
                            # est attribué mais il ne contient pas d'infosgeogroupes

                            if len(profil.infosGeogroups) < 1:
                                # le profil de l'utilisateur est déjà récupéré et reste actif (NB: a priori, il n'a pas de profil)
                                result = 1
                                self.profil = profil

                                # si l'utilisateur n'a pas de profil, il faut indiquer que le groupe actif est vide
                                if "défaut" in profil.title:
                                    RipartHelper.save_groupeactif(self.projectDir, "Aucun")
                                else:
                                    RipartHelper.save_groupeactif(self.projectDir, profil.geogroup.name)

                                    # On enregistre le groupe comme groupe préféré (par défaut) pour la création de signalement
                                    # Si ce n'est pas le même qu'avant, on vide les thèmes préférés
                                    preferredGroup = RipartHelper.load_preferredGroup(self.projectDir)
                                    if preferredGroup != profil.geogroup.name:
                                        RipartHelper.save_preferredThemes(self.projectDir, [])

                                    RipartHelper.save_preferredGroup(self.projectDir, profil.geogroup.name)

                            # sinon le choix d'un autre groupe est présenté à l'utilisateur
                            # le formulaire est proposé même si l'utilisateur n'appartient qu'à un groupe
                            # afin qu'il puisse remplir sa clé Géoportail
                            else:

                                dlgChoixGroupe = FormChoixGroupe(profil, self.groupeactif)
                                dlgChoixGroupe.exec_()
                                # bouton Valider
                                if not dlgChoixGroupe.bCancel:
                                    result = 1

                                    # le choix du nouveau profil est validé
                                    # le nouvel id et nom du groupe sont retournés dans un tuple
                                    idNomGroupe = dlgChoixGroupe.save()

                                    # si l'utilisateur n'appartient qu'à un seul gorupe, le profil chargé reste actif
                                    if len(profil.infosGeogroups) == 1:
                                        self.profil = profil
                                    else:
                                        # récupère le profil et un message dans un tuple
                                        profilMessage = client.setChangeUserProfil(idNomGroupe[0])
                                        messTmp = profilMessage[1]

                                        # setChangeUserProfil retourne un message "Le profil du groupe xx est déjà actif"
                                        if messTmp.find('actif') != -1:
                                            # le profil chargé reste actif
                                            self.profil = profil
                                        else:
                                            # setChangeUserProfil retourne un message vide
                                            # le nouveau profil devient actif
                                            self.profil = profilMessage[0]

                                    # Sauvegarde du groupe actif
                                    # dans le xml du projet utilisateur
                                    RipartHelper.save_groupeactif(self.projectDir, idNomGroupe[1])
                                    self.groupeactif = idNomGroupe[1]

                                    # On enregistre le groupe comme groupe préféré pour la création de signalement
                                    # Si ce n'est pas le même qu'avant, on vide les thèmes préférés
                                    formPreferredGroup = RipartHelper.load_preferredGroup(self.projectDir)
                                    if formPreferredGroup != profil.geogroup.name:
                                        RipartHelper.save_preferredThemes(self.projectDir, [])
                                    RipartHelper.save_preferredGroup(self.projectDir, profil.geogroup.name)

                                # Bouton Annuler
                                elif dlgChoixGroupe.cancel:
                                    result = -1
                                    print("rejected")
                                    self.loginWindow.close()
                                    self.loginWindow = None
                                    return

                            # les infos de connexion présentée à l'utilisateur
                            dlgInfo = FormInfo()

                            # Modification du logo en fonction du groupe
                            if profil.logo != "":
                                dlgInfo.logo.setPixmap(QtGui.QPixmap("{0}{1}".format(self.urlHostRipart, profil.logo)))
                            elif profil.title == "Profil par défaut":
                                dlgInfo.logo.setPixmap(QtGui.QPixmap(":/plugins/RipartPlugin/images/logo_IGN.png"))

                            dlgInfo.textInfo.setText(u"<b>Connexion réussie à l'Espace collaboratif</b>")
                            dlgInfo.textInfo.append("<br/>Serveur : {}".format(self.urlHostRipart))
                            dlgInfo.textInfo.append("Login : {}".format(self.login))
                            dlgInfo.textInfo.append("Groupe : {}".format(self.profil.title))
                            if self.profil.zone == cst.ZoneGeographique.UNDEFINED:
                                zoneExtraction = RipartHelper.load_CalqueFiltrage(self.projectDir).text
                                if zoneExtraction == "" or zoneExtraction is None:
                                    dlgInfo.textInfo.append("Zone : pas de zone définie")
                                else:
                                    dlgInfo.textInfo.append("Zone : {}".format(zoneExtraction))
                                self.profil.zone = zoneExtraction
                            else:
                                dlgInfo.textInfo.append("Zone : {}".format(self.profil.zone.__str__()))

                            dlgInfo.exec_()
                            if dlgInfo.Accepted:
                                self.client = client
                                result = 1
                                self.logger.debug("result 1")
                        else:
                            # fix_print_with_import
                            print("error")
                    except Exception as e:
                        result = -1
                        self.pwd = ""
                        self.logger.error(format(e))

                        try:
                            self.loginWindow.setErreur(ClientHelper.notNoneValue(format(e)))
                        except Exception as e2:
                            self.loginWindow.setErreur("la connexion a échoué")
                        self.loginWindow.exec_()
        else:
            try:
                client = Client(self.urlHostRipart, self.login, self.pwd, self.proxy)
                result = 1
                self.logger.debug("result =" + str(result))
                self.client = client
            except RipartException as e:
                # fix_print_with_import
                print(format(e))
                result = -1

        if result == 1:
            self.ripClient = client
            self.logger.debug("ripclient")

        return result

    def saveLogin(self, login):
        """
        Sauvegarde du login dans le contexte et dans le fichier ripart.xml
        """
        self.login = login
        RipartHelper.save_login(self.projectDir, login)

    def getOrCreateDatabase(self):
        """
        Retourne la base de données spatialite contenant les tables des remarques et croquis
        Si la BD n'existe pas, elle est créée
        """
        curs = None
        dbName = self.projectFileName + "_espaceco"
        self.dbPath = self.projectDir + "/" + dbName + self.sqlite_ext

        if not os.path.isfile(self.dbPath):
            try:
                shutil.copy(self.plugin_path + os.path.sep + RipartHelper.ripart_files_dir + os.path.sep +
                            RipartHelper.ripart_db, self.dbPath)
                self.logger.debug("copy espaceco.sqlite")
            except Exception as e:
                self.logger.error("no espaceco.sqlite found in plugin directory" + format(e))
                raise e
        try:
            self.conn = spatialite_connect(self.dbPath)

            # creating a Cursor
            curs = self.conn.cursor()
            sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='Signalement'"
            curs.execute(sql)
            if curs.fetchone() is None:
                # create layer Signalement
                RipartHelper.createRemarqueTable(self.conn)

            for lay in RipartHelper.croquis_layers:
                sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='" + lay + "'"
                curs.execute(sql)
                if curs.fetchone() is None:
                    # create layer
                    RipartHelper.createCroquisTable(self.conn, lay, RipartHelper.croquis_layers[lay])

        except RipartException as e:
            self.logger.error(format(e))
            raise
        finally:
            curs.close()
            self.conn.close()

    def appendUri_WFS(self, url, nomCouche, bbox):
        uri = QgsDataSourceUri()
        uri.setConnection("", "", self.login, self.pwd)
        uri.setParam('request', 'GetFeature')
        if str(bbox) != "None":
            uri.setParam('bbox', bbox.boxToString())

        # Mon guichet
        if '&' in url:
            tmp = url.split('&')
            database = tmp[1].split('=')
            typeName = "{}:{}".format(database[1], nomCouche)
            uri.setParam('url', tmp[0])
            uri.setParam('typename', typeName)
            uri.setParam('filter', 'detruit:false')
            uri.setParam('maxNumFeatures', '5000')
            uri.setParam('pagingEnabled', 'true')
            uri.setParam('restrictToRequestBBOX', '1')
        # Autres Geoservices
        else:
            uri.setParam('url', url)
            uri.setParam('service', cst.WFS)

        return uri

    def importWFS(self, layer, structure):
        # Création éventuelle de la table SQLite liée à la couche
        sqliteManager = SQLiteManager()

        # Si la table du nom de la couche existe,
        # elle est vidée, détruite et recréée
        if SQLiteManager.isTableExist(layer.nom):
            sqliteManager.emptyTable(layer.nom)
            sqliteManager.deleteTable(layer.nom)
        bColumnDetruitExist = sqliteManager.createTableFromLayer(layer, structure)

        # Création de la source pour la couche dans la carte liée à la table SQLite
        uri = self.getUriDatabaseSqlite()
        self.logger.debug(uri.uri())
        print("url : {}".format(uri.uri()))
        geometryName = structure['geometryName']
        uri.setDataSource('', layer.nom, geometryName)
        uri.setSrid(str(cst.EPSGCRS))
        parameters = {'uri': uri.uri(), 'name': layer.nom, 'genre': 'spatialite', 'databasename': layer.databasename,
                      'sqliteManager': sqliteManager, 'idName': structure['idName'],
                      'geometryName': geometryName, 'geometryDimension': structure['attributes'][geometryName]['is3d'],
                      'geometryType': structure['attributes'][geometryName]['type']}

        vlayer = GuichetVectorLayer(parameters)
        # vlayer = QgsVectorLayer(uri.uri(), layer.nom, 'spatialite')
        vlayer.setCrs(QgsCoordinateReferenceSystem(cst.EPSGCRS, QgsCoordinateReferenceSystem.EpsgCrsId))
        return vlayer, bColumnDetruitExist

    def addGuichetLayersToMap(self, guichet_layers, bbox, nameGroup):
        """
        Add guichet layers to the current map
        """
        try:
            # Quelles sont les cartes chargées dans le projet QGIS courant
            maplayers = self.getAllMapLayers()
            root = self.QgsProject.instance().layerTreeRoot()

            # Le groupe existe t-il dans le projet
            nodeGroup = None
            nodesGroup = root.findGroups()
            for nodeGroup in nodesGroup:
                # Si le groupe existe déjà, on sort
                if nodeGroup.name() == nameGroup:
                    break

            # Si le groupe n'existe pas et que des couches doivent être chargées
            # alors il y a création du groupe dans le projet
            nbLayersWFS = 0
            for layer in guichet_layers:
                if layer.type == cst.WFS:
                    nbLayersWFS += 1

            if nodeGroup is None and len(nodesGroup) == 0 and nbLayersWFS != 0:
                newNode = QgsLayerTreeGroup(nameGroup)
                root.insertChildNode(0, newNode)
                nodeGroup = root.findGroup(nameGroup)

            # Il y a déjà un groupe dans le projet
            # Il faut indiquer à l'utilisateur que c'est impossible
            # d'ajouter un nouveau groupe dans le projet
            if nodeGroup is not None:
                if nodeGroup.name() != nameGroup and (len(nodesGroup) == 1):
                    QMessageBox.warning(None, "Charger les couches de mon groupe",
                                        u"Votre projet QGIS contient des couches d'un autre groupe Espace "
                                        u"collaboratif (" + nodeGroup.name() + "). \nPour pouvoir charger les données "
                                                                               "du groupe " + nameGroup + ", veuillez supprimer les couches existantes de "
                                                                                                          "votre projet QGIS ou travailler dans un nouveau projet." + "\n\nNB : "
                                                                                                                                                                      "ces couches seront simplement supprimées de la carte QGIS en cours, "
                                                                                                                                                                      "elles resteront disponibles sur l'Espace collaboratif.")
                    return

            for layer in guichet_layers:
                if layer.nom in maplayers:
                    message = "La couche {} existe déjà, voulez-vous continuer ?".format(layer.nom)
                    reply = QMessageBox.question(None, 'IGN Espace Collaboratif', message, QMessageBox.Yes,
                                                 QMessageBox.No)
                    if reply == QMessageBox.No:
                        continue
                '''
                Ajout des couches WFS selectionnées dans "Mon guichet"
                '''
                if layer.type == cst.WFS:
                    # Récupération de la structure de la future table
                    structure = self.client.connexionFeatureTypeJson(layer.url, layer.nom)
                    if structure['database_type'] == 'bduni' and structure['database_versioning'] is True:
                        layer.isStandard = False
                    sourceLayer = self.importWFS(layer, structure)
                    if not sourceLayer[0].isValid():
                        print("Layer {} failed to load !".format(layer.nom))
                        continue
                    self.formatLayer(layer, sourceLayer[0], nodeGroup, structure, bbox, sourceLayer[1])

                '''
                Ajout des couches WMTS selectionnées dans "Mon guichet"
                '''
                if layer.type == cst.WMTS:
                    importWmts = importWMTS(self, layer)
                    titleLayer_uri = importWmts.getWtmsUrlParams(layer.layer_id)
                    rlayer = QgsRasterLayer(titleLayer_uri[1], titleLayer_uri[0], 'wms')
                    if not rlayer.isValid():
                        print("Layer {} failed to load !".format(rlayer.name()))
                        continue

                    QgsProject.instance().addMapLayer(rlayer, False)
                    # Insertion à la fin avec -1
                    root.insertLayer(-1, rlayer)
                    self.logger.debug("Layer {} added to map".format(rlayer.name()))
                    print("Layer {} added to map".format(rlayer.name()))

            # Refraichissement de la carte
            self.mapCan.refresh()

        except Exception as e:
            self.logger.error(format(e))
            self.iface.messageBar(). \
                pushMessage("Remarque",
                            str(e),
                            level=1, duration=10)
            print(str(e))

    def formatLayer(self, layer, newVectorLayer, nodeGroup, structure, bbox, bColumnDetruitExist):
        geometryName = structure['geometryName']
        newVectorLayer.isStandard = layer.isStandard
        idNameForDatabase = structure['idName']
        newVectorLayer.idNameForDatabase = idNameForDatabase
        newVectorLayer.geometryNameForDatabase = geometryName
        newVectorLayer.databasename = layer.databasename
        sridLayer = int(structure['attributes'][geometryName]['srid'])
        newVectorLayer.srid = sridLayer
        newVectorLayer.geometryDimensionForDatabase = structure['attributes'][geometryName]['is3d']
        newVectorLayer.geometryTypeForDatase = structure['attributes'][geometryName]['type']

        # Remplissage de la table SQLite liée à la couche
        parameters = {'databasename': layer.databasename, 'layerName': layer.nom, 'role': layer.role,
                      'geometryName': geometryName, 'sridProject': cst.EPSGCRS,
                      'sridLayer': sridLayer, 'bbox': bbox,
                      'detruit': bColumnDetruitExist, 'isStandard': layer.isStandard,
                      'is3D': structure['attributes'][geometryName]['is3d']}
        wfsGet = WfsGet(self, parameters)
        wfsGet.gcms_get_bis()

        # Stockage des données utiles à la synchronisation d'une couche après fermeture/ouverture de QGIS
        valStandard = 1
        if not layer.isStandard:
            valStandard = 0
        dim = 0
        if structure['attributes'][geometryName]['is3d']:
            dim = 1

        parametersForTableOfTables = {'layer': layer.nom, 'idName': idNameForDatabase, 'standard': valStandard,
                                      'database': layer.databasename, 'srid': sridLayer,
                                      'geometryName': geometryName, 'geometryDimension': dim,
                                      'geometryType': structure['attributes'][geometryName]['type']}
        SQLiteManager.InsertIntoTableOfTables(parametersForTableOfTables)

        # On stocke le srid de la layer pour pouvoir traiter le post
        newVectorLayer.srid = parameters['sridLayer']

        # Modification du formulaire d'attributs
        efffa = EditFormFieldFromAttributes(newVectorLayer, structure)
        newVectorLayer.correspondanceChampType = efffa.readData()

        # Modification de la symbologie de la couche
        listOfValuesFromItemStyle = self.client.getListOfValuesFromItemStyle(structure)
        newVectorLayer.setModifySymbols(listOfValuesFromItemStyle)

        # Affichage des données en fonction de l'échelle
        newVectorLayer.setDisplayScale(layer.minzoom, layer.maxzoom)

        # Paramétrage de l'emprise
        newVectorLayer.updateExtents(True)

        # Une couche en visualisation est non modifiable
        if layer.role == 'visu' or layer.role == 'ref':
            newVectorLayer.setReadOnly()

        # Ajout de la couche dans la carte
        QgsProject.instance().addMapLayer(newVectorLayer, False)
        nodeGroup.addLayer(newVectorLayer)
        self.guichetLayers.append(newVectorLayer)
        self.logger.debug("Layer {} added to map".format(newVectorLayer.name()))
        print("Layer {} added to map".format(newVectorLayer.name()))
        print("Layer {} contains {} objects".format(newVectorLayer.name(), len(list(newVectorLayer.getFeatures()))))

    def getUriDatabaseSqlite(self):
        uri = QgsDataSourceUri(cst.EPSG4326)
        dbName = self.projectFileName + "_espaceco"
        self.dbPath = self.projectDir + "/" + dbName + self.sqlite_ext
        uri.setDatabase(self.dbPath)
        return uri

    def addRipartLayersToMap(self):
        """Add ripart layers to the current map
        """
        uri = self.getUriDatabaseSqlite()
        self.logger.debug(uri.uri())

        maplayers = self.getAllMapLayers()
        root = self.QgsProject.instance().layerTreeRoot()
        for table in RipartHelper.croquis_layers_name:
            if table not in maplayers:
                uri.setDataSource('', table, 'geom')
                uri.setSrid(str(cst.EPSGCRS))
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                vlayer.setCrs(QgsCoordinateReferenceSystem(cst.EPSGCRS, QgsCoordinateReferenceSystem.EpsgCrsId))
                QgsProject.instance().addMapLayer(vlayer, False)
                root.insertLayer(0, vlayer)
                self.logger.debug("Layer " + vlayer.name() + " added to map")

                # ajoute les styles aux couches
                style = os.path.join(self.projectDir, "espacecoStyles", table + ".qml")
                vlayer.loadNamedStyle(style)

        self.mapCan.refresh()

    def getAllMapLayers(self):
        """
        Return the list of layer names which are loaded in the map
        :return dictionnaire des couches chargées sur la carte (key: layer name, value: layer id)
        :rtype dictionary
        """
        layers = QgsProject.instance().mapLayers()
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
        layers = QgsProject.instance().mapLayers()
        for key in layers:
            layer = layers[key]
            if type(layer) is QgsVectorLayer and layer.geometryType() is not None and layer.geometryType() == \
                    QgsWkbTypes.PolygonGeometry:
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
        mapByName = QgsProject.instance().mapLayersByName(layName)
        if len(mapByName) > 0:
            return mapByName[0]
        else:
            return None

    def emptyAllRipartLayers(self):
        """
        Supprime toutes les remarques, vide les tables de la base ripart.sqlite
        """
        ripartLayers = RipartHelper.croquis_layers
        ripartLayers[RipartHelper.nom_Calque_Signalement] = "POINT"
        try:
            self.conn = spatialite_connect(self.dbPath)
            for table in ripartLayers:
                RipartHelper.emptyTable(self.conn, table)
            ripartLayers.pop(RipartHelper.nom_Calque_Signalement, None)
            self.conn.commit()
        except RipartException as e:
            self.logger.error(format(e))
            raise
        finally:
            self.conn.close()
        self.refresh_layers()

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
            # self.conn= sqlite3.connect(self.dbPath)
            self.conn = spatialite_connect(self.dbPath)

            sql = "UPDATE " + RipartHelper.nom_Calque_Signalement + " SET "
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
        remLay = self.getLayerByName(RipartHelper.nom_Calque_Signalement)
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
        attCroquis = RipartHelper.load_attCroquis(self.projectDir)

        # Recherche tous les features sélectionnés sur la carte (pour les transformer en croquis)
        listCroquis = []
        mapLayers = self.mapCan.layers()
        for lay in mapLayers:
            if type(lay) is not QgsVectorLayer:
                continue
            for f in lay.selectedFeatures():
                # la liste des croquis
                croquiss = []
                # le type du feature
                ftype = f.geometry().type()
                geom = f.geometry()
                isMultipart = geom.isMultipart()
                # if geom.isMultipart() => explode to single parts
                if isMultipart and ftype == QgsWkbTypes.PolygonGeometry:
                    for poly in geom.asMultiPolygon():
                        croquiss.append(
                            self.makeCroquis(QgsGeometry.fromPolygonXY(poly), QgsWkbTypes.PolygonGeometry, lay.crs(),
                                             f[0]))
                elif isMultipart and ftype == QgsWkbTypes.LineGeometry:
                    for line in geom.asMultiPolyline():
                        croquiss.append(
                            self.makeCroquis(QgsGeometry.fromPolylineXY(line), QgsWkbTypes.LineGeometry, lay.crs(),
                                             f[0]))
                elif isMultipart and ftype == QgsWkbTypes.PointGeometry:
                    for pt in geom.asMultiPoint():
                        croquiss.append(
                            self.makeCroquis(QgsGeometry.fromPointXY(pt), QgsWkbTypes.PointGeometry, lay.crs(), f[0]))
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
            destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS)
            transformer = QgsCoordinateTransform(layerCrs, destCrs, QgsProject.instance())
            if ftype == QgsWkbTypes.PolygonGeometry:
                geomPoints = geom.asPolygon()
                if len(geomPoints) > 0:
                    geomPoints = geomPoints[0]  # les points du polygone
                else:
                    self.logger.debug(u"geomPoints problem " + str(fId))
                newCroquis.type = newCroquis.sketchType.Polygone
            elif ftype == QgsWkbTypes.LineGeometry:
                geomPoints = geom.asPolyline()
                newCroquis.type = newCroquis.sketchType.Ligne
            elif ftype == QgsWkbTypes.PointGeometry:
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
        dbName = self.projectFileName + "_espaceco"
        self.dbPath = self.projectDir + "/" + dbName + self.sqlite_ext
        tmpTable = "tmpTable"
        allCroquisPoints = []
        if len(listCroquis) == 0:
            return None

        cr = listCroquis[0]
        try:
            self.conn = spatialite_connect(self.dbPath)
            cur = self.conn.cursor()

            sql = u"Drop table if Exists " + tmpTable
            cur.execute(sql)

            sql = u"CREATE TABLE " + tmpTable + " (" + \
                  u"id INTEGER NOT NULL PRIMARY KEY, textGeom TEXT, centroid TEXT)"
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
        point = None
        try:
            dbName = self.projectFileName + "_espaceco"
            self.dbPath = self.projectDir + "/" + dbName + self.sqlite_ext
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
            point = None

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
        table = RipartHelper.nom_Calque_Signalement
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
        crlayers = RipartHelper.croquis_layers
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
                RipartHelper.showMessageBox(message)
                raise Exception(u"Les projets actifs diffèrent entre le serveur et le client")
