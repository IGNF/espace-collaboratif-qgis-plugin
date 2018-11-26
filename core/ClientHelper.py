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
    def stringToStringType(val):
        """Retourne un string à partir d'un texte unicode ou string
        """
        if val==None:
            return ""

        #elif type(val)==type('str'):
            #return val
        else :
            #return val.encode('utf-8');
            return val
    
    @staticmethod
    def getEncodeType(val):
        """Retourne une valeur unicode à partir d'un texte (unicode ou string)
        """
        
        if val==None:
            return ""
        #elif type(val)==type('str'):
        #   return val.decode('utf8')
        else :
            return val
        
    @staticmethod
    def getValForDB(val):
        val=ClientHelper.stringToStringType(val)
        val=val.replace("'","''")
        val=val.replace('"','""')
        return val
        
        
    @staticmethod
    def getErrorMessage(code):
        if code == 401:
            return ClientHelper.stringToStringType('Login et/ou mot de passe erroné(s)')
        elif code =="no_profile":
            return ClientHelper.stringToStringType("Accès refusé. Pas de profil actif.")
        else:
            return ClientHelper.stringToStringType("Impossible d'accéder au service Ripart") 
                           
 
    
    @staticmethod
    def notNoneValue(val):
        """Retourne une chaine vide si le paramètre = None
        """
        if val ==None:
            return ""
        else: 
            return val