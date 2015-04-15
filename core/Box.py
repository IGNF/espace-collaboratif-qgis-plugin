# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''


class Box(object):
    '''
    Représente une boite englobante
    
    '''

    XMin=None
    XMax=None
    YMin=None
    YMax=None
  
    
    
    def __init__(self, xMin=None, yMin=None, xMax=None, yMax=None):
        """
        Constructeur à partir de deux points 
        """
        if xMin is None or yMin is None or xMax is None or yMax is None:
            self.XMin=None
            self.YMin=None
            self.XMax=None
            self.YMax=None
            
        else:                   
            self.XMin=min(xMin,xMax)
            self.XMax=max(xMin,xMax)
                
            self.YMin=min(yMin,yMax)
            self.YMax=max(yMin,yMax)
        