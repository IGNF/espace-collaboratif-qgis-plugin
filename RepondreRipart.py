# -*- coding: utf-8 -*-
'''
Created on 8 oct. 2015

@author: AChang-Wailing
'''
from __future__ import absolute_import

from builtins import str
from builtins import object
from .core.RipartLoggerCl import RipartLogger

from qgis.PyQt import QtCore, QtGui
from PyQt5.QtCore import *
from qgis.PyQt.QtWidgets import QMessageBox, QComboBox
from qgis.core import  QgsGeometry
from qgis.gui import QgsMessageBar

from .RipartHelper import RipartHelper
from .core.Box import Box
from .core.Client import Client
from .core.ClientHelper import ClientHelper
from .core import ConstanteRipart as cst
from .FormRepondre import FormRepondreDialog
from .FormView import FormView

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
        """Affichage de la fenêtre de réponse ou de la fenêtre de visualisation du signalement
        
        :param isView: true si on veut afficher la fenêtre de visualisation, false pour la fenêtre de réponse
        :type isView: boolean
        """
        try:
            
            activeLayer = self.context.iface.activeLayer()
            if activeLayer==None or activeLayer.name() != RipartHelper.nom_Calque_Signalement:
                self.context.iface.messageBar().pushMessage("Attention", u'Le calque "Signalement" doit être le calque actif', level=1, duration=5)
                return
            else:
                #get selected features
                selFeats = activeLayer.selectedFeatures()
                
                if len(selFeats)==0:
                    self.context.iface.messageBar().pushMessage("Attention", u'Pas de signalement sélectionné', level=1, duration=10)
                    return
                
       
                remIds=[]
                for feat in selFeats:  
                    remIds.append(feat.attribute('NoSignalement'))
                    
                if len(remIds)>1:
                    self.context.iface.messageBar().pushMessage("Attention", 
                                        u'Plusieurs signalements sélectionnés. Un seul sera pris en compte (signalement no='+str(remIds[0])+')',
                                        level=1, duration=10)
                    
            if  self.context.ripClient == None :
                self.context.getConnexionRipart()
                if self.context.ripClient == None : #la connexion a échoué, on ne fait rien
                    self.context.iface.messageBar().pushMessage("",u"Un problème de connexion avec le service RIPart est survenu.Veuillez rééssayer", level=2, duration=5)       
                    return
          
            
            client= self.context.client
            remId=remIds[0]
            remarque= client.getGeoRem(remId)
             
            if remarque.statut.__str__() not in cst.openStatut and not isView:  
                mess= "Impossible de répondre au signalement n°"+ str(remId) + \
                         ", car il est clôturé depuis le "+ remarque.dateValidation
                                                    
                self.context.iface.messageBar().pushMessage("Attention",ClientHelper.getEncodeType(mess), level=1, duration=5)
                return
               
            if remarque.autorisation not in ["RW","RW+","RW-"] and not isView:
                mess="Vous n'êtes pas autorisé à modifier le signalement n°"+ str(remId)
                self.context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=10)
                return
                
            if isView:
                self.logger.debug("view remark")
                formView= FormView(self.context)                
                formView.setRemarque(remarque) 
                formView.setWindowFlags(Qt.WindowStaysOnTopHint)
                formView.show()
                return formView
                    
            else:    
                self.logger.debug("answer to remark")               
                formReponse= FormRepondreDialog()
                    
                res=formReponse.setRemarque(remarque)
                 
                r=formReponse.exec_()
                    
                if formReponse.answer :
                    remarque.statut=formReponse.newStat
                    remMaj=client.addReponse(remarque,ClientHelper.stringToStringType(formReponse.newRep),
                                                ClientHelper.stringToStringType(formReponse.repTitre) ) 
                           
                    self.context.updateRemarqueInSqlite(remMaj)
                    mess="de l'ajout d'une réponse au signalement n°" + str(remId) 
                    
                    if hasattr(activeLayer, "setCacheImage"):
                        activeLayer.setCacheImage(None)
                    activeLayer.triggerRepaint()
                    activeLayer.removeSelection()
                   
                    
                    self.context.iface.messageBar().pushMessage("Succès", mess, level=2, duration=15)
               
        except Exception as e:
            self.logger.error(format(e) + ";" + str(type(e)) + " " +str(e))
            raise
        
       