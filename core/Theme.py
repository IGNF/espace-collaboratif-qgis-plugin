# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015
Updated on 27 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""
from .Group import Group


class Theme(object):
    """
    Classe représentant un thème
    """
    def __init__(self):
        """
        Constructor
        """
        self.group = Group()
        self.attributes = []
        self.isFiltered = False
        self.isGlobal = False
