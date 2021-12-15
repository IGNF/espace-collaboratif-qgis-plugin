# -*- coding: utf-8 -*-
"""
Created on 30 sept. 2015
Updated on 15 dec. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse
"""


class ClientHelper(object):
    """
    Méthodes utiles
    """
    @staticmethod
    def getValForDB(val):
        valForDB = ''
        if type(val) is list:
            for tmp in val:
                valForDB = ClientHelper.notNoneValue(tmp)
                valForDB = valForDB.replace("'", "''")
                valForDB = valForDB.replace('"', '""')
        else:
            valForDB = ClientHelper.notNoneValue(val)
            valForDB = valForDB.replace("'", "''")
            valForDB = valForDB.replace('"', '""')
        return valForDB

    @staticmethod
    def getErrorMessage(code):
        if code == 401:
            return ClientHelper.notNoneValue('Login et/ou mot de passe erroné(s)')
        elif code == "no_profile":
            return ClientHelper.notNoneValue("Accès refusé. Pas de profil actif.")
        else:
            return ClientHelper.notNoneValue("Impossible d'accéder à l'Espace Collaboratif") 

    @staticmethod
    def notNoneValue(val):
        """Retourne une chaine vide si le paramètre = None
        """
        if val is None:
            return ""
        else: 
            return val
