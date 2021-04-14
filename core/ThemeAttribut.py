# -*- coding: utf-8 -*-
'''
Created on 8 nov. 2017
Updated on 26 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
'''

from PyQt5.QtCore import *


class ThemeAttribut(object):
    """
    Classe représentant un attribut d'un thème
    """
    theme = ""
    tagNom = ""
    tagDisplay = ""
    valeur = ""
    defaultval = None
    valeurs = {}
    type = None
    obligatoire = None

    def __init__(self, theme="", nom="", valeur=""):
        """
        Constructeur
        
        :param nom: le nom de l'attribut
        :type nom:string
        
        :param valeur: la valeur de l'attribut
        :type valeur:string
        """
        self.theme = theme
        self.tagNom = nom
        self.valeur = valeur
        self.valeurs = {}
        self.obligatoire = False

    def addValeur(self, key, value):
        self.valeurs[key] = value

    def setDefaultVal(self, val):
        self.defaultval = val

    def setType(self, attType):
        self.type = attType

    def setObligatoire(self):
        self.obligatoire = True

    def setTagDisplay(self, display):
        self.tagDisplay = display

    def setTagNom(self, nom):
        self.tagNom = nom
