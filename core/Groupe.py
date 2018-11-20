# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''

from builtins import object
class Groupe(object):
    """
    Classe représentant un groupe Ripart
    """
    
    # identifiant du groupe
    id=""
    
    # nom du groupe 
    nom=""

        
    def __init__(self, idGroup="" , nom=""):
        """
        Constructor
        
        :param idGroup identifiant du groupe
        :type string       
        :param nom le nom du groupe
        :type string  
        """
        self.id=idGroup
        self.nom=nom
        