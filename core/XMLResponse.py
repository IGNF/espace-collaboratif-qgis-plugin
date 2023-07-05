# -*- coding: utf-8 -*-
"""
Created on 26 janv. 2015
Updated on 8 dec. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""
import xml.etree.ElementTree as ET
from .Profil import Profil
from . import ConstanteRipart as cst
from .Remarque import Remarque
from .Theme import Theme
from .ThemeAttributes import ThemeAttributes
from .Point import Point
from .Author import Author
from .Sketch import Sketch
from .Group import Group
from .InfosGeogroup import InfosGeogroup
from .SketchAttributes import SketchAttributes
from .GeoResponse import GeoResponse
from datetime import datetime
from .ClientHelper import ClientHelper
from .RipartLoggerCl import RipartLogger
from .Layer import Layer

import re


class XMLResponse(object):
    """
    Classe pour le parsing des réponses xml et l'extraction des informations nécessaires
    """

    # la réponse du serveur (au format xml)
    response = ""

    # racine du document xml
    root = ""

    logger = RipartLogger("ripart.XMLResponse").getRipartLogger()

    def __init__(self, response):
        """Constructeur
        
        :param response: la réponse du serveur (xml)
        :type response: string 
        """
        self.logger.debug("init 1 :")

        self.response = ClientHelper.notNoneValue(response)

        self.logger.debug("xmlreponse 2 :")

        try:
            self.root = ET.fromstring(self.response)
            self.logger.debug(str(self.root))
        except Exception as e:
            self.logger.error(str(e))

        self.logger.debug("init !!")

    def checkResponseValidity(self):
        """Contrôle la validité de la réponse. 
        
        Si le code erreur="OK", la réponse est valide
        :return un dictionnaire à 2 clés, message et code
        """
        errMessage = {'message': '', 'code': ''}
        try:
            erreur = self.root.findall('./REPONSE/ERREUR')
            for m in erreur:
                errMessage['message'] = m.text
                errMessage['code'] = m.attrib['code']
        except KeyError as e:
            self.logger.error(str(e))
        except Exception as e:
            self.logger.error(str(e))
        return errMessage

    def checkResponseWfsTransactions(self):
        message = {'message': '', 'status': 'SUCCESS', 'fid': [], 'urlTransaction': ''}
        try:
            fids = []
            insertResult = self.root.find('{http://www.opengis.net/wfs}InsertResult')
            featuresId = insertResult.findall('{http://www.opengis.net/ogc}FeatureId')
            for featureId in featuresId:
                fids.append(featureId.attrib['fid'])
            message['fid'] = fids
            transactionResult = self.root.find('{http://www.opengis.net/wfs}TransactionResult')
            status = transactionResult.find('{http://www.opengis.net/wfs}Status')
            if status.find('{http://www.opengis.net/wfs}SUCCESS') is None:
                message['status'] = 'FAILED'
            message['message'] = transactionResult.find('{http://www.opengis.net/wfs}Message').text
            message['urlTransaction'] = transactionResult.find('{http://www.opengis.net/wfs}TransactionURL').text
        except Exception as e:
            self.logger.error(str(e))
        return message

    def extractNomProfil(self):
        try:
            node = self.root.find('./PROFIL/TITRE')
            nomProfil = node.text

        except Exception as e:
            self.logger.error('extractNomProfil:' + str(e))
            raise

        return nomProfil

    def extractProfil(self):
        """Extraction du profil à partir de la réponse xml
        
        :return: profil de l'utilisateur
        """
        profil = Profil()

        try:
            # aut= Auteur()
            node = self.root.find('./AUTEUR/NOM')
            profil.author.name = node.text

            node = self.root.find('./PROFIL/ID_GEOPROFIL')
            profil.id_Geoprofil = node.text

            node = self.root.find('./PROFIL/TITRE')
            profil.title = node.text

            gr = Group()
            node = self.root.find('./PROFIL/ID_GEOGROUPE')
            gr = node.text

            node = self.root.find('./PROFIL/GROUPE')
            profil.geogroup.name = node.text

            node = self.root.find('./PROFIL/ID_GEOGROUPE')
            profil.geogroup.id = node.text

            node = self.root.find('./PROFIL/LOGO')
            if node is not None and node.text:
                profil.logo = node.text
            else:
                profil.logo = ""

            node = self.root.find('./PROFIL/FILTRE')
            profil.filtre = node.text

            node = self.root.find('./PROFIL/PRIVE')
            profil.prive = True if node.text == 1 else False

            # va chercher les thèmes associés au profil
            themes = self.getThemes()
            profil.themes = themes[0]
            profil.filteredThemes = themes[1]
            profil.globalThemes = themes[2]

            # va chercher les infos de tous les geogroupes de l'utilisateur
            infosgeogroups = self.getInfosGeogroup(profil)
            profil.infosGeogroups = infosgeogroups

        except Exception as e:
            self.logger.error('extractProfil:' + str(e))
            raise

        return profil

    def findDatabaseName(self, urlStr):
        # La chaine url est de type
        # https://espacecollaboratif.ign.fr/gcms/wfs?service=wfs&databasename=bdtopo_metropole
        pos = urlStr.find('&')
        if pos == -1:
            return ""
        return urlStr[pos+14:len(urlStr)]

    def getInfosGeogroup(self, profil):
        """Extraction des infos utilisateur sur ses geogroupes
        :return les infos
        """
        global infosgeogroup
        infosgeogroups = []

        try:
            # informations sur le geogroupe
            nodesGr = self.root.findall('GEOGROUPE')
            for nodegr in nodesGr:
                infosgeogroup = InfosGeogroup()
                infosgeogroup.group = Group()
                infosgeogroup.group.name = (nodegr.find('NOM')).text
                infosgeogroup.group.id = (nodegr.find('ID_GEOGROUPE')).text

                # Récupération du commentaire par défaut des signalements
                infosgeogroup.reportDefaultComment = nodegr.find('COMMENTAIRE_GEOREM').text

                # Récupération des layers du groupe
                for nodelayer in nodegr.findall('LAYERS/LAYER'):
                    layer = Layer()
                    layer.type = nodelayer.find('TYPE').text
                    layer.nom = nodelayer.find('NOM').text
                    layer.description = nodelayer.find('DESCRIPTION').text
                    layer.minzoom = nodelayer.find('MINZOOM').text
                    layer.maxzoom = nodelayer.find('MAXZOOM').text
                    layer.extent = nodelayer.find('EXTENT').text
                    # cas particulier de la balise <ROLE> qui n'existe
                    # que dans la base de qualification
                    role = nodelayer.find('ROLE')
                    if role is not None:
                        layer.role = role.text
                    layer.visibility = nodelayer.find('VISIBILITY').text
                    layer.opacity = nodelayer.find('OPACITY').text
                    tilezoom = nodelayer.find('TILEZOOM')
                    if tilezoom is not None:
                        layer.tilezoom = tilezoom.text
                    url = nodelayer.find('URL')
                    if url is None or url.text is None:
                        continue
                    layer.url = url.text
                    layer.databasename = self.findDatabaseName(url.text)
                    print("groupe : {0} layer : {1} databasename : {2}".format(infosgeogroup.group.name, layer.nom, layer.databasename))
                    layer_id = nodelayer.find('LAYER')
                    if layer_id is not None:
                        layer.layer_id = layer_id.text
                    infosgeogroup.layers.append(layer)
                try:
                    # Récupération des thèmes du groupe
                    themesAttDict = self.get_themes_attributes(nodegr.findall('THEMES/ATTRIBUT'))

                    nodes = nodegr.findall('THEMES/THEME')

                    # Récupérer les thèmes à afficher dans le profil (balise <FILTER>)
                    # Exemple : [{"group_id":375,"themes":["Test_signalement","test leve",
                    # "Theme_table_bool_TestEcriture"]},{"group_id":1,"themes":["Bati"]}]

                    filterDict = nodegr.find('FILTER').text
                    groupFilters = re.findall('\{.*?\}', filterDict)
                    filteredThemes = self.getFilteredThemes(groupFilters, infosgeogroup.group.id)
                    infosgeogroup.filteredThemes = filteredThemes

                    for node in nodes:
                        theme = Theme()
                        theme.group = Group()

                        name = (node.find('NOM')).text
                        theme.group.name = name
                        if name in filteredThemes:
                            theme.isFiltered = True

                        theme.group.id = infosgeogroup.group.id
                        if ClientHelper.notNoneValue(theme.group.name) in themesAttDict:
                            theme.attributes.extend(themesAttDict[ClientHelper.notNoneValue(theme.group.name)])

                        infosgeogroup.themes.append(theme)
                        profil.allThemes.append(theme)

                except Exception as e:
                    self.logger.error(str(e))
                    raise Exception("Erreur dans la récupération des thèmes du groupe")

                infosgeogroups.append(infosgeogroup)

        except Exception as e:
            self.logger.error(str(e))
            raise Exception("Erreur dans la récupération des informations du groupe " + infosgeogroup.group.name)

        return infosgeogroups

    def get_themes_attributes(self, thAttNodes):
        """Récupération des attributs des thèmes de signalement
        :return dictionnaire contenant pour chaque thème la liste de ses attributs
        """
        themesAttDict = {}
        thAttributs = []

        for attNode in thAttNodes:

            nomTh = ClientHelper.notNoneValue(attNode.find('NOM').text)
            attNodeATT = attNode.find('ATT')
            nomAtt = attNodeATT.text
            thAttribut = ThemeAttributes(nomTh, nomAtt, "")
            thAttribut.setTagDisplay(nomAtt)
            display_tag = attNodeATT.get('display')
            if display_tag is not None:
                thAttribut.setTagDisplay(display_tag)

            attType = attNode.find('TYPE').text
            thAttribut.setType(attType)

            attObligatoire = attNode.find('OBLIGATOIRE')
            if attObligatoire is not None:
                thAttribut.setObligatoire()

            for val in attNode.findall('VALEURS/VAL'):
                valDisplay = val.get('display')
                if valDisplay is not None:
                    thAttribut.addValeur(val.text, valDisplay)
                else:
                    thAttribut.addValeur(val.text, "")

            for val in attNode.findall('VALEURS/DEFAULTVAL'):
                thAttribut.defaultval = val.text

            thAttributs.append(thAttribut)
            if nomTh not in themesAttDict:
                themesAttDict[nomTh] = []
            themesAttDict[nomTh].append(thAttribut)

        return themesAttDict

    def getFilteredThemes(self, groupFilters, idGeogroup):

        """Récupération des thèmes à afficher dans le profil
        :return les thèmes filtrés
        """

        filteredThemes = []

        for groupFilter in groupFilters:
            # Si le filtre ne concerne pas le geogroupe en cours, on ne le traite pas
            # car les thèmes des autres groupes ne sont envoyés que dans la partie profil actif de geoaut_get
            listElements = groupFilter.split(":")
            idGroupe = listElements[1].split(",")[0]

            if idGeogroup == "":
                processFilter = True
            else:
                idGeogroupInt = int(idGeogroup)
                idGroupInt = int(idGroupe)
                intDiff = idGeogroupInt - idGroupInt
                if intDiff == 0:
                    processFilter = True
                else:
                    processFilter = False

            if processFilter:
                listThemesTmp = listElements[len(listElements) - 1]
                listThemesTmp = listThemesTmp[1:len(listThemesTmp) - 2]
                filteredThemesTmp = re.findall('\".*?\"', listThemesTmp)
                # Suppression des guillemets
                for i in range(len(filteredThemesTmp)):
                    currTheme = self.convertEncodedCharacters(filteredThemesTmp[i].strip("\""))
                    filteredThemes.append(currTheme)

        return filteredThemes

    def getThemes(self):
        """Extraction des thèmes associés au profil
        :return les thèmes et la liste des thèmes cochés dans le profil
        """
        themes = []
        try:
            themesAttDict = self.get_themes_attributes(self.root.findall('THEMES/ATTRIBUT'))

            # Récupération du filtre sur les thèmes
            filterDict = self.root.find('PROFIL/FILTRE').text
            filteredThemes = []
            globalThemes = []
            if filterDict is not None:
                groupFilters = re.findall('\{.*?\}', filterDict)
                filteredThemes = self.getFilteredThemes(groupFilters, "")

            nodes = self.root.findall('THEMES/THEME')

            for node in nodes:
                theme = Theme()
                theme.group = Group()

                name = (node.find('NOM')).text
                theme.group.name = name
                if name in filteredThemes or len(filteredThemes) == 0:
                    theme.isFiltered = True

                isGlobal = (node.find('GLOBAL')).text
                if isGlobal == '1':
                    theme.isGlobal = True
                    globalThemes.append(name)

                theme.group.id = (node.find('ID_GEOGROUPE')).text
                if ClientHelper.notNoneValue(theme.group.name) in themesAttDict:
                    theme.attributes.extend(themesAttDict[ClientHelper.notNoneValue(theme.group.name)])
                themes.append(theme)

        except Exception as e:
            self.logger.error(str(e))
            raise Exception("Erreur dans la récupération des thèmes du profil : {}".format(str(e)))

        return [themes, filteredThemes, globalThemes]

    def getVersion(self):
        """Retourne la version du service ripart    
        :return la version du service
        """
        v = ""
        try:
            v = self.root.attrib['version']

        except KeyError as e:
            self.logger.error(str(e))

        except Exception as e:
            self.logger.error(str(e))

        return v

    def getDate(self):
        """Retourne la date de la réponse xml
        """
        date = ""
        try:
            node = self.root.find('PAGE/DATE')
            date = node.text
        except Exception as e:
            self.logger.error('getTotalResponse :' + str(e))
        return date

    def getTotalResponse(self):
        """Retourne le nombre total de réponses
        :return: nombre total de réponse
        """
        total = 0
        try:
            node = self.root.find('PAGE/TOTAL')
            total = node.text
        except Exception as e:
            self.logger.error('getTotalResponse :' + str(e))

        return total

    def extractRemarques(self):
        """Extraction des remarques de la réponse xml
        """
        remarques = {}

        try:
            georems = self.root.findall('GEOREM')

            for node in georems:

                rem = Remarque()
                themes = []

                rem.id = (node.find('ID_GEOREM')).text

                nfind = node.find('AUTORISATION')
                if nfind is not None:
                    rem.autorisation = nfind.text

                for th in node.findall('THEME'):
                    nameGroup = (th.find('NOM')).text
                    idGroup = (th.find('ID_GEOGROUPE')).text

                    theme = Theme()
                    theme.group = Group(idGroup, nameGroup)

                    for att in th.findall('ATTRIBUT'):
                        nomAtt = att.attrib["nom"]
                        valAtt = att.text
                        attribut = ThemeAttributes(nameGroup, nomAtt, valAtt)
                        theme.attributes.append(attribut)

                    themes.append(theme)

                rem.themes = themes

                nfind = node.find('LIEN')
                if nfind is not None:
                    rem.lien = nfind.text
                    rem.lien.replace("&amp;", "&")

                nfind = node.find('LIEN_PRIVE')
                if nfind is not None:
                    rem.lienPrive = nfind.text
                    rem.lienPrive.replace("&amp;", "&")

                nfind = node.find('DATE')
                if nfind is not None:
                    rem.dateCreation = nfind.text

                nfind = node.find('MAJ')
                if nfind is not None:
                    rem.dateMiseAJour = nfind.text

                nfind = node.find('DATE_VALID')
                if nfind is not None:
                    rem.dateValidation = nfind.text

                lon = (node.find('LON')).text
                lat = (node.find('LAT')).text
                rem.position = Point(lon, lat)

                nfind = node.find('STATUT')
                if nfind is not None:
                    rem.statut = nfind.text

                nfind = node.find('ID_DEP')
                if nfind is not None:
                    rem.departement.id = nfind.text

                nfind = node.find('DEPARTEMENT')
                if nfind is not None:
                    rem.departement.name = nfind.text

                nfind = node.find('COMMUNE')
                if nfind is not None:
                    rem.commune = nfind.text

                nfind = node.find('INSEE_COM')
                if nfind is not None:
                    rem.insee = nfind.text

                nfind = node.find('COMMENTAIRE')
                if nfind is not None:
                    rem.commentaire = nfind.text

                rem.author = Author()
                nfind = node.find('ID_AUTEUR')
                if nfind is not None:
                    rem.author.id = nfind.text

                nfind = node.find('AUTEUR')
                if nfind is not None:
                    rem.author.name = nfind.text

                rem.group = Group()
                nfind = node.find('ID_GEOGROUPE')
                if nfind is not None:
                    rem.group.id = nfind.text

                nfind = node.find('GROUPE')
                if nfind is not None:
                    rem.group.name = nfind.text

                nfind = node.find('ID_PARTITION')
                if nfind is not None:
                    rem.id_partition = nfind.text

                # croquis
                rem = self.getCroquisForRem(rem, node)

                # documents
                rem = self.getDoc(rem, node)

                # réponses (GEOREP)
                rem = self.getGeoRep(rem, node)

                rem.source = (node.find('SOURCE')).text

                remarques[rem.id] = rem

        except Exception as e:
            self.logger.error(str(e))
            raise Exception("Une erreur est survenue dans l'importation des remarques : {}".format(str(e)))

        return remarques

    def getCroquisForRem(self, rem, node):
        """ Extrait les croquis d'une remarque et les ajoute dans l'objet Remarque (rem)

        :param rem un objet Remarque
        :type rem: Remarque

        :param node: le noeud de la remarque dans le fichier xml (<GEOREM> ...</GEOREM>)
        :type node: Element

        :return la remarque avec les croquis
        :rtype Remarque
        """
        try:
            objets = node.findall('CROQUIS/objet')
            for ob in objets:

                # Récupération du type
                typeObjet = ob.attrib['type']
                if not typeObjet.startswith("Multi"):
                    typeCroquis = typeObjet
                else:
                    if typeObjet == "MultiPoint":
                        typeCroquis = "Point"
                    elif typeObjet == "MultiLigne":
                        typeCroquis = "Ligne"
                    elif typeObjet == "MultiPolygone":
                        typeCroquis = "Polygone"
                    else:
                        self.logger.error("Type de croquis inconnu pour le signalement " + str(rem.id) + " : " + typeObjet)
                        return

                # Récupération du nom
                nomCroquis = ob.find('nom').text

                # Récupération des attributs
                attributes = ob.findall('attributs/attribut')
                listAttCroquis = []
                for att in attributes:
                    attribute = SketchAttributes()
                    attribute.name = att.attrib['name']
                    attribute.valeur = att.text
                    listAttCroquis.append(attribute)

                # On itère sur les géométries de l'objet xml.
                # Si c'est un croquis avec une géométrie multiple, il peut y en avoir plusieurs.
                # Si le croquis a une géométrie simple, il n'y en a qu'une.

                coords = ob.iterfind('.//gml:coordinates', cst.namespace)
                coordinates = ""
                for c in coords:

                    # On crée un croquis par ensemble de coordonnées récupérées
                    sketch = Sketch()
                    sketch.type = typeCroquis
                    sketch.name = nomCroquis
                    sketch.attributes = listAttCroquis

                    pts = c.text.split(" ")
                    for spt in pts:
                        try:
                            pt = Point()
                            latlon = spt.split(",")
                            if len(latlon) == 4:
                                pt.longitude = float(latlon[0] + "." + latlon[1])
                                pt.latitude = float(latlon[2] + "." + latlon[3])
                            elif len(latlon) == 2 or len(latlon) == 3:
                                pt.longitude = float(latlon[0])
                                pt.latitude = float(latlon[1])

                            if pt.longitude is not None and pt.latitude is not None:
                                coordinates += str(pt.longitude) + " " + str(pt.latitude) + ","
                                sketch.addPoint(pt)

                        except Exception as e:
                            self.logger.error(str(e))
                            raise Exception("Erreur dans la récupération de l'un des points du croquis pour le signalement "
                                            + str(rem.id) + " : {}".format(str(e)))

                    sketch.coordinates = coordinates[:-1]

                    # Ajout du croquis au signalement
                    rem.addCroquis(sketch)

        except Exception as e:
            self.logger.error(str(e))
            raise Exception("Erreur dans la récupération du croquis pour le signalement " + str(rem.id) + " : {}".format(str(e)))

        return rem

    def getDoc(self, rem, node):
        """Extraction des documents attachés à une remarque
        
        :param rem un objet Remarque
        :type rem: Remarque
        
        :param node: le noeud de la remarque dans le fichier xml (<GEOREM> ...</GEOREM>)
        :type node: Element
        
        :return la remarque avec les croquis
        :rtype Remarque
        """
        docs = node.findall('DOC')
        for doc in docs:
            rem.addDocument(doc)
        return rem

    def getGeoRep(self, rem, node):
        """Extraction des réponses d'une remarque
        """
        responses = node.findall("GEOREP")

        for response in responses:
            georep = GeoResponse()

            gr = Group()
            gr.id = response.find('ID_GEOREP').text
            gr.name = response.find('TITRE').text
            georep.group = gr

            georep.author = Author()
            georep.author.id = response.find('ID_AUTEUR').text
            georep.author.name = response.find('AUTEUR').text

            georep.status = cst.STATUT.__getitemFromString__(response.find('STATUT').text)
            georep.date = datetime.strptime(response.find('DATE').text, "%Y-%m-%d %H:%M:%S")
            georep.response = response.find('REPONSE').text

            rem.addGeoResponse(georep)

        return rem

    def convertEncodedCharacters(self, substring):
        # Equivalences entre les caractères spéciaux de l'API et les chaines Python
        charConversion = {
            "\\u00e0": 'à',
            "\\u00e2": 'â',
            "\\u00e4": 'ä',
            "\\u00e7": 'ç',
            "\\u00e8": 'è',
            "\\u00e9": 'é',
            "\\u00ea": 'ê',
            "\\u00eb": 'ë',
            "\\u00ee": 'î',
            "\\u00ef": 'ï',
            "\\u00f4": 'ô',
            "\\u00f6": 'ö',
            "\\u00f9": 'ù',
            "\\u00fb": 'û',
            "\\u00fc": 'ü',
        }

        newString = substring
        for c, v in charConversion.items():
            newString = newString.replace(c, v)
        return newString


if __name__ == "__main__":
    x = """<?xml version='1.0' encoding='UTF-8'?>
                            <geors version='0.1'>
                            <REPONSE type='action=connect'>
                                <ERREUR code='OK'>OK</ERREUR>
                                <ALEA1>6117245975489987c2c8028.02593919</ALEA1>
                                <ALEA2>141784489354899890b49555.72390296</ALEA2>
                                <SITE>Demo-RIPart</SITE>
                            </REPONSE>
                            </geors>
                    """
    xml = XMLResponse(x)
    mess = xml.checkResponseValidity()
    version = xml.getVersion()
    print(version)
