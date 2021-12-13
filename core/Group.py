# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""


class Group(object):
    """
    Classe représentant un groupe de l'espace collaboratif
    """
    
    # identifiant du groupe
    id = ""
    
    # nom du groupe 
    name = ""

    def __init__(self, id_group="", name=""):
        """
        Constructor
        
        :param id_group identifiant du groupe
        :type string       
        :param name le nom du groupe
        :type string  
        """
        self.id = id_group
        self.name = name
