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
    
    #identifiant de l'auteur
    id = ""
   
    #nom de l'auteur
    name = ""

    def __init__(self, idAuthor="", name=""):
        """
        Constructeur
  
        :param idAuteur: identifiant de l'auteu r
        :type idAuteur: string
        
        :param nom: nom de l'auteur
        :type nom:string
        """
        self.id = idAuthor
        self.name = name
