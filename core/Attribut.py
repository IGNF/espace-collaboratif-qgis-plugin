# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''

class Attribut(object):
    '''
    Classe représentant un attribut (d'un croquis)
    sous forme nom/valeur
    '''
    nom=""
    valeur=""

  
        
    def __init__(self, nom="", valeur=""):
        """
        Constructeur
        
        :param nom: le nom de l'attribut
        :type nom:string
        :param valeur: la valeur de l'attribut
        :type valeur:string
        """
        self.nom=nom
        self.valeur=valeur