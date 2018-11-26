# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
'''


class Point(object):
    """
    Classe représentant un Point Ripart, donné en longitude/latitude
    """
    
    # La longitude (WGS84 en degrés décimaux) du point
    longitude = None
    
    # La latitude (WGS84 en degrés décimaux) du point
    latitude = None

    def __init__(self, lon= None, lat=None):
        """
        Constructeur à partir d'une longitude/latitude
        
        :param lon  La longitude (WGS84 en degrés décimaux) du point
        :type float
        :param lat  La latitude (WGS84 en degrés décimaux) du point
        :type float
        """
        self.longitude = lon
        self.latitude  = lat
        
        
    def isEmpty(self): 
        """
        Teste si le point est vide
        """
        return self.longitude is None or self.latitude is None
    
    def eq(self,b):
        if (self.longitude == b.longitude and self.latitude==b.latitude):
            return True
        else :
            return False
    
    
"""if __name__ == "__main__":
    
    a=Point(1,2)
    b=Point(2.1,3)
    
    c= Point(1,2)
    r= a.eq( b)
    
    print r
    print a.eq(c)
    
    print a.isEmpty()
    
    print Point().isEmpty()
"""