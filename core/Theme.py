# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
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
        #self.isFiltered = False
        self.isFiltered = True
