# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0, 26/11/2018

@author: AChang-Wailing
"""
from PyQt5.QtCore import QDate, QDateTime


class SketchAttributes(object):
    """
    Classe représentant un attribut (d'un croquis)
    sous forme nom/valeur
    """
    name = ""
    value = ""

    def __init__(self, name="", value=""):
        """
        Constructeur
        
        :param name: le nom de l'attribut
        :type name:string
        
        :param value: la valeur de l'attribut
        :type value:string
        """
        self.name = name

        typeAtt = type(value)
        if typeAtt == QDate:
            value = value.toString('yyyy-MM-dd')
        elif typeAtt == QDateTime:
            value = value.toString('yyyy-MM-dd hh:mm:ss')
        elif typeAtt != str:
            value = str(value)

        self.value = value
