# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''

from Point import *
from ConstanteRipart import *
from Groupe import *
from Auteur import *
from Croquis import *
from Theme import *
from GeoReponse import *
from Enum import *

class Remarque(object):
    '''
    classdocs
    '''
    #Identifiant de la remarque
    id = None
    
    # Url vers la remarque sur le site  web  publicde Ripart
    lien =""
    
    #Url vers la partie privée du site web de Ripart
    lienPrive=""
    
    # date de création de la remarque Ripart
    dateCreation = None
    
    # date de mise-à-jour de la remarque Ripart
    dateMiseAJour = None
    
    #date de validation de la remarque Ripart
    dateValidation = None
    
    #position de la remarque ripart (lon/lat)
    position = Point()
    
    #statut de la remarque
    statut= ConstanteRipart.STATUT.undefined
    
    #département de la remarque (indicatif + nom)
    departement=""
    
    #commune de la remarque
    commune=""
    
    #auteur de la remarque
    auteur = Auteur()
    
    
    #Définit les droits d'action de l'utilisateur en cours sur la remarque Ripart
    autorisation=""
 
    #
    id_partition=""
    
    # groupe sous lequel l'auteur a crée la remarque Ripart 
    groupe= Groupe()
    
    # réponses de la remarque Ripart
    reponses = list()
    
    # croquis de la remarque  list(Croquis)
    croquis = list()
    
    
    #documents attachés à la remarque  (liste de string)
    documents= list()
    
    
    #thèmes attachés à la remarque  list(Theme)
    themes = list()
    
    #
    hash= ""
    

    def __init__(self):
        '''
        Constructor
        '''
        
    def concatenateThemes(self):
        """
        Concat�ne les noms de tous les th�mes de la remarque
        :return:  concat�ation des noms de tous les th�mes de la remarque 
        """
        result=""
        
        for t in self.themes:
            if isinstance(t, Theme):           
                result += t.groupe.nom
                
        return result         
                
                
    def isCroquisEmpty(self):
         return len(self.croquis) == 0
     
     
    def getAuteurNom(self):
         return self.auteur.nom
                
     
    def getAuteurId(self):   
         return self.auteur.id
     
     
    def getLongitude(self):
         this.position.longitude
         
    def getLatitude(self):
         this.position.latitude
         
    def getFirstDocument(self):
         if len(self.documents)==0 :
             return ""
         else :
             return self.documents[0]
         
         
             
                
                
if __name__ == "__main__":
    rem = Remarque()
    th = Theme()
    th.groupe= Groupe("10","themaA")
    rem.themes.append(th)
    th2= Theme()
    th2.groupe= Groupe("11","themaB")
    rem.themes.append(th2)
    
    print rem.concatenateThemes()
        