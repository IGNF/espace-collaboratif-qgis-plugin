# -*- coding: utf-8 -*-
import os

from qgis.PyQt import QtGui, uic, QtWidgets 
from qgis.PyQt.QtWidgets import QMessageBox
from PyQt5.QtCore import *
from qgis.core import *

from .core.RipartLoggerCl import RipartLogger
from .core.Client import Client
from .core import ConstanteRipart
from .core import Profil
from .core.ClientHelper import ClientHelper

from .FormInfo import FormInfo

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormConnexion_dialog_base.ui'))


class FormConnexionDialog(QtWidgets.QDialog, FORM_CLASS):
    """ Fenêtre de login
    """
    context = None
    urlhost = ""
    connect = False
    cancel = False
    
    #logger
    logger = RipartLogger("FormConnexionDialog").getRipartLogger()
    
    def __init__(self, parent=None):
        """Constructor."""
        
        super(FormConnexionDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
   
        self.textError.setVisible(False)
           
        self.btnConnect.clicked.connect(self.connectToService)
      
        self.btnCancel.clicked.connect(self.cancel)

    def setLogin(self,login):
        self.lineEditLogin.setText(login)  
    
    def getLogin(self):
        return self.lineEditLogin.text()
    
    def getPwd(self):
        return self.lineEditPwd.text()
    
    def setErreur(self,message):
        self.textError.setText(message)
        self.textError.setVisible(True)
        
    def getEvent(self):
        """Retour de différents codes suivant l'action effectuée
        """
        if self.cancel:
            return 0
        elif self.connect:
            return 1
        else:
            return -1    
    
    @pyqtSlot()
    def connectToService(self):
        """Connexion au service Ripart
        """
        
        self.logger.debug("connectToService")

        login = self.lineEditLogin.text()
        pwd = self.lineEditPwd.text()
        
        if len(login) == 0 or len(pwd) == 0:
            QMessageBox.information(self, "Ripart", "Veuillez saisir votre login et votre mot de passe")
        else:
            self.cancel = False
            self.connect = True
            self.close()

    def setContext(self,context):
        """Set du contexte
        """
        self.context = context
        self.lineEditLogin.setText(context.login)
        self.lineEditPwd.setText("")
        self.setUrlHost(context.urlHostRipart)  

    def setUrlHost(self,urlhost):
        """Set de l'url du service ripart
        """
        self.urlhost = urlhost

    @pyqtSlot()
    def cancel(self):
        self.cancel = True
        self.connect = False
        self.close()
