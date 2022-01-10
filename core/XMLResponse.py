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
from .ThemeAttribut import ThemeAttribut
from .Point import Point
from .Auteur import Auteur
from .Croquis import Croquis
from .Groupe import Groupe
from .InfosGeogroupe import InfosGeogroupe
from .Attribut import Attribut
from .GeoReponse import GeoReponse
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

    def getAleas(self):
        """ Extraction des Aleas       
        :return une liste contenant les 2 aleas
        """

        aleas = list()

        try:
            alea1 = self.root.find('./REPONSE/ALEA1')
            aleas.append(alea1.text)

            alea2 = self.root.find('./REPONSE/ALEA2')
            aleas.append(alea2.text)

        except Exception as e:
            self.logger.error(str(e))
            raise Exception('Probleme de connexion')

        return aleas

    def getConnectValues(self):
        """Extraction des paramètres de connexion
        
        :return: un dictionnaire contenant les paramètres de connexion (ID_AUTEUR, JETON, SITE)
        """
        connectValues = {'ID_AUTEUR': None, 'JETON': None, 'SITE': None}

        try:
            id_auteur = self.root.find('./REPONSE/ID_AUTEUR')
            if id_auteur is not None:
                connectValues['ID_AUTEUR'] = id_auteur.text
            else:
                raise Exception("ID_AUTEUR inexistant dans la réponse xml")

            jeton = connectValues['JETON'] = self.root.find('./REPONSE/JETON')
            if jeton is not None:
                connectValues['JETON'] = jeton.text
            else:
                raise Exception("JETON inexistant dans la réponse xml")

            site = connectValues['SITE'] = self.root.find('./REPONSE/SITE')
            if site is not None:
                connectValues['SITE'] = site.text
            else:
                raise Exception("SITE inexistant dans la réponse xml")

        except Exception as e:
            self.logger.error(str(e))
            raise

        return connectValues

    def getCurrentJeton(self):
        """Extraction du nouveau jeton
           
        :return le jeton
        """

        jeton = ""

        try:
            jetonNode = self.root.find('./REPONSE/JETON')

            if jetonNode is not None:
                jeton = jetonNode.text
            else:
                raise Exception('Pas de jeton')

        except Exception as e:
            self.logger.error('getCurrentJeton:' + str(e))
            raise

        return jeton

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
            profil.auteur.nom = node.text

            node = self.root.find('./PROFIL/ID_GEOPROFIL')
            profil.id_Geoprofil = node.text

            node = self.root.find('./PROFIL/TITRE')
            profil.titre = node.text

            gr = Groupe()
            node = self.root.find('./PROFIL/ID_GEOGROUPE')
            gr = node.text

            node = self.root.find('./PROFIL/GROUPE')
            profil.geogroupe.nom = node.text

            node = self.root.find('./PROFIL/ID_GEOGROUPE')
            profil.geogroupe.id = node.text

            node = self.root.find('./PROFIL/LOGO')
            if node is not None and node.text:
                profil.logo = node.text

            node = self.root.find('./PROFIL/FILTRE')
            profil.filtre = node.text

            node = self.root.find('./PROFIL/PRIVE')
            profil.prive = True if node.text == 1 else False

            # va chercher les thèmes associés au profil
            themes = self.getThemes()
            profil.themes = themes[0]
            profil.filteredThemes = themes[1]

            # va chercher les infos de tous les geogroupes de l'utilisateur
            infosgeogroupes = self.getInfosGeogroupe(profil)
            profil.infosGeogroupes = infosgeogroupes


        except Exception as e:
            self.logger.error('extractProfil:' + str(e))
            raise

        return profil

    def getInfosGeogroupe(self, profil):
        """Extraction des infos utilisateur sur ses geogroupes
        :return les infos
        """
        infosgeogroupes = []

        try:
            # informations sur le geogroupe
            nodesGr = self.root.findall('GEOGROUPE')
            for nodegr in nodesGr:
                infosgeogroupe = InfosGeogroupe()
                infosgeogroupe.groupe = Groupe()
                infosgeogroupe.groupe.nom = (nodegr.find('NOM')).text
                infosgeogroupe.groupe.id = (nodegr.find('ID_GEOGROUPE')).text

                # Récupération du commentaire par défaut des signalements
                infosgeogroupe.georemComment = nodegr.find('COMMENTAIRE_GEOREM').text

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
                    if url is not None:
                        layer.url = url.text
                    layer_id = nodelayer.find('LAYER')
                    if layer_id is not None:
                        layer.layer_id = layer_id.text

                    infosgeogroupe.layers.append(layer)


                try:
                    # Récupération des thèmes du groupe
                    themesAttDict = self.get_themes_attributes(nodegr.findall('THEMES/ATTRIBUT'))

                    nodes = nodegr.findall('THEMES/THEME')

                    # Récupérer les thèmes à afficher dans le profil (balise <FILTER>)
                    # Exemple : [{"group_id":375,"themes":["Test_signalement","test leve",
                    # "Theme_table_bool_TestEcriture"]},{"group_id":1,"themes":["Bati"]}]

                    filterDict = nodegr.find('FILTER').text
                    groupFilters = re.findall('\{.*?\}', filterDict)
                    filteredThemes = self.getFilteredThemes(groupFilters, infosgeogroupe.groupe.id)
                    infosgeogroupe.filteredThemes = filteredThemes

                    for node in nodes:
                        theme = Theme()
                        theme.groupe = Groupe()

                        nom = (node.find('NOM')).text
                        theme.groupe.nom = nom
                        if nom in filteredThemes:
                            theme.isFiltered = True

                        theme.groupe.id = infosgeogroupe.groupe.id
                        if ClientHelper.notNoneValue(theme.groupe.nom) in themesAttDict:
                            theme.attributs.extend(themesAttDict[ClientHelper.notNoneValue(theme.groupe.nom)])

                        infosgeogroupe.themes.append(theme)
                        profil.allThemes.append(theme)

                except Exception as e:
                    self.logger.error(str(e))
                    raise Exception("Erreur dans la récupération des thèmes du groupe")

                infosgeogroupes.append(infosgeogroupe)

        except Exception as e:
            self.logger.error(str(e))
            raise Exception("Erreur dans la récupération des informations sur le GEOGROUPE")

        return infosgeogroupes


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
            thAttribut = ThemeAttribut(nomTh, nomAtt, None)
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


    def getFilteredThemes(self, groupFilters, idGeogroupe):

        """Récupération des thèmes à afficher dans le profil
        :return les thèmes filtrés
        """

        filteredThemes = []

        for groupFilter in groupFilters:
            # Si le filtre ne concerne pas le geogroupe en cours, on ne le traite pas
            # car les thèmes des autres groupes ne sont envoyés que dans la partie profil actif de geoaut_get
            listElements = groupFilter.split(":")
            idGroupe = listElements[1].split(",")[0]

            processFilter = False

            if idGeogroupe == "":
                processFilter = True
            else:
                idGeogroupeInt = int(idGeogroupe)
                idGroupeInt = int(idGroupe)
                intDiff = idGeogroupeInt - idGroupeInt
                if intDiff == 0:
                    processFilter = True
                else:
                    processFilter = False

            if processFilter:
                listThemesTmp = listElements[len(listElements) - 1]
                listThemesTmp = listThemesTmp[1:len(listThemesTmp) - 2]
                filteredThemesTmp = re.findall('\".*?\"', listThemesTmp)
                # Suppression des guillements
                for i in range(len(filteredThemesTmp)):
                    currTheme = self.convertEncodedCharacters(filteredThemesTmp[i].strip("\""))
                    filteredThemes.append(currTheme)

        return filteredThemes

    def getThemes(self):
        """Extraction des thèmes associés au profil     
        :return les thèmes et la liste des thèmes cochés dans le profil
        """
        themes = []
        themesAttDict = {}

        try:

            themesAttDict = self.get_themes_attributes(self.root.findall('THEMES/ATTRIBUT'))

            # Récupération du filtre sur les thèmes
            filterDict = self.root.find('PROFIL/FILTRE').text
            filteredThemes = []
            if filterDict != None:
                groupFilters = re.findall('\{.*?\}', filterDict)
                filteredThemes = self.getFilteredThemes(groupFilters, "")

            nodes = self.root.findall('THEMES/THEME')

            for node in nodes:
                theme = Theme()
                theme.groupe = Groupe()

                nom = (node.find('NOM')).text
                theme.groupe.nom = nom
                if nom in filteredThemes or len(filteredThemes) == 0:
                    theme.isFiltered = True

                theme.groupe.id = (node.find('ID_GEOGROUPE')).text
                if ClientHelper.notNoneValue(theme.groupe.nom) in themesAttDict:
                    theme.attributs.extend(themesAttDict[ClientHelper.notNoneValue(theme.groupe.nom)])
                themes.append(theme)

        except Exception as e:
            self.logger.error(str(e))
            raise Exception("Erreur dans la récupération des thèmes du profil : {}".format(str(e)))

        return [themes, filteredThemes]

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
        
        :param remarques: dictionnaire  de remarques
        :type remarques: Dictionary of Remarque (key: identifiant de la ramarque, value: la remarque
        :return: dictionnaire de remarques (dans l'ordre inverse d'identifiants)
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
                    nomGroupe = (th.find('NOM')).text
                    idGroupe = (th.find('ID_GEOGROUPE')).text

                    theme = Theme()
                    theme.groupe = Groupe(idGroupe, nomGroupe)

                    for att in th.findall('ATTRIBUT'):
                        nomAtt = att.attrib["nom"]
                        valAtt = att.text
                        attribut = ThemeAttribut(nomGroupe, nomAtt, valAtt)
                        theme.attributs.append(attribut)

                    themes.append(theme)

                rem.themes = themes

                nfind = node.find('LIEN')
                if nfind is not None:
                    rem.lien = nfind.text
                    rem.lien.replace("&amp;", "&");

                nfind = node.find('LIEN_PRIVE')
                if nfind is not None:
                    rem.lienPrive = nfind.text
                    rem.lienPrive.replace("&amp;", "&");

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

                rem.departement = Groupe()
                nfind = node.find('ID_DEP')
                if nfind is not None:
                    rem.departement.id = nfind.text

                nfind = node.find('DEPARTEMENT')
                if nfind is not None:
                    rem.departement.nom = nfind.text

                nfind = node.find('COMMUNE')
                if nfind is not None:
                    rem.commune = nfind.text

                nfind = node.find('COMMENTAIRE')
                if nfind is not None:
                    rem.commentaire = nfind.text

                rem.auteur = Auteur()
                nfind = node.find('ID_AUTEUR')
                if nfind is not None:
                    rem.auteur.id = nfind.text

                nfind = node.find('AUTEUR')
                if nfind is not None:
                    rem.auteur.nom = nfind.text

                rem.groupe = Groupe()
                nfind = node.find('ID_GEOGROUPE')
                if nfind is not None:
                    rem.groupe.id = nfind.text

                nfind = node.find('GROUPE')
                if nfind is not None:
                    rem.groupe.nom = nfind.text

                nfind = node.find('ID_PARTITION')
                if nfind is not None:
                    rem.id_partition = nfind.text

                # croquis
                rem = self.getCroquisForRem(rem, node)

                # documents
                rem = self.getDoc(rem, node)

                # réponses (GEOREP)
                rem = self.getGeoRep(rem, node)

                # rem.hash = (node.find('HASH')).text
                rem.source = (node.find('SOURCE')).text

                remarques[rem.id] = rem

        except Exception as e:
            self.logger.error(str(e))
            raise Exception("Une erreur est survenue dans l'importation des remarques : {}".format(str(e)))

        return remarques

    def getNodeText(self, node):
        if node is not None:
            return node.text
        else:
            return ""


    def getCroquisForRem(self, rem, node):
        """ Extrait les croquis d'une remarque et les ajoute dans l'objet Remarque (rem)

        :param rem un objet Remarque
        :type rem: Remarque

        :param node: le noeud de la remarque dans le fichier xml (<GEOREM> ...</GEOREM>)
        :type node: string

        :return la remarque avec les croquis
        :rtype Remarque
        """

        try:

            objets = node.findall('CROQUIS/objet')

            for ob in objets:

                # Récupération du type
                typeObjet = ob.attrib['type']
                typeCroquis = ""

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
                attributs = ob.findall('attributs/attribut')
                listAttCroquis = []
                for att in attributs:
                    attribut = Attribut()
                    attribut.nom = att.attrib['name']
                    attribut.valeur = att.text
                    listAttCroquis.append(attribut)

                # On itère sur les géométries de l'objet xml.
                # Si c'est un croquis avec une géométrie multiple, il peut y en avoir plusieurs.
                # Si le croquis a une géométrie simple, il n'y en a qu'une.

                coords = ob.iterfind('.//gml:coordinates', cst.namespace)
                coordinates = ""
                for c in coords:

                    # On crée un croquis par ensemble de coordonnées récupérées
                    croquis = Croquis()
                    croquis.type = typeCroquis
                    croquis.nom = nomCroquis
                    croquis.attributs = listAttCroquis

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
                                croquis.addPoint(pt)

                        except Exception as e:
                            self.logger.error(str(e))
                            raise Exception("Erreur dans la récupération de l'un des points du croquis pour le signalement "
                                            + str(rem.id) + " : {}".format(str(e)))

                    croquis.coordinates = coordinates[:-1]

                    # Ajout du croquis au signalement
                    rem.addCroquis(croquis)

        except Exception as e:
            self.logger.error(str(e))
            raise Exception("Erreur dans la récupération du croquis pour le signalement " + str(rem.id) + " : {}".format(str(e)))

        return rem



    def getDoc(self, rem, node):
        """Extraction des documents attachés à une remarque
        
        :param rem un objet Remarque
        :type rem: Remarque
        
        :param node: le noeud de la remarque dans le fichier xml (<GEOREM> ...</GEOREM>)
        :type node: string
        
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
        reponses = node.findall("GEOREP")

        for rep in reponses:
            georep = GeoReponse()

            gr = Groupe()
            gr.id = rep.find('ID_GEOREP').text
            gr.nom = rep.find('TITRE').text
            georep.groupe = gr

            georep.auteur = Auteur()
            georep.auteur.id = rep.find('ID_AUTEUR').text
            georep.auteur.nom = rep.find('AUTEUR').text

            georep.statut = cst.STATUT.__getitemFromString__(rep.find('STATUT').text)
            georep.date = datetime.strptime(rep.find('DATE').text, "%Y-%m-%d %H:%M:%S")
            georep.reponse = rep.find('REPONSE').text

            rem.addGeoReponse(georep)

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
