# -*- coding: utf-8 -*-
"""
Created on 26/11/2018
Updated on 15 dec. 2020

@author: AChang-Wailing, EPeyrouse
"""


class Box(object):
    """
    Représente une boite englobante
    """
    XMin = None
    XMax = None
    YMin = None
    YMax = None

    def __init__(self, xMin=None, yMin=None, xMax=None, yMax=None):
        """
        Constructeur à partir de deux points 
        
        :param xMin coord X min
        :type float
        :param yMin coord y min
        :type float
        :param xMax coord X max
        :type float
        :param yMax coord Y max
        :type float
        """
        if xMin is None or yMin is None or xMax is None or yMax is None:
            self.XMin = None
            self.YMin = None
            self.XMax = None
            self.YMax = None

        else:
            self.XMin = min(xMin, xMax)
            self.XMax = max(xMin, xMax)
            self.YMin = min(yMin, yMax)
            self.YMax = max(yMin, yMax)

    def boxToString(self):
        strBox = str(self.XMin) + "," + str(self.YMin) + "," + str(self.XMax) + "," + str(self.YMax)

        return strBox

    def isEmpty(self):
        """
        Test si la boite est vide 
        """
        return self.XMin is None or self.YMin is None or self.XMax is None or self.YMax is None
