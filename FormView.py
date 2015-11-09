# -*- coding: utf-8 -*-
'''
Created on 9 nov. 2015

@author: AChang-Wailing
'''
import os
import logging
from core.RipartLoggerCl import RipartLogger 
from PyQt4 import QtGui, uic
import core.ConstanteRipart as cst
from core.ClientHelper import ClientHelper


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormView_base.ui'))


class FormView(QtGui.QDialog, FORM_CLASS):
    """Forme de visualisation de l'historique de la remarque
    """


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(FormView, self).__init__(parent)
        
        self.setupUi(self)
        
    
    
    def setRemarque(self,remarque):
        self.lblMessage.setText(u"Message de la remarque n°" + remarque.id)
        statutIndex=cst.statuts.index(remarque.statut )
        self.textStatut.setText( cst.statutLibelle[statutIndex])
        self.textMessage.setText(ClientHelper.getEncodeType(remarque.commentaire))
        self.textOldRep.setHtml(ClientHelper.getEncodeType(remarque.concatenateReponseHTML()))
     
        
  