# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""


class Point(object):
    """
    Classe représentant un Point (Signalement), donné en longitude/latitude.
    """

    def __init__(self, lon=None, lat=None) -> None:
        """
        Définit un point à partir d'une longitude/latitude.
        
        :param lon: longitude du point (WGS84 en degrés décimaux)
        :type lon: float

        :param lat: latitude du point (WGS84 en degrés décimaux)
        :type lat: float
        """

        # La longitude (WGS84 en degrés décimaux) du point
        self.__longitude = lon
        # La latitude (WGS84 en degrés décimaux) du point
        self.__latitude = lat

    def getLongitude(self) -> float:
        """
        :return: la longitude
        """
        return self.__longitude

    def getLatitude(self) -> float:
        """
        :return: la latitude
        """
        return self.__latitude

    def isValid(self) -> bool:
        """
        :return: False, si le premier point n'est pas égal au dernier point
        """
        if self.__longitude != self.__latitude:
            return False

    def isNone(self) -> bool:
        """
        :return: True, si les coordonnées sont à None
        """
        if self.__latitude is None and self.__longitude is None:
            return True
