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
from Magicwand import Magicwand
from RipartHelper import RipartHelper

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormView_base.ui'))

context=None
remarqueId=None

class FormView(QtGui.QDialog, FORM_CLASS):
    """
    Forme de visualisation de l'historique de la remarque + sélection/déselection croquis + ouverture document joint 
    """
    selCroquis=None
    
    logger=RipartLogger("FormView").getRipartLogger()

    def __init__(self,  context):
        '''
        Constructor
        '''
        super(FormView, self).__init__(None)
        
        self.setupUi(self)
      
        self.context= context
              
        self.btnCroquis.clicked.connect(self.toggleCroquis)
        
        self.textEditCntCroquisDetail.setFrameStyle(QtGui.QFrame.NoFrame)
        self.textEditCntCroquisDetail.viewport().setAutoFillBackground(False)
        
        self.btnDoc.clicked.connect(self.openDoc)
    
       
        
    def setRemarque(self,remarque):
        try:
            self.lblMessage.setText(u"Message de la remarque n°" + remarque.id)
            statutIndex=cst.statuts().index(remarque.statut )
            self.textStatut.setText( cst.statutLibelle[statutIndex])
            self.textMessage.setText(ClientHelper.getEncodeType(remarque.commentaire))
            self.textOldRep.setHtml(ClientHelper.getEncodeType(remarque.concatenateReponseHTML()))
            self.remarqueId= remarque.id
            
            self.doc=remarque.getFirstDocument()
            self.btnDoc.setText("Pas de document joint")
            if self.doc !="":
                self.btnDoc.setText("Voir document joint")
                self.btnDoc.setEnabled(True)
            
        except Exception as e:
            self.logger.error("setRemarque")
            raise e  
            
        
    def toggleCroquis(self):
        if self.selCroquis == None:
            self.selectCroquis()
        else:
            self.deselectCroquis()
            self.selCroquis = None
        
    
    
    def selectCroquis(self):     
        nbCroquis=0
        cntMessage=""
        try:        
            self.selCroquis=self.context.getCroquisForRemark(self.remarqueId,{})
            
            for cr in self.selCroquis:
                lay=self.context.getLayerByName(cr) 
                lay.setSelectedFeatures( self.selCroquis[cr])
                
                nbCroquis+=len(self.selCroquis[cr])
                
                cntMessage+=str(len(self.selCroquis[cr]))+ " "+ cr +"\n"
            
            self.lblCntCroquis.setText(u"Nombre de croquis sélectionnés: "+  str(nbCroquis))
            
            self.textEditCntCroquisDetail.setText(cntMessage)
           
        except Exception as e:
            self.logger.error("selectCroquis "+ e.message)
      
            
    def deselectCroquis(self):
        try:
            for cr in self.selCroquis:
                lay=self.context.getLayerByName(cr) 
                lay.deselect( self.selCroquis[cr])
            
            self.lblCntCroquis.setText(u"Nombre de croquis sélectionnés: -")
            self.textEditCntCroquisDetail.setText(u"")
            
        except Exception as e:
            self.logger.error("deselectCroquis "+ e.message)
    
    
    def openDoc(self):
        #os.startfile(self.doc)
        RipartHelper.open_file(self.doc)