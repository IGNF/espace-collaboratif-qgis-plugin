# -*- coding: utf-8 -*-
'''
Created on 1 oct. 2015

@author: AChang-Wailing
'''
import logging
from core.RipartLoggerCl import RipartLogger
from PyQt4 import QtCore, QtGui
from qgis.core import  QgsGeometry
from RipartHelper import RipartHelper
from core.Box import Box
from core.Client import Client
from PyQt4.QtGui import QMessageBox, QProgressBar
from core.ClientHelper import ClientHelper
from PyQt4.QtCore import *
import time

class ImporterRipart(object):
    """Importation des remarques dans le projet QGIS
    """
   

    logger=RipartLogger("ImporterRipart").getRipartLogger()
    
    context=None
    
    progressMessageBar=None
    progress=None

    def __init__(self,context):
        '''
        Constructor
        '''
        self.context=context
        
        
        """self.progressMessageBar = self.context.iface.messageBar().createMessage(u"Téléchargemenrt de remarques en cours...")
        self.progress = QProgressBar()
        self.progress.setMaximum(10)
        self.progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.progressMessageBar.layout().addWidget(self.progress)
        
        self.context.progress=self.progress"""
        
        """for i in range(10):
            time.sleep(1)
            self.progress.setValue(i + 1)
        """
     
    def doImport(self):
        self.logger.debug("doImport")
        
        filtreLay=None
        
        res=self.context.getConnexionRipart()
        
        self.context.addRipartLayersToMap()
        if not res:
            return
        else: 
        
          
            filtre=  RipartHelper.load_CalqueFiltrage(self.context.projectDir).text
              
            if (filtre!=None):    
                self.logger.debug("Spatial filter :"+filtre)
                filtreLay=self.context.getLayerByName(filtre)
                if filtreLay ==None: 
                    message="La carte en cours ne contient pas le calque '" + \
                            filtre + \
                            "' définit pour être le filtrage spatial (ou le calque n'est pas activé).\n\n"+\
                            "Souhaitez-vous poursuivre l'importation des remarques Ripart sur la France entière ? "+\
                            "(Cela risque de prendre un temps long.)"
                    message=ClientHelper.getEncodeType(message)
                    reply= QMessageBox.question(None,'IGN Ripart',message,QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        bbox=None
                    else : 
                        return
                 
                else:  
                    #emprise=> getExtent + trabnsfrom in 4326 crs 
                    #filtreExtent= filtreLay.extent()
                    filtreExtent= RipartHelper.getBboxFromLayer(filtreLay) 
                    
                    bbox= Box(filtreExtent.xMinimum(),filtreExtent.yMinimum(),filtreExtent.xMaximum(),filtreExtent.yMaximum())
            else:
                bbox= None
   
            #vider les tables ripart
            self.context.emptyAllRipartLayers()
            
            pagination =RipartHelper.load_ripartXmlTag(self.context.projectDir, RipartHelper.xml_Pagination).text
            date= RipartHelper.load_ripartXmlTag(self.context.projectDir, RipartHelper.xml_DateExtraction).text
            groupFilter=RipartHelper.load_ripartXmlTag(self.context.projectDir,RipartHelper.xml_Group).text
            
            if groupFilter=='true':
                groupId=self.context.profil.geogroupe.id
            else:
                groupId=-1
        
            #self.context.iface.messageBar().pushWidget(self.progressMessageBar, self.context.iface.messageBar().INFO)
           
            #self.context.progress.setMaximum( len(remsToKeep))  
            #self.context.startProgressbar()
            #self.context.iface.messageBar().pushWidget( self.context.progressMessageBar, self.context.iface.messageBar().INFO)
            
            rems = self.context.client.getRemarques(self.context.profil.zone, bbox, pagination,date, groupId)
                
         
            
            #Filtrage spatial affiné des remarques.
            if bbox!=None:
                remsToKeep ={}

                for key in rems:
                    ptx= rems[key].position.longitude
                    pty = rems[key].position.latitude
                    pt ="POINT("+ ptx + " "+ pty +")"
                    ptgeom= QgsGeometry.fromWkt(pt)
                    
                    if RipartHelper.isInGeometry(ptgeom, filtreLay):
                        remsToKeep[key]=rems[key]
            else:
                remsToKeep= rems
                
            #self.context.zoom(remsToKeep)        
            
            try:  
                         
                self.context.addRemarques(remsToKeep)
                
     
            except Exception as e:
                raise

            finally:
                self.context.iface.messageBar().clearWidgets()   
            
        
        
        