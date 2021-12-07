# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""

from datetime import datetime
import xml.etree.cElementTree as et
from .Groupe import Groupe
from .Author import Author
from . import ConstanteRipart


class GeoReponse(object):
    """
    Classe pour définir un objet réponse de Ripart.
    """
    #Groupe contenant l'Id et le titre de l'object GeoReponse
    groupe= Groupe()
    
    # L'auteur de la réponse
    auteur= Author()
    
    # La réponse incluse dans l'object GeoReponse
    reponse =""
    
    # La date de la réponse
    date = datetime.now()
    
    # Le statut de la GeoReponse
    statut = ConstanteRipart.STATUT.undefined

    
    
    def __init__(self):
        '''
        Constructor
        '''
        self.groupe=Groupe()
        self.auteur=Author()
        self.reponse= ""
        self.date = datetime.now()
        self.statut=ConstanteRipart.STATUT.undefined
    
         
    def id(self):
        """
        Retourne l'id de la GeoReponse 
        """
        return self.groupe.id
    
    
    def titre(self):
        """
        Retourne le titre de la GeoReponse 
        """
        return self.groupe.nom
    
 
    def encodeToXML(self): 
        """
        Retourne la réponse au format xml
        """
        sxml  ="<GEOREP>"
        sxml +="<ID_GEOREP>" +self.id() + "</ID_GEOREP>"
        sxml += "<ID_AUTEUR>"+self.auteur.id.__str__()+"</ID_AUTEUR>"
        sxml +="<AUTEUR>"+self.auteur.nom+"</AUTEUR>"
        sxml +="<TITRE>"+self.titre()+"</TITRE>"
        sxml +="<STATUT>"+self.statut.__str__()+"</STATUT>"
        sxml +="<DATE>"+self.date.strftime("%Y-%m-%d %H:%M:%S")+"</DATE>"
        sxml +="<REPONSE>"+self.reponse+"</REPONSE>"   
        sxml +="</GEOREP>"   
  
        tree= et.fromstring(sxml)
        
        return tree
      

    
    
    