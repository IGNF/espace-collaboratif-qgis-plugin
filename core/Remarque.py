# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""
from .Point import Point
from . import ConstanteRipart
from .Group import Group
from .Author import Author
from .Theme import Theme
from datetime import datetime
from .ClientHelper import ClientHelper
from .RipartLoggerCl import RipartLogger


class Remarque(object):
    """
    Classe représentant une remarque
    """

    # Identifiant de la remarque
    id = None

    # Url vers la remarque sur le site  web  public de l'Espace collaboratif
    lien = ""

    # Url vers la partie privée du site web de l'Espace collaboratif
    lienPrive = ""

    # date de création de la remarque 
    dateCreation = datetime.now()

    # date de mise-à-jour de la remarque 
    dateMiseAJour = datetime.now()

    # date de validation de la remarque
    dateValidation = None

    # position de la remarque (lon/lat)
    position = Point()

    # statut de la remarque
    statut = ConstanteRipart.STATUT.undefined

    # Le département où est située la remarque (indicatif + nom)
    departement = None

    # commune de la remarque
    commune = ""

    insee = ""

    # texte de la remarque
    commentaire = ""

    # auteur de la remarque
    author = Author()

    # Définit les droits d'action de l'utilisateur en cours sur la remarque
    autorisation = ""

    #
    id_partition = ""

    # groupe sous lequel l'auteur a crée la remarque 
    group = Group()

    # réponses de la remarque Ripart (liste d'objet GeoReponse)
    responses = []

    # croquis de la remarque  list(Croquis)
    croquis = []

    # documents attachés à la remarque  (liste de string)
    documents = []

    # thèmes attachés à la remarque  list(Theme)
    themes = []

    hash = ""

    source = ""

    logger = RipartLogger("ripart.client").getRipartLogger()

    def __init__(self):
        """Constructor
        """
        self.id = None
        self.lien = ""
        self.lienPrive = ""
        self.dateCreation = datetime.now()
        self.dateMiseAJour = datetime.now()
        self.dateValidation = None
        self.position = Point()
        self.statut = ConstanteRipart.STATUT.undefined
        self.departement = Group()
        self.commune = ""
        self.insee = ""
        self.commentaire = ""
        self.author = Author()
        self.autorisation = ""
        self.id_partition = ""
        self.group = Group()
        self.responses = []
        self.croquis = []
        self.documents = []
        self.themes = []
        self.hash = ""
        self.source = ""

    def getAttribut(self, attName, subAtt=None):
        att = getattr(self, attName)
        if att is None:
            return ""
        elif subAtt is not None:
            return ClientHelper.getValForDB(getattr(att, subAtt))
        else:
            return ClientHelper.getValForDB(att)

    def themesToJson(self):
        result = ''
        res = ''
        for t in self.themes:
            i = 0
            tmp = ''
            for att in t.attributes:
                if i == 0:
                    result += '{'
                    result += '"{0}":'.format(att.theme)
                    result += '{'
                tmp += '"{0}": {1},'.format(att.nom, att.valeur)
                i = i+1
            if tmp != '':
                res = tmp[:-1] + '}'
            if len(self.themes) > 1:
                res = tmp[:-1] + ','
        if res != '':
            result += res[:-1] + '}}'
        return result

    def concatenateThemes(self, bDoubleQuote=True):
        """Concatène les noms de tous les thèmes de la remarque
        
        :return:  concaténation des noms de tous les thèmes de la remarque 
        :rtype: string
        """
        result = ""

        for t in self.themes:
            if isinstance(t, Theme):
                result += ClientHelper.getValForDB(t.group.name)

                # attributs du thème
                z = 0
                for att in t.attributes:
                    if z == 0:
                        result += "("
                        z += 1
                    if att.valeur is None:
                        att.valeur = ""
                    if bDoubleQuote:
                        result += ClientHelper.getValForDB(att.nom + "=" + att.valeur + ",")
                    else:
                        tmp = att.nom + "=" + att.valeur + ","
                        result += tmp
                if z > 0:
                    result = result[:-1]
                    result += ")"
                result += "|"

        return result[:-1]

    def isCroquisEmpty(self):
        """True s'il n'y a pas de croquis associé à la remarque. False dans le cas contraire.
        """
        return len(self.croquis) == 0

    def getLongitude(self):
        """Retourne la longitude 
        """
        return self.position.longitude

    def getLatitude(self):
        """Retourne la latitude
        """
        return self.position.latitude

    def getAllDocuments(self):
        """Retourne les documents attachés à la remarque (s'il y en a)
        """
        if len(self.documents) == 0:
            return ""
        else:
            docs = ""
            for i in range(len(self.documents)):
                docs += self.documents[i].text + " "
            return docs[:-1]

    def getAllDocumentsForDisplay(self):
        """Retourne les documents attachés à la remarque (s'il y en a)
        """
        if len(self.documents) == 0:
            return ""
        else:
            docs = []
            for i in range(len(self.documents)):
                doc = self.documents[i].text + "\n"
                docs.append(doc)
        return docs

    def concatenateResponseHTML(self):
        """Crée et retourne la réponse au format html, à partir des réponses existantes pour la remarque
        """
        concatenate = ""

        if len(self.responses) == 0:
            concatenate += "<font color=\"red\">Pas de réponse actuellement pour la remarque n°" + self.id.__str__() + ".</font>"
        else:
            count = len(self.responses)
            for response in self.responses:
                concatenate += "<li><b><font color=\"green\">Réponse n°" + count.__str__()
                count -= 1
                if len(response.author.name) != 0:
                    concatenate += " par " + ClientHelper.notNoneValue(response.author.name)
                if response.date is not None:
                    concatenate += " le " + response.date.strftime("%Y-%m-%d %H:%M:%S")
                if response.status is not None:
                    concatenate += ", " + ConstanteRipart.statutLibelle[
                        ConstanteRipart.getStatuts().index(response.statut.__str__())]
                concatenate += ".</font></b><br/>"

                if response.title() is not None and response.title() != "":
                    concatenate += "<b>" + ClientHelper.notNoneValue(response.title().strip()) + "</b><br/>"
                if response.response is not None:
                    concatenate += ClientHelper.notNoneValue(response.response.strip().replace("\n", "<br/>")) + "</li>"

        return concatenate

    def concatenateResponse(self):
        """Crée et retourne la réponse à partir des réponses existantes pour la remarque
        """
        concatenate = ""

        if len(self.responses) == 0:
            concatenate += "Ce signalement n'a pas reçu de réponses."
        else:
            count = len(self.responses)
            for response in self.responses:
                concatenate += "Réponse n°" + count.__str__()
                count -= 1

                if response.author.name is not None:
                    author_name = response.author.name
                    if len(author_name) != 0:
                        concatenate += " par " + response.author.name
                if response.date is not None:
                    concatenate += " le " + response.date.strftime("%Y-%m-%d %H:%M:%S")

                try:
                    if response.response is not None:
                        concatenate += ".\n" + response.response.strip() + "\n"
                    else:
                        self.logger.error("No message in response " + self.id)
                except Exception as e:
                    self.logger.error(format(e))

        return concatenate

    def setPosition(self, position):
        """ Set de la position de la remarque
        :param position la position de la remarque  (point)
        """
        self.position = position

    def setCommentaire(self, commentaire):
        """Set du commentaire
        :param commentaire le commentaire (message) de la remarque
        """
        self.commentaire = commentaire

    def addDocument(self, document):
        """Ajoute un document à la remarque
        :param document : le document à ajouter à la remarque
        :type document : string
        """
        self.documents.append(document)

    def addCroquis(self, croquis):
        """ Ajoute un croquis à la liste de croquis de la remarque
        
        :param croquis: le croquis 
        :type croquis: Croquis
        """
        self.croquis.append(croquis)

    def addCroquisList(self, listCroquis):
        """Ajoute une liste de croquis à la liste de croquis de la remarque
         
         :param listCroquis: la liste de croquis 
         :type listCroquis: list (de Croquis)
        """
        self.croquis.extend(listCroquis)

    def clearCroquis(self):
        """ Supprime tous les croquis de la liste"""
        self.croquis = []

    def addGeoResponse(self, response):
        """Ajoute une réponse à la remarque
          
        :param response: la réponse
        :type response: GeoResponse
        """
        self.responses.append(response)

    def addThemeList(self, listThemes):
        """Ajoute une liste de thèmes
        
        :param listThemes: la liste de thèmes
        :type listThemes : list (de Theme)
        """
        self.themes.extend(listThemes)
