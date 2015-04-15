# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''

class Auteur(object):
    '''
    Classe représentant un auteur
    '''
    
    #identifiant de l'auteur
    id=""
    #nom de l'auteur
    nom=""
    

  
        
        
    def __init__(self, id="", nom=""):
        '''
        Constructor
        '''
      
        self.id=id
        self.nom=nom