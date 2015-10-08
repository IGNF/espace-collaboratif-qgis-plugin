# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RipartPluginDialog
                                 A QGIS plugin
 IGN_Ripart
                             -------------------
        begin                : 2015-01-21
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Alexia Chang-Wailing/IGN
        email                : a
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import logging
import core.RipartLogger 

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox


from PyQt4.QtCore import *


from core.Client import Client

from core import ConstanteRipart
from core import Profil
from core.ClientHelper import ClientHelper
#from Contexte import Contexte
from qgis.core import *

from FormInfo import FormInfo

"""import sys 
sys.path.append(r'D:\eclipse\plugins\org.python.pydev_3.9.1.201501081637\pysrc') """


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'FormConnexion_dialog_base.ui'))


class FormConnexionDialog(QtGui.QDialog, FORM_CLASS):
    
    context= None
    urlhost =""
    connect=False
    cancel=False
    
    #logger
    logger=logging.getLogger("FormConnexionDialog")
    
    def __init__(self, parent=None):
        """Constructor."""
        super(FormConnexionDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
   
        self.lblErreur.setVisible(False)
           
        self.btnConnect.clicked.connect(self.connectToService)
      
        self.btnCancel.clicked.connect(self.cancel)
     
    
    def setLogin(self,login):
        self.lineEditLogin.setText(login)  
    
    def getLogin(self):
        return self.lineEditLogin.text()
    
    def getPwd(self):
        return self.lineEditPwd.text()
    
    
    def setErreur(self,message):
        self.lblErreur.setText(message)
        self.lblErreur.setVisible(True)
        
        
    def getEvent(self):
        if self.cancel :
            return 0
        elif self.connect:
            return 1
        else :
            return -1    
    
    @pyqtSlot()
    def connectToService(self):
        self.logger.debug("connectToService")

        login= self.lineEditLogin.text()
        pwd= self.lineEditPwd.text()
        
        if len(login)==0 or len(pwd)==0 :
            QMessageBox.information(self,"Ripart","Veuillez saisir votre login et votre mot de passe")
        else:
            self.cancel=False
            self.connect=True
            
            self.close()
        """self.lblErreur.setVisible(False)
              
        login= self.lineEditLogin.text()
        pwd= self.lineEditPwd.text()

        if len(login)==0 or len(pwd)==0 :
            QMessageBox.information(self,"Ripart","Veuillez saisir votre login et votre mot de passe")
        else:
            
            #connexion au serveur
            try:
                
                client = Client(self.urlhost, login, pwd)
                
                profil=client.getProfil()
                
                if profil != None :
                    self.context.profil= profil
                    self.context.saveLogin(login)
                    
                    
                self.setEnabled(False)
               
                dlgInfo=FormInfo()
                dlgInfo.textInfo.setText(u"<b>Connexion réussie au service Ripart.</b>")
                dlgInfo.textInfo.append("<br/>Serveur : "+ self.urlhost)
                dlgInfo.textInfo.append("Login : "+  login)
                dlgInfo.textInfo.append("Profil: "+ profil.titre)
                dlgInfo.textInfo.append("Zone : "+ profil.zone.__str__())
                
             
                r=dlgInfo.exec_()
               
                #r=QMessageBox.information(self,"Ripart connexion",self.urlhost+'\n'+profil.titre)
                if dlgInfo.Accepted:
                    self.close()
                    self.setEnabled(True)
                    self.context.login=login
                    self.context.pwd=pwd
                    self.context.client= client
                    #self.context.addRipartLayersToMap()
                               
            except Exception as e:       
                #self.lblErreur.setText(ClientHelper.getEncodeType(str(e)))
                self.lblErreur.setText(ClientHelper.getEncodeType(e.message))
                self.lblErreur.setVisible(True)
                #QMessageBox.information(self,"IGN Ripart - ERREUR",ClientHelper.getEncodeType(str(e)))
        """      
              
            
        
    def setContext(self,context):
        self.context=context
        self.lineEditLogin.setText(context.login)
        self.lineEditPwd.setText("")
        self.setUrlHost(context.urlHostRipart)  
    
    def setUrlHost(self,urlhost):
        self.urlhost = urlhost
  
        
    @pyqtSlot()
    def cancel(self):
        #self.reject
        self.cancel=True
        self.connect=False
        self.close()
       