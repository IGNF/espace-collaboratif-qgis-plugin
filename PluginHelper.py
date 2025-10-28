# -*- coding: utf-8 -*-
"""
Created on 29 sept. 2015
Updated on 30 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""
import os
import subprocess
import sys
import ntpath
import Lib.xml.etree.ElementTree as ET
from Lib.xml.etree.ElementTree import Element
from datetime import datetime
from typing import Optional
from PyQt5.QtWidgets import QMessageBox, QApplication
from qgis.core import QgsProject
from .core.PluginLogger import PluginLogger
from .core import Constantes as cst


class PluginHelper:
    """
    Classe contenant des utilitaires pour le plugin espace collaboratif.
    """
    ripart_files_dir = "files"
    ripart_db = "espaceco.sqlite"
    ripart_help_file = "ENR_Espace_co_plugin_pour_qgis.pdf"

    # fichier de configuration
    nom_Fichier_Parametres_EspaceCo = "espaceco.xml"

    # dossier des fichiers de style .qml
    qmlStylesDirectory = "espacecoStyles"

    sketchLayers = {cst.nom_Calque_Croquis_Polygone: 'POLYGON', cst.nom_Calque_Croquis_Ligne: 'LINESTRING',
                    cst.nom_Calque_Croquis_Point: 'POINT'}

    # liste des noms, car le dictionnaire ne préserve pas l'ordre des éléments
    reportSketchLayersName = [cst.nom_Calque_Croquis_Polygone, cst.nom_Calque_Croquis_Ligne,
                              cst.nom_Calque_Croquis_Point, cst.nom_Calque_Signalement]

    calque_Signalement_Lyr = "Signalement.lyr"
    xml_Serveur = "Serveur"
    xml_Map = "Map"
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
    xml_proxy = "Proxy"
    xml_GroupeActif = "groupe_actif"
    xml_GroupePrefere = "groupe_prefere"
    xml_Root = "root"

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
            message = "Veuillez ouvrir (ou enregistrer) un projet avant d'utiliser cette fonctionnalité."
            PluginHelper.showMessageBox(message)
            raise Exception(message)
        nbPoints = fname.count(".")
        if nbPoints != 1:
            message = "Le nom de votre projet QGIS ne doit pas contenir de point en dehors de son extension (.qgz). " \
                      "Merci de le renommer."
            PluginHelper.showMessageBox(message)
            raise Exception(message)
        projectFileName = fname[:fname.find(".")]
        return "{}_{}".format(projectFileName, PluginHelper.nom_Fichier_Parametres_EspaceCo)

    @staticmethod
    def getXPath(tagName, parentTag) -> str:
        """
        La balise principale 'Serveur' peut contenir les sous balises suivantes :
         - URLHost
         - groupe_actif
         - groupe_prefere
         - Login
         - Proxy
        La balise principale 'Map' peut contenir les sous balises suivantes :
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
    def checkXmlFile(projectDir) -> Optional[ET.ElementTree]:
        xmlFileDirectory = "{}/{}".format(projectDir, PluginHelper.getConfigFile())
        try:
            tree = ET.parse(xmlFileDirectory)
            return tree
        except ET.ParseError as e:
            message = "PluginHelper.checkXmlFile, erreur d'analyse : {0} sur le fichier {1}. " \
                      "Il est corrompu, veuillez contacter le support.".format(e, xmlFileDirectory)
            PluginHelper.logger.info(message)
            PluginHelper.showMessageBox(message)
            return

    @staticmethod
    def load_urlhost(projectDir) -> Element:
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: l'url sauvegardée dans le fichier xml, une chaine vide si la balise principale 'Serveur' n'existe pas
        """
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            urlhost = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_UrlHost, PluginHelper.xml_Serveur))
            if urlhost is None:
                urlhost = PluginHelper.addXmlElement(projectDir, PluginHelper.xml_UrlHost, PluginHelper.xml_Serveur)
        except Exception as e:
            PluginHelper.logger.error(str(e))
            raise Exception(e)
        return urlhost

    @staticmethod
    def load_login(projectDir) -> Element:
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: le login sauvegardé dans le fichier xml, une chaine vide si la balise principale 'Serveur' n'existe pas
        """
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            login = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_Login, PluginHelper.xml_Serveur))
            if login is None:
                login = PluginHelper.addXmlElement(projectDir, PluginHelper.xml_Login, PluginHelper.xml_Serveur)
        except Exception as e:
            PluginHelper.logger.error(str(e))
            raise Exception(e)
        return login

    @staticmethod
    def load_proxy(projectDir) -> Element:
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: le proxy sauvegardé dans le fichier xml, une chaine vide si la balise principale 'Serveur' n'existe pas
        """
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            proxy = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_proxy, PluginHelper.xml_Serveur))
            if proxy is None:
                proxy = PluginHelper.addXmlElement(projectDir, PluginHelper.xml_proxy, PluginHelper.xml_Serveur)
        except Exception as e:
            PluginHelper.logger.error(str(e))
            raise Exception(e)
        return proxy

    @staticmethod
    def loadActiveCommunityName(projectDir) -> Element:
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: le nom de la communauté active sauvegardée dans le fichier xml, (groupe utilisé par l'utilisateur
                 pour travailler) une chaine vide si la balise principale 'Serveur' n'existe pas
        """
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            activeCommunity = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_GroupeActif,
                                                                 PluginHelper.xml_Serveur))
            if activeCommunity is None:
                activeCommunity = PluginHelper.addXmlElement(projectDir, PluginHelper.xml_GroupeActif,
                                                             PluginHelper.xml_Serveur)
        except Exception as e:
            PluginHelper.logger.error(str(e))
            raise Exception(e)
        return activeCommunity

    @staticmethod
    def load_preferredGroup(projectDir) -> Element:
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: le nom du groupe préféré sauvegardé dans le fichier xml, (groupe utilisé le plus souvent
                 par l'utilisateur pour travailler) une chaine vide si la balise principale 'Serveur' n'existe pas
        """
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            groupePrefere = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_GroupePrefere,
                                                               PluginHelper.xml_Serveur))
            if groupePrefere is None:
                groupePrefere = PluginHelper.addXmlElement(projectDir, PluginHelper.xml_GroupePrefere,
                                                           PluginHelper.xml_Serveur)
        except Exception as e:
            PluginHelper.logger.error(str(e))
            raise Exception(e)
        return groupePrefere

    @staticmethod
    def load_CalqueFiltrage(projectDir) -> Element:
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: le nom du calque de filtrage sauvegardé dans le fichier xml, une chaine vide si la balise principale
                 'Serveur' n'existe pas
        """
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            calque = xmlroot.find(PluginHelper.getXPath(PluginHelper.xml_Zone_extraction, PluginHelper.xml_Map))
        except Exception as e:
            PluginHelper.logger.error(str(e))
            raise Exception(e)
        return calque

    @staticmethod
    def load_XmlTag(projectDir, tag, parent=None) -> Element:
        """
        Recherche un élément (tag) dans le fichier xml. Si l'élément n'existe pas, il est créé.

        NB : une exception est envoyée, si la recherche du nœud xml a échoué.
        
        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: string
        
        :param tag: xpath de l'élément cherché
        :type tag: str
        
        :param parent: xpath de l'élément parent
        :type parent: str
        
        :return: l'élément xml recherché
        """
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            node = xmlroot.find(PluginHelper.getXPath(tag, parent))
            if node is None:
                node = PluginHelper.addXmlElement(projectDir, tag, parent)
        except Exception as e:
            PluginHelper.logger.error(str(e))
            raise Exception(e)
        return node

    @staticmethod
    def addXmlElement(projectDir, elem, parentElem, value=None) -> Element:
        """
        Ajoute un élément (tag) dans le fichier xml. Si l'élément n'existe pas, il est créé.

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
        tree = PluginHelper.checkXmlFile(projectDir)
        xmlroot = tree.getroot()
        if parentElem != PluginHelper.xml_Root:
            parentNode = xmlroot.find(parentElem)
        else:
            parentNode = xmlroot
        if parentNode is None:
            parentNode = PluginHelper.addXmlElement(projectDir, parentElem, PluginHelper.xml_Root)
        elementNode = ET.SubElement(parentNode, elem)
        if value is not None:
            elementNode.text = value
        tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")
        return elementNode

    @staticmethod
    def load_attCroquis(projectDir) -> {}:
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: les attributs de croquis sauvegardés dans le fichier xml de configuration
        """
        attCroquis = {}
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            nodes = xmlroot.findall(PluginHelper.getXPath(PluginHelper.xml_AttributsCroquis, PluginHelper.xml_Map))
            for cr in nodes:
                nomCalque = cr.find(PluginHelper.xml_BaliseNomCalque).text
                attCroquis[nomCalque] = []
                fields = cr.iter(PluginHelper.xml_BaliseChampCalque)
                for f in fields:
                    attCroquis[nomCalque].append(f.text)
        except Exception as e:
            PluginHelper.logger.error(str(e))
            raise Exception(e)
        return attCroquis

    @staticmethod
    def load_preferredThemes(projectDir) -> []:
        """
        NB : une exception est envoyée, si la recherche du nœud xml a échoué.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :return: les thèmes sauvegardés dans le fichier de configuration xml
        """
        prefThemes = []
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            prefThs = xmlroot.findall(
                PluginHelper.getXPath(PluginHelper.xml_Themes + "/" + PluginHelper.xml_Theme + "/"
                                      + PluginHelper.xml_Map, PluginHelper.xml_Map))
            for n in prefThs:
                prefThemes.append(PluginHelper.notNoneValue(n.text))
        except Exception as e:
            PluginHelper.logger.error(str(e))
            raise Exception(e)
        return prefThemes

    @staticmethod
    def addNode(projectDir, tag, value, parentTag=None) -> None:
        """
        Ajoute un nœud dans le fichier xml de configuration.

        NB : une exception est envoyée si l'ajout dans le fichier xml est impossible.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :param tag: nom de la sous balise
        :type tag: str

        :param value: valeur prise par la sous balise
        :type value: str

        :param parentTag: balise principale
        :type parentTag: str
        """
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
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
            raise Exception(e)

    @staticmethod
    def removeNode(projectDir, tag, parentTag=None) -> None:
        """
        Supprime un nœud dans le fichier xml de configuration.

        NB : une exception est envoyée si la suppression dans le fichier xml est impossible.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :param tag: nom de la sous balise
        :type tag: str

        :param parentTag: nom de la balise principale
        :type parentTag: str
        """
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
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
            raise Exception(e)

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
    def setXmlTagValue(projectDir, tag, value, parentTag=None) -> None:
        """
        Enregistre une valeur à un tag dans le fichier xml de configuration en fonction d'une balise principale.

        NB : une exception est envoyée si l'écriture dans le fichier xml est impossible.

        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: str

        :param tag: nom de la sous balise
        :type tag: str

        :param value: valeur prise par la sous balise
        :type value: str

        :param parentTag: balise principale
        :type parentTag: str
        """
        try:
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            node = xmlroot.find(PluginHelper.getXPath(tag, parentTag))
            node.text = value
            tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

        except Exception as e:
            PluginHelper.logger.error(format(e))
            raise Exception(e)

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
            tree = PluginHelper.checkXmlFile(projectDir)
            xmlroot = tree.getroot()
            mapNode = xmlroot.find(PluginHelper.xml_Map)
            nodeAtributsCroquis = ET.SubElement(mapNode, PluginHelper.xml_AttributsCroquis)
            nodeNom = ET.SubElement(nodeAtributsCroquis, PluginHelper.xml_BaliseNomCalque)
            nodeNom.text = calqueName
            for val in values:
                field = ET.SubElement(nodeAtributsCroquis, PluginHelper.xml_BaliseChampCalque)
                field.text = val

            tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")
        except Exception as e:
            PluginHelper.logger.error(format(e))
            raise Exception(e)

    @staticmethod
    def removeAttCroquis(projectDir) -> None:
        """
        Suppression de balises dans le fichier xml de configuration du projet.

        :param projectDir: le chemin complet du fichier de configuration
        :type projectDir: str
        """
        tree = PluginHelper.checkXmlFile(projectDir)
        xmlroot = tree.getroot()
        maptag = xmlroot.find(PluginHelper.xml_Map)
        for c in maptag.findall(PluginHelper.xml_AttributsCroquis):
            maptag.remove(c)
        tree.write(projectDir + "/" + PluginHelper.getConfigFile(), encoding="utf-8")

    @staticmethod
    def formatDate(sdate) -> str:
        """
        Transforme une date donnée au format dd/MM/yyyy %H:%M:%S en yyyy-MM-dd %H:%M:%S.

        NB : une exception de type ValueError est envoyée si la transformation s'est mal passée.
        
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
    # def getGeometryWorkZone(projectDir) -> Optional[QgsGeometry]:
    #     """
    #     Vérifie si la zone de travail est conforme aux exigences de filtrage des objets après extraction
    #     de signalements ou de données provenant de l'espace collaboratif.
    #
    #     :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
    #     :type projectDir: str
    #
    #     :return: la géométrie de la zone de travail ou None
    #     """
    #     geometryWorkZone = None
    #     nameWorkZone = PluginHelper.load_CalqueFiltrage(projectDir).text
    #     layerWorkZone = QgsProject.instance().mapLayersByName(nameWorkZone)
    #     if len(layerWorkZone) > 1:
    #         message = "Le filtrage des objets sera impossible car plusieurs couches portent le même nom " \
    #                   "dans le projet. Il faut une seule couche représentant la zone de travail pour filtrer" \
    #                   " les objets après extraction des données.".format(nameWorkZone)
    #         QgsProject.instance().iface.messageBar().pushMessage("", message, level=2, duration=3)
    #         return geometryWorkZone
    #     layerWorkZone[0].layer.startEditing()
    #     layerWorkZone[0].selectAll()
    #     feats = layerWorkZone[0].selectedFeatures()
    #     nb = len(list(feats))
    #     if nb > 1:
    #         message = "Le filtrage des objets sera impossible car la couche {0} contient plusieurs objets." \
    #                   "Il faut une seule zone de travail pour filtrer les objets après extraction des données.".format(
    #                     nameWorkZone)
    #         QgsProject.instance().iface.messageBar().pushMessage("", message, level=2, duration=3)
    #         return geometryWorkZone
    #     for feat in feats:
    #         geometryWorkZone = feat.geometry()
    #     if len(list(geometryWorkZone.parts())) > 1:
    #         message = "Le filtrage des objets sera impossible car la zone de travail est une surface multiple." \
    #                   "Il faut une surface simple pour filtrer les objets après extraction des données.".format(
    #                     nameWorkZone)
    #         QgsProject.instance().fa.iface.messageBar().pushMessage("", message, level=2, duration=3)
    #         return geometryWorkZone
    #     layerWorkZone[0].rollBack()
    #     layerWorkZone[0].removeSelection()
    #     return geometryWorkZone

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

    @staticmethod
    def refreshAllLayers():
        """
        Rafraîchit toutes les couches du projet QGIS :
        - Recompte les entités
        - Rafraîchit l'affichage
        - Réinitialise la source de données
        - Recharge les données si nécessaire
        """
        project = QgsProject.instance()
        for layer in project.mapLayers().values():
            if layer.isValid():
                if layer.providerType() != 'spatialite':
                    continue
                uri = layer.dataProvider().dataSourceUri()
                layer.setDataSource(uri, layer.name(), "spatialite")
                layer.triggerRepaint()
                layer.reload()  # recharge les données depuis la source
                print(f"{layer.name()} → {layer.featureCount()} entités")
            else:
                print(f"{layer.name()} → couche invalide")

    @staticmethod
    def setCursor():
        """
        Restaure tous les curseurs empilés en fonction du nombre réel de curseurs empilés
        """
        count = 0
        alertThreshold = 50  # seuil au-delà duquel on considère qu'il y a un problème
        while QApplication.overrideCursor() is not None:
            QApplication.restoreOverrideCursor()
            count += 1
            if count > alertThreshold:
                print(
                    f"Alerte : plus de {alertThreshold} curseurs restaurés. Comportement potentiellement anormal.")
                break
        print(f"{count} curseur(s) restauré(s).")

