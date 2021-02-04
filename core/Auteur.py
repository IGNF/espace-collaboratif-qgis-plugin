# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

version 3.0.0, 26/11/2018

@author: AChang-Wailing
'''

class Auteur(object):
    """
    Classe représentant un auteur
    """
    
    #identifiant de l'auteur
    id=""
   
    #nom de l'auteur
    nom=""
     
        
    def __init__(self, idAuteur="", nom=""):
        """
        Constructeur
  
        :param idAuteur: identifiant de l'auteu r
        :type idAuteur: string
        
        :param nom: nom de l'auteur
        :type nom:string
        """
        self.id=idAuteur
        self.nom=nom