# -*- coding: utf-8 -*-

'''
Created on 22 janv. 2015

@author: AChang-Wailing
'''

import logging
import RipartLogger
from Point import *
import ConstanteRipart
from Groupe import *
from Auteur import *
from Croquis import *
from Theme import *
from GeoReponse import *
from Enum import *
from Remarque import *
from RipartServiceRequest import *
from XMLResponse import *
import hashlib
import re
import time
from pydev_console_utils import Null
from Box import *

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
    
    message = None
    
    logger=logging.getLogger("ripart.client")
    
   
    

    '''
      Constructor
    '''
    def __init__(self, url, login, pwd):
        
        self.__url=url
        self.__login=login
        self.__password=pwd
        self.message = self.connect()
        
        
    """
    Connexion d'un utilisateur par son login et mot de passe
    :return: Si la connexion se fait, retourne l'id de l'auteur; sinon retour du message d'erreur
    """     
    def connect(self):
        
        result =None
        
        try:
                     
            self.logger.debug("tentative de connexion; " + self.__url + ' connect ' + self.__login)
            
            
            data =RipartServiceRequest.makeGetRequest(self.__url, {'action':'connect','login':self.__login})
            
            xmlResponse = XMLResponse(data)
            
            errMessage = xmlResponse.checkResponseValidity()
            
            if (errMessage['code']=='OK'):
                self.logger.debug('connect �tape OK')
                result = self.connect2(xmlResponse)
       
                self.__version= xmlResponse.getVersion()
                 
        except Exception as e:
            self.logger.error(str(e))
        
        return result
    
    
    
    """
    Deuxième requête pour la connexion 
    """
    def connect2(self,xml):
        
        result= None
        
        errMessage = xml.checkResponseValidity()
        aleas = xml.getAleas()
        
        if len(aleas)<2:
            raise Exception('Connexion impossible')
        
        else:
            alea1 = aleas[0]
            alea2 = aleas[1]
            
            parameters = {}
            
            parameters['action']='connect'
            parameters['login']=self.__login
            parameters['session_password_md5']= Client.getMD5Hash(alea1+self.__password)
            parameters['next_session_password_md5']= Client.getMD5Hash(alea2+self.__password)
            
            data= RipartServiceRequest.makeGetRequest(self.__url, parameters)
            xmlResponse = XMLResponse(data)
            errMessage = xmlResponse.checkResponseValidity()
            
            
            if errMessage['code'] =='OK':
                self.logger.debug("connect étape 2 ok")
                connectValues = xmlResponse.getConnectValues()
                   
                self.__auteur = Auteur(connectValues['ID_AUTEUR'], self.__login)
                self.__jeton= connectValues['JETON']
                
                result =connectValues['ID_AUTEUR']
                
            else:
                result = errMessage['message']
                raise Exception('result')
                

        
        return result
    
    
    """
    retourne la version du service ripart
    :return: version du service ripart
    """
    def getVersion(self):
        return self.__version
    
    
    """
    retourne le profil de l'utilisateur
    :return: le profil
    """
    def getProfil(self):
        
        if self.__profil is None:
            self.__profil = self.getProfilFromService()
            
        return self.__profil
    
    
    """
    requête au service pour le porfil utilisateur
    :return: le profil de l'utilisateur
    """
    def getProfilFromService(self):
        profil= None
       
        data = self.getauth_get()
        
        #on ajoute cette ligne à cause d'un probème d'encodage dans la réponse du service !
        data    = re.sub('(<STATUTXT>)(.*)(</STATUTXT>)','',data, flags=re.MULTILINE)
        
        
        xml = XMLResponse(data)
        errMessage = xml.checkResponseValidity()
        
        if errMessage['code'] =='OK':
            profil = xml.extractProfil()
            profil.auteur = self.__auteur
            self.__jeton = xml.getCurrentJeton()
            
        return profil
        
        
      
    """
    Recherche les remarques.
    Boucle sur la méthode privée GetRemarques, pour récupérer d'éventuelles MAJ ou nouvelles remarques
    faites entre le début et la fin de la requête 
    """
    def getRemarques(self,zone,box,pagination, date,idGroupe):
        
        remarques =[]
        
        #on stocke d'abord les objets Remarque dans un dictionnaire, pour éviter d'éventuels doublons.
        dicoRems={}
        
        #la date-heure actuelle (début de la requête)
        dt = time.strftime("%Y-%m-%d %H:%I:%S")
        dtTmp = dt
        
        total = self.__getRemarques(zone, box, pagination, date, idGroupe, dicoRems)
    
        while total >1 :
            dt = time.strftime("%Y-%m-%d %H:%I:%S")
            total = self.__getRemarques(zone, box, pagination, dtTmp, idGroupe, dicoRems)
            dtTmp= dt
    
        return dicoRems
    
    
    """
    """
    def __getRemarques(self,zone,box,pagination, date,idGroupe,dicoRems):
        
        try:
            data=self.georem_get(zone, box, pagination, date, idGroupe, 0)
        except Exception as e:
            self.logger.error(str(e))
            raise 
        
        xml = XMLResponse(data)
        errMessage = xml.checkResponseValidity()
        
        total = 0
        count=pagination
        
        if errMessage['code'] =='OK':
            total = xml.getTotalResponse()
            dicoRems = xml.extractRemarques(dicoRems)
            
            
            
            # TODO
        return total
    
    """
    Consulte les informations de l’auteur
    http://ripart.ign.fr/?action=geoaut_get&jeton_md5=XXXX&id_auteur=AA où XXX = MD5(AA+AA+protocole+jeton)
    """
    def getauth_get(self):
        
        data= None
        #geoauth_url = self.__url + "?action=geoaut_get"
        
        if (self.__jeton is None or self.__auteur is None or self.__auteur.id is None):
            return None
        
        else:
            tocrypt= self.__auteur.id + self.__auteur.id + ConstanteRipart.RIPART_CLIENT_PROTOCOL + self.__jeton

            jeton_md5 = self.getMD5Hash(tocrypt)
            
            params = {}
            params['action']='geoaut_get'
            params['jeton_md5']=jeton_md5
            params['id_auteur']=self.__auteur.id
           
            data= RipartServiceRequest.makeGetRequest(self.__url, params)
        
        return data
    
    
    
    
    
    """
    Va chercher les remarques sur le service Ripart
    :return: réponse xml 
    """
    def georem_get(self,zone,box,pagination,sdate,idGroupe,count,id_georem=0):
        
        data = None
        
        if (self.__jeton is None or self.__auteur.id is None):
            return None
        else:
            
            tocrypt=str(id_georem )+ self.__auteur.id + ConstanteRipart.RIPART_CLIENT_PROTOCOL + self.__jeton
            jeton_md5 = self.getMD5Hash(tocrypt)
            
            params = {}
            params['action']='georem_get'
            params['jeton_md5']=jeton_md5
            params['id_auteur']=self.__auteur.id
            
            if (box !=None):       
                if ( box.XMin != None and box.XMax != None and box.YMin!=None and box.YMax!= None):  
                    params['box']= str(box.XMin)+','+str(box.XMax) +','+ str(box.YMin) +',' +str(box.YMax)
            
            if idGroupe > -1:
                params['id_geogroupe']= idGroupe
            
            params['debut']=sdate
            params['nb']= pagination
            params['debut_rem']= count
            params['zone']= zone
            params['tri'] ='id_georem'
            
            
            data= RipartServiceRequest.makeGetRequest(self.__url, params)
            
        return data
    
    
    
    
    @staticmethod
    def getMD5Hash(source):
        hash =hashlib.md5(source).hexdigest()
        
        return hash
     
     
        
     
if __name__ == "__main__":   
    
    c= Client('http://demo-ripart.ign.fr','mborne','mborne')
    
    profil= c.getProfil()
    
    
    c.getRemarques(zone,box,pagination, date,idGroupe)
    
    
    #jeton_md5=Client.getMD5Hash("354354_RIPART_AGIS_6451269889536854cb8eb12afd46.85829670")
    
    print 'fin'
    