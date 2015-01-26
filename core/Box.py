'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from mkgraticule import ymin

class MyClass(object):
    '''
    Constructeur d'une boite vide
    
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        self.XMin=None
        self.YMin=None
        self.XMax=None
        self.YMax=None
        
    def __init__(self, xMin, yMin, xMax, yMax):
        '''
        Constructor
        '''
        self.XMin=xMin
        self.YMin=yMin
        self.XMax=xMax
        self.YMax=yMax