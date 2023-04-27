# -*- coding: utf-8 -*-
"""
Created on 8 nov. 2017
Updated on 26 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""


class ThemeAttributes(object):
    """
    Classe représentant un attribut d'un thème
    """

    def __init__(self, theme="", name="", value=""):
        """
        Constructeur
        
        :param nom: le nom de l'attribut
        :type nom:string
        
        :param valeur: la valeur de l'attribut
        :type valeur:string
        """
        self.__theme = theme
        self.__name = name
        self.__value = value
        self.__defaultValue = None
        self.__values = []
        self.__type = None
        self.__mandatory = False

    def setType(self, attType):
        self.__type = attType

    def setMandatory(self):
        self.__mandatory = True

    def setTagDisplay(self, display):
        self.__tagDisplay = display

    def setDefaultValue(self, defaultValue):
        self.__defaultValue = defaultValue

    def setValues(self, values):
        x = values.split('|')
        for value in x:
            self.__values.append(value)
