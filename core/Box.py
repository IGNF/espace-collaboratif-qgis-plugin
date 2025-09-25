# -*- coding: utf-8 -*-
"""
Created on 26/11/2018
Updated on 15 dec. 2020

@author: AChang-Wailing, EPeyrouse
"""
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject


class Box(object):
    """
    Classe représentant une boite englobante définie sur deux points.
    """

    def __init__(self, xMin=None, yMin=None, xMax=None, yMax=None) -> None:
        """
        Constructeur à partir de deux points.

        :param xMin: coord X min
        :type xMin: float
        :param yMin: coord Y min
        :type yMin: float
        :param xMax: coord X max
        :type xMax: float
        :param yMax: coord Y max
        :type yMax: float
        """
        if xMin is None or yMin is None or xMax is None or yMax is None:
            raise Exception("Impossible de continuer l'action en cours, la boite englobante de la zone de travail "
                            "n'est pas définie, veuillez importer une zone de travail cohérente.")

        self.__XMin = min(xMin, xMax)
        self.__XMax = max(xMin, xMax)
        self.__YMin = min(yMin, yMax)
        self.__YMax = max(yMin, yMax)

    def getXMin(self) -> float:
        """:return: le X minimum"""
        return self.__XMin

    def getXMax(self) -> float:
        """:return: le X maximum"""
        return self.__XMax

    def getYMin(self) -> float:
        """:return: le Y minimum"""
        return self.__YMin

    def getYMax(self) -> float:
        """:return: le Y maximum"""
        return self.__YMax

    def boxToStringWithSrid(self, sridProject, sridLayer) -> str:
        """
        Transformation des coordonnées en texte avec changement de projection.

        :param sridProject: système de projection source (le projet QGIS)
        :type sridProject: str

        :param sridLayer: système de projection cible (la couche serveur)
        :type sridLayer: str

        :return: les coordonnées de la boite sous la forme : 'XMin,YMin,XMax,YMax'
        """
        crsProject = QgsCoordinateReferenceSystem.fromEpsgId(sridProject)
        crsLayer = QgsCoordinateReferenceSystem.fromEpsgId(sridLayer)
        transformer = QgsCoordinateTransform(crsProject, crsLayer, QgsProject.instance())
        mini = transformer.transform(self.__XMin, self.__YMin)
        maxi = transformer.transform(self.__XMax, self.__YMax)
        strBox = str(mini.x()) + "," + str(mini.y()) + "," + str(maxi.x()) + "," + str(maxi.y())
        return strBox
