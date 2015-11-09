# -*- coding: utf-8 -*-
'''
Created on 8 oct. 2015

@author: AChang-Wailing
'''

from core.RipartLoggerCl import RipartLogger
import time
from PyQt4 import QtCore, QtGui
from qgis.core import  QgsGeometry
from RipartHelper import RipartHelper
from core.Box import Box
from core.Client import Client
from PyQt4.QtGui import QMessageBox,QComboBox
from core.ClientHelper import ClientHelper
import core.ConstanteRipart as cst
from FormRepondre import FormRepondreDialog
import time
from qgis.gui import QgsMessageBar
from FormView import FormView


class RepondreRipart(object):
    """"Classe pour les réponses Ripart
    """
    logger=RipartLogger("RepondreRipart").getRipartLogger()
    context=None

    def __init__(self, context):
        '''
        Constructor
        '''
        self.context=context
        
        
        
    def do(self, isView=False):  
        try:
            
            activeLayer = self.context.iface.activeLayer()
            if activeLayer==None or activeLayer.name() != RipartHelper.nom_Calque_Remarque:
                self.context.iface.messageBar().pushMessage("Attention", u'Le calque "Remarque_Ripart" doit être le calque actif', level=1, duration=5)
                return
            else:
                #get selected features
                selFeats = activeLayer.selectedFeatures()
                
                if len(selFeats)==0:
                    self.context.iface.messageBar().pushMessage("Attention", u'Pas de remarque sélectionnée', level=1, duration=10)
                    return
                
                remIds=[]
                for feat in selFeats:  
                    remIds.append(feat.attribute('NoRemarque'))
                    
            res=self.context.getConnexionRipart()    
            if res==1:
                client= self.context.client
                remId=int(remIds[0])
                remarque= client.getRemarque(remId)
                
                if remarque.statut.__str__() not in cst.openStatut and not isView:  
                    mess= "Impossible de répondre à la remarque Ripart n°"+ str(remId) + \
                          ", car elle est clôturée depuis le "+ remarque.dateValidation
                          
                          
                    self.context.iface.messageBar().pushMessage("Attention",ClientHelper.getEncodeType(mess), level=1, duration=5)
                    return
               
                if remarque.autorisation not in ["RW+","RW-"] and not isView:
                    mess=u"Vous n'êtes pas autorisé à modifier la remarque Ripart n°"+ str(remId)
                    self.context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=10)
                    return
                
                if isView:
                    self.logger.debug("view remark")
                    formView= FormView()
                    formView.setRemarque(remarque)
                    formView.exec_()
                    
                else:    
                    self.logger.debug("answer to remark")               
                    formReponse= FormRepondreDialog()
                    
                    res=formReponse.setRemarque(remarque)
                 
                    r=formReponse.exec_()
                    
                    if formReponse.answer :
                        remarque.statut=formReponse.newStat
                        remMaj=client.addReponse(remarque,ClientHelper.stringToStringType(formReponse.newRep))            
                        self.context.updateRemarqueInSqlite(remMaj)
                        mess=u"de l'ajout d'une réponse à la remarque Ripart n°" + str(remId) 
                        self.context.iface.messageBar().pushMessage(u"Succès", mess, level=QgsMessageBar.INFO, duration=15)
                      

        except Exception as e:
            self.logger.error(e.message)
            raise
        
        