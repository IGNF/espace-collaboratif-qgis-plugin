# -*- coding: utf-8 -*-
"""
Created on 25 may 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""

from .Group import Group


class InfosGeogroup(object):
    """
    Classe représentant les infos du <GEOGROUPE> de l'utilisateur
    """
    # ID & Nom du Geogroupe
    group = Group()

    # Couches visibles sur les cartes de ce groupe (dans l'ordre dans lequel les superposer)
    layers = []

    # Thèmes du groupe
    themes = []

    def __init__(self):
        """
        Constructor
        """
        self.group = Group()
        self.layers = []
        self.themes = []
        self.filteredThemes = []
        self.georemComment = ""
