# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from Enum import *
from _pydev_imports_tipper import TYPE_ATTR
from array import *
from Attribut import *
from Point import *


class Croquis(object):
    '''
    classdocs
    '''
    CroquisType = Enum( "Vide","Point","Ligne","Polygone","Texte","Fleche") 
    
    #Type du croquis
    type = CroquisType.Vide
    
    # Nom du croquis
    nom = None
    
    #La liste des attributs (cl�,valeur)
    attributs = list()
    
    #La liste des points composant le croquis (coordonn�es)
    points = list()
    

  

    def __init__(self, nom=None, type=CroquisType.Vide, points=None):
        """
        Constructeur d'un croquis
        
        :param nom: string le nom du croquis
        :param type: CroquisType le type du croquis
        :param points: une liste de points 
        """
        self.nom = nom
        
        self.type = type
        if points is None:
            self.points=list()
        else:
            self.points= points


    def setType(self,type):     
        """
        définit le type
        """
        self.type=type
         
         
         
    def addPoint(self,point):
        """
        Ajoute un point � la liste des points du croquis

        :param point:  un objet Point
        """
        self.points.append(point)
       
       
       

if __name__ == "__main__":
    c= Croquis()
    
    pt= Point(2,3)
    
    print c.CroquisType.Point
    for each in c.CroquisType:
            print 'Day:', each


