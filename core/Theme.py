# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015
Updated on 27 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""

from .Groupe import *


class Theme(object):
    """
    Classe représentant un thème
    """
    
    groupe = Groupe()
    
    #liste d'attributs
    attributs = []

    def __init__(self, params= None):
        """
        Constructor
        """
        self.groupe = Groupe()
        self.attributs = []
        self.isFiltered = False
        #self.isFiltered = True
