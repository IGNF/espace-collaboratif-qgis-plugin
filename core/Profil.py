# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
'''

from .Auteur import *
from .Groupe import Groupe
from . import ConstanteRipart 


class Profil(object):
    """
    Classe représentant le profil de l'utilisateur
    """
  
    
    #Nom de l'auteur   
    auteur=Auteur()
                        
    #Nom du Geogroupe    
    geogroupe= Groupe()
        
    #Titre du Geogroupe   
    titre=""
        
        
    #Statut (privilèges) du profil        
    statut=""
        
    #Lien vers le logo du profil
    logo=""

        
    #Filtre du profil       
    filtre=""
        
    #La zone géographique de travail du profil        
    zone= ConstanteRipart.ZoneGeographique.UNDEFINED

        
    #Indique si le profil a accès aux groupes privés
    prive = False

        
    #Les éventuels thèmes attacés au profil      
    themes = list()

        
    #identifiant geoprofil    
    id_Geoprofil=""

   
    