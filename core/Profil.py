# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''

from Auteur import *
from Groupe import *
from ConstanteRipart import *
from Theme import *


class Profil(object):
    '''
    classdocs
    '''
    
    
    #Nom de l'auteur   
    auteur=Auteur()
                        
    #Nom du Geogroupe    
    geogroupe= Groupe()
        
    #Titre du Geogroupe   
    titre=""
        
        
    #Statut (privil�ges) du profil        
    statut=""
        
    #Lien vers le logo du profil
    logo=""

        
    #Filtre du profil       
    filtre=""
        
    #La zone g�ographique de travail du profil        
    zone= ConstanteRipart.ZoneGeographique.UNDEFINED

        
    #Indique si le profil a acces aux groupes prives
    prive = False

        
    #Les �ventuels th�mes attach�s au profil      
    themes = list()

        
    #identifiant geoprofil    
    id_Geoprofil=""


    