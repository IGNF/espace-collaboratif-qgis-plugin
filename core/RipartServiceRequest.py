# -*- coding: utf-8 -*-
"""
Created on 26 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""

from .RipartLoggerCl import RipartLogger
from . import requests
from .requests.auth import HTTPBasicAuth


class RipartServiceRequest(object):
    """
    Classe pour les requêtes http vers le service ripart
    """

    logger = RipartLogger("ripart.RipartServiceRequest").getRipartLogger()

    @staticmethod
    def makeHttpRequest(url, authent=None, proxies=None, params=None, data=None, files=None):
        """  Effectue une requête HTTP GET ou POST
        
        :param url: url de base de la requête
        :type url: string
        :param params: paramètres à passer (sous forme de dictionnaire) pour une requête GET
        :type params: Dictionary
        :param data : paramètres pour une requête POST
        :type data: Dictionary
        :param files : fichiers à uploader
        :type files: Dictionary

        :return la réponse du serveur (xml)
        :rtype: string
        """
        try:
            if data is None and files is None:
                r = requests.get(url, auth=HTTPBasicAuth(authent['login'], authent['password']), proxies=proxies,
                                 params=params, verify=False)
            else:
                r = requests.post(url, auth=HTTPBasicAuth(authent['login'], authent['password']), proxies=proxies,
                                  data=data, files=files, verify=False)

            #if not r.text.startswith("<?xml version='1.0' encoding='UTF-8'?>"):
            if r.status_code != 200:
                RipartServiceRequest.logger.error(r.text)
                raise Exception(r.reason)
            
            r.encoding = 'utf-8'
            response = r.text

        except Exception as e:
            RipartServiceRequest.logger.error(format(e))
            raise Exception(u"Connexion impossible.\nVeuillez vérifier les paramètres de connexion\n(Aide>Configurer "
                            u"le plugin.\nErreur : )" + format(e))
        
        return response
