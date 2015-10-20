# -*- coding: utf-8 -*-
'''
Created on 29 sept. 2015

@author: AChang-Wailing
'''
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QMessageBox
from qgis.core import *
from qgis.core import QgsCoordinateReferenceSystem, QgsMessageLog
from RipartException import RipartException

import os.path
import shutil
from  RipartHelper import  RipartHelper
import logging
from core.RipartLoggerCl import RipartLogger

import ntpath
from core.Profil import Profil

# importing pyspatialite
from pyspatialite import dbapi2 as db
#import sqlite3

from qgis._core import QgsDataSourceURI,QgsVectorLayer, QgsMapLayerRegistry

from FormConnexion_dialog import FormConnexionDialog
from FormInfo import FormInfo
from core.Client import Client
from core.ClientHelper import ClientHelper

class Contexte(object):
    """
    Contexte et initialisation  
    """
    #instance du Contexte 
    instance =None
    
    #identifiants de connexion
    login=""
    pwd=""
    urlHostRipart=""    
    profil=None
    
    client=None
    
    loginWindow=None
 
    #le répertoire du projet qgis
    projectDir= ""    
    #le nom du fichier (projet qgis)
    projectFileName=""
    
    dbPath=""
    
    #répertoire du plugin
    plugin_path = os.path.dirname(os.path.realpath(__file__))
    
    #fichier xml de configuration
    ripartXmlFile=""
    
    #
    QObject= None
    QgsProject=None
    iface=None
    
    #map canvas,la carte courante
    mapCan = None
    
    #Le système géodésique employé par le service Ripart (WGS84; EPSG:2154)
    spatialRef= None
    
    
    conn=None

    logger=None
    
    progressMessageBar=None
    progress=None
    

    def __init__(self, QObject,QgsProject):
        '''
        Constructor
        ''' 
        self.QObject=QObject
        self.QgsProject= QgsProject
        self.mapCan = QObject.iface.mapCanvas()
        
        self.iface= QObject.iface
        
        self.login=""
        self.pwd=""
        self.urlHostRipart=""
        
        self.logger=RipartLogger("Contexte").getRipartLogger()

        #self.logger.debug("test logger Contexte")
        self.spatialRef = QgsCoordinateReferenceSystem( RipartHelper.epsgCrs, QgsCoordinateReferenceSystem.EpsgCrsId)
        
        #s = QSettings()
        #s.setValue("/Projections/defaultBehaviour", "useProject")
        #defaultCrs= s.value('/Projections/projectDefaultCrs')
        #s.setValue('/Projections/projectDefaultCrs', 'EPSG:4326')
        
        try:
            #set du répertoire et fichier du projet qgis
            self.setProjectParams(QgsProject)
           
            #contrôle l'existence du fichier de configuration
            self.checkConfigFile()      
            
            self.getOrCreateDatabase()
            
            #self.addRipartLayersToMap()
            
        except RipartException as e:
            #self.logger.setLevel(logging.DEBUG)
            self.logger.error("init contexte:" + e.message)
   
            raise
              
        
      
    @staticmethod    
    def getInstance(QObject=None,QgsProject=None):
        if not Contexte.instance:
            try:
                Contexte.instance= Contexte(QObject,QgsProject)
                Contexte.instance.logger.debug("instance de contexte créée")
                #QgsMessageLog.logMessage("Your plugin code has been executed correctly", level=QgsMessageLog.INFO, tag="ripart")
            except RipartException as e:
                Contexte.instance=None
                raise e
            
        elif  (Contexte.instance.projectDir!= QgsProject.instance().homePath() or
              Contexte.instance.projectFileName+".qgs"!=ntpath.basename(QgsProject.instance().fileName())) :
            Contexte.instance = Contexte(QObject,QgsProject)
            Contexte.instance.logger.debug("nouvelle instance de contexte créée")
       
        #Contexte.instance.addRipartLayersToMap()
        
        return Contexte.instance
    
    
    def setProjectParams(self,QgsProject):
        """set des paramètres du projet
        """
        self.projectDir=QgsProject.instance().homePath()
        if self.projectDir =="":
            """msgBox = QMessageBox()
            msgBox.setWindowTitle("IGN RIPart")
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText(u"Votre projet QGIS doit être enregistré avant de pouvoir utiliser l'extension RIPart")
            ret = msgBox.exec_()"""

            self.iface.messageBar().pushMessage("Attention",
                                                 u"Votre projet QGIS doit être enregistré avant de pouvoir utiliser l'extension RIPart",
                                                  level=1, duration =10)
            raise RipartException(u"Projet QGIS non enregistré") 
    
        fname=ntpath.basename(QgsProject.instance().fileName())
        
        self.projectFileName= fname[:fname.find(".")]
        
    
    
    def checkConfigFile(self):
        """Contrôle de l'existence du fichier de configuration
        """
        ripartxml=self.projectDir+"\\"+ RipartHelper.nom_Fichier_Parametres_Ripart
        if not os.path.isfile(ripartxml) :
            try:
                shutil.copy(self.plugin_path+"\\"+RipartHelper.ripart_files_dir+"\\"+ RipartHelper.nom_Fichier_Parametres_Ripart,
                             ripartxml)
                self.logger.debug("copy ripart.xml" )
            except Exception as e:
                self.logger.error("no ripart.xml found in plugin directory" + e.message)
                raise e
           
    
    
    
    def setConnexionRipartParam(self):
        """Set des informations de connexion (login + url)
        """
        self.logger.debug("setConnexionRipart")
        ret=""
        if len(self.projectFileName)==0:
            """msgBox = QMessageBox()
            msgBox.setWindowTitle("IGN RIPart")
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText(u"Votre projet QGIS doit être enregistré avant de pouvoir utiliser l'extension RIPart")
            ret = msgBox.exec_()"""
        else:
            self.urlHostRipart = RipartHelper.load_urlhost(self.projectDir).text;
            self.login = RipartHelper.load_login(self.projectDir).text;
        
        return ret
    
     
     
     
    def getConnexionRipart(self,newLogin=False):
        self.logger.debug("GetConnexionRipart ")
        
        result= -1;
        
        self.urlHostRipart=RipartHelper.load_ripartXmlTag(self.projectDir, RipartHelper.xml_UrlHost).text
        self.logger.debug("this.URLHostRipart " + self.urlHostRipart)
 
        
        self.loginWindow = FormConnexionDialog()
        
        self.login = RipartHelper.load_ripartXmlTag(self.projectDir,RipartHelper.xml_Login).text
        
        if (self.login =="" or self.pwd=="" or newLogin):
            self.loginWindow.setLogin(self.login)
            self.loginWindow.exec_()

            while (result<0):      
                if self.loginWindow.cancel:
                    print "rejected"
                    self.loginWindow = None
                    result=0
                elif self.loginWindow.connect :
                    print "connect"
                    self.login = self.loginWindow.getLogin()
                    self.pwd=self.loginWindow.getPwd()
                    
                    try: 
                        client = Client(self.urlHostRipart, self.login, self.pwd)
                        profil = client.getProfil()
                        
                        if profil != None :
                            self.profil= profil
                            self.saveLogin(self.login)
                          
                            dlgInfo=FormInfo()
                            dlgInfo.textInfo.setText(u"<b>Connexion réussie au service Ripart.</b>")
                            dlgInfo.textInfo.append("<br/>Serveur : "+ self.urlHostRipart)
                            dlgInfo.textInfo.append("Login : "+  self.login)
                            dlgInfo.textInfo.append("Profil: "+ profil.titre)
                            dlgInfo.textInfo.append("Zone : "+ profil.zone.__str__())
    
                            dlgInfo.exec_()
                            
                            if dlgInfo.Accepted:
                                self.client=client
                                result= 1
                    except Exception as e:
                        result=-1
                        self.pwd=""
                        self.loginWindow.setErreur(ClientHelper.getEncodeType(e.message))
                        self.loginWindow.exec_()
                        
        else: 
            try: 
                client = Client(self.urlHostRipart, self.login, self.pwd)   
                result=1
                self.client=client
            except RipartException as e:
                print e.message
                
        return result
    
    

    def saveLogin(self,login):
        self.login=login
        RipartHelper.save_login( self.projectDir, login)
    
   
    def getOrCreateDatabase(self):
        """
        """
        dbName = self.projectFileName +"_RIPART"
        self.dbPath = self.projectDir+"/"+dbName+".sqlite"
        
        createDb=False
            
        if not os.path.isfile(self.dbPath) :
            createDb=True
            try:
                shutil.copy(self.plugin_path+"\\"+RipartHelper.ripart_files_dir+"\\"+ RipartHelper.ripart_db,
                             self.dbPath)
                self.logger.debug("copy ripart.sqlite" )
            except Exception as e:
                self.logger.error("no ripart.sqlite found in plugin directory" + e.message)
                raise e
        try:    
            self.conn= db.connect(self.dbPath)
    
            # creating a Cursor
            cur = self.conn.cursor()
           
            sql="SELECT name FROM sqlite_master WHERE type='table' AND name='Remarque_Ripart'"  
            cur.execute(sql)       
            if cur.fetchone() ==None:
                #create layer Remarque_Ripart
                RipartHelper.createRemarqueTable(self.conn)
            
            for lay in RipartHelper.croquis_layers:  
                sql="SELECT name FROM sqlite_master WHERE type='table' AND name='"+lay+"'"
                cur.execute(sql)       
                if cur.fetchone() ==None:
                    #create layer 
                    RipartHelper.createCroquisTable(self.conn,lay,RipartHelper.croquis_layers[lay])
                    
        except RipartException as e:
            self.logger.error(e.message)
            raise
        finally:
            cur.close()
            self.conn.close()
        
      
      
      
    def addRipartLayersToMap(self):
        """Add ripart layers to the current map """
        uri =QgsDataSourceURI()
        uri.setDatabase(self.projectFileName +"_RIPART.sqlite")
        
        maplayers=self.getMapLayers()
        
        ripartLayers= RipartHelper.croquis_layers
        ripartLayers[RipartHelper.nom_Calque_Remarque]="POINT"
        
        
        root = self.QgsProject.instance().layerTreeRoot()
        
        for table in RipartHelper.croquis_layers_name: 
            if table not in maplayers:
                uri.setDataSource('',  table, 'geom')
                uri.setSrid('4326')
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite') 
                vlayer.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
                QgsMapLayerRegistry.instance().addMapLayer(vlayer,False)
                                
                root.insertLayer(0,vlayer)
        
        self.mapCan.refresh()
        
           
           
            
    def getMapLayers(self):
        """Return the list of layer names which are loaded in the map"""
        
        layers = self.mapCan.layers()
        
        layerNames=[]
        maplayers={}
        for l in layers:
            layerNames.append(l.name())
            maplayers[l.name()]= l.id()
        
        return maplayers
    
    
    def getLayerByName(self,layName):
        layers = self.mapCan.layers()
   
        for l in layers:
            if l.name() == layName :
                return l
        
        return None
    
    def emptyAllRipartLayers(self):
        """Supprime toutes les remarques vide les tables de la base ripart.sqlite 
        """
        ripartLayers= RipartHelper.croquis_layers
        ripartLayers[RipartHelper.nom_Calque_Remarque]="POINT"
              
        try:
        
            self.conn= db.connect(self.dbPath)
            
            for table in ripartLayers:
                RipartHelper.emptyTable(self.conn, table)
                
            self.conn.commit()    
        except RipartException as e:
            self.logger.error(e.message)
            raise
        finally:
            self.conn.close()
        
        self.refresh_layers()
        
        
        
    def refresh_layers(self):
        """
        """
        for layer in self.mapCan.layers():
            layer.triggerRepaint()


    def addRemarques(self,rems):
        """
        """
        try:
            self.conn= db.connect(self.dbPath)
         
            i=1
  
            for remId in rems:
                RipartHelper.insertRemarques(self.conn, rems[remId])
                
                #self.progress.setValue(i + 1)
                #i+=1
       
            self.conn.commit()   
           
        except Exception as e:
            self.logger.error(e.message)
            raise
        finally:
            self.conn.close()
     
     
     
    def updateRemarqueInSqlite(self,rem):
        """Met à jour une remarque (après l'ajout d'une réponse 
        
        :param rem : la remarque à mettre à jour
        :type rem: Remarque
        """
        try:
            self.conn= db.connect(self.dbPath)
            
            sql ="UPDATE "+ RipartHelper.nom_Calque_Remarque+" SET " + \
                " Date_MAJ= '" + rem.getAttribut("dateMiseAJour") +"'," + \
                " Date_validation= '" + rem.getAttribut("dateValidation") +"'," + \
                " Réponses= '" + ClientHelper.getValForDB(rem.concatenateReponse()) +"' "\
                " WHERE NoRemarque = " + str(rem.id)
            
            cur= self.conn.cursor()
            cur.execute(sql)
            
            self.conn.commit()

        except Exception as e :
            self.logger.error(e.message)
            raise
        finally:
            cur.close()
            self.conn.close()
        
    def startProgressbar(self):  
        self.progressMessageBar = self.iface.messageBar().createMessage(u"Téléchargement des remarques en cours...")
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.progressMessageBar.layout().addWidget(self.progress)
        
        self.progress=self.progress
        
        
        
    """def getRemarqueById(self,remId):
        
        remarque= self.client.getRemarque(remId)     
        
        return remarque"""