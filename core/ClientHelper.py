# -*- coding: utf-8 -*-
'''
Created on 30 sept. 2015

version 3.0.0, 26/11/2018

@author: AChang-Wailing
'''

class ClientHelper(object):
    '''
    Méthodes utiles
    '''

    @staticmethod
    def getValForDB(val):
        val=ClientHelper.notNoneValue(val)
        val=val.replace("'","''")
        val=val.replace('"','""')
        return val
        
        
    @staticmethod
    def getErrorMessage(code):
        if code == 401:
            return ClientHelper.notNoneValue('Login et/ou mot de passe erroné(s)')
        elif code =="no_profile":
            return ClientHelper.notNoneValue("Accès refusé. Pas de profil actif.")
        else:
            return ClientHelper.notNoneValue("Impossible d'accéder à l'Espace Collaboratif") 
                           
 
    
    @staticmethod
    def notNoneValue(val):
        """Retourne une chaine vide si le paramètre = None
        """
        if val ==None:
            return ""
        else: 
            return val