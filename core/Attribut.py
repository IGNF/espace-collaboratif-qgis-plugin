# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''

class Attribut(object):
    '''
    Classe repr�sentant un attribut (d'un croquis)
    sous forme nom/valeur
    '''
    nom=""
    valeur=""

    def __init__(self):
        '''
        Constructor
        '''
        
    def __init__(self, nom, valeur):
        self.nom=nom
        self.valeur=valeur