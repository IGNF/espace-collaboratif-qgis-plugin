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
import os.path
from  RipartHelper import  RipartHelper
import logging
import core.RipartLogger 
#from FormConnexion_dialog import FormConnexionDialog
import ntpath
from core.Profil import Profil

class Contexte(object):
    '''
    classdocs
    '''
    login=""
    pwd=""
    urlHostRipart=""
    
    profil=None
    
    mapCan = None
    
    #qgis project dir
    projectDir= ""    
    
    projectFileName=""
    
    instance =None
    
    QObject= None
    
    ripartXmlFile=""
    
    logger=logging.getLogger("Contexte")
    

    def __init__(self, QObject,QgsProject):
        '''
        Constructor
        '''
        self.QObject=QObject
        self.mapCan = QObject.iface.mapCanvas()
        
        self.login=""
        self.pwd=""
        self.urlHostRipart=""
        
        self.setProjectParams(QgsProject)
        
        
       
        checkConfig=self.checkConfigFile()
        
        

      
    @staticmethod    
    def getInstance(QObject=None,QgsProject=None):
        if not Contexte.instance:
            Contexte.instance = Contexte(QObject,QgsProject)
        Contexte.instance.setProjectParams(QgsProject)
        return Contexte.instance
    
    
    def setProjectParams(self,QgsProject):
        self.projectDir=QgsProject.instance().homePath()
        self.projectFileName=ntpath.basename(QgsProject.instance().fileName())
        
    
    def checkConfigFile(self):
        
        #TODO
        """if not os.path.isfile(self.projectDir+"\\"+ RipartHelper.nom_Fichier_Parametres_Ripart) :
            try:
                 os.path.c
            except Exception e:
        """       
        return True    
    
    def setConnexionRipartParam(self):
        self.logger.debug("getConnexionRipart")
        ret=""
        if len(self.projectFileName)==0:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning !")
            msgBox.setText("dsdqds")
            ret = msgBox.exec_()
        else:
            self.urlHostRipart = RipartHelper.load_urlhost(self.projectDir).text;
            self.login = RipartHelper.load_login(self.projectDir).text;
        
        return ret
    
    """def getConnexionRipart(self,loginWindow):
        self.logger.debug("getConnexionRipart")
        
        if len(self.projectFileName)==0:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning !")
            msgBox.exec_()
            
        
        self.urlHostRipart = RipartHelper.load_urlhost(self.projectDir);
        self.login = RipartHelper.load_login(self.projectDir).text;
    
        
        loginWindow.lineEditLogin.setText(self.login)
        
        loginWindow.setUrlHost(self.urlHostRipart)
        
        loginWindow.setUrlHost(self.urlHostRipart)
        
        loginWindow.show()
        
        
        
        #loginWindow= FormConnexionDialog
        
        #loginWindow.lineEditLogin.text("zzz")
        
        """