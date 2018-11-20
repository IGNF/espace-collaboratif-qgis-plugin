# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''

from builtins import str
from builtins import object
from PyQt5.QtCore import *

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
        
        typeAtt=type(valeur)
        if typeAtt==QDate:
            valeur=valeur.toString('yyyy-MM-dd')
        elif typeAtt==QDateTime:
            valeur=valeur.toString('yyyy-MM-dd hh:mm:ss')
        elif typeAtt!=str:
            valeur=str(valeur)
            
        self.valeur=valeur