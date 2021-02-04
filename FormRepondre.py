# -*- coding: utf-8 -*-
'''
Created on 8 oct. 2015

@author: AChang-Wailing
'''
from __future__ import absolute_import
from builtins import range
import os

from qgis.PyQt import QtGui, uic, QtWidgets
from qgis.PyQt.QtWidgets import QMessageBox
from PyQt5.QtCore import *
from PyQt5.Qt import  QDialogButtonBox

from .core.RipartLoggerCl import RipartLogger 
from .core import ConstanteRipart as cst
from .core.ClientHelper import ClientHelper


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormRepondre_base.ui'))


class FormRepondreDialog(QtWidgets.QDialog, FORM_CLASS):
    """
    Formulaire de réponse à une remarque
    """
    
    answer= False
    cancel = True
    newRep =""
    newStat =""
    repTitre = ""

    def __init__(self, parent=None):
        """Constructor."""
        
        super(FormRepondreDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
         
        self.btnSend.clicked.connect(self.sendResponse)
        self.btnCancel.clicked.connect(self.cancel)
        self.btnCancel.button(QDialogButtonBox.Cancel).setText("Annuler")
        
        for i in range(0,9):
            if cst.statutLibelle[i]!="En attente de validation":
                self.cboxStatut.addItem(cst.statutLibelle[i],i)
          
        
    
    def setRemarque(self,remarque):
        self.lblMessage.setText(u"Message de la remarque n°" + remarque.id);
        self.setStatut(remarque.statut)
        self.textMessage.setText(ClientHelper.notNoneValue(remarque.commentaire))
        self.textOldRep.setHtml(ClientHelper.notNoneValue(remarque.concatenateReponseHTML()))
     
        
    def setStatut(self,statut):
        st=[i for i in range(len(cst.statutLibelle)) if cst.statuts()[i]==statut]
        self.cboxStatut.setCurrentIndex(st[0])
      
        
    def sendResponse(self):
        self.cancel=False
        self.answer=True
        self.newRep=self.textNewRep.toPlainText()
        self.newStat= cst.statuts()[self.cboxStatut.currentIndex()]
        self.repTitre = self.textTitre.text()
        self.close()
        
        
    def cancel(self):
        self.cancel=True
        self.answer=False
        self.close()
        
        