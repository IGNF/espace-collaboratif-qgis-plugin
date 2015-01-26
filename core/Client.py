# -*- coding: utf-8 -*-
'''
Created on 22 janv. 2015

@author: AChang-Wailing
'''

import logging
from Point import *
from ConstanteRipart import *
from Groupe import *
from Auteur import *
from Croquis import *
from Theme import *
from GeoReponse import *
from Enum import *
from Remarque import *

class Client:
    '''
    classdocs
    '''
    __url=""
    __login = ""
    __password=""
    __jeton = None
    __auteur = None
    __version = None
    __profil = None
    
    __message = None
    
    __logger=logging.getLogger("ripart.Client")
    
    

    '''
      Constructor
    '''
    def __init__(self, url, login, pwd):
        
        self.__url=url
        self.__login=login
        self.__password=pwd
        self.__message = self.connect()
        
        
    
    def connect(self):
        """
         Connexion d'un utilisateur par son login et mot de passe
         :return: Si la connexion se fait, retourne l'id de l'auteur; sinon retour du message d'erreur
         """
         
        result =None
        
        try:
            
            connectUrl = self.__url + "?action=connect&login=" + self.__login;
            
            __logger.debug("tentative de connexion; " + connectUrl)
            
            data =""
            
        except Exception as e:
            __logger.error(str(e))
        
        return connectUrl