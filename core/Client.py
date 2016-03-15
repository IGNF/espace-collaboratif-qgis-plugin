# -*- coding: utf-8 -*-

'''
Created on 22 janv. 2015

@author: AChang-Wailing
'''

import xml.etree.ElementTree as ET
from collections import OrderedDict
import hashlib
import re
import time
import os.path

from PyQt4.QtGui import QMessageBox, QProgressBar
from PyQt4.QtCore import *

import ConstanteRipart
from Auteur import Auteur
from Croquis import Croquis
from Theme import Theme
from GeoReponse import GeoReponse
from Enum import Enum
from Remarque import Remarque
from Profil import Profil
from RipartServiceRequest import RipartServiceRequest
from XMLResponse import XMLResponse
from Box import Box
from ClientHelper import ClientHelper

from RipartLoggerCl import RipartLogger

import requests
from requests.auth import HTTPBasicAuth

class Client:
    """"
    Cette classe sert de client pour le service RIPart
    """
    
    __url=""
    __login = ""
    __password=""
    __auteur = None
    __version = None
    __profil = None
    __auth = None
    
    
    # message d'erreur lors de la connexion ou d'un appel au service ("OK" ou message d'erreur)
    message = ""
    

    logger=RipartLogger("ripart.client").getRipartLogger()


    def __init__(self, url, login, pwd):
        """Constructeur
        Initialisation du client et connexion au service ripart
        """       
        self.__url=url
        self.__login=login
        self.__password=pwd
        
           
        self.__auth={}
        self.__auth['login']=self.__login
        self.__auth['password']=self.__password
      
        
        
        
    def setIface(self,iface):
        self.iface=iface

      
    def connect(self):
        """ Connexion d'un utilisateur par son login et mot de passe
        
        :return: Si la connexion se fait, retourne l'id de l'auteur; sinon retour du message d'erreur
        """  
        result =None
        try:               
            self.logger.debug("tentative de connexion; " + self.__url + ' connect ' + self.__login)
            
            r= requests.get(self.__url, auth=HTTPBasicAuth(self.__login, self.__password))
            
            
        except Exception as e:
            
            self.logger.error(e.message)
            raise Exception(e.message)
        
        #return result
        return self
    
    
    
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
        
        data =  requests.get(self.__url +"/api/georem/geoaut_get.xml", 
                             auth=HTTPBasicAuth(self.__login, self.__password))   
          
        xml = XMLResponse(data.text)
        errMessage = xml.checkResponseValidity()
        
        if errMessage['code'] =='OK':
            profil = xml.extractProfil()
          
        else:
            if errMessage['message']!="":
                result =errMessage['message']
            elif errMessage['code']!="":
                result =ClientHelper.getErrorMessage(errMessage['code'])
            else: 
                result =ClientHelper.getErrorMessage( data.status_code)
          
            raise Exception(ClientHelper.stringToStringType(result))
            
        return profil
        
    

    def getGeoRems(self,parameters):
        """Recherche les remarques.
        Boucle sur la méthode privée __getGeoRemsTotal, pour récupérer d'éventuelles MAJ ou nouvelles remarques
        faites entre le début et la fin de la requête 
        
        :param parameters: les paramètres de la requête
        :type parameters : dictionary
        """   
        #progressbar pour le chargement des remarques
        self.progressMessageBar = self.iface.messageBar().createMessage(u"Téléchargement des remarques depuis le serveur ...")
        self.progress = QProgressBar()
     
        self.progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
       
        self.progressMessageBar.layout().addWidget(self.progress)
        self.iface.messageBar().pushWidget(self.progressMessageBar, self.iface.messageBar().INFO)
        self.progress.setValue(0)
                
        result = self.__getGeoRemsTotal(parameters)
        total = int(result["total"])   #nb de remarques récupérées
        sdate = result["sdate"];    #date de la réponse du serveur
        
        while (total > 1) :
            parameters['updatingDate'] = sdate
            tmp = self.__getGeoRemsTotal(parameters)
            
            result['dicoRems'].update(tmp['dicoRems']) #add the tmp result to the result['dicoRems'] dictionnary
            total=tmp['total']
            sdate = tmp["sdate"]; 
            
            self.logger.debug("loop on total result "+ " total="+ str(result['total']) +",datetime="+sdate )

        
        # tri des remarques par ordre décroissant d'id
        dicoRems= OrderedDict(sorted(result['dicoRems'].items(), key=lambda t: t[0],reverse=True))
                 
        return dicoRems



    def __getGeoRemsTotal(self,parameters):
        """Recherche les remarques en fonction des paramètres et retourne le nombre total de remarques trouvées
        
        :param parameters: les paramètres de la requête
        :type parameters : dictionary
        
        :return dictionnaire contenant les remarques
        :rtype dictionary
        """
        
        pagination = parameters['pagination']
        total = 0
        dicoRems={}
        
        try:
            data = RipartServiceRequest.makeHttpRequest(self.__url +"/api/georem/georems_get.xml", 
                                                        authent= self.__auth,
                                                        params=parameters)
        except Exception as e:
            self.logger.error(str(e))
            raise 
          
        xml = XMLResponse(data)
        errMessage = xml.checkResponseValidity()

        count=int(pagination)
      
        if errMessage['code'] =='OK':
            total = int(xml.getTotalResponse())
            sdate = xml.getDate();
            dicoRems = xml.extractRemarques()          
           
            if int(pagination) > total:
                progressMax = int(pagination)
            else:
                progressMax= total
                
            self.progress.setMaximum(progressMax)
            self.progress.setValue(count)
     
            while (total - count)  > 0:
                
                parameters["offset"]= count.__str__()
            
                data = RipartServiceRequest.makeHttpRequest(self.__url +"/api/georem/georems_get.xml",authent=auth,params=parameters)     
                xml = XMLResponse(data)
                
                count += int(pagination)
                
                errMessage2 = xml.checkResponseValidity()
                if errMessage2['code'] =='OK':
                    dicoRems.update(xml.extractRemarques())          
                    
            
                self.progress.setValue(count)
                
        return {'total':total, 'sdate': sdate, 'dicoRems':dicoRems}

        
    
    def getGeoRem(self, idRemarque):
        """Requête pour récupérer une remarque avec un identifiant donné
        
        :param idRemarque: identifiant de la remarque que l'on souhaite récupérer
        :type idRemarque: int
        
        :return la remarque
        :rtype Remarque
        """   
        rem =Remarque()
        remarques =[]
        
        parameters ={}
       
        uri =self.__url +"/api/georem/georem_get/" + str(idRemarque)+".xml"
        
        data= RipartServiceRequest.makeHttpRequest(uri,authent= self.__auth)   
        
        xmlResponse = XMLResponse(data)
        errMessage = xmlResponse.checkResponseValidity()
        
        total = xmlResponse.getTotalResponse()
        
        if errMessage['code']=="OK":
           
            if int(total) == 1:
                remarques = xmlResponse.extractRemarques()
                rem=remarques.values()[0]    
                
        return rem
        
    
    def addReponse(self,remarque,reponse,titreReponse):
        """Ajoute une réponse à une remarque

        :param remarque: la remarque
        :type remarque: Remarque
        
        :param reponse : la réponse
        :type reponse: string
        
        :param titreReponse: le titre de la réponse
        :type titreReponse : string 
        
        :return la remarque à laquelle a été ajoutée la réponse
        """
        remModif = None
        
        try:
            parameters= {}
            parameters['id'] = str(remarque.id)
            parameters['title'] = titreReponse
            parameters['content'] = reponse
            parameters['status'] = remarque.statut.__str__()
            
            uri = self.__url +"/api/georem/georep_post.xml"
            data = RipartServiceRequest.makeHttpRequest(uri,authent= self.__auth,data= parameters)  
            
            xmlResponse = XMLResponse(data)
            errMessage = xmlResponse.checkResponseValidity()
            
            if errMessage['code']=="OK":
                rems =[]
                rems= xmlResponse.extractRemarques()
                if len(rems) ==1:
                    remModif=rems.values()[0]
                else:
                    raise Exception("Problème survenu lors de l'ajout d'une réponse")
       
        except Exception as e:
            raise Exception(errMessage["message"],e)
                
        return  remModif
    
   
    
    
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
            jeton_md5 =Client.getMD5Hash("0" + self.__auteur.id + ConstanteRipart.RIPART_CLIENT_PROTOCOL + self.__jeton)
            
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
            
            files={}
            for document in documents:
                if  os.path.isfile(document) :
                    docCnt +=1
                    if os.path.getsize(document) > ConstanteRipart.MAX_TAILLE_UPLOAD_FILE:
                        raise Exception("Le fichier "+ document + " est de taille supérieure à " + \
                                        str(ConstanteRipart.MAX_TAILLE_UPLOAD_FILE))  
                    
                    docs["upload"+str(docCnt)]=document
                    
                    fname=os.path.basename(document)
                    files = {"upload"+str(docCnt):  (fname, open(document, 'rb'))}
                    params ['filename']=os.path.basename(document)
   
       
            #envoi de la requête
            data = RipartServiceRequest.makeHttpRequest(self.__url,  data=params, files=files)             
                    
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
            
            
            self.__jeton = xmlResponse.getCurrentJeton()
            
 
            
        except Exception as e:
            self.logger.error(str(e))
            raise Exception(e)
                
        return rem
    
    
    def createGeoRem(self,remarque):
        """Ajout d'une nouvelle remarque
       
        """
        rem= None
        try:
            
            params = {}
           
            params['version']=self.__version
            #params['geogroupe']= str(self.getProfil().geogroupe.id)
            params['comment']= remarque.commentaire
            
            geom= "POINT("+str(remarque.getLongitude())+" "+ str(remarque.getLatitude()) +")"
            
            params['geometry']=geom

            params['territory']= self.getProfil().zone.__str__()
            
            
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
                    
                params["attributes"]=ET.tostring(doc)
                
            params['protocol']=ConstanteRipart.RIPART_CLIENT_PROTOCOL
            params['version'] =ConstanteRipart.RIPART_CLIENT_VERSION
            
            """  #ajout des croquis
            if not remarque.isCroquisEmpty() :
                croquis= remarque.croquis
                gmlurl="http://www.opengis.net/gml"
                doc = ET.Element("CROQUIS",{"xmlns:gml":gmlurl})
                
                for cr in croquis:
                    doc= cr.encodeToXML(doc)
                    
                params["croquis"] =ET.tostring(doc)
                
          
            
            #ajout des documents joints
            documents = remarque.documents
            docCnt=0
            docs= {}
            
            files={}
            for document in documents:
                if  os.path.isfile(document) :
                    docCnt +=1
                    if os.path.getsize(document) > ConstanteRipart.MAX_TAILLE_UPLOAD_FILE:
                        raise Exception("Le fichier "+ document + " est de taille supérieure à " + \
                                        str(ConstanteRipart.MAX_TAILLE_UPLOAD_FILE))  
                    
                    docs["upload"+str(docCnt)]=document
                    
                    fname=os.path.basename(document)
                    files = {"upload"+str(docCnt):  (fname, open(document, 'rb'))}
                    params ['filename']=os.path.basename(document)
   """
       
            #envoi de la requête
            #data = RipartServiceRequest.makeHttpRequest(self.__url,  data=params, files=files) 
            data = RipartServiceRequest.makeHttpRequest(self.__url,  data=params)             
                    
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
            
            
            self.__jeton = xmlResponse.getCurrentJeton()
            
 
            
        except Exception as e:
            self.logger.error(str(e))
            raise Exception(e)
                
        return rem
    
    
    
   
    def getauth_get(self):      
        """Consulte les informations de l’auteur
        http://ripart.ign.fr/?action=geoaut_get&jeton_md5=XXXX&id_auteur=AA où XXX = MD5(AA+AA+protocole+jeton)
        """       
        data= None
        
        data= RipartServiceRequest.makeHttpRequest(self.__url+"/collaboratif-site/profile/")
        
        
        """if (self.__jeton is None or self.__auteur is None or self.__auteur.id is None):
            return None
        
        else:
            tocrypt= self.__auteur.id + self.__auteur.id + ConstanteRipart.RIPART_CLIENT_PROTOCOL + self.__jeton

            jeton_md5 =Client.getMD5Hash(tocrypt)
            
            params = {}
            params['action']=ConstanteRipart.RIPART_GEOAUT_GET
            params['jeton_md5']=jeton_md5
            params['id_auteur']=self.__auteur.id
           
            data= RipartServiceRequest.makeHttpRequest(self.__url, data=params)"""
        
        return data
    
    
  
    
    
    def georem_get0(self,zone,box,pagination,sdate,idGroupe,count,id_georem=0):
        '''Va chercher les remarques sur le service Ripart
        :return: réponse xml 
       ''' 
        data = None
        
        if ( self.__auteur.id is None):
            return None
        else:
            
            tocrypt=str(id_georem )+ self.__auteur.id + ConstanteRipart.RIPART_CLIENT_PROTOCOL + self.__jeton
            jeton_md5 =Client.getMD5Hash(tocrypt)
            
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
   
    """def georem_get(self,zone,box,pagination,sdate,idGroupe,count,id_georem=0):
        '''Va chercher les remarques sur le service Ripart
        :return: réponse xml 
       ''' 
        data = None
        
        if (self.__jeton is None or self.__auteur.id is None):
            return None
        else:
            
            tocrypt=str(id_georem )+ self.__auteur.id + ConstanteRipart.RIPART_CLIENT_PROTOCOL + self.__jeton
            jeton_md5 =Client.getMD5Hash(tocrypt)
            
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
            
        return data"""
    
    
    
    
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
    