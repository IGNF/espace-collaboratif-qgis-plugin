# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""


class Point(object):
    """
    Classe représentant un Point (Signalement), donné en longitude/latitude
    """
    
    # La longitude (WGS84 en degrés décimaux) du point
    longitude = None
    
    # La latitude (WGS84 en degrés décimaux) du point
    latitude = None

    def __init__(self, lon=None, lat=None):
        """
        Constructeur à partir d'une longitude/latitude
        
        :param lon La longitude (WGS84 en degrés décimaux) du point
        :param lat La latitude (WGS84 en degrés décimaux) du point
        """
        self.longitude = lon
        self.latitude = lat
