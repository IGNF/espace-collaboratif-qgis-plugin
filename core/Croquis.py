'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from enum import Enum
from _pydev_imports_tipper import TYPE_ATTR


class Croquis(object):
    '''
    classdocs
    '''
    type = CroquisType.Vide
    nom = None
    attributs = array(Attribut)
    points = array(Point)
    

    def __init__(self, params):
        '''
        Constructor
        '''
        self.type = CroquisType.Vide




class CroquisType(Enum):    
    Vide = 0
    Point    
    Ligne    
    Polygone 
    Texte  
    Fleche   