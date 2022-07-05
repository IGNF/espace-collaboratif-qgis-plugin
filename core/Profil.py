# -*- coding: utf-8 -*-

"""
Created on 23 janv. 2015
Updated on 9 sept. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""
from .Author import Author
from .Group import Group
from . import ConstanteRipart 


class Profil(object):
    """
    Classe représentant le profil de l'utilisateur
    """

    # Nom de l'auteur
    author = Author()
                        
    # Nom du Geogroupe
    geogroup = Group()
        
    # Titre du Geogroupe
    title = ""

    # Statut (privilèges) du profil
    statut = ""
        
    # Lien vers le logo du profil
    logo = ""

    # Filtre du profil
    filtre = ""

    # La zone géographique de travail du profil
    zone = ConstanteRipart.ZoneGeographique.UNDEFINED

    # Indique si le profil a accès aux groupes privés
    prive = False

    # Les éventuels thèmes attachés au profil
    # Liste des thèmes du profil actif
    themes = list()

    # Liste des noms des thèmes filtrés
    filteredThemes = list()

    # Liste de tous les thèmes du profil de l'utilisateur (issus de tous ses groupes)
    allThemes = list()

    # Liste des noms des thèmes globaux
    globalThemes = list()

    # identifiant geoprofil
    id_Geoprofil = ""

    # Les différents groupes de l'utilisateur
    infosGeogroups = list()
