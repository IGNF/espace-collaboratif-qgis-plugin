# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''

class Point(object):
    '''
    classdocs
    '''
    longitude = None
    latitude = None

    def __init__(self, longitude= None, latitude=None):
        '''
        Constructor
        '''
        self.longitude = longitude 
        self.latitude  = latitude 
        
        
    def isEmpty(self): 
        """
        Teste si le point est vide
        """
        return self.longitude is None or self.latitude is None