# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from __future__ import absolute_import
from builtins import object
from .Groupe import *

class Theme(object):
    """
    Classe représentant un thème
    """
    
    groupe= Groupe()
    
    #liste d'attributs
    attributs=[]

    def __init__(self, params= None):
        """
        Constructor
        """
        self.groupe=Groupe()
        self.attributs= []