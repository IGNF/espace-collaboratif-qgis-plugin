# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from _pydev_imps._pydev_xmlrpclib import DateTime
from Groupe import *
from Auteur import *
from ConstanteRipart import *

class GeoReponse(object):
    '''
    classdocs
    '''
    groupe= Groupe()
    
    auteur= Auteur()
    
    reponse =""
    
    date = DateTime()
    
    statut = ConstanteRipart.STATUT.undefined
    
    

    def __init__(self):
        '''
        Constructor
        '''
        
    
    def id(self):
        return self.groupe.id
    
    def titre(self):
        return self.groupe.nom
    
    '''
     TODO
    '''
    def encodeToXML(self):   
        pass
    
    
    
    