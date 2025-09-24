# -*- coding: utf-8 -*-
"""
Created on 29 sept. 2015
Updated on 30 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""

import errno
import os
import shutil
import subprocess
import sys
import ntpath
import xml.etree.ElementTree as ET
from datetime import datetime
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from .core.ClientHelper import ClientHelper
from .core.RipartLoggerCl import RipartLogger
from .core import ConstanteRipart as cst
from .core.SQLiteManager import SQLiteManager
from qgis.utils import spatialite_connect


class RipartHelper:
    """
    Classe contenant des utilitaires pour le plugin
    """
    ripart_files_dir = "files"
    ripart_db = "espaceco.sqlite"
    ripart_help_file = "ENR_Espace_co_plugin_pour_qgis.pdf"

    # fichier de configuration
    nom_Fichier_Parametres_Ripart = "espaceco.xml"

    # dossier des fichiers de style .qml
    qmlStylesDir = "espacecoStyles"

    nom_Calque_Signalement = "Signalement"
    # nom_Calque_Croquis_Fleche = "Croquis_EC_Fleche"
    # nom_Calque_Croquis_Texte = "Croquis_EC_Texte"
    nom_Calque_Croquis_Polygone = "Croquis_EC_Polygone"
    nom_Calque_Croquis_Ligne = "Croquis_EC_Ligne"
    nom_Calque_Croquis_Point = "Croquis_EC_Point"

    croquis_layers = {nom_Calque_Croquis_Polygone: 'POLYGON', nom_Calque_Croquis_Ligne: 'LINESTRING',
                      nom_Calque_Croquis_Point: 'POINT'}

    # liste des noms, car le dictionnaire ne préserve pas l'ordre des éléments
    croquis_layers_name = [nom_Calque_Croquis_Polygone, nom_Calque_Croquis_Ligne,
                           nom_Calque_Croquis_Point, nom_Calque_Signalement]

    calque_Signalement_Lyr = "Signalement.lyr"

    xmlServeur = "Serveur"
    xmlMap = "Map"

    xml_UrlHost = "URLHost"
    xml_Login = "Login"
    xml_DateExtraction = "Date_extraction"
    xml_Pagination = "Pagination"
    xml_Themes = "Themes_preferes"
    xml_Theme = "Theme"
    xml_Zone_extraction = "Zone_extraction"
    xml_AfficherCroquis = "Afficher_Croquis"
    xml_AttributsCroquis = "Attributs_croquis"

    xml_BaliseNomCalque = "Calque_Nom"
    xml_BaliseChampCalque = "Calque_Champ"
    # xml_Group = "./Map/Import_pour_groupe"
    xml_Group = "Import_pour_groupe"
    xml_Map = "./Map"

    xml_proxy = "Proxy"
    xml_GroupeActif = "groupe_actif"
    xml_GroupePrefere = "groupe_prefere"

    defaultDate = "1900-01-01 00:00:00"
    defaultPagination = 100
    longueurMaxChamp = 5000

    logger = RipartLogger("RipartHelper").getRipartLogger()

    @staticmethod
    def getConfigFile():
        fname = ntpath.basename(QgsProject.instance().fileName())
        projectFileName = fname[:fname.find(".")]
        return "{}_espaceco.xml".format(projectFileName)

    @staticmethod
    def getXPath(tagName, parentName):
        """Construction du xpath
        """
        xpath = "./" + parentName + "/" + tagName
        return xpath

    @staticmethod
    def load_urlhost(projectDir):
        """Retourne l'url sauvegardé dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        urlhost = ""
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            urlhost = xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_UrlHost, "Serveur"))
            if urlhost is None:
                urlhost = RipartHelper.addXmlElement(projectDir, "URLHost", "Serveur")

        except Exception as e:
            RipartHelper.logger.error(str(e))

        return urlhost

    @staticmethod
    def load_login(projectDir):
        """Retourne le login sauvegardé dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        login = ""
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            login = xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_Login, "Serveur"))
            if login is None:
                login = RipartHelper.addXmlElement(projectDir, "Login", "Serveur")

        except Exception as e:
            RipartHelper.logger.error(str(e))

        return login

    @staticmethod
    def save_login(projectDir, login):
        """Enregistre le login dans le fichier de configuration
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        
        :param login: le login
        :type login: string
        """
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            xlogin = xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_Login, "Serveur"))
            xlogin.text = login

            tree.write(projectDir + "/" + RipartHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            RipartHelper.logger.error(format(e))

    @staticmethod
    def load_proxy(projectDir):
        """Retourne le proxy sauvegardé dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        proxy = ""
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            proxy = xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_proxy, "Serveur"))
            if proxy is None:
                proxy = RipartHelper.addXmlElement(projectDir, RipartHelper.xml_proxy, "Serveur")

        except Exception as e:
            RipartHelper.logger.error(str(e))

        return proxy

    @staticmethod
    def save_proxy(projectDir, proxy):
        """Enregistre le proxy dans le fichier de configuration
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        
        :param proxy: le proxy
        :type proxy: string
        """
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            xproxy = xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_proxy, "Serveur"))
            xproxy.text = proxy

            tree.write(projectDir + "/" + RipartHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            RipartHelper.logger.error(format(e))

    @staticmethod
    def load_groupeactif(projectDir):
        """Retourne le groupe actif sauvegardé dans le fichier de configuration xml

                :param projectDir: le chemin vers le répertoire du projet
                :type projectDir: string
                """
        groupeactif = ""
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            groupeactif = xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_GroupeActif, "Serveur"))
            if groupeactif is None:
                groupeactif = RipartHelper.addXmlElement(projectDir, RipartHelper.xml_GroupeActif, "Serveur")

        except Exception as e:
            RipartHelper.logger.error(str(e))

        return groupeactif

    @staticmethod
    def save_groupeactif(projectDir, groupeactif):
        """Enregistre le groupe actif dans le fichier de configuration

                :param projectDir: le chemin vers le répertoire du projet
                :type projectDir: string

                :param groupeactif: le groupe actif de l'utilisateur
                :type groupeactif: string
                """
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            xgroupeactif = xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_GroupeActif, "Serveur"))
            xgroupeactif.text = groupeactif

            tree.write(projectDir + "/" + RipartHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            RipartHelper.logger.error(format(e))

    @staticmethod
    def load_preferredGroup(projectDir):
        """Retourne le groupe actif sauvegardé dans le fichier de configuration xml

                :param projectDir: le chemin vers le répertoire du projet
                :type projectDir: string
                """
        groupePrefere = ""
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            groupePrefere = xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_GroupePrefere, "Serveur"))
            if groupePrefere is None:
                groupePrefere = RipartHelper.addXmlElement(projectDir, RipartHelper.xml_GroupePrefere, "Serveur")

        except Exception as e:
            RipartHelper.logger.error(str(e))

        return ClientHelper.notNoneValue(groupePrefere.text)

    @staticmethod
    def save_preferredGroup(projectDir, preferredGroup):
        """Enregistre le groupe préféré pour la création de signalement dans le fichier de configuration

                :param projectDir: le chemin vers le répertoire du projet
                :type projectDir: string

                :param preferredGroup: le groupe préféré de l'utilisateur
                :type preferredGroup: string
                """
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            xgroupePrefere = xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_GroupePrefere, "Serveur"))
            xgroupePrefere.text = preferredGroup

            tree.write(projectDir + "/" + RipartHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            RipartHelper.logger.error(format(e))

    @staticmethod
    def load_CalqueFiltrage(projectDir):
        """Retourne le nom du calque de filtrage sauvegardé dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        calque = ""
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            calque = xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_Zone_extraction, "Map"))

        except Exception as e:
            RipartHelper.logger.error(str(e))

        return calque

    @staticmethod
    def load_ripartXmlTag(projectDir, tag, parent=None):
        """Recherche un élément (tag) dans le fichier xml.
        Si l'élément n'existe pas ,il est créé
        
        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: string
        
        :param tag: xpath de l'élément cherché
        :type tag: string
        
        :param parent: xpath de l'élément parent
        :type parent: string
        
        :return l'élément xml recherché
        :rtype Element
        """
        node = None
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            node = xmlroot.find(RipartHelper.getXPath(tag, parent))

            if node is None:
                node = RipartHelper.addXmlElement(projectDir, tag, parent)

        except Exception as e:
            RipartHelper.logger.error(str(e))

        return node

    @staticmethod
    def addXmlElement(projectDir, elem, parentElem, value=None):
        tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
        xmlroot = tree.getroot()
        if parentElem != "root":
            parentNode = xmlroot.find(parentElem)
        else:
            parentNode = xmlroot
        if parentNode is None:
            parentNode = RipartHelper.addXmlElement(projectDir, parentElem, "root")

        elementNode = ET.SubElement(parentNode, elem)

        if value is not None:
            elementNode.text = value

        tree.write(projectDir + "/" + RipartHelper.getConfigFile(), encoding="utf-8")

        return elementNode

    @staticmethod
    def load_attCroquis(projectDir):
        """Retourne les attributs de croquis sauvegardés dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        attCroquis = {}
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            nodes = xmlroot.findall(RipartHelper.getXPath(RipartHelper.xml_AttributsCroquis, "Map"))

            for cr in nodes:
                nomCalque = cr.find(RipartHelper.xml_BaliseNomCalque).text
                attCroquis[nomCalque] = []
                fields = cr.iter(RipartHelper.xml_BaliseChampCalque)
                for f in fields:
                    attCroquis[nomCalque].append(f.text)

        except Exception as e:
            RipartHelper.logger.error(str(e))

        return attCroquis

    @staticmethod
    def load_preferredThemes(projectDir):
        """Retourne les thèmes sauvegardés dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        prefThemes = []
        try:
            print(RipartHelper.getConfigFile())
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()

            prefThs = xmlroot.findall(
                RipartHelper.getXPath(RipartHelper.xml_Themes + "/" + RipartHelper.xml_Theme, "Map"))

            for n in prefThs:
                prefThemes.append(ClientHelper.notNoneValue(n.text))

        except Exception as e:
            RipartHelper.logger.error(str(e))

        return prefThemes

    @staticmethod
    def save_preferredThemes(projectDir, prefThemes):
        """Enregistre les thèmes dans le fichier de config
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        
        :param prefThemes: la liste de  thèmes
        :type prefThemes: list de Theme
        """
        # first load Themes_prefs tag (create the tag if the tag doesn't exist yet)
        themesNode = RipartHelper.load_ripartXmlTag(projectDir, RipartHelper.xml_Themes, "Map")
        RipartHelper.removeNode(projectDir, RipartHelper.xml_Theme, "Map/" + RipartHelper.xml_Themes)

        for th in prefThemes:
            RipartHelper.addXmlElement(projectDir, RipartHelper.xml_Theme, "Map/" + RipartHelper.xml_Themes,
                                       th.group.name)

    @staticmethod
    def addNode(projectDir, tag, value, parentTag=None):
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            if parentTag is None:
                parentNode = xmlroot
            else:
                parentNode = xmlroot.find(parentTag)

            newTag = ET.SubElement(parentNode, tag)
            newTag.text = value

            tree.write(projectDir + "/" + RipartHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            RipartHelper.logger.error(format(e))

    @staticmethod
    def removeNode(projectDir, tag, parentTag=None):
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            if parentTag is None:
                parentNode = xmlroot
            else:
                parentNode = xmlroot.find(parentTag)

            for c in parentNode.findall(tag):
                parentNode.remove(c)

            tree.write(projectDir + "/" + RipartHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            RipartHelper.logger.error(format(e))

    @staticmethod
    def setXmlTagValue(projectDir, tag, value, parent=None):
        """Donne une valeur à un tag du fichier de config
        """
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            node = xmlroot.find(RipartHelper.getXPath(tag, parent))
            node.text = value

            tree.write(projectDir + "/" + RipartHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            RipartHelper.logger.error(format(e))

    @staticmethod
    def setAttributsCroquis(projectDir, calqueName, values):
        try:
            tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
            xmlroot = tree.getroot()
            mapNode = xmlroot.find(RipartHelper.xml_Map)

            nodeAtributsCroquis = ET.SubElement(mapNode, 'Attributs_croquis')
            nodeNom = ET.SubElement(nodeAtributsCroquis, 'Calque_Nom')
            nodeNom.text = calqueName
            for val in values:
                field = ET.SubElement(nodeAtributsCroquis, 'Calque_Champ')
                field.text = val

            tree.write(projectDir + "/" + RipartHelper.getConfigFile(), encoding="utf-8")
        except Exception as e:
            # fix_print_with_import
            print(format(e))

    @staticmethod
    def removeAttCroquis(projectDir):
        tree = ET.parse(projectDir + "/" + RipartHelper.getConfigFile())
        xmlroot = tree.getroot()
        maptag = xmlroot.find('Map')
        for c in maptag.findall('Attributs_croquis'):
            maptag.remove(c)
        tree.write(projectDir + "/" + RipartHelper.getConfigFile(), encoding="utf-8")

    @staticmethod
    def createRemarqueTable(conn):
        """
        Création de la table Signalement
        """
        cur = conn.cursor()
        sql = u"CREATE TABLE Signalement (" + \
              u"id INTEGER NOT NULL PRIMARY KEY, " + \
              u"NoSignalement INTEGER, " + \
              u"Auteur TEXT, " + \
              u"Commune TEXT, " + \
              u"Département TEXT, " + \
              u"Département_id  TEXT, " + \
              u"Date_création TEXT, " + \
              u"Date_MAJ TEXT, " + \
              u"Date_validation TEXT, " + \
              u"Thèmes TEXT, " + \
              u"Statut TEXT, " + \
              u"Message TEXT, " + \
              u"Réponses TEXT, " + \
              u"URL TEXT, " + \
              u"URL_privé TEXT, " + \
              u"Document TEXT, " + \
              u"Autorisation TEXT)"
        print(sql)
        res = cur.execute(sql)
        print(res)
        conn.commit()
        # creating a POINT Geometry column
        sql = "SELECT AddGeometryColumn('Signalement', 'geom', " + str(cst.EPSGCRS) + ", 'POINT', 'XY')"
        print(sql)
        res = cur.execute(sql)
        print(res)
        cur.close()
        conn.commit()

    @staticmethod
    def createCroquisTable(conn, table, geomType):
        """Création d'une table de croquis
        
        :param conn: la connexion à la base de données
        :type conn: 
        
        :param table: le nom de la table à créer
        :type table: string
        
        :param geomType: le type de la géométrie 
        :type: string
        """
        cur = conn.cursor()
        sql = u"CREATE TABLE " + table + " (" + \
              u"id INTEGER NOT NULL PRIMARY KEY, " + \
              u"NoSignalement INTEGER, " + \
              u"Nom TEXT, " + \
              u"Attributs_croquis, " + \
              u"Lien_objet_BDUNI TEXT) "
        print(sql)
        res = cur.execute(sql)
        print(res)
        conn.commit()
        # creating a POINT Geometry column
        sql = "SELECT AddGeometryColumn('" + table + "', "
        sql += "'geom', " + str(cst.EPSGCRS) + ", '" + geomType + "', 'XY')"
        print(sql)
        res = cur.execute(sql)
        print(res)
        cur.close()
        conn.commit()

    @staticmethod
    def emptyTable(conn, table):
        """Vide le contenu de la table donnée en paramètre
        
        :param conn: la connexion à la base de données
        :type conn: 
        
        :param table: la table à vider
        :type: string
        """
        cur = conn.cursor()
        try:
            sql = u"DELETE FROM " + table
            cur.execute(sql)
        finally:
            cur.close()

    @staticmethod
    def insertRemarques(conn, rem, bCommit):
        """Insertion d'une nouvelle remarque dans la table Signalement
        
        @param conn: la connexion à la base de données
        @type conn: 
        
        @param rem: la remarque à ajouter
        @type rem: Remarque

        @param bCommit: fait une transaction tous les 200 objets
        @type bCommit: bool
        """
        RipartHelper.logger.debug("insertRemarques")
        cur = conn.cursor()
        try:
            RipartHelper.logger.debug("INSERT rem id:" + str(rem.id))

            ptx = rem.position.longitude
            pty = rem.position.latitude

            if type(rem.dateCreation) == datetime:
                rem.dateCreation = RipartHelper.formatDatetime(rem.dateCreation)
            if type(rem.dateMiseAJour) == datetime:
                rem.dateMiseAJour = RipartHelper.formatDatetime(rem.dateMiseAJour)
            if type(rem.dateValidation) == datetime:
                rem.dateValidation = RipartHelper.formatDatetime(rem.dateValidation)

            if rem.dateValidation is None:
                rem.dateValidation = ""

            geom = " GeomFromText('POINT(" + str(ptx) + " " + str(pty) + ")', {})".format(cst.EPSGCRS)

            sql = u"INSERT INTO " + RipartHelper.nom_Calque_Signalement
            sql += u" (NoSignalement, Auteur, Commune, Département, Département_id, Date_création, Date_MAJ, "
            sql += u"Date_validation, Thèmes, Statut, Message, Réponses, URL, URL_privé, Document, Autorisation, geom) "
            sql += u"VALUES ("
            sql += str(rem.id) + ", '"
            sql += ClientHelper.getValForDB(rem.author.name) + "', '"
            sql += rem.getAttribut("commune") + "', '"
            #sql += rem.getAttribut("insee") + "', '" - ajouté en v4.2.0 puis supprimé en v4.2.1 car crée des problèmes dans les projets existants
            sql += rem.getAttribut("departement", "name") + "', '"
            sql += rem.getAttribut("departement", "id") + "', '"
            sql += rem.dateCreation + "', '"
            sql += rem.dateMiseAJour + "', '"
            sql += rem.dateValidation + "', '"
            # TODO voir avec Noémie si on garde le code JSON
            sql += rem.concatenateThemes() + "', '"
            #sql += rem.themesToJson() + "', '"
            sql += rem.statut.__str__() + "', '"
            sql += rem.getAttribut("commentaire") + "', '"
            sql += ClientHelper.getValForDB(rem.concatenateResponse()) + "', '"
            sql += rem.getAttribut("lien") + "', '"
            sql += rem.getAttribut("lienPrive") + "', '"
            sql += ClientHelper.getValForDB(rem.getAllDocuments()) + "', '"
            sql += rem.getAttribut("autorisation") + "', "
            sql += geom + ")"
            result = SQLiteManager.isColumnExist(RipartHelper.nom_Calque_Signalement, 'Auteur')
            if result[0] != 1:
                SQLiteManager.deleteTable(RipartHelper.nom_Calque_Signalement)
                dbName = RipartHelper.getConfigFile().replace("xml", "sqlite")
                dbPath = QgsProject.instance().homePath() + "/" + dbName
                connexion = spatialite_connect(dbPath)
                RipartHelper.createRemarqueTable(connexion)
                SQLiteManager.vacuumDatabase()
            cur.execute(sql)
            rowcount = cur.rowcount
            if rowcount != 1:
                RipartHelper.logger.error("No row inserted:" + sql)
            ###################
            if bCommit:
                conn.commit()
            ###################
            if len(rem.croquis) > 0:
                croquis = rem.croquis
                for cr in croquis:
                    sql = "INSERT INTO %s (NoSignalement, Nom, Attributs_croquis, geom) VALUES "
                    if len(cr.points) == 0:
                        return

                    values = "(" + str(rem.id) + ",'" + \
                             ClientHelper.getValForDB(cr.name) + "', '" + \
                             ClientHelper.getValForDB(cr.getAttributsInStringFormat()) + "', %s)"
                    sql += values

                    sgeom = " GeomFromText('%s(%s)', {})".format(cst.EPSGCRS)
                    coord = cr.getCoordinatesFromPoints()

                    if str(cr.type) == "Point" or str(cr.type) == "Texte":
                        geom = sgeom % ('POINT', coord)
                        sql = sql % (RipartHelper.nom_Calque_Croquis_Point, geom)
                    elif str(cr.type) == "Ligne" or str(cr.type) == "Fleche":
                        geom = sgeom % ('LINESTRING', coord)
                        sql = sql % (RipartHelper.nom_Calque_Croquis_Ligne, geom)
                    elif str(cr.type) == 'Polygone':
                        geom = sgeom % ('POLYGON(', coord + ")")
                        sql = sql % (RipartHelper.nom_Calque_Croquis_Polygone, geom)
                    cur.execute(sql)
                ###################
                if bCommit:
                    conn.commit()
                ###################

        except Exception as e:
            raise e
        finally:
            cur.close()

    @staticmethod
    def isInGeometry(pt, geomLayer):
        """Si le point est dans la géométrie (définie par les objets d'une couche donnée)
        
        :param pt le point
        :type pt : geometry
        
        :param geomLayer: le calque
        :param geomLayer: QgsVectorlayer
        """
        layerCrs = geomLayer.crs()
        destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
        xform = QgsCoordinateTransform(layerCrs, destCrs, QgsProject.instance())
        featsPoly = geomLayer.getFeatures()
        isWithin = False

        for featPoly in featsPoly:
            geomPoly = featPoly.geometry()
            geomPoly.transform(xform)
            if pt.within(geomPoly):
                isWithin = True

        return isWithin

    @staticmethod
    def formatDate(sdate):
        """
        Transforme une date donnée au format dd/MM/yyyy %H:%M:%S en yyyy-MM-dd %H:%M:%S
        
        :param sdate la date à tranformer
        :type sdate: string
        
        :return date au format yyyy-MM-dd %H:%M:%S
        :rtype: string
        """
        rdate = ''
        try:
            if len(sdate.split("/")) > 0:
                dt = datetime.strptime(sdate, '%d/%m/%Y %H:%M:%S')
                rdate = dt.strftime('%Y-%m-%d %H:%M:%S')
            elif len(sdate.split("-")) > 0:
                rdate = sdate
        except Exception as e:
            rdate = RipartHelper.defaultDate
        return rdate

    @staticmethod
    def formatDatetime(dt):
        """Retourne la date au format '%Y-%m-%d %H:%M:%S'
        
        :param dt : la date
        :type dt: datetime
        """
        rdate = dt.strftime('%Y-%m-%d %H:%M:%S')
        return rdate

    @staticmethod
    def showMessageBox(message):
        """Affiche une fen^tre avec le message donné
        
        :param message
        :type message: string
        """
        msgBox = QMessageBox()
        msgBox.setWindowTitle("IGN Espace Collaboratif")
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(message)
        msgBox.exec_()

    @staticmethod
    def copy(src, dest):
        """Copie un fichier ou un répertoire 
        
        :param src: le fichier ou répertoire source
        :type src: string
        
        :param dest : le fichier ou répertoire de destionation
        :type dest: string
        """
        try:
            if not os.path.exists(dest):
                shutil.copytree(src, dest)

        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                if not os.path.exists(dest):
                    shutil.copy(src, dest)
            else:
                print('Directory not copied. Error: %s' % e)

    @staticmethod
    def open_file(filename):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    @staticmethod
    def getGeometryWorkZone(projectDir):
        geometryWorkZone = None
        nameWorkZone = RipartHelper.load_CalqueFiltrage(projectDir).text
        layerWorkZone = QgsProject.instance().mapLayersByName(nameWorkZone)
        if len(layerWorkZone) > 1:
            return geometryWorkZone
        layerWorkZone[0].startEditing()
        layerWorkZone[0].selectAll()
        feats = layerWorkZone[0].selectedFeatures()
        nb = len(list(feats))
        if nb > 1:
            message = "Le filtrage des objets sera impossible car la couche {0} contient plusieurs objets." \
                      "Il faut une seule zone de travail pour filtrer les objets après extraction des données.".format(nameWorkZone)
            QgsProject.instance().iface.messageBar().pushMessage("", message, level=2, duration=5)
            return geometryWorkZone
        for feat in feats:
            geometryWorkZone = feat.geometry()
        if len(list(geometryWorkZone.parts())) > 1:
             message = "Le filtrage des objets sera impossible car la zone de travail est une surface multiple." \
                      "Il faut une surface simple pour filtrer les objets après extraction des données.".format(nameWorkZone)
             QgsProject.instance().iface.messageBar().pushMessage("", message, level=2, duration=5)
             return geometryWorkZone
        layerWorkZone[0].rollBack()
        layerWorkZone[0].removeSelection()
        return geometryWorkZone
