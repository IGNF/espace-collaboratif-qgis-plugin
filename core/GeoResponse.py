# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""
from datetime import datetime
import xml.etree.cElementTree as ET
from .Group import Group
from .Author import Author
from . import Constantes


class GeoResponse(object):
    """
    Classe pour définir un objet réponse de Ripart.
    """
    # Groupe contenant l'Id et le titre de l'object GeoResponse
    group = None
    
    # L'auteur de la réponse
    author = None
    
    # La réponse incluse dans l'object GeoResponse
    response = None
    
    # La date de la réponse
    date = None
    
    # Le statut de la GeoResponse
    status = None

    def __init__(self):
        self.group = Group()
        self.author = Author()
        self.response = ""
        self.date = datetime.now()
        self.status = Constantes.STATUT.undefined

    def id(self):
        """
        Retourne l'id de la GeoResponse
        """
        return self.group.getId()

    def title(self):
        """
        Retourne le titre de la GeoResponse
        """
        return self.group.getName()

    def encodeToXML(self): 
        """
        Retourne la réponse au format xml
        """
        sxml = "<GEOREP>"
        sxml += "<ID_GEOREP>{0}</ID_GEOREP>".format(self.id())
        sxml += "<ID_AUTEUR>{0}</ID_AUTEUR>".format(self.author.id.__str__())
        sxml += "<AUTEUR>{0}</AUTEUR>".format(self.author.name)
        sxml += "<TITRE>{0}</TITRE>".format(self.title())
        sxml += "<STATUT>{0}</STATUT>".format(self.status.__str__())
        sxml += "<DATE>{0}</DATE>".format(self.date.strftime("%Y-%m-%d %H:%M:%S"))
        sxml += "<REPONSE>{0}</REPONSE>".format(self.response)
        sxml += "</GEOREP>"
        tree = ET.fromstring(sxml)
        return tree
