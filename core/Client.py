# -*- coding: utf-8 -*-

'''
Created on 22 janv. 2015

@author: AChang-Wailing
'''

import logging
#import RipartLogger 
import xml.etree.ElementTree as ET
from collections import OrderedDict

import ConstanteRipart
#from Groupe import Groupe
from Auteur import Auteur
from Croquis import Croquis
from Theme import Theme
from GeoReponse import GeoReponse
from Enum import Enum
from Remarque import Remarque
from Profil import Profil
from RipartServiceRequest import RipartServiceRequest
from XMLResponse import XMLResponse
import hashlib
import re
import time
from Box import Box
import os.path
from ClientHelper import ClientHelper

class Client:
    """"
    Cette classe sert de client pour le service RIPart
    """
    
    __url=""
    __login = ""
    __password=""
    __jeton = None
    __auteur = None
    __version = None
    __profil = None
    
    # message d'erreur lors de la connexion ou d'un appel au service ("OK" ou message d'erreur)
    message = ""
    
    logger=logging.getLogger("ripart.client")
    


    def __init__(self, url, login, pwd):
        """Constructeur
        Initialisation du client et connexion au service ripart
        """       
        self.__url=url
        self.__login=login
        self.__password=pwd
        self.message = self.connect()

      
    def connect(self):
        """ Connexion d'un utilisateur par son login et mot de passe
        
        :return: Si la connexion se fait, retourne l'id de l'auteur; sinon retour du message d'erreur
        """  
        result =None
        try:               
            self.logger.debug("tentative de connexion; " + self.__url + ' connect ' + self.__login)
        
            data =RipartServiceRequest.makeHttpRequest(self.__url, params={'action':'connect','login':self.__login})
            
            xmlResponse = XMLResponse(data)
            
            #contrôle la validité et récupère les aléas
            errMessage = xmlResponse.checkResponseValidity()
            
            if (errMessage['code']=='OK'):
                self.logger.debug('connect étape OK')
                result = self.connect2(xmlResponse)
       
                self.__version= xmlResponse.getVersion()
            else :
                #result = errMessage["message"]
                result =ClientHelper.getErrorMessage(errMessage['code'])
                raise Exception(result)
                 
        except Exception as e:
            
            self.logger.error(e.message)
            raise Exception(e.message)
        
        return result
    
    
    
   
    def connect2(self,xml):
        """Deuxième requête pour la connexion 
        
        :return ID_AUTEUR ou message d'erreu
        """    
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
            
            data= RipartServiceRequest.makeHttpRequest(self.__url, data=parameters)
            xmlResponse = XMLResponse(data)
            errMessage = xmlResponse.checkResponseValidity()
            
            
            if errMessage['code'] =='OK':
                self.logger.debug("connect étape 2 ok")
                connectValues = xmlResponse.getConnectValues()
                   
                self.__auteur = Auteur(connectValues['ID_AUTEUR'], self.__login)
                self.__jeton= connectValues['JETON']
                
                result =connectValues['ID_AUTEUR']
                
            else:
                result =ClientHelper.getErrorMessage(errMessage['code'])
                """if errMessage['code']=='bad_pass' or errMessage['code']=='bad_login':
                    result=u"Login et/ou mot de passe erroné(s)"
                else:
                    result = errMessage['message']"""
                raise Exception(result)
       
        return result
    
    
    
    def getVersion(self):
        """retourne la version du service ripart
        :return: version du service ripart
        """
        return self.__version
    
    
   
    def getProfil(self):
        """retourne le profil de l'utilisateur
        :return: le profil
        """       
        
        if self.__profil is None:
            self.__profil = self.getProfilFromService()
            
        return self.__profil
    
    
    
    def getProfilFromService(self):
        """requête au service pour le profil utilisateur      
        :return: le profil de l'utilisateur
        """
        profil= None
       
        data = self.getauth_get()
        
        self.logger.debug("getProfilFromService")
        
        
        #on ajoute cette ligne à cause d'un probème d'encodage dans la réponse du service !
        data    = re.sub('(<STATUTXT>)(.*)(</STATUTXT>)','',data, flags=re.MULTILINE)
        
        
        self.logger.debug(data)
        
        
        xml = XMLResponse(data)
        errMessage = xml.checkResponseValidity()
        
        if errMessage['code'] =='OK':
            profil = xml.extractProfil()
            profil.auteur = self.__auteur
            self.__jeton = xml.getCurrentJeton()
        else:
            result =ClientHelper.getErrorMessage(errMessage['code'])
            raise Exception(ClientHelper.stringToStringType(result))
            
        return profil
        
        
      
    
    def getRemarques(self,zone,box,pagination, date,idGroupe):
        """Recherche les remarques.
        Boucle sur la méthode privée GetRemarques, pour récupérer d'éventuelles MAJ ou nouvelles remarques
        faites entre le début et la fin de la requête 
        
        :param zone: code de la zone géographique
        :type zone: ConstanteRipart.ZoneGeographique
        
        :param box: bounding box dans laquelle on cherche des remarques
        :type box: Box
        
        :param pagination: nombre de remarques par réponse
        :type pagination int
        
        :param date: date à partir de laquelle on cherche les remarques
        :type date: str  (yyyy-mm-dd HH:MM:SS)
        
        :param idGroupe: identifiant du groupe de l'utilisateur
        :type idGroupe: int
        """   
      
        #on stocke les objets Remarque dans un dictionnaire, pour éviter d'éventuels doublons.
        dicoRems={}
        
        #la date-heure actuelle (début de la requête)
        dt = time.strftime("%Y-%m-%d %H:%I:%S")
        dtTmp = dt
        
        result= self.__getRemarques(zone, box, pagination, date, idGroupe)
        
   
        while int(result['total']) >1 :
            dt = time.strftime("%Y-%m-%d %H:%I:%S")
            tmp=self.__getRemarques(zone, box, pagination, dtTmp, idGroupe)
            
            result['dicoRems'].update(tmp['dicoRems'])
            result['total']=tmp['total']
            dtTmp= dt
    
        dicoRems= OrderedDict(sorted(result['dicoRems'].items(), key=lambda t: t[0],reverse=True))
                               
        
        return  dicoRems
    
    
   
    def __getRemarques(self,zone,box,pagination, date,idGroupe):
        """Recherche les remarques et retourne le nombre total de remarques trouvées
         
        :param zone: code de la zone géographique
        :type zone: ConstanteRipart.ZoneGeographique
        
        :param box: bounding box dans laquelle on cherche des remarques
        :type box: Box
        
        :param pagination: nombre de remarques par réponse
        :type pagination int
        
        :param date: date à partir de laquelle on cherche les remarques
        :type date: str  (yyyy-mm-dd HH:MM:SS)
        
        :param idGroupe: identifiant du groupe de l'utilisateur
        :type idGroupe: int
         """
        
        try:
            data=self.georem_get(zone, box, pagination, date, idGroupe, 0)
        except Exception as e:
            self.logger.error(str(e))
            raise 
        
        self.logger.debug("DATA:"+ data)
        xml = XMLResponse(data)
        errMessage = xml.checkResponseValidity()
        
        total = 0
        dicoRems={}
       
        count=int(pagination)
        
        if errMessage['code'] =='OK':
            total = xml.getTotalResponse()
            dicoRems = xml.extractRemarques()          
            self.__jeton= xml.getCurrentJeton()
            
            #TODO Progressbar ?
            
            while (int(total) - count)  > 0:
                data = self.georem_get(zone, box, pagination, date, idGroupe, count)
                xml = XMLResponse(data)
                
                count += int(pagination)
                
                errMessage2 = xml.checkResponseValidity()
                if errMessage2['code'] =='OK':
                    dicoRems.update(xml.extractRemarques())          
                    self.__jeton= xml.getCurrentJeton()
                     
        
        return {'total':total, 'dicoRems':dicoRems}
    
    
    
    def getRemarque(self, idRemarque):
        """Requête pour récupérer une remarque avec un identifiant donné
        ripart.ign.fr/?action=georem_get&jeton_md5=XXXX&id_auteur=AA&id_georem=RR 
        où XXX = MD5(RR+AA+protocole+jeton).
        
        :param idRemarque: identifiant de la remarque que l'on souhaite récupérer
        :type idRemarque: int
        
        :return la remarque
        :rtype Remarque
        """
        rem =Remarque()
        remarques =[]
        
        data= self.georem_getById(idRemarque)
        
        xmlResponse = XMLResponse(data)
        errMessage = xmlResponse.checkResponseValidity()
        
        total = xmlResponse.getTotalResponse()
        
        if errMessage['code']=="OK":
            self.__jeton =xmlResponse.getCurrentJeton()
            
            if int(total) == 1:
                remarques = xmlResponse.extractRemarques()
                rem=remarques.values()[0]    
                
        return rem
        
        
        
    def georem_getById(self,id_georem):
        """Va chercher une remarque donnée par son identifiant
        
        :param id_georem: identifiant de la remarque
        :type id_georem: int
        :return: remarque au format xml
        :rtype string (xml)
        """
        data=None
        georem_url =self.__url + "?action=georem_get"
        
        if self.__jeton==None or self.__auteur.id==None :
            return None
        else:
            jeton_md5 = self.getMD5Hash(str(id_georem) + self.__auteur.id +ConstanteRipart.RIPART_CLIENT_PROTOCOL+self.__jeton)
            
            georem_url += "&jeton_md5=" + jeton_md5 + \
                          "&id_auteur=" + self.__auteur.id + \
                          "&id_georem=" + str(id_georem);
        
            data = RipartServiceRequest.makeHttpRequest(georem_url)
            
        return data
    
    
    def addReponse(self,remarque,reponse):
        """Ajoute une réponse à une remarque
        ripart.ign.fr/?action=georem_put&id_georem=RR&id_auteur=AA&jeton_md5=XXXX&hash=HH 
        où XXX = MD5(RR+AA+protocole+jeton).
        
        :param remarque: la remarque
        :type remarque: Remarque
        :param reponse : la réponse
        :type reponse: string
        :return la remarque à laquelle a été ajoutée la réponse
        """
      
        try:
            tohash=remarque.id+ self.__auteur.id + ConstanteRipart.RIPART_CLIENT_PROTOCOL + self.__jeton
            jeton_md5 = self.getMD5Hash(tohash)
            
            params = {}
            params['action']=ConstanteRipart.RIPART_GEOREM_PUT
            params['id_georem']=str(remarque.id)
            params['id_auteur']=self.__auteur.id
            params['jeton_md5']=jeton_md5
            params['hash']=remarque.hash
            params['reponse']=reponse
            params['statut']= remarque.statut.__str__()
            
            data = RipartServiceRequest.makeHttpRequest(self.__url, data=params)
            
            xmlResponse = XMLResponse(data)
            errMessage = xmlResponse.checkResponseValidity()
            
            if errMessage['code']=="OK":
                rems =[]
                rems= xmlResponse.extractRemarques()
                if len(rems) ==1:
                    remarque=rems.values()[0]
                else:
                    raise Exception("Problème survenu lors de l'ajout d'une réponse")
                
        except Exception as e:
            raise Exception(errMessage["message"],e)
                
        return remarque
    
    
    
    def createRemarque(self,remarque):
        """Ajout d'une nouvelle remarque
        ripart.ign.fr/?action=georem_post&id_auteur=AA&jeton_md5=XXXX 
        où XXX = MD5(0+AA+protocole+jeton).
        
        :param remarque : la remarque à créer
        :type remarque: Remarque
        :return la remarque créée
        :rtype: Remarque
        """
        
        rem= None
        try:
            jeton_md5 = self.getMd5Hash("0" + self.__auteur.id + ConstanteRipart.RIPART_CLIENT_PROTOCOL + self.__jeton)
            
            params = {}
            params['action']=ConstanteRipart.RIPART_GEOREM_POST
            params['jeton_md5']=jeton_md5
            params['id_auteur']=self.__auteur.id
            params['version']=self.__version
            params['geogroupe']= str(self.getProfil().geogroupe.id)
            params['com']= remarque.commentaire
            params['lon']= str(remarque.getLongitude())
            params['lat']= str(remarque.getLatitude())
            params['zone_geo']= self.getProfil().zone.__str__()
            
            
            #Ajout des thèmes selectionnés en générant le xml associé
            themes = remarque.themes
            
            if themes!= None and len(themes)>0:
                doc = ET.Element("THEMES")
                
                for t in themes:
                    th= ET.SubElement(doc,"THEME")
                    grId=ET.SubElement(th,"ID_GEOGROUPE")
                    grId.text= t.groupe.id
                    nom= ET.SubElement(th,"NOM")
                    nom.text=t.groupe.nom
                    
                params["themes"]=ET.tostring(doc)
            
            #ajout des croquis
            if not remarque.isCroquisEmpty() :
                croquis= remarque.croquis
                gmlurl="http://www.opengis.net/gml"
                doc = ET.Element("CROQUIS",{"xmlns:gml":gmlurl})
                
                for cr in croquis:
                    doc= cr.encodeToXML(doc)
                    
                params["croquis"] =ET.tostring(doc)
                
            #département
            dep = remarque.departement
            if dep!=None and str(dep.id).strip() not in [None, ""]:
                params["adm1"]=dep.nom
                params["nadm1"]=dep.id
                
            #commune
            commune = remarque.commune
            if commune.strip() not in [None, ""]:
                params["adm2"]=commune
            
            #ajout des documents joints
            documents = remarque.documents
            docCnt=0
            docs= {}
            
            for document in documents:
                if  os.path.isfile(document) :
                    docCnt +=1
                    if os.path.getsize(document) > ConstanteRipart.MAX_TAILLE_UPLOAD_FILE:
                        raise Exception("Le fichier "+ document + " est de taille supérieure à " + \
                                        ConstanteRipart.MAX_TAILLE_UPLOAD_FILE)  
                    
                    docs["upload"+docCnt]=document
                    
            #envoi de la requête
            data = RipartServiceRequest.makeHttpRequest(self.__url,  data=params, files=docs)             
                    
            xmlResponse = XMLResponse(data)
            errMessage= xmlResponse.checkResponseValidity()
            
            if errMessage['code'] =='OK': 
                rems= xmlResponse.extractRemarques()
                if len(rems)==1:
                    rem =rems.values()[0]
                else :
                    self.logger.error("Problème lors de l'ajout de la remarque")
                    raise Exception("Problème lors de l'ajout de la remarque")
            else:
                self.logger.error(errMessage['message'])
                raise Exception(errMessage['message'])
                
        except Exception as e:
            self.logger.error(str(e))
            raise Exception(e)
                
        return rem
    
    
    
   
    def getauth_get(self):      
        """Consulte les informations de l’auteur
        http://ripart.ign.fr/?action=geoaut_get&jeton_md5=XXXX&id_auteur=AA où XXX = MD5(AA+AA+protocole+jeton)
        """       
        data= None
        
        if (self.__jeton is None or self.__auteur is None or self.__auteur.id is None):
            return None
        
        else:
            tocrypt= self.__auteur.id + self.__auteur.id + ConstanteRipart.RIPART_CLIENT_PROTOCOL + self.__jeton

            jeton_md5 = self.getMD5Hash(tocrypt)
            
            params = {}
            params['action']=ConstanteRipart.RIPART_GEOAUT_GET
            params['jeton_md5']=jeton_md5
            params['id_auteur']=self.__auteur.id
           
            data= RipartServiceRequest.makeHttpRequest(self.__url, data=params)
        
        return data
    
     
   
    def georem_get(self,zone,box,pagination,sdate,idGroupe,count,id_georem=0):
        """Va chercher les remarques sur le service Ripart
        :return: réponse xml 
        """     
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
                    params['box']= str(box.XMin) +','+ str(box.YMin) +','+str(box.XMax)+',' +str(box.YMax)
            
            if idGroupe > -1:
                params['id_geogroupe']= idGroupe
            
            params['debut']=sdate
            params['nb']= pagination
            params['debut_rem']= count
            params['zone']= zone
            params['tri'] ='id_georem'
            
            
            data= RipartServiceRequest.makeHttpRequest(self.__url, data=params)
            
        return data
    
    
    
    
    """
    méthode pour crypter une chaîne de caractères en MD5
    """
    @staticmethod
    def getMD5Hash(source):
        md5hash =hashlib.md5(source).hexdigest()
        
        return md5hash
     
    @staticmethod
    def get_MAX_TAILLE_UPLOAD_FILE():
        return ConstanteRipart.MAX_TAILLE_UPLOAD_FILE
    
     
     
if __name__ == "__main__":   
    
    c= Client('http://demo-ripart.ign.fr','mborne','mborne')
    
    profil= c.getProfil()
    
    
 
    print 'fin'
    