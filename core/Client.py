# -*- coding: utf-8 -*-

'''
Created on 22 janv. 2015

version 3.0.0, 26/11/2018

@author: AChang-Wailing
'''
import xml.etree.ElementTree as ET
from collections import OrderedDict
import re
import time
import os.path

from qgis.PyQt.QtWidgets import QMessageBox, QProgressBar
from PyQt5.QtCore import *

from . import ConstanteRipart
from .Enum import Enum
from .Remarque import Remarque
from .RipartServiceRequest import RipartServiceRequest
from .XMLResponse import XMLResponse
from .ClientHelper import ClientHelper
from .NoProfileException import NoProfileException

from .RipartLoggerCl import RipartLogger

from . import requests
from .requests.auth import HTTPBasicAuth
import os



class Client(object):
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

    __proxies = None 
    
    
    # message d'erreur lors de la connexion ou d'un appel au service ("OK" ou message d'erreur)
    message = ""
    
    logger=RipartLogger("ripart.client").getRipartLogger()


    def __init__(self, url, login, pwd, proxies):
        """Constructeur
        Initialisation du client et connexion au service ripart
        """       
        self.__url=url
        self.__login=login
        self.__password=pwd
               
        self.__auth={}
        self.__auth['login']=self.__login
        self.__auth['password']=self.__password
        self.__proxies = proxies
        
             
    def setIface(self,iface):
        """sets the QgsInterface instance, to be able to access the QGIS application objects (map canvas, menus, ...)
        """
        self.iface=iface

      
    def connect(self):
        """ Connexion d'un utilisateur par son login et mot de passe
        
        :return: Si la connexion se fait, retourne l'id de l'auteur; sinon retour du message d'erreur
        """  
        result =None
        try:               
            self.logger.debug("tentative de connexion; " + self.__url + ' connect ' + self.__login) 
            r= requests.get(self.__url, proxies=self.__proxies,auth=HTTPBasicAuth(self.__login, self.__password))
                    
        except Exception as e:         
            self.logger.error(format(e))
            raise Exception(format(e))
        
        return self
    
    
    
    def getVersion(self):
        """Retourne la version du service ripart
        :return: version du service ripart
        """
        return self.__version
    
    
    def getProfil(self):
        """Retourne le profil de l'utilisateur
        :return: le profil
        """       
        if self.__profil is None:
            self.__profil = self.getProfilFromService()
        
        return self.__profil
    
    
    def getProfilFromService(self):
        """Requête au service pour le profil utilisateur      
        :return: le profil de l'utilisateur
        """
        profil= None

        self.logger.debug("getProfilFromService " + self.__url +"/api/georem/geoaut_get.xml")


        data =  requests.get(self.__url +"/api/georem/geoaut_get.xml", 
                             auth=HTTPBasicAuth(self.__login, self.__password),
                             proxies= self.__proxies)   

    
        self.logger.debug("data auth ")
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
          
            raise Exception(ClientHelper.notNoneValue(result))
            
        return profil
        
   

    def getGeoRems(self,parameters):
        """Recherche les remarques.
        Boucle sur la méthode privée __getGeoRemsTotal, pour récupérer d'éventuelles MAJ ou nouvelles remarques
        faites entre le début et la fin de la requête 
        
        :param parameters: les paramètres de la requête
        :type parameters : dictionary
        """   
        
        #progressbar pour le chargement des remarques
        self.progressMessageBar = self.iface.messageBar().createMessage("Téléchargement des signalements depuis le serveur ...")

        self.progress = QProgressBar()
        self.progress.setMaximum(200)      
     
        self.progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
       
        self.progressMessageBar.layout().addWidget(self.progress)
        
        self.iface.messageBar().pushWidget(self.progressMessageBar, level= 0)
        self.iface.mainWindow().repaint()
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
        dicoRems= OrderedDict(sorted(list(result['dicoRems'].items()), key=lambda t: t[0],reverse=True))
                 
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
                                                        proxies = self.__proxies,
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
                 
                data = RipartServiceRequest.makeHttpRequest(self.__url +"/api/georem/georems_get.xml",authent=self.__auth,proxies = self.__proxies,params=parameters)
                    
                xml = XMLResponse(data)
                    
                count += int(pagination)
                    
                errMessage2 = xml.checkResponseValidity()
                if errMessage2['code'] =='OK':
                    dicoRems.update(xml.extractRemarques())          
                        
                
                self.progress.setValue(count)
            
                    
            return {'total':total, 'sdate': sdate, 'dicoRems':dicoRems}
        
        else:
            err =errMessage.get('message')
            raise NoProfileException(err)
       

        

    def getGeoRem(self, idSignalement):
        """Requête pour récupérer une remarque avec un identifiant donné
        
        :param idRemarque: identifiant de la remarque que l'on souhaite récupérer
        :type idRemarque: int
        
        :return la remarque
        :rtype Remarque
        """   
        rem =Remarque()
        remarques =[]
        
        uri =self.__url +"/api/georem/georem_get/" + str(idSignalement)+".xml"
        
        data= RipartServiceRequest.makeHttpRequest(uri,authent= self.__auth,proxies = self.__proxies) 
        
        xmlResponse = XMLResponse(data)
        errMessage = xmlResponse.checkResponseValidity()
        
        total = xmlResponse.getTotalResponse()
        
        if errMessage['code']=="OK":
           
            if int(total) == 1:
                remarques = xmlResponse.extractRemarques()
                rem=list(remarques.values())[0]    
                
        return rem


    def setChangeUserProfil(self, idProfil):
        profil = None

        try:
            uri = self.__url + "/api/georem/geoaut_switch_profile/" + idProfil
            data = RipartServiceRequest.makeHttpRequest(uri, authent=self.__auth, proxies=self.__proxies)
            xmlResponse = XMLResponse(data)
            errMessage = xmlResponse.checkResponseValidity()

            if errMessage['code'] == 'OK':
                profil = xmlResponse.extractProfil()
            else:
                if errMessage['message'] != "":
                    result = errMessage['message']
                elif errMessage['code'] != "":
                    result = ClientHelper.getErrorMessage(errMessage['code'])
                else:
                    result = ClientHelper.getErrorMessage(data.status_code)

                raise Exception(ClientHelper.notNoneValue(result))

        except Exception as e:
            self.logger.error(str(e))
            raise Exception(e)

        return profil



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
            
            data = RipartServiceRequest.makeHttpRequest(uri,authent= self.__auth,proxies = self.__proxies,data= parameters)    
            xmlResponse = XMLResponse(data)
            errMessage = xmlResponse.checkResponseValidity()
            
            if errMessage['code']=="OK":
                rems =[]
                rems= xmlResponse.extractRemarques()
                if len(rems) ==1:
                    remModif=list(rems.values())[0]
                else:
                    raise Exception("Problème survenu lors de l'ajout d'une réponse")
       
        except Exception as e:
            raise Exception(errMessage["message"],e)
                
        return remModif


    def createRemarque(self,remarque):
        """Ajout d'une nouvelle remarque
        :param remarque : la remarque à créer
        :type remarque: Remarque
        :return la remarque créée
        :rtype: Remarque
        """
        rem= None
        
        try:
            params = {}
            params['version']= ConstanteRipart.RIPART_CLIENT_VERSION
            params['protocol']=ConstanteRipart.RIPART_CLIENT_PROTOCOL
            params['comment']= ClientHelper.notNoneValue(remarque.commentaire)         
            geometry = "POINT(" + str(remarque.getLongitude()) +" " + str(remarque.getLatitude()) + ")"
            params['geometry']= geometry
            params['territory']= self.getProfil().zone.__str__()
            
            #Ajout des thèmes selectionnés
            themes = remarque.themes
            
            if themes!= None and len(themes)>0:
                doc = ET.Element("THEMES")
                
                attributes = ""
                
                for t in themes:
                    """th= ET.SubElement(doc,"THEME")
                    grId=ET.SubElement(th,"ID_GEOGROUPE")
                    grId.text= t.groupe.id
                    nom= ET.SubElement(th,"NOM")
                    nom.text=t.groupe.nom"""
                    
                    groupeIdAndNom = ClientHelper.notNoneValue ('"' + t.groupe.id + "::" + t.groupe.nom )
                    
                    attributes +=  ClientHelper.notNoneValue(groupeIdAndNom + "\"=>\"1\",")
                    
                    for at in t.attributs :
                        attributes += groupeIdAndNom + "::" + at.nom + '"=>"' + at.valeur + '",'

                attributes = attributes[:-1]
                params["attributes"]= attributes
            
            
            #ajout des croquis
            if not remarque.isCroquisEmpty() :
                croquis= remarque.croquis
                gmlurl="http://www.opengis.net/gml"
                doc = ET.Element("CROQUIS",{"xmlns:gml":gmlurl})
                
                for cr in croquis:
                    doc= cr.encodeToXML(doc)
                    
                params["sketch"] =ET.tostring(doc)
                
                
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
         
                  
                    files = {"upload"+str(docCnt):  open(ClientHelper.notNoneValue(document), 'rb')}

   
            #raise Exception("TEST")
        
            #envoi de la requête
            uri = self.__url +"/api/georem/georem_post.xml"
            
            data = RipartServiceRequest.makeHttpRequest(uri, authent= self.__auth,proxies = self.__proxies, data=params, files=files) 
                    
            xmlResponse = XMLResponse(data)
            errMessage= xmlResponse.checkResponseValidity()
            
            if errMessage['code'] =='OK': 
                rems= xmlResponse.extractRemarques()
                if len(rems)==1:
                    rem =list(rems.values())[0]
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
        

     
    @staticmethod
    def get_MAX_TAILLE_UPLOAD_FILE():
        return ConstanteRipart.MAX_TAILLE_UPLOAD_FILE