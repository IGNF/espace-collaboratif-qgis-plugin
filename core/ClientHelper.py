# -*- coding: utf-8 -*-
'''
Created on 30 sept. 2015

@author: AChang-Wailing
'''


class ClientHelper(object):
    '''
    classdocs
    '''


    @staticmethod
    def stringToStringType(val):
        
        if val==None:
            return ""

        elif type(val)==type('str'):
            return val
        else :
            return val.encode('utf-8');
    
    @staticmethod
    def getEncodeType(val):
        
        if val==None:
            return u""
        elif type(val)==type('str'):
            return val.decode('utf8')
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
        if code in ['bad_login','bad_pass']:
            return ClientHelper.stringToStringType('Login et/ou mot de passe erroné(s)')
        elif code =="no_group":
            return ClientHelper.stringToStringType("Accès refusé. L'utilisateur n'appartient à aucun groupe.")
        else:
            return code
        
        return code
    
    
    @staticmethod
    def notNoneValue(val):
        if val ==None:
            return ""
        else: 
            return val