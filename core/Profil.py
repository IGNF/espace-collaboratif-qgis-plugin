# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015
Modified on 29 mai 2020
version 3.0.0 , 26/11/2018

@author: AChang-Wailing
@author: EPeyrouse
'''

from .Auteur import *
from .InfosGeogroupe import *
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

    #Les éventuels thèmes attachés au profil
    themes = list()

    #identifiant geoprofil    
    id_Geoprofil=""

    #Les différents groupes de l'utilisateur
    infosGeogroupes = list()

    # La liste des couches Geoportail visible avec la clé geoportail utilisateur
    layersCleGeoportail = []