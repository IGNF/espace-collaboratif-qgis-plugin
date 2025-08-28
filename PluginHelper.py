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
from typing import Optional

from Lib.xml.etree.ElementTree import Element
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsGeometry
from .core.PluginLogger import PluginLogger
from .core import Constantes as cst


class PluginHelper:
    """
    Classe contenant des utilitaires pour le plugin espace collaboratif.
    """
    ripart_files_dir = "files"
    ripart_db = "espaceco.sqlite"
    ripart_help_file = "ENR_Espace_co_Add-in_ArcGIS_Pro_2_0_0.pdf"

    # fichier de configuration
    nom_Fichier_Parametres_Ripart = "espaceco.xml"

    # dossier des fichiers de style .qml
    qmlStylesDir = "espacecoStyles"

    sketchLayers = {cst.nom_Calque_Croquis_Polygone: 'POLYGON', cst.nom_Calque_Croquis_Ligne: 'LINESTRING',
                    cst.nom_Calque_Croquis_Point: 'POINT'}

    # liste des noms, car le dictionnaire ne préserve pas l'ordre des éléments
    reportSketchLayersName = [cst.nom_Calque_Croquis_Polygone, cst.nom_Calque_Croquis_Ligne,
                              cst.nom_Calque_Croquis_Point, cst.nom_Calque_Signalement]

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

    logger = PluginLogger("PluginHelper").getPluginLogger()

    @staticmethod
    def getConfigFile() -> str:
        """
        Le fichier xml de configuration est lié au projet QGIS de l'utilisateur.
        Il se trouve à l'emplacement du projet.
        Il doit être de la forme "nomProjet_espaceco.xml"

        NB : une exception est envoyée :
        - si le fichier n'existe pas (projet nouveau ou non enregistré)
        - si le nom du projet contient un point

        :return: le nom du fichier xml de configuration.
        """
        fname = ntpath.basename(QgsProject.instance().fileName())
        if fname == '':
            message = "Veuillez ouvrir (ou enregistrer) le projet avant d'utiliser cette fonctionnalité."
            PluginHelper.showMessageBox(message)
            raise Exception(message)
        nbPoints = fname.count(".")
        if nbPoints != 1:
            message = "Le nom de votre projet QGIS ne doit pas contenir de point en dehors de son extension (.qgz). " \
                      "Merci de le renommer."
            PluginHelper.showMessageBox(message)
            raise Exception(message)
        projectFileName = fname[:fname.find(".")]
        return "{}_espaceco.xml".format(projectFileName)

    @staticmethod
    def getXPath(tagName, parentTag) -> str:
        """
        La balise principale 'Serveur' contient les sous balises suivantes :
         - URLHost
         - groupe_actif
         - groupe_prefere
         - Login
         - Proxy
        La balise principale 'Map' contient les sous balises suivantes :
         - Date_extraction
         - Pagination
         - Zone_extraction
         - Themes_preferes
         - Afficher_Croquis
         - Import_pour_groupe

        :param tagName: le nom de la sous balise
        :type tagName: str

        :param parentTag: le nom de la balise principale ('Map' ou 'Serveur')
        :type parentTag: str

        :return: le nœud xml en fonction de la "Balise principale/Sous balise" ('Map'/'Date_extraction' par exemple)
        """
        xpath = "./" + parentTag + "/" + tagName
        return xpath

    @staticmethod
    def load_urlhost(projectDir) -> str:
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: l'url sauvegardée dans le fichier xml, une chaine vide si la balise principale 'Serveur' n'existe pas
        """
        urlhost = ""
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            urlhost = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_UrlHost, "Serveur"))
            if urlhost is None:
                urlhost = PluginHelper.addXmlElement(projectDir, "URLHost", "Serveur")

        except Exception as e:
            PluginHelper.logger.error(str(e))

        return urlhost

    @staticmethod
    def load_login(projectDir) -> str:
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: le login sauvegardé dans le fichier xml, une chaine vide si la balise principale 'Serveur' n'existe pas
        """
        login = ""
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            login = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_Login, "Serveur"))
            if login is None:
                login = PluginHelper.addXmlElement(projectDir, "Login", "Serveur")

        except Exception as e:
            PluginHelper.logger.error(str(e))

        return login

    @staticmethod
    def save_login(projectDir, login) -> None:
        """
        Enregistre le login dans le fichier xml de configuration.

        NB : une exception est envoyée, si l'enregistrement du nœud xml a échoué.
        
        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str
        
        :param login: le nom du login utilisateur
        :type login: str
        """
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            xlogin = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_Login, "Serveur"))
            xlogin.text = login
            tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            PluginHelper.logger.error(format(e))

    @staticmethod
    def load_proxy(projectDir):
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: le proxy sauvegardé dans le fichier xml, une chaine vide si la balise principale 'Serveur' n'existe pas
        """
        proxy = ""
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            proxy = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_proxy, "Serveur"))
            if proxy is None:
                proxy = PluginHelper.addXmlElement(projectDir, PluginHelper.xml_proxy, "Serveur")

        except Exception as e:
            PluginHelper.logger.error(str(e))

        return proxy

    @staticmethod
    def save_proxy(projectDir, proxy):
        """
        Enregistre le proxy dans le fichier xml de configuration.

        NB : une exception est envoyée, si l'enregistrement du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :param proxy: le nom du proxy
        :type proxy: str
        """
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            xproxy = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_proxy, "Serveur"))
            xproxy.text = proxy

            tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            PluginHelper.logger.error(format(e))

    @staticmethod
    def loadActiveCommunityName(projectDir):
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: le nom de la communauté active sauvegardée dans le fichier xml, (groupe utilisé par l'utilisateur
                 pour travailler) une chaine vide si la balise principale 'Serveur' n'existe pas
        """
        activeCommunity = ""
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            activeCommunity = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_GroupeActif, "Serveur"))
            if activeCommunity is None:
                activeCommunity = PluginHelper.addXmlElement(projectDir, PluginHelper.xml_GroupeActif, "Serveur")

        except Exception as e:
            PluginHelper.logger.error(str(e))

        return activeCommunity

    @staticmethod
    def saveActiveCommunityName(projectDir, activeCommunity):
        """
        Enregistre le groupe actif dans le fichier xml de configuration.

        NB : une exception est envoyée, si l'enregistrement du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :param activeCommunity: le nom du groupe actif
        :type activeCommunity: str
        """
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            xActiveCommunity = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_GroupeActif, "Serveur"))
            xActiveCommunity.text = activeCommunity
            tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            PluginHelper.logger.error(format(e))

    @staticmethod
    def load_preferredGroup(projectDir):
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: le nom du groupe préféré sauvegardé dans le fichier xml, (groupe utilisé le plus souvent
                 par l'utilisateur pour travailler) une chaine vide si la balise principale 'Serveur' n'existe pas
        """
        groupePrefere = ""
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            groupePrefere = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_GroupePrefere, "Serveur"))
            if groupePrefere is None:
                groupePrefere = PluginHelper.addXmlElement(projectDir, PluginHelper.xml_GroupePrefere, "Serveur")

        except Exception as e:
            PluginHelper.logger.error(str(e))

        return groupePrefere

    @staticmethod
    def save_preferredGroup(projectDir, preferredGroup):
        """
        Enregistre le groupe préféré de l'utilisateur dans le fichier xml de configuration.

        NB : une exception est envoyée, si l'enregistrement du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :param preferredGroup: le nom du groupe préféré
        :type preferredGroup: str
        """
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            xgroupePrefere = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_GroupePrefere, "Serveur"))
            xgroupePrefere.text = preferredGroup

            tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            PluginHelper.logger.error(format(e))

    @staticmethod
    def load_CalqueFiltrage(projectDir):
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: le nom du calque de filtrage sauvegardé dans le fichier xml, une chaine vide si la balise principale
                 'Serveur' n'existe pas
        """
        calque = ""
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            calque = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_Zone_extraction, "Map"))

        except Exception as e:
            PluginHelper.logger.error(str(e))

        return calque

    @staticmethod
    def load_XmlTag(projectDir, tag, parent=None) -> Optional[Element]:
        """
        Recherche un élément (tag) dans le fichier xml.
        Si l'élément n'existe pas, il est créé.
        
        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: string
        
        :param tag: xpath de l'élément cherché
        :type tag: str
        
        :param parent: xpath de l'élément parent
        :type parent: str
        
        :return: l'élément xml recherché
        """
        node = None
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            node = xmlroot.find(PluginHelper.getXPath(tag, parent))
            if node is None:
                node = PluginHelper.addXmlElement(projectDir, tag, parent)

        except Exception as e:
            PluginHelper.logger.error(str(e))

        return node

    @staticmethod
    def addXmlElement(projectDir, elem, parentElem, value=None) -> Element:
        """
        Ajoute un élément (tag) dans le fichier xml.
        Si l'élément n'existe pas, il est créé.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: string

        :param elem: le nom de la sous balise ('Login' par exemple)
        :type elem: str

        :param parentElem: le nom de la balise principale ('Serveur' ou 'Map')
        :type parentElem: str

        :param value: la valeur (éventuelle) de la sous balise
        :type value: str

        :return: le xNode de l'élément ajouté
        """
        tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
        xmlroot = tree.getroot()
        if parentElem != "root":
            parentNode = xmlroot.find(parentElem)
        else:
            parentNode = xmlroot
        if parentNode is None:
            parentNode = PluginHelper.addXmlElement(projectDir, parentElem, "root")

        elementNode = ET.SubElement(parentNode, elem)

        if value is not None:
            elementNode.text = value

        tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

        return elementNode

    @staticmethod
    def load_attCroquis(projectDir) -> {}:
        """
        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: les attributs de croquis sauvegardés dans le fichier xml de configuration
        """
        attCroquis = {}
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            nodes = xmlroot.findall(PluginHelper.getXPath(PluginHelper.xml_AttributsCroquis, "Map"))

            for cr in nodes:
                nomCalque = cr.find(PluginHelper.xml_BaliseNomCalque).text
                attCroquis[nomCalque] = []
                fields = cr.iter(PluginHelper.xml_BaliseChampCalque)
                for f in fields:
                    attCroquis[nomCalque].append(f.text)

        except Exception as e:
            PluginHelper.logger.error(str(e))

        return attCroquis

    @staticmethod
    def load_preferredThemes(projectDir) -> []:
        """
        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: les thèmes sauvegardés dans le fichier de configuration xml
        """
        prefThemes = []
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()

            prefThs = xmlroot.findall(
                PluginHelper.getXPath(PluginHelper.xml_Themes + "/" + PluginHelper.xml_Theme, "Map"))

            for n in prefThs:
                prefThemes.append(PluginHelper.notNoneValue(n.text))

        except Exception as e:
            PluginHelper.logger.error(str(e))

        return prefThemes

    @staticmethod
    def save_preferredThemes(projectDir, prefThemes) -> None:
        """
        Enregistre les thèmes préférés de l'utilisateur dans le fichier xml de configuration.
        
        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str
        
        :param prefThemes: la liste des thèmes
        :type prefThemes: list
        """
        PluginHelper.load_XmlTag(projectDir, PluginHelper.xml_Themes, "Map")
        PluginHelper.removeNode(projectDir, PluginHelper.xml_Theme, "Map/" + PluginHelper.xml_Themes)
        for th in prefThemes:
            PluginHelper.addXmlElement(projectDir, PluginHelper.xml_Theme, "Map/" + PluginHelper.xml_Themes,
                                       th.getName())

    @staticmethod
    def addNode(projectDir, tag, value, parentTag=None):
        """
        Ajoute un nœud dans le fichier xml de configuration.
        NB: une exception est envoyée si l'ajout dans le fichier xml est impossible.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :param tag: nom de la sous balise
        :type tag: str

        :param value: valeur prise par la sous balise
        :param value: str

        :param parentTag: balise principale
        :type parentTag: str
        """
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            if parentTag is None:
                parentNode = xmlroot
            else:
                parentNode = xmlroot.find(parentTag)

            newTag = ET.SubElement(parentNode, tag)
            newTag.text = value

            tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            PluginHelper.logger.error(format(e))

    @staticmethod
    def removeNode(projectDir, tag, parentTag=None) -> None:
        """
        Supprime un nœud dans le fichier xml de configuration.
        NB: une exception est envoyée si la suppression dans le fichier xml est impossible.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :param tag: nom de la sous balise
        :type tag: str

        :param parentTag: nom de la balise principale
        :type parentTag: str
        """
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            if parentTag is None:
                parentNode = xmlroot
            else:
                parentNode = xmlroot.find(parentTag)

            for c in parentNode.findall(tag):
                parentNode.remove(c)

            tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            PluginHelper.logger.error(format(e))

    @staticmethod
    def setXmlTagValue(projectDir, tag, value, parentTag=None) -> None:
        """
        Enregistre une valeur à un tag dans le fichier xml de configuration en fonction d'une balise principale.
        NB : une exception est envoyée si l'écriture dans le fichier xml est impossible.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :param tag: nom de la sous balise
        :type tag: str

        :param value: valeur prise par la sous balise
        :param value: str

        :param parentTag: balise principale
        :type parentTag: str
        """
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            node = xmlroot.find(PluginHelper.getXPath(tag, parentTag))
            node.text = value

            tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            PluginHelper.logger.error(format(e))

    @staticmethod
    def setAttributsCroquis(projectDir, calqueName, values):
        """
        Copie les attributs du croquis choisis par l'utilisateur dans la boite de configuration
        qui seront liés au croquis.

        NB : une exception est envoyée si l'écriture dans le fichier xml est impossible.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :param calqueName: le nom de la zone de travail du projet de l'utilisateur
        :type calqueName: str

        :param values: les attributs du croquis choisis par l'utilisateur
        :type values: list
        """
        try:
            tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
            xmlroot = tree.getroot()
            mapNode = xmlroot.find(PluginHelper.xml_Map)

            nodeAtributsCroquis = ET.SubElement(mapNode, 'Attributs_croquis')
            nodeNom = ET.SubElement(nodeAtributsCroquis, 'Calque_Nom')
            nodeNom.text = calqueName
            for val in values:
                field = ET.SubElement(nodeAtributsCroquis, 'Calque_Champ')
                field.text = val

            tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")
        except Exception as e:
            # fix_print_with_import
            print(format(e))

    @staticmethod
    def removeAttCroquis(projectDir) -> None:
        """
        Suppression de balises dans le fichier xml de configuration du projet.

        :param projectDir: le chemin complet du fichier de configuration
        :type projectDir: str
        """
        tree = ET.parse(projectDir + "/" + PluginHelper.getConfigFile())
        xmlroot = tree.getroot()
        maptag = xmlroot.find('Map')
        for c in maptag.findall('Attributs_croquis'):
            maptag.remove(c)
        tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

    @staticmethod
    def formatDate(sdate) -> str:
        """
        Transforme une date donnée au format dd/MM/yyyy %H:%M:%S en yyyy-MM-dd %H:%M:%S.
        
        :param sdate: la date à transformer
        :type sdate: str
        
        :return: la date au format yyyy-MM-dd %H:%M:%S
        """
        # Vérifie si la chaîne est vide ou None
        if not sdate:
            return PluginHelper.defaultDate

        try:
            # Si le format semble être avec des "/", on tente le parsing
            if "/" in sdate:
                dt = datetime.strptime(sdate, '%d/%m/%Y %H:%M:%S')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            # Si le format semble déjà être au bon format ISO, on le retourne tel quel
            elif "-" in sdate:
                return sdate
            else:
                # Format inconnu
                return PluginHelper.defaultDate
        except ValueError:
            # Erreur de parsing
            return PluginHelper.defaultDate

    @staticmethod
    def showMessageBox(message) -> None:
        """
        Affiche une fenêtre QMessageBox de type avertissement avec le message donné en entrée.
        
        :param message: le message à afficher à l'utilisateur
        :type message: string
        """
        msgBox = QMessageBox()
        msgBox.setWindowTitle("IGN Espace Collaboratif")
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(message)
        msgBox.exec_()

    @staticmethod
    def copy(src, dest) -> None:
        """
        Copie un fichier ou un répertoire. Une OSError est envoyée si la copie n'est pas possible.
        
        :param src: le fichier ou répertoire source
        :type src: str
        
        :param dest : le fichier ou répertoire de destination
        :type dest: str
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
    def open_file(filename) -> None:
        """
        Ouverture automatique d'un fichier, par exemple le fichier de log, si l'utilisateur en fait la demande.

        :param filename: le chemin complet vers le fichier à ouvrir
        :type filename: str
        """
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    @staticmethod
    # TODO Mélanie : cette fonction n'est pas mis en service ? Dois-je l'intégrer au code ?
    def getGeometryWorkZone(projectDir) -> Optional[QgsGeometry]:
        """
        Vérifie si la zone de travail est conforme aux exigences de filtrage des objets après extraction
        de signalements ou de données provenant de l'espace collaboratif.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: la géométrie de la zone de travail ou None
        """
        geometryWorkZone = None
        nameWorkZone = PluginHelper.load_CalqueFiltrage(projectDir).text
        layerWorkZone = QgsProject.instance().mapLayersByName(nameWorkZone)
        if len(layerWorkZone) > 1:
            message = "Le filtrage des objets sera impossible car plusieurs couches portent le même nom " \
                      "dans le projet. Il faut une seule couche représentant la zone de travail pour filtrer" \
                      " les objets après extraction des données.".format(nameWorkZone)
            QgsProject.instance().iface.messageBar().pushMessage("", message, level=2, duration=3)
            return geometryWorkZone
        layerWorkZone[0].startEditing()
        layerWorkZone[0].selectAll()
        feats = layerWorkZone[0].selectedFeatures()
        nb = len(list(feats))
        if nb > 1:
            message = "Le filtrage des objets sera impossible car la couche {0} contient plusieurs objets." \
                      "Il faut une seule zone de travail pour filtrer les objets après extraction des données.".format(
                        nameWorkZone)
            QgsProject.instance().iface.messageBar().pushMessage("", message, level=2, duration=3)
            return geometryWorkZone
        for feat in feats:
            geometryWorkZone = feat.geometry()
        if len(list(geometryWorkZone.parts())) > 1:
            message = "Le filtrage des objets sera impossible car la zone de travail est une surface multiple." \
                      "Il faut une surface simple pour filtrer les objets après extraction des données.".format(
                        nameWorkZone)
            QgsProject.instance().iface.messageBar().pushMessage("", message, level=2, duration=3)
            return geometryWorkZone
        layerWorkZone[0].rollBack()
        layerWorkZone[0].removeSelection()
        return geometryWorkZone

    @staticmethod
    def notNoneValue(val):
        """
        Transforme une chaine de caractères None en chaine de caractères vide.

        :param val: la valeur à transformer si nécessaire
        :type val: str

        :return: une chaine vide si val = None, val sinon
        """
        if val is None:
            return ""
        else:
            return val

    @staticmethod
    def keyExist(key, data) -> bool:
        """
        Vérifie si une clé existe dans le dictionnaire passé en entrée.

        :param key: la valeur de la clé à chercher
        :type key: str

        :param data: les données sous forme de dictionnaire
        :type data: dict

        :return: vrai si la clé est trouvée, false sinon
        """
        if key in data:
            return True
        return False

    @staticmethod
    def keysExists(keyA, keyB, data) -> bool:
        """
        :param keyA: la valeur de la 1ère clé à chercher
        :type keyA: str

        :param keyB: la valeur de la 2ème clé à chercher dans le dictionnaire retourné par la recherche de la 1ère clé
        :type keyB: str

        :param data: les données sous forme de dictionnaire
        :type data: dict

        :return: vrai si la 1ère et la 2ème clé sont trouvées, false sinon
        """
        if data[keyA] is None:
            return False
        if PluginHelper.keyExist(keyA, data):
            datum = data[keyA]
            if datum[keyB] is None:
                return False
            if PluginHelper.keyExist(keyB, datum):
                return True
        return False
