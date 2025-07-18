# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""
from .Enum import Enum


class Sketch(object):
    """
    Classe représentant un croquis
    """
    '''
    Vide : pas de croquis
    Point : un point du croquis
    Ligne : une polyligne du croquis
    Polygone : un polygone simple (sans trous et non multiple) du croquis.
    Texte : un champ texte du croquis
    Fleche : une flêche du croquis
    '''
    sketchType = Enum("Vide", "Point", "Ligne", "Polygone", "Texte", "Fleche")
    typeToStr = {sketchType.Point: 'Point', sketchType.Texte: 'Texte', sketchType.Ligne: 'Ligne',
                 sketchType.Fleche: 'Fleche', sketchType.Polygone: 'Polygone'}
    typeToWKT = {sketchType.Point: 'POINT', sketchType.Texte: 'POINT', sketchType.Ligne: 'LINESTRING',
                 sketchType.Fleche: 'LINESTRING', sketchType.Polygone: 'POLYGON'}

    def __init__(self) -> None:
        # Type du croquis
        self.type = self.sketchType.Vide

        # Nom du croquis
        self.name = ""

        # La liste des attributs (clé, valeur)
        self.attributesList = list()

        # La liste des points composants le croquis (coordonnées)
        self.__points = list()

        self.coordinates = ""

    def getAllPoints(self) -> list:
        return self.__points

    def addPoint(self, point) -> None:
        """
        Ajoute un point à la liste des points du croquis

        :param point:  un objet Point
        """
        self.__points.append(point)

    def addAttribut(self, attribute) -> None:
        """Ajoute un attribut à la liste des attributs du croquis
        
        :param attribute : l'objet Attribut
        :type attribute: Attribute
        """
        self.attributesList.append(attribute)

    def getAttributes(self) -> dict:
        attributes = {}
        for attribute in self.attributesList:
            attributes[attribute.name] = attribute.value
        return attributes

    def getPoint(self, i):
        """Recherche un point dans la liste de Points par sa position dans la liste
         
        :param i: la position du point à trouver
        :type i: int
        
        :return le point cherché
        :rtype Point
        """
        return self.__points[i]

    def longitude(self, i) -> float:
        """Retourne la longitude pour le point i
        
        :param i: l'index du point dans la liste
        :type i: int
        
        :return la longitude
        :rtype float
        """
        return self.getPoint(i).longitude

    def latitude(self, i) -> float:
        """Retourne la latitude pour le point i
        
        :param i: l'index du point dans la liste
        :type i: int
        
        :return la latitude
        :rtype float
        """
        return self.getPoint(i).latitude

    def firstCoord(self):
        """Retourne le premier point de la liste
        
        :return le premier point
        :rtype Point
        """
        if len(self.__points) > 0:
            return self.__points[0]
        else:
            return None

    def lastCoord(self):
        """Retourne le dernier point de la liste
        
        :return le dernier point
        :rtype Point
        """
        if len(self.__points) > 0:
            return self.__points[-1]
        else:
            return None

    def isValid(self) -> bool:
        """Contrôle la validité de la géométrie
        """
        nPoints = len(self.__points)
        if nPoints == 0 \
                or ((self.type == self.sketchType.Point or self.type == self.sketchType.Texte) and nPoints != 1) \
                or (self.type == self.sketchType.Polygone and not self.firstCoord().eq(self.lastCoord())) \
                or (self.type == self.sketchType.Vide and nPoints > 0):
            return False
        return True

    def getCoordinatesFromPointsToPost(self) -> str:
        coord = ""
        for pt in self.__points:
            coord += str(pt.longitude) + " " + str(pt.latitude) + ", "
        if self.type not in self.typeToWKT:
            return ''
        # Cas particulier pour les polygones
        if self.type == self.sketchType.Polygone:
            geometryWKT = '{0}(({1}))'.format(self.typeToWKT[self.type], coord[:-2])
        else:
            geometryWKT = '{0}({1})'.format(self.typeToWKT[self.type], coord[:-2])
        return geometryWKT

    def getTypeEnumInStr(self, typeEnum) -> str:
        return self.typeToStr[typeEnum]
