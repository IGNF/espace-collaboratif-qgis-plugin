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

from qgis.core import QgsDataSourceURI,QgsVectorLayer, QgsMapLayerRegistry

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
    
 
    #le répertoire du projet qgis
    projectDir= ""    
    #le nom du fichier (projet qgis)
    projectFileName=""
    
    #répertoire du plugin
    plugin_path = os.path.dirname(os.path.realpath(__file__))
    
    #fichier xml de configuration
    ripartXmlFile=""
    
    #
    QObject= None
    
    #map canvas,la carte courante
    mapCan = None
    
    #Le système géodésique employé par le service Ripart.
    spatialRef= None
    
    conn=None

    logger=None
    

    def __init__(self, QObject,QgsProject):
        '''
        Constructor
        ''' 
        self.QObject=QObject
        self.mapCan = QObject.iface.mapCanvas()
        
        self.iface= QObject.iface
        
        self.login=""
        self.pwd=""
        self.urlHostRipart=""
        
        self.logger=RipartLogger("Contexte").getRipartLogger()

        #self.logger.debug("test logger Contexte")
        self.spatialRef = QgsCoordinateReferenceSystem( RipartHelper.epsgCrs, QgsCoordinateReferenceSystem.EpsgCrsId)
        
        try:
            #set du répertoire et fichier du projet qgis
            self.setProjectParams(QgsProject)
           
            #contrôle l'existence du fichier de configuration
            self.checkConfigFile()      
            
            self.getOrCreateDatabase()
            
            self.addRipartLayersToMap()
            
        except RipartException as e:
            #self.logger.setLevel(logging.DEBUG)
            self.logger.debug(e.message)
   
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
            
        elif  (Contexte.instance.projectDir!= QgsProject.instance().homePath() or
              Contexte.instance.projectFileName!=ntpath.basename(QgsProject.instance().fileName())) :
            Contexte.instance = Contexte(QObject,QgsProject)
            Contexte.instance.logger.debug("nouvelle instance de contexte créée")
       
        
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

            self.iface.messageBar().pushMessage("Attention", u"Votre projet QGIS doit être enregistré avant de pouvoir utiliser l'extension RIPart", level=1)
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
        self.logger.debug("getConnexionRipart")
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
    
    

    def saveLogin(self,login):
        self.login=login
        RipartHelper.save_login( self.projectDir, login)
    
   
    def getOrCreateDatabase(self):
        """
        """
        dbName = self.projectFileName +"_RIPART"
        dbPath = self.projectDir+"/"+dbName+".sqlite"
        
        createDb=False
            
        if not os.path.isfile(dbPath) :
            createDb=True
            try:
                shutil.copy(self.plugin_path+"\\"+RipartHelper.ripart_files_dir+"\\"+ RipartHelper.ripart_db,
                             dbPath)
                self.logger.debug("copy ripart.sqlite" )
            except Exception as e:
                self.logger.error("no ripart.sqlite found in plugin directory" + e.message)
                raise e
            
        self.conn= db.connect(dbPath)

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
    
        cur.close()
        self.conn.close()
        
      
    def addRipartLayersToMap(self):
        """Add ripart layers to the current map """
        uri =QgsDataSourceURI()
        uri.setDatabase(self.projectFileName +"_RIPART.sqlite")
        
        maplayers=self.getMapLayers()
        
        ripartLayers= RipartHelper.croquis_layers
        ripartLayers[RipartHelper.nom_Calque_Remarque]="POINT"
        
        for table in ripartLayers: 
            if table not in maplayers:
                uri.setDataSource('',  table, 'geom')
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')    
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        
        
            
    def getMapLayers(self):
        """Return the list of layer names which are loaded in the map"""
        
        layers = self.QObject.iface.mapCanvas().layers()
        layerNames=[]
        for l in layers:
            layerNames.append(l.name())
        
        return layerNames
             