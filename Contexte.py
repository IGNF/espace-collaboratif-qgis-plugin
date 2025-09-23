# -*- coding: utf-8 -*-
"""
Created on 29 sept. 2015
Updated on 30 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""
import os.path
import ntpath
import time
from datetime import datetime
from typing import Optional

import requests

from PyQt5 import QtGui
from PyQt5.QtGui import QImage
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import spatialite_connect
from qgis.core import QgsCoordinateReferenceSystem, QgsFeatureRequest, QgsCoordinateTransform, QgsGeometry,\
    QgsVectorLayer, QgsRasterLayer, QgsProject, QgsWkbTypes, QgsLayerTreeGroup, QgsDataSourceUri, QgsMapLayerType,\
    QgsLayerTreeLayer, QgsMapLayer
from .Import_WMTS import importWMTS
from .core.PluginLogger import PluginLogger
from .core.SketchAttributes import SketchAttributes
from .core.Point import Point
from .core.Sketch import Sketch
from .core import Constantes as cst
from .core.Community import Community
from .core.CommunitiesMember import CommunitiesMember
from .core.GuichetVectorLayer import GuichetVectorLayer
from .core.EditFormFieldFromAttributes import EditFormFieldFromAttributes
from .core.WfsGet import WfsGet
from .core.SQLiteManager import SQLiteManager
from .core.ProgressBar import ProgressBar
from .core.ign_keycloak.KeycloakService import KeycloakService
from .core.FlagProject import FlagProject
from .Import_WMSR import ImportWMSR
from .PluginHelper import PluginHelper
from .FormInfo import FormInfo
from .FormChoixGroupe import FormChoixGroupe


class Contexte(object):
    """
    Classe de contexte du projet.
    """
    # instance du Contexte
    instance = None

    # client pour le service RIPart
    client = None

    # fenêtre de connexion
    loginWindow = None

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
    proxyHttp = "http://proxy.ign.fr:3128"
    proxyHttps = "https://proxy.ign.fr:3128"

    # le logger
    logger = None

    # les statistiques
    guichetLayers = []

    # extension sqlite
    sqlite_ext = ".sqlite"

    def __init__(self, QObject, QgsProject):
        """
        Constructeur.
        Initialisation du contexte et de la session utilisateur.

        :param QObject: classe fondamentale de Qt
        :type QObject: QObject

        :param QgsProject: le projet en cours
        :type QgsProject: QgsProject
        """
        self.login = None
        self.__listNameIdFromAllUserCommunities = None
        self.projectDir = QgsProject.instance().homePath()
        self.projectFileName = ntpath.basename(QgsProject.instance().fileName())
        self.QObject = QObject
        self.QgsProject = QgsProject
        self.mapCan = QObject.iface.mapCanvas()
        self.iface = QObject.iface
        self.logger = PluginLogger("Contexte").getPluginLogger()
        self.spatialRef = QgsCoordinateReferenceSystem(cst.EPSGCRS4326, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
        self.dbPath = SQLiteManager.getBaseSqlitePath()
        self.__userCommunity = None
        self.__activeCommunityName = ''
        self.__userName = ''
        self.__listNameOfCommunities = None
        self.__mapToolsReport = None
        self.__communities = None
        # Connexion avec keycloack
        self.__keycloakService = None
        self.__tokenAccess = ''
        self.__tokenType = ''
        self.__tokenTimerStart = 0
        self.__tokenExpireIn = 0
        self.urlHostEspaceCo = ''
        # Par défaut dictionnaire des proxies à vide
        # sinon il doit être rempli avec {"http": "http://proxy.ign.fr:3128", "https": "https://proxy.ign.fr:3128"}
        # {"http": self.proxyHttp, "https": self.proxyHttps}
        self.proxies = {}

        try:
            # retrouve les formats de fichiers joints acceptés à partir du fichier formats.txt.
            formatFile = open(os.path.join(self.plugin_path, 'files', 'formats.txt'), 'r')
            lines = formatFile.readlines()
            self.formats = [x.split("\n")[0] for x in lines]

            self.urlHostEspaceCo = self.__setUrlHostEspaceCo()

        except Exception as e:
            self.logger.error("init contexte:" + format(e))
            raise

    def getCommunities(self) -> []:
        """
        :return: les groupes auxquels l'utilisateur est abonné.
        """
        return self.__communities

    def setCommunities(self, communities) -> None:
        """
        Affecte les groupes de l'utilisateur au contexte.

        :param communities: les groupes avec leurs caractéristiques
        :type communities: list
        """
        self.__communities = communities

    def getListNameIdFromAllUserCommunities(self) -> []:
        """
        :return: la liste des noms de groupes de l'utilisateur
        """
        return self.__listNameIdFromAllUserCommunities

    def setListNameIdFromAllUserCommunities(self, listNameIdFromAllUserCommunities) -> None:
        """
        Affecte la liste des noms de groupes de l'utilisateur au contexte.

        :param listNameIdFromAllUserCommunities: la liste des groupes utilisateur paramétrée dans l'espace collaboratif
        :type listNameIdFromAllUserCommunities: list
        """
        self.__listNameIdFromAllUserCommunities = listNameIdFromAllUserCommunities

    def getUserNameCommunity(self) -> str:
        """
        :return: le nom de l'utilisateur du groupe actif auquel il appartient
        """
        return self.__userName

    def setUserNameCommunity(self, userName) -> None:
        """
        Affecte le nom de l'utilisateur du groupe actif au Contexte.

        :param userName: le nom de l'utilisateur
        :type userName: str
        """
        self.__userName = userName

    def getUserCommunity(self) -> Community:
        """
        :return: le groupe de l'utilisateur
        """
        return self.__userCommunity

    def setUserCommunity(self, community) -> None:
        """
        Affecte le groupe de l'utilisateur au Contexte.

        :param community: le groupe de l'utilisateur et ses caractéristiques
        :type community: Community
        """
        self.__userCommunity = community

    def setActiveCommunityName(self, name) -> None:
        """
        Affecte le nom du groupe actif de l'utilisateur au Contexte.

        :param name: le nom du groupe actif
        :type name: str
        """
        self.__activeCommunityName = name

    def getActiveCommunityName(self) -> str:
        """
        :return: le nom du groupe actif de l'utilisateur
        """
        return self.__activeCommunityName

    def __setUrlHostEspaceCo(self) -> str:
        """
        Affecte le nom de l'url host de l'espace collaboratif trouvé dans le fichier de configuration au contexte.
        Si vide ou None donne un nom d'url par défaut.
        """
        url = PluginHelper.load_urlhost(self.projectDir).text
        if url == '' or url is None:
            url = 'https://espacecollaboratif.ign.fr'
        return url

    @staticmethod
    def IsLayerInMap(layerName) -> bool:
        """
        Recherche une couche dans le projet.

        :param layerName: le nom de la couche
        :type layerName: str

        :return: True, si la couche existe dans le projet, False sinon
        """
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == layerName:
                return True
        return False

    @staticmethod
    def getInstance(QObject=None, QgsProject=None, bFlag=False):
        """
        :param QObject: classe fondamentale de Qt

        :param QgsProject: le projet en cours

        :param bFlag: indique si l'utilisateur a cliqué sur les boutons de connexion ou sur l'aide du plugin
        :type bFlag: bool

        :return: l'instance unique du Contexte.
        """
        # Si l'utilisateur a cliqué sur le bouton de connexion ou sur l'aide du plugin alors le projet doit être
        # marqué comme tel. Les fichiers de paramètres sont alors copiés dans le répertoire du projet utilisateur.
        if bFlag:
            flp = FlagProject()
            bResBoolEntry = flp.isBoolEntryInProject()
            if not bResBoolEntry:
                flp.setWriteBoolEntryInProject()
            bResCopyFiles = flp.AreFilesCopiedInProject()
            if not bResCopyFiles:
                flp.copyFilesToProject()

        if not Contexte.instance or (Contexte.instance.projectDir != QgsProject.instance().homePath() or
                                     ntpath.basename(QgsProject.instance().fileName()) not in [
                                         Contexte.instance.projectFileName + ".qgs",
                                         Contexte.instance.projectFileName + ".qgz"]):
            Contexte.instance = Contexte.__createInstance(QObject, QgsProject)
        return Contexte.instance

    @staticmethod
    def __createInstance(QObject, QgsProject):
        """
        Création de l'instance du contexte du projet.

        :param QObject: classe fondamentale de Qt
        :type QObject: QObject

        :param QgsProject: le projet en cours
        :type QgsProject: QgsProject

        :return: l'instance unique du projet ou None si problème d'instanciation
        """
        try:
            Contexte.instance = Contexte(QObject, QgsProject)
            Contexte.instance.logger.debug("Nouvelle instance de contexte créée")
        except Exception as e:
            return None
        return Contexte.instance

    def getConnexionEspaceCollaboratifWithKeycloak(self, bAutomaticConnection) -> bool:
        """
        Lance la connexion au service de l'espace collaboratif en utilisant les fonctionnalités d’authentification
        et d’autorisation de Keycloak.

        :param bAutomaticConnection: à True dans le cas d'une connexion obligatoire, False sinon
        :type bAutomaticConnection: bool

        :return: True si la connexion à l'espace collaboratif est établie, False sinon
        """
        if bAutomaticConnection is False:
            return True

        if self.__keycloakService is not None:
            self.__keycloakService.logout()
            self.__keycloakService = None

        self.logger.debug("getConnexionEspaceCollaboratifWithKeycloak")
        self.__tokenTimerStart = time.perf_counter()
        KEYCLOAK_SERVER_URI = "https://sso.geopf.fr/"
        KEYCLOAK_CLIENT_ID = "espaceco-qgis"
        KEYCLOAK_CLIENT_SECRET = "rv8rOUBCnHsh7LH63FXw3vetaxbmCLso"
        KEYCLOAK_REALM_NAME = "geoplateforme"
        self.__keycloakService = KeycloakService(KEYCLOAK_SERVER_URI, KEYCLOAK_REALM_NAME, KEYCLOAK_CLIENT_ID,
                                                 client_secret=KEYCLOAK_CLIENT_SECRET, proxies=self.proxies)
        r = self.__keycloakService.get_authorization_code(["email", "profile", "openid", "roles"])
        r = self.__keycloakService.get_access_token(r["code"][0])
        self.__tokenAccess = r["access_token"]
        self.__tokenExpireIn = r["expires_in"]
        print(self.__tokenExpireIn)
        print(datetime.now())
        self.__tokenType = r["token_type"]
        r = self.__keycloakService.get_userinfo(r["access_token"])
        self.login = r['email']
        return self.__connectToService()

    def __connectToService(self) -> bool:
        """
        Après la connexion avec Keycloak
         - recherche les groupes de l'utilisateur
         - propose à l'utilisateur le choix du groupe de travail à travers le dialogue "Paramètres de travail"
        En fonction de la réponse de l'utilisateur
         - clic sur Continuer
            - enregistrement dans le contexte du groupe avec ses caractéristiques
            - sauvegarde du groupe dans le xml de configuration
            - affiche les informations de connexion et de travail à l'utilisateur
         - clic sur le bouton Annuler → fermeture de la boite de dialogue

        :return: True si la connexion est établie et si l'utilisateur n'a pas annulé son choix, False sinon
        """
        PluginHelper.save_login(self.projectDir, self.login)
        xmlgroupeactif = PluginHelper.load_XmlTag(self.projectDir, PluginHelper.xml_GroupeActif, "Serveur")
        if xmlgroupeactif is not None:
            self.__activeCommunityName = PluginHelper.load_XmlTag(self.projectDir, PluginHelper.xml_GroupeActif,
                                                                  "Serveur").text
            if self.__activeCommunityName is not None:
                self.logger.debug("Contexte.__activeCommunityName " + self.__activeCommunityName)
        try:
            # Recherche des communautés
            communities = CommunitiesMember(self.urlHostEspaceCo, self.__tokenType, self.__tokenAccess, self.proxies)
            communities.extractCommunities()
            self.setCommunities(communities.getCommunities())
            # La liste des communautés à afficher dans la boite de choix des communautés
            self.setListNameIdFromAllUserCommunities(communities.getListNameIdFromAllUserCommunities())
            self.setUserNameCommunity(communities.getUserName())
            dlgSelectedCommunities = FormChoixGroupe(self)
            dlgSelectedCommunities.exec_()
            # bouton Continuer (le choix du nouveau profil est validé)
            if not dlgSelectedCommunities.getCancel():
                # Le nouvel id et nom du groupe sont retournés dans un tuple idNameCommunity
                idNameCommunity = dlgSelectedCommunities.getIdAndNameFromSelectedCommunity()

                # La communauté de l'utilisateur est stocké dans le contexte
                self.setUserCommunity(communities.getUserCommunity(idNameCommunity[1]))
                self.setActiveCommunityName(idNameCommunity[1])

                # Sauvegarde du groupe actif dans le xml du projet utilisateur
                PluginHelper.saveActiveCommunityName(self.projectDir, idNameCommunity[1])
                self.setActiveCommunityName(idNameCommunity[1])

                # On enregistre le groupe comme groupe préféré pour la création de signalement
                # Si ce n'est pas le même qu'avant, on vide les thèmes préférés
                formPreferredGroup = PluginHelper.load_preferredGroup(self.projectDir)
                if formPreferredGroup != idNameCommunity[1]:
                    # TODO Mélanie, il s'agit bien des themes utilisateur (ceux dans community)
                    #  et non activeThemes ou shared_themes ?
                    PluginHelper.save_preferredThemes(self.projectDir, self.getUserCommunity().getTheme())
                PluginHelper.save_preferredGroup(self.projectDir, idNameCommunity[1])
            # Bouton Annuler
            elif dlgSelectedCommunities.getCancel():
                dlgSelectedCommunities.close()
                self.__connectionResult = False
                return self.__connectionResult
            # Les informations de connexion sont montrées à l'utilisateur
            self.__displayLoginInformationsOnScreen()
            self.__connectionResult = True
        except Exception as e:
            self.logger.error(format(e))
            self.client = None
            self.profil = None
            self.__connectionResult = False
            PluginHelper.showMessageBox(PluginHelper.notNoneValue(format(e)))
        return self.__connectionResult

    def __displayLoginInformationsOnScreen(self) -> None:
        """
        Affiche à l'écran et à destination de l'utilisateur les informations de connexion à l'espace collaboratif.
        """
        dlgInfo = FormInfo()
        # Modification du logo en fonction du groupe
        # TODO : si utilisateur sans groupe getUserCommunity est a None, il faut faire un test et changer le code
        # TODO faire une fonction __setDisplayLogo()
        # TODO sai1 sur la qualif par exemple
        if self.getUserCommunity().getLogo() != "":
            image = QImage()
            image.loadFromData(requests.get(self.getUserCommunity().getLogo()).content)
            dlgInfo.logo.setPixmap(QtGui.QPixmap(image))
        elif self.getUserCommunity().getName() == "Profil par défaut":
            dlgInfo.logo.setPixmap(QtGui.QPixmap(":/plugins/ign_espace_collaboratif_qgis/images/logo_IGN.png"))
        dlgInfo.textInfo.setText(u"<b>Connexion réussie à l'Espace collaboratif</b>")
        dlgInfo.textInfo.append("<br/>Serveur : {}".format(self.urlHostEspaceCo))
        dlgInfo.textInfo.append("Login : {}".format(self.login))
        dlgInfo.textInfo.append("Groupe : {}".format(self.getUserCommunity().getName()))
        zoneExtraction = PluginHelper.load_CalqueFiltrage(self.projectDir).text
        if zoneExtraction == "" or zoneExtraction is None or len(
                self.QgsProject.instance().mapLayersByName(zoneExtraction)) == 0:
            dlgInfo.textInfo.append("Zone de travail : pas de zone définie")
            PluginHelper.setXmlTagValue(self.projectDir, PluginHelper.xml_Zone_extraction, "", "Map")
        else:
            dlgInfo.textInfo.append("Zone de travail : {}".format(zoneExtraction))
        # TODO faut-il contrôler (mais de quelle manière ?) la zone de travail de l'utilisateur
        #  avec la variable emprises (FR, 38185, autre) de community qui autorise les droits de saisie
        #  sachant que nous n'avons pas pour l'instant l'emprise géographique stockée sur le serveur
        #  Faut-il indiquer l'emprise sur le serveur ? pour distinguer emprise serveur et zone de travail QGIS ?
        #  je l'ai ajouté dans le doute
        strEmprises = ''
        if len(self.getUserCommunity().getEmprises()) == 0:
            strEmprises = 'aucune,'
        else:
            for emprise in self.getUserCommunity().getEmprises():
                strEmprises += "{},".format(emprise)
        dlgInfo.textInfo.append("Emprise(s) serveur : {}".format(strEmprises[:-1]))
        dlgInfo.exec_()

    def getTokenType(self):
        """
        :return: le type de jeton d'authentification à l'espace collaboratif
        """
        return self.__tokenType

    def getTokenAccess(self):
        """
        :return: le jeton d'authentification à l'espace collaboratif
        """
        return self.__tokenAccess

    def createTablesReportsAndSketchs(self) -> None:
        """
        Création des tables de signalements et de croquis dans la base SQLite du projet utilisateur.
        """
        for table in PluginHelper.reportSketchLayersName:
            SQLiteManager.emptyTable(table)
            SQLiteManager.deleteTable(table)
            if table == cst.nom_Calque_Signalement:
                SQLiteManager.createReportTable()
            elif table in PluginHelper.sketchLayers:
                SQLiteManager.createSketchTable(table, PluginHelper.sketchLayers[table])
        SQLiteManager.vacuumDatabase()

    def importWFS(self, layer) -> ():
        """
        Import des couches WFS sélectionnées dans la boite de dialogue "Charger les couches de mon groupe"
        dans le projet QGIS de l'utilisateur.

        :param layer: la couche à importer dans le projet
        :type layer: QgsVectorLayer

        :return: la nouvelle couche de type GuichetVectorLayer créée et un booléen indiquant si la colonne
                 'détruit' existe (couche BDUni)
        """
        # Création éventuelle de la table SQLite liée à la couche
        sqliteManager = SQLiteManager()

        # Si la table du nom de la couche existe,
        # elle est vidée, détruite et recréée
        SQLiteManager.emptyTable(layer.name())
        SQLiteManager.deleteTable(layer.name())
        bColumnDetruitExist = sqliteManager.createTableFromLayer(layer)

        # Création de la source de données pour la couche dans la carte liée à la table SQLite
        uri = self.getUriDatabaseSqlite()
        self.logger.debug(uri.uri())
        uri.setDataSource('', layer.name(), layer.geometryName)
        uri.setSrid(str(cst.EPSGCRS4326))
        geomDim = ""
        geomType = ""
        for attribute in layer.attributes:
            if attribute['name'] != layer.geometryName:
                continue
            geomDim = attribute['is3d']
            geomType = attribute['type']
        parameters = {'uri': uri.uri(), 'name': layer.name(), 'genre': 'spatialite', 'databasename': layer.databasename,
                      'sqliteManager': sqliteManager, 'idName': layer.idName,
                      'geometryName': layer.geometryName, 'geometryDimension': geomDim,
                      'geometryType': geomType}

        vlayer = GuichetVectorLayer(parameters)
        # vlayer = QgsVectorLayer(uri.uri(), layer.name, 'spatialite')
        vlayer.setCrs(QgsCoordinateReferenceSystem(cst.EPSGCRS4326, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId))
        return vlayer, bColumnDetruitExist

    def addGuichetLayersToMap(self, guichet_layers, bbox, nameGroup) -> None:
        """
        Ajoute au projet les couches sélectionnées par l'utilisateur au projet courant.
        Les couches WFS sont ajoutées dans un groupe QGIS préfixé "[ESPACE CO] nomCouche" et formatées (formatLayer)
        en récupérant les informations envoyées par le serveur. Ces couches sont de type GuichetVectorLayer qui dérive
        de QgsVectorLayer.
        Les couches WMS et WMS-R sont ajoutées à la suite des autres.

        NB : une Exception est envoyée si la récupération, l'import et la transformation des couches
        se sont mal passées.

        :param guichet_layers: liste des couches sélectionnées par l'utilisateur dans la boite
                               "Charger les couches de mon groupe"
        :type guichet_layers: list

        :param bbox: la boite englobante de la zone de travail utilisateur
        :type bbox: Box

        :param nameGroup: le nom du groupe utilisateur
        :type nameGroup: str
        """
        progress = None
        try:
            # Quelles sont les cartes chargées dans le projet QGIS courant
            maplayers = self.getAllMapLayers()
            root = self.QgsProject.instance().layerTreeRoot()

            # Le groupe existe-t-il dans le projet
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
            # sauf celui-ci a cliqué sur Non à la demande de destruction dans ce cas la fonction retourne False
            if not self.removeLayers(guichet_layers, maplayers):
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
                Ajout des couches WFS sélectionnées dans "Mon guichet"
                '''
                if layer.type == cst.FEATURE_TYPE:
                    sourceLayer = self.importWFS(layer)
                    if not sourceLayer[0].isValid():
                        endMessage += "Layer {} failed to load !\n".format(layer.name())
                        continue
                    endMessage += self.getAndFormatLayer(layer, sourceLayer[0], nodeGroup, bbox, sourceLayer[1])
                    endMessage += "\n"

                if layer.type == cst.GEOSERVICE:
                    '''
                    Ajout des couches WMTS selectionnées dans "Mon guichet"
                    '''
                    if layer.geoservice['type'] == cst.WMTS:
                        importWmts = importWMTS(self, layer)
                        titleLayer_uri = importWmts.getWtmsUrlParams(layer.geoservice['layers'])
                        print("titleLayer_uri : {}".format(titleLayer_uri))
                        if 'Exception' in titleLayer_uri[0]:
                            endMessage += "{0} : {1}\n\n".format(layer.name(), titleLayer_uri[1])
                            continue
                        rlayer = QgsRasterLayer(titleLayer_uri[1], titleLayer_uri[0], 'wms')
                        if not rlayer.isValid():
                            endMessage = "Layer {} failed to load !".format(rlayer.name())
                            continue

                        self.QgsProject.instance().addMapLayer(rlayer, False)
                        # Insertion à la fin avec -1
                        root.insertLayer(-1, rlayer)
                        tmp = "Couche {0} ajoutée à la carte.\n\n".format(rlayer.name())
                        self.logger.debug(tmp)
                        message = tmp
                        endMessage += message

                    '''
                    Ajout des couches WMS-R selectionnées dans "Mon guichet"
                    '''
                    if layer.geoservice['type'] == cst.WMS:
                        importWmsr = ImportWMSR(layer)
                        titleLayer_uri = importWmsr.getWmsrUrlParams()
                        print("titleLayer_uri : {}".format(titleLayer_uri))
                        rlayer = QgsRasterLayer(titleLayer_uri[1], titleLayer_uri[0], 'wms')
                        if not rlayer.isValid():
                            endMessage += "Layer {} failed to load !".format(rlayer.name())
                            continue

                        self.QgsProject.instance().addMapLayer(rlayer, False)
                        # Insertion à la fin avec -1
                        root.insertLayer(-1, rlayer)
                        self.logger.debug("Layer {} added to map".format(rlayer.name()))
                        message = "Couche {0} ajoutée à la carte.\n\n".format(rlayer.name())
                        endMessage += message
            progress.close()

            # Rafraichissement de la carte
            self.mapCan.refresh()
            QMessageBox.information(self.iface.mainWindow(), cst.IGNESPACECO, endMessage)

        except Exception as e:
            if progress is not None:
                progress.close()
            message = str(format(e))
            if message.find('getMaxNumrec') != -1:
                message = "Attention la table est peut-être vide de données " \
                          "ou n'existe pas. Veuillez contacter le gestionnaire de votre groupe. {}".format(str(e))
            self.logger.error(message)
            self.iface.messageBar(). \
                pushMessage("Remarque",
                            str(e),
                            message,
                            level=1, duration=3)
            print(str(e))

    def hideColumn(self, layer, columnName) -> None:
        """
        Masquer un champ dans le formulaire d'attributs de QGIS pour une couche donnée en entrée.

        NB : fonction non utilisée (mais pourrait servir)

        :param layer: la couche dont on doit masquer le champ
        :type layer: QgsVectorLayer

        :param columnName: le nom du champ
        :type columnName: str
        """
        config = layer.attributeTableConfig()
        columns = config.columns()
        for column in columns:
            if column.name == columnName:
                column.hidden = True
                break
        config.setColumns(columns)
        layer.setAttributeTableConfig(config)

    def replaceSpecialCharacter(self, replaceTo) -> str:
        """
        Remplace une liste de caractères spéciaux par une chaine vide et la passe en minuscules.

        :param replaceTo: la chaine de caractères supposée contenir des caractères spéciaux.
        :type replaceTo: str

        :return: la chaine de caractères en minuscules sans caractères spéciaux
        """
        tmp = replaceTo.replace(' ', '')
        tmp = tmp.replace('-', '')
        tmp = tmp.replace('_', '')
        tmp = tmp.replace('+', '')
        tmp = tmp.replace('.', '')
        tmp = tmp.replace('(', '')
        tmp = tmp.replace(')', '')
        return tmp.lower()

    def removeLayers(self, guichet_layers, maplayers, bAskForConfirmation=True) -> bool:
        """
        Supprime les couches WFS et WMS présentent dans le projet en fonction de la sélection de l'utilisateur
        dans la boite "Charger les couches de mon groupe".

        :param guichet_layers: liste des couches sélectionnées par l'utilisateur dans la boite
                               "Charger les couches de mon groupe"
        :type guichet_layers: list

        :param maplayers: la liste des couches présentes dans le projet
        :type maplayers: dict

        :param bAskForConfirmation: à True s'il faut demander l'avis utilisateur, False sinon
        :type bAskForConfirmation: bool

        :return: True si la suppression a pu s'effectuer, False si l'utilisateur change d'avis
        """
        tmp = ''
        removeLayers = set()
        for gLayer in guichet_layers:
            noSpecialCharacterInLayerName = self.replaceSpecialCharacter(gLayer.name())
            # Cas particulier des couches WMTS
            nameLayers = self.replaceSpecialCharacter(gLayer.layers)
            for k, v in maplayers.items():
                noSpecialCharacterInMapLayerName = self.replaceSpecialCharacter(v.name())
                if (noSpecialCharacterInLayerName == noSpecialCharacterInMapLayerName) or \
                        (nameLayers.find(noSpecialCharacterInMapLayerName) != -1):
                    removeLayers.add(v.name())
                    tmp += "{}, ".format(v.name())
        return self.removeLayersById(removeLayers, tmp, bAskForConfirmation)

    def removeLayersFromProject(self, guichet_layers, layersInTableOfTables, bAskForConfirmation=True):
        """
        À partir de la liste des couches présentent dans "guichet_layers", supprime les couches WFS (présentent
        dans la table des tables de la base SQLite du projet et pour le groupe préfixé "[ESPACE CO] ") et WMS
        présentent dans le projet.

        NB : si la couche n'est pas retrouvée dans la table des tables mais qu'elle existe dans le projet,
        alors, elle est supprimée

        :param guichet_layers: liste des couches sélectionnées par l'utilisateur dans la boite
                               "Charger les couches de mon groupe"
        :type guichet_layers: list

        :param layersInTableOfTables: la liste des couches présentes dans la table des tables
                                      dans la base SQLite du projet
        :type layersInTableOfTables: list

        :param bAskForConfirmation: à True s'il faut demander l'avis utilisateur, False sinon
        :type bAskForConfirmation: bool

        :return: True si la suppression a pu s'effectuer, False si l'utilisateur change d'avis
        """
        tmp = ''
        removeLayers = set()
        for layer in guichet_layers:
            # Dans ce cas précis, "maplayers" représente la liste des couches présentent dans la table des tables
            # même si "mapLayers" est vide, les couches peuvent encore exister dans le projet
            if layer.name() not in layersInTableOfTables or len(layersInTableOfTables) == 0:
                listLayers = QgsProject.instance().mapLayersByName(layer.name())
                if len(listLayers) == 1:
                    # Vérifie si la couche appartient à un groupe ESPACECO ?
                    if listLayers[0].type() != QgsMapLayerType.RasterLayer:
                        root = QgsProject.instance().layerTreeRoot()
                        nodesGroup = root.findGroups()
                        searchedGroup = None
                        for ng in nodesGroup:
                            if ng.name().find(cst.ESPACECO) != -1:
                                searchedGroup = ng
                                break
                        if searchedGroup is not None:
                            for child in searchedGroup.children():
                                # Vérifie si l'enfant est une couche et si c'est celle recherchée
                                if isinstance(child, QgsLayerTreeLayer) and child.layerId() == listLayers[0].id():
                                    print("{0} : {1}".format(layer.name(), len(list(listLayers[0].getFeatures()))))
                                    removeLayers.add((layer.name()))
                                    tmp += "{}, ".format(layer.name())
            else:
                removeLayers.add(layer.name())
                tmp += "{}, ".format(layer.name())
        return self.removeLayersById(removeLayers, tmp, bAskForConfirmation)

    def removeLayersById(self, removeLayers, tmp, bAskForConfirmation) -> bool:
        """
        Suppression de couche(s) dans un projet par leur identifiant QGIS.

        :param removeLayers: les liste des couches à supprimer
        :type removeLayers: set

        :param tmp: la liste des noms de couches à supprimer séparés par une virgule pour le texte du message
                    d'avertissement de suppression à l'utilisateur
        :type tmp: str

        :param bAskForConfirmation: à True s'il faut demander l'avis utilisateur, False sinon
        :type bAskForConfirmation: bool

        :return: True si la suppression a pu s'effectuer, False si l'utilisateur change d'avis
        """
        if len(removeLayers) == 0:
            return True

        if bAskForConfirmation:
            if len(removeLayers) == 1:
                message = "La couche [{}] existe déjà, elle va être supprimée.\nVoulez-vous continuer ?".format(
                    tmp[:-2])
            else:
                message = "Les couches [{}] existent déjà, elles vont être supprimées.\nVoulez-vous continuer ?"\
                    .format(tmp[:-2])
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

    def getAndFormatLayer(self, layer, newVectorLayer, nodeGroup, bbox, bColumnDetruitExist) -> str:
        """
        - Lance une requête GET vers le serveur de l'espace collaboratif pour récupérer les données de la couche.
        - Stocke dans la table des tables de la base SQLite les données nécessaires à l'envoi de mises à jour
        vers le serveur.
        - Modification du formulaire d'attributs de la couche.
        - Modification de la symbologie de la couche pour se rapprocher au plus près de la représentation graphique
        du site espace collaboratif
        - Ajout de la couche au groupe préfixé "[ESPACE CO] Nom du groupe"

        :param layer: la couche brute issue de la sélection du groupe de l'utilisateur
        :type layer: Layer

        :param newVectorLayer: la nouvelle couche formatée à importer dans le projet
        :type newVectorLayer: GuichetVectorLayer

        :param nodeGroup: l'identifiant du noeud dans lequel est ajouté la couche en cours de traitement
        :type nodeGroup: QgsLayerTreeGroup

        :param bbox: boite englobante de la zone de travail utilisateur
        :type bbox: Box

        :param bColumnDetruitExist: indique si la colonne "detruit" existe dans la couche (BDUni uniquement)
        :type bColumnDetruitExist: bool

        :return: un message de fin de traitement
        """
        geometryName = layer.geometryName
        newVectorLayer.isStandard = layer.isStandard
        idNameForDatabase = layer.idName
        newVectorLayer.idNameForDatabase = idNameForDatabase
        newVectorLayer.geometryNameForDatabase = geometryName
        newVectorLayer.databasename = layer.databasename
        newVectorLayer.srid = layer.srid
        newVectorLayer.geometryDimensionForDatabase = layer.is3d
        newVectorLayer.geometryTypeForDatabase = layer.geometryType
        headers = {'Authorization': '{} {}'.format(self.getTokenType(), self.getTokenAccess())}
        # Remplissage de la table SQLite liée à la couche
        parameters = {'databasename': layer.databasename, 'layerName': layer.name(),
                      'sridLayer': layer.srid, 'role': layer.role, 'isStandard': layer.isStandard,
                      'is3D': layer.is3d, 'geometryName': geometryName, 'sridProject': cst.EPSGCRS4326,
                      'bbox': bbox, 'detruit': bColumnDetruitExist, 'numrec': "0",
                      'urlHostEspaceCo': self.urlHostEspaceCo, 'headers': headers,
                      'proxies': self.proxies, 'databaseid': layer.databaseid, 'tableid': layer.tableid
                      }
        wfsGet = WfsGet(parameters)
        maxNumrecMessage = wfsGet.gcmsGet(True)

        # Stockage des données utiles à la synchronisation d'une couche après fermeture/ouverture de QGIS
        valStandard = 1
        if not layer.isStandard:
            valStandard = 0
        dim = 0
        if layer.is3d:
            dim = 1

        parametersForTableOfTables = {'layer': layer.name(), 'idName': idNameForDatabase, 'standard': valStandard,
                                      'database': layer.databasename, 'databaseid': layer.databaseid,
                                      'srid': layer.srid, 'geometryName': geometryName, 'geometryDimension': dim,
                                      'geometryType': layer.geometryType, 'numrec': maxNumrecMessage[0],
                                      'tableid': layer.tableid}
        SQLiteManager.InsertIntoTableOfTables(parametersForTableOfTables)

        # On stocke le srid de la layer pour pouvoir traiter le post
        newVectorLayer.srid = parameters['sridLayer']

        # Modification du formulaire d'attributs
        efffa = EditFormFieldFromAttributes(newVectorLayer, layer.attributes)
        # print("layer.attributes:\n{}".format(layer.attributes))
        efffa.readDataAndApplyConstraints()

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

    def getAllMapLayers(self) -> {}:
        """
        Recherche l'ensemble des couches du projet utilisateur.

        :return: l'ensemble des couches chargées sous la forme {key: layer name, value: QgsMapLayer}
        """
        layers = self.QgsProject.instance().mapLayers()
        maplayers = {}
        for key in layers:
            layer = layers[key]
            maplayers[layer.name()] = layer
        return maplayers

    def getMapPolygonLayers(self) -> {}:
        """
        Recherche dans le projet les couches qui sont de type 'polygon' ou 'multipolygon'.

        :return: les couches trouvées sous la forme {key: layer id, value: layer name}
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
            polylayers[layer.id()] = layer.name()
        return polylayers

    def getLayerByName(self, layName) -> Optional[QgsMapLayer]:
        """
        Recherche dans le projet la couche donnée par son nom en paramètre.

        :param layName: le nom de la couche
        :type layName: str

        :return: la PREMIERE couche trouvée, None sinon
        """
        mapByName = self.QgsProject.instance().mapLayersByName(layName)
        if len(mapByName) > 0:
            return mapByName[0]
        else:
            return None

    def refreshLayers(self) -> None:
        """
        Rafraichissement à l'écran de l'ensemble des couches du projet.
        """
        for layer in self.mapCan.layers():
            layer.triggerRepaint()

    def countReportsByStatut(self, statut):
        """
        Lance une QgsFeatureRequest pour sélectionner les signalements avec le statut donné en paramètre.

        :param statut: le statut du signalement
        :type statut: str

        :return: le nombre de signalements sélectionnés dans la couche 'Signalement'
        """
        remLay = self.getLayerByName(cst.nom_Calque_Signalement)
        expression = '"Statut" = \'' + statut + '\''
        filtFeatures = remLay.getFeatures(QgsFeatureRequest().setFilterExpression(expression))
        return len(list(filtFeatures))

    def asSelectedFeaturesInMap(self) -> bool:
        """
        Vérifie si la sélection comporte un ou plusieurs objets sans distinction de couches.

        :return: True si la sélection contient un ou plusieurs objets, False sinon
        """
        mapLayers = self.mapCan.layers()
        for layer in mapLayers:
            if type(layer) is QgsVectorLayer or type(layer) is GuichetVectorLayer:
                if len(layer.selectedFeatures()) > 0:
                    return True
        return False

    def makeSketchFromSelection(self) -> []:
        """
        Transformation en croquis du (ou des) objet(s) sélectionné(s) par l'utilisateur (peu importe la couche utilisée
        pour cette création).

        :return: la liste des croquis
        """
        # Chargement à partir du fichier de configuration des attributs de l'objet sélectionné.
        # Ces attributs deviendront les attributs du croquis.
        # attCroquis est un dictionnaire : key: nom calque, value: liste des attributs
        attCroquis = PluginHelper.load_attCroquis(self.projectDir)

        # La listes de croquis définitifs
        listCroquis = []
        mapLayers = self.mapCan.layers()
        # Recherche tous les objets sélectionnés sur la carte pour les transformer en croquis
        for lay in mapLayers:
            # Quelques vérifications d'usage
            if type(lay) is not QgsVectorLayer and type(lay) is not GuichetVectorLayer:
                continue
            if len(lay.selectedFeatures()) == 0:
                continue
            # Si le CRS de la couche n'est pas défini, on prévient l'utilisateur et on sort
            if not lay.sourceCrs().isValid():
                nom = lay.name()
                message = "La couche {0} ne peut pas être utilisée pour créer un signalement car son système " \
                          "de projection n'est pas défini. Veuillez le définir avant de créer " \
                          "un signalement.".format(nom)
                PluginHelper.showMessageBox(message)
                return []
            # Autant de croquis que d'objets sélectionnés qui peuvent être issus de différentes couches
            for f in lay.selectedFeatures():
                # la liste des croquis temporaires
                croquiss = []
                # le type du feature
                ftype = f.geometry().type()
                geom = f.geometry()
                isMultipart = geom.isMultipart()
                # if geom.isMultipart() => explode to single parts
                if isMultipart and ftype == QgsWkbTypes.GeometryType.PolygonGeometry:
                    for poly in geom.asMultiPolygon():
                        croquiss.append(
                            self.makeSketch(QgsGeometry.fromPolygonXY(poly), ftype, lay.crs(), f[0]))
                elif isMultipart and ftype == QgsWkbTypes.GeometryType.LineGeometry:
                    for line in geom.asMultiPolyline():
                        croquiss.append(
                            self.makeSketch(QgsGeometry.fromPolylineXY(line), ftype, lay.crs(), f[0]))
                elif isMultipart and ftype == QgsWkbTypes.GeometryType.PointGeometry:
                    for pt in geom.asMultiPoint():
                        croquiss.append(
                            self.makeSketch(QgsGeometry.fromPointXY(pt), ftype, lay.crs(), f[0]))
                else:
                    croquiss.append(self.makeSketch(geom, ftype, lay.crs(), f[0]))

                # Transfert vers le croquis des éventuels attributs de l'objet sélectionné
                # Ajout du croquis temporaire vers la liste définitive
                for croquisTemp in croquiss:
                    if lay.name() in attCroquis:
                        for att in attCroquis[lay.name()]:
                            idx = lay.fields().lookupField(att)
                            attribut = SketchAttributes(att, f.attributes()[idx])
                            croquisTemp.addAttribut(attribut)
                    listCroquis.append(croquisTemp)

        return listCroquis

    def makeSketch(self, geom, ftype, layerCrs, fId) -> Optional[Sketch]:
        """
        Génère un croquis à partir d'une géométrie.
        Les coordonnées des points du croquis doivent être transformées dans le crs de l'espace collaboratif (4326).

        NB : une exception est envoyée vers le fichier de log, si problème dans la création du croquis.

        :param geom: la géométrie du futur croquis
        :type geom: QgsGeometry

        :param ftype: le type de l'objet géométrique
        :type ftype: QgsWkbTypes

        :param layerCrs: le système de coordonnées de référence du calque dont provient le feature
        :type layerCrs: QgsCoordinateReferenceSystem

        :param fId: l'id de l'objet géométrique (valeur du premier attribut du feature)
        :type fId: int

        :return: le croquis créé ou None si problème dans la création du croquis
        """
        newSketch = Sketch()
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
                newSketch.type = newSketch.sketchType.Polygone
            elif ftype == QgsWkbTypes.GeometryType.LineGeometry:
                geomPoints = geom.asPolyline()
                newSketch.type = newSketch.sketchType.Ligne
            elif ftype == QgsWkbTypes.GeometryType.PointGeometry:
                geomPoints = [geom.asPoint()]
                newSketch.type = newSketch.sketchType.Point
            else:
                newSketch.type = newSketch.sketchType.Vide

            for pt in geomPoints:
                pt = transformer.transform(pt)
                newSketch.addPoint(Point(pt.x(), pt.y()))

        except Exception as e:
            self.logger.error(u"in makeCroquis:" + format(e))
            return None

        return newSketch

    def selectReportByNumero(self, noSignalements) -> None:
        """
        Sélection des signalements par leur numéro (identifiant espace collaboratif).

        :param noSignalements: contient les numéros de signalements formatés pour la condition sql : IN
                               en vue d'une requête vers la base SQLite du projet en cours
        :type noSignalements: str
        """
        self.conn = spatialite_connect(self.dbPath)
        cur = self.conn.cursor()
        table = cst.nom_Calque_Signalement
        lay = self.getLayerByName(table)
        sql = "SELECT * FROM " + table + "  WHERE noSignalement IN (" + noSignalements + ")"
        rows = cur.execute(sql)
        featIds = []
        for row in rows:
            featIds.append(row[0])
        lay.selectByIds(featIds)

    def getCroquisForReport(self, noSignalement, croquisSelFeats) -> {}:
        """
        Retourne le (ou les) croquis associé(s) à un signalement.

        :param noSignalement: l'identifiant du signalement
        :type noSignalement: int

        :param croquisSelFeats: dictionnaire contenant le (ou les) croquis
                                 (key: le nom de la table du croquis, value: liste des identifiants de croquis)
        :type croquisSelFeats: dict

        :return: dictionnaire contenant les croquis ou vide si pas de croquis associé(s) au signalement
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

    def getUriDatabaseSqlite(self) -> QgsDataSourceUri:
        """
        Initialise la structure de connexion à la base SQLite.

        :return: la source de connexion
        """
        uri = QgsDataSourceUri(cst.EPSG4326)
        uri.setDatabase(SQLiteManager.getBaseSqlitePath())
        return uri
