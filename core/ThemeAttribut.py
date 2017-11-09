# -*- coding: utf-8 -*-
'''
Created on 08/11/2017

@author: AChang-Wailing
'''

from PyQt4.QtCore import *

class ThemeAttribut(object):
    '''
    Classe représentant un attribut d'un thème
    
    '''
    theme=""
    nom=""
    valeur=""

  
        
    def __init__(self, theme="", nom="", valeur=""):
        """
        Constructeur
        
        :param nom: le nom de l'attribut
        :type nom:string
        
        :param valeur: la valeur de l'attribut
        :type valeur:string
        """
        self.theme = theme
        self.nom=nom
        self.valeur=valeur