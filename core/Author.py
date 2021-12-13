# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0, 26/11/2018

@author: AChang-Wailing
"""


class Author(object):
    """
    Classe représentant un auteur
    """
    
    # identifiant de l'auteur
    id = ""
   
    # nom de l'auteur
    name = ""

    def __init__(self, id_author="", name=""):
        """
        Constructeur
  
        :param id_author: identifiant de l'auteu r
        :type id_author: string
        
        :param name: nom de l'auteur
        :type name:string
        """
        self.id = id_author
        self.name = name
