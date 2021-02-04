# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015
Updated on 9 sept. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
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
    filteredThemes = list() # Liste des thèmes filtrés

    #identifiant geoprofil    
    id_Geoprofil=""

    #Les différents groupes de l'utilisateur
    infosGeogroupes = list()

    # La liste des couches Geoportail visible avec la clé geoportail utilisateur
    layersCleGeoportail = {}