'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from _pydev_imps._pydev_xmlrpclib import DateTime

class GeoReponse(object):
    '''
    classdocs
    '''
    groupe= Groupe()
    
    auteur= Auteur()
    
    reponse = Reponse()
    
    date = DateTime()
    
    statut = Statut()
    
    

    def __init__(self, params):
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
    
    
    
    