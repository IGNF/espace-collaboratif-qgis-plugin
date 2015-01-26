# -*- coding: utf-8 -*-
'''
Created on 22 janv. 2015

@author: AChang-Wailing
'''

import logging

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
    
    logging.basicConfig(filename='example.log',level=logging.DEBUG)

    '''
      Constructor
    '''
    def __init__(self, url, login, pwd):
        
        self.__url=url
        self.__login=login
        self.__password=pwd
        self.__message = self.connect()
        
        
    
    def connect(self):
        result =""
        logging.debug('This message should go to the log file')

        
        connectUrl = self.__url + "?action=connect&login=" + self.__login;
        
        return connectUrl