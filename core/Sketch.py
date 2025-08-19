# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""
from .Enum import Enum
from .Point import Point


class Sketch(object):
    """
    Classe représentant un croquis. Un croquis est toujours lié à un signalement. Il apporte une précision
    sur le pourquoi de la création d'un signalement.
    Les croquis peuvent être de type :
     - Vide : pas de croquis
     - Point : un point du croquis
     - Ligne : une polyligne du croquis
     - Polygone : un polygone simple (sans trous et non multiple) du croquis.
     - Texte : un champ texte du croquis
     - Fleche : une flêche du croquis
    """
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
        """
        :returns: la liste de points de type Point constituant le croquis
        """
        return self.__points

    def addPoint(self, point) -> None:
        """
        Ajoute un point à la liste des points du croquis.

        :param point:  un objet Point
        """
        self.__points.append(point)

    def addAttribut(self, attribute) -> None:
        """
        Ajoute un attribut à la liste des attributs du croquis.
        
        :param attribute: l'objet Attribut
        :type attribute: Attribute
        """
        self.attributesList.append(attribute)

    def getAttributes(self) -> dict:
        """
        :return: les attributs du croquis sous la forme [nom, valeur]
        """
        attributes = {}
        for attribute in self.attributesList:
            attributes[attribute.name] = attribute.value
        return attributes

    def getPoint(self, i) -> Point:
        """
        Recherche un point par sa position dans la liste de points du croquis.
         
        :param i: l'indice du point à trouver
        :type i: int
        
        :return: le point cherché
        """
        return self.__points[i]

    def longitude(self, i) -> float:
        """
        :param i: l'index du point dans la liste
        :type i: int
        
        :return: la longitude pour le point d'indice i
        """
        return self.getPoint(i).getLongitude()

    def latitude(self, i) -> float:
        """
        :param i: l'index du point dans la liste
        :type i: int
        
        :return: la latitude pour le point d'indice i
        """
        return self.getPoint(i).getLatitude()

    def firstCoord(self) -> Point:
        """
        :return: le premier point de la liste
        """
        if len(self.__points) > 0:
            return self.__points[0]
        else:
            return Point()

    def lastCoord(self) -> Point:
        """
        :return: le dernier point de la liste
        """
        if len(self.__points) > 0:
            return self.__points[-1]
        else:
            return Point()

    def isValid(self) -> bool:
        """
        Contrôle la validité de la géométrie pour un type de croquis.
         - coordonnées différentes de None
         - nombre de points différent de 0
         - Point ou Texte : nombre de points égal à 1
         - Polygone : premier et dernier point égal
         - Vide : nombre de points égal à 0

        :return: False, si la géométrie n'est pas conforme
        """
        nPoints = len(self.__points)
        if nPoints == 0 \
                or self.firstCoord().isNone() \
                or ((self.type == self.sketchType.Point or self.type == self.sketchType.Texte) and nPoints != 1) \
                or (self.type == self.sketchType.Polygone and not self.firstCoord().isValid()
                    or self.lastCoord().isValid()) \
                or (self.type == self.sketchType.Vide and nPoints > 0):
            return False
        return True

    def getCoordinatesFromPointsToPost(self) -> str:
        """
        Transforme la géométrie WGS84 en géométrie WKT compatible QGIS.

        :return: la géométrie du croquis au format WKT
        """
        coord = ""
        for pt in self.__points:
            coord += str(pt.getLongitude()) + " " + str(pt.getLatitude()) + ", "
        if self.type not in self.typeToWKT:
            return ''
        # Cas particulier pour les polygones
        if self.type == self.sketchType.Polygone:
            geometryWKT = '{0}(({1}))'.format(self.typeToWKT[self.type], coord[:-2])
        else:
            geometryWKT = '{0}({1})'.format(self.typeToWKT[self.type], coord[:-2])
        return geometryWKT

    def getTypeEnumInStr(self, typeEnum) -> str:
        """
        :return: le type de croquis sous forme texte
        """
        return self.typeToStr[typeEnum]
