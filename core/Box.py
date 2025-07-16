# -*- coding: utf-8 -*-
"""
Created on 26/11/2018
Updated on 15 dec. 2020

@author: AChang-Wailing, EPeyrouse
"""
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject


# Représente une boite englobante
class Box(object):

    def __init__(self, xMin=None, yMin=None, xMax=None, yMax=None) -> None:
        """
        Constructeur à partir de deux points
        :param xMin coord X min
        :param yMin coord y min
        :param xMax coord X max
        :param yMax coord Y max
        """
        if xMin is None or yMin is None or xMax is None or yMax is None:
            raise Exception("Impossible de continuer l'action en cours, la boite englobante de la zone de travail "
                            "n'est pas définie, veuillez importer une zone de travail cohérente.")

        self.__XMin = min(xMin, xMax)
        self.__XMax = max(xMin, xMax)
        self.__YMin = min(yMin, yMax)
        self.__YMax = max(yMin, yMax)

    def getXMin(self) -> float:
        return self.__XMin

    def getXMax(self) -> float:
        return self.__XMax

    def getYMin(self) -> float:
        return self.__YMin

    def getYMax(self) -> float:
        return self.__YMax

    def boxToStringWithSrid(self, sridProject, sridLayer) -> str:
        crsProject = QgsCoordinateReferenceSystem(sridProject)
        crsLayer = QgsCoordinateReferenceSystem(sridLayer)
        transformer = QgsCoordinateTransform(crsProject, crsLayer, QgsProject.instance())
        mini = transformer.transform(self.__XMin, self.__YMin)
        maxi = transformer.transform(self.__XMax, self.__YMax)
        strBox = str(mini.x()) + "," + str(mini.y()) + "," + str(maxi.x()) + "," + str(maxi.y())
        return strBox
