# -*- coding: utf-8 -*-
"""
Created on 25 may 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""
from .Group import Group

"""
    Classe représentant les infos du groupe ,auquel appartient l'utilisateur
"""


class InfosGeogroup(object):

    def __init__(self):
        # ID & Nom du Geogroupe
        self.group = Group()
        # Le nom est mis vide par défaut
        self.group.name = ''
        # La liste des couches visibles sur les cartes de ce groupe (dans l'ordre dans lequel les superposer)
        self.layers = []
        # Les thèmes particuliers appartenant au groupe pour faciliter la saisie des thèmes d'un signalement
        self.themes = []
        # Les thèmes filtrés par l'utilisateur pour son groupe qui peuvent appartenir à d'autres groupes
        # pour faciliter la saisie des thèmes d'un signalement
        self.filteredThemes = []
        # Commentaire par défaut des signalements
        self.reportDefaultComment = ""
