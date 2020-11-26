# -*- coding: utf-8 -*-
"""
Created on 25 mai 2020

version 4.0.0

@author: EPeyrouse
"""

from .Groupe import *


class InfosGeogroupe(object):
    """
    Classe représentant les infos du <GEOGROUPE> de l'utilisateur
    """
    # ID & Nom du Geogroupe
    groupe = Groupe()

    # Couches visibles sur les cartes de ce groupe (dans l'ordre dans lequel les superposer)
    layers = []

    def __init__(self, parent=None):
        """
        Constructor
        """
        self.groupe = Groupe()
        self.layers = []
