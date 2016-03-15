# -*- coding: utf-8 -*-
'''
Created on 1 oct. 2015

@author: AChang-Wailing
'''
import logging
from core.RipartLoggerCl import RipartLogger

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMessageBox, QProgressBar, QApplication
from PyQt4.QtCore import *
from qgis.core import  QgsGeometry,QgsCoordinateReferenceSystem,QgsCoordinateTransform

from pyspatialite import dbapi2 as db

from RipartHelper import RipartHelper
from core.Box import Box
from core.Client import Client
from core.ClientHelper import ClientHelper
import core.ConstanteRipart as cst


class ImporterRipart(object):
    """Importation des remarques dans le projet QGIS
    """
    logger=RipartLogger("ImporterRipart").getRipartLogger()
    
    #le contexte de la carte
    context=None
    
    #barre de progression (des remarques importées)
    progressMessageBar=None
    progress=None
    progressVal=0


    def __init__(self,context):
        """
        Constructor
        Initialisation du contexte et de la progressbar
        
        :param context: le contexte de la carte actuelle
        :type context: Contexte
        """
        self.context=context
   
        self.progressMessageBar = self.context.iface.messageBar().createMessage(u"Placement des remarques sur la carte...")
        self.progress = QProgressBar()
        self.progress.setMaximum(200)        
        self.progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)     
        self.progressMessageBar.layout().addWidget(self.progress)
     
     
    def doImport(self):
        """Téléchargement et import des remarques sur la carte   
        """
        self.logger.debug("doImport")
        
        params={}    #paramètres pour la requête au service Ripart
        
        filtreLay=None
        
        if  self.context.ripClient == None :
            self.context.getConnexionRipart()
            if self.context.ripClient == None : #la connexion a échouée, on ne fait rien
                self.context.iface.messageBar().pushMessage("",u"Un problème de connexion avec le service RIPart est survenu.Veuillez rééssayer", level=2, duration=5)            
                return
        
        self.context.addRipartLayersToMap()
        
        
        #filtre spatial
        filtre=  RipartHelper.load_CalqueFiltrage(self.context.projectDir).text
              
        if (filtre!=None):    
            self.logger.debug("Spatial filter :"+filtre)
            
            filtreLay=self.context.getLayerByName(filtre)
            bbox=self.getSpatialFilterBbox(filtre,filtreLay)
            if bbox==-999:
                return
            
        else:
            message="Impossible de déterminer dans le fichier de paramétrage Ripart, le nom du calque à utiliser pour le filtrage spatial.\n\n" + \
                    "Souhaitez-vous poursuivre l'importation des remarques Ripart sur la France entière ? "+\
                    "(Cela risque de prendre un temps long.)"
            if self.noFilterWarningDialog(message):
                bbox= None
            else : 
                return
   
        QApplication.setOverrideCursor(Qt.BusyCursor)

        #vider les tables ripart
        self.context.emptyAllRipartLayers()
              
        pagination =RipartHelper.load_ripartXmlTag(self.context.projectDir, RipartHelper.xml_Pagination,"Map").text
        if pagination ==None :
            pagination = RipartHelper.defaultPagination
           
        date= RipartHelper.load_ripartXmlTag(self.context.projectDir, RipartHelper.xml_DateExtraction,"Map").text
            
        date= RipartHelper.formatDate(date)
 
        groupFilter=RipartHelper.load_ripartXmlTag(self.context.projectDir,RipartHelper.xml_Group,"Map").text
            
        if groupFilter=='true':
            groupId=self.context.profil.geogroupe.id
                
            params['group'] = str(groupId)
           
        self.context.client.setIface(self.context.iface)
            
            
        params['territory'] = self.context.profil.zone
        if bbox !=None:
            params['box'] = bbox.boxToString()
            
        params['pagination'] = pagination
        params['updatingDate'] = date
           
            
        rems = self.context.client.getGeoRems(params)
        #rems = self.context.client.getRemarques(self.context.profil.zone, bbox, pagination,date, groupId)

        self.context.iface.messageBar().pushWidget(self.progressMessageBar, self.context.iface.messageBar().INFO)
        self.progress.setValue(100)
           

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
                
        cnt= len(remsToKeep)
    
        try:  
            i=100
            try:
                self.context.conn= db.connect(self.context.dbPath)
    
                for remId in remsToKeep:
                    RipartHelper.insertRemarques(self.context.conn, remsToKeep[remId])
                    i+=1
                    self.progressVal= int(round(i*100/cnt))
                    self.progress.setValue(self.progressVal)
  
                self.context.conn.commit()   
                   
            except Exception as e:
                self.logger.error(e.message)
                raise
            finally:
                self.context.conn.close()
                
            if cnt>1:                
                remLayer=self.context.getLayerByName(RipartHelper.nom_Calque_Remarque)
                remLayer.updateExtents()
                box = remLayer.extent()
                self.setMapExtent(box)
                    
            elif filtreLay!=None:
                box=filtreLay.extent()
                self.setMapExtent(box)

            #Résultat 
            self.showImportResult(cnt)
               
                
        except Exception as e:
            raise

        finally:
            self.context.iface.messageBar().clearWidgets()   
            QApplication.setOverrideCursor(Qt.ArrowCursor)
                
     
    def getSpatialFilterBbox(self,filtre,filtreLay):
        """Retourne la boundingbox du filtre spatial
        
        :param filtre: le nom du calque utilisé comme filtre
        :type: string
        
        :param filtreLay: le layer correspondant 
        :type filtreLay: QgsVectorLayer
        """
        bbox=None
        
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
                    return -999
                 
        else:  
            #emprise=> getExtent + transform in 4326 crs 
            filtreExtent= RipartHelper.getBboxFromLayer(filtreLay) 
                    
            bbox= Box(filtreExtent.xMinimum(),filtreExtent.yMinimum(),filtreExtent.xMaximum(),filtreExtent.yMaximum()) 
            
        return bbox  
        
    def noFilterWarningDialog(self,message):
        """Avertissement si pas de filtre spatial
        """       
        message=ClientHelper.getEncodeType(message)
        reply= QMessageBox.question(None,'IGN Ripart',message,QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            return True
        else : 
            return False
        
    def setMapExtent(self,box):
        """set de l'étendue de la carte
        
        :param box: bounding box
        """
        source_crs=QgsCoordinateReferenceSystem(RipartHelper.epsgCrs)
                    
        mapCrs=self.context.mapCan.mapRenderer().destinationCrs().authid()
        dest_crs=QgsCoordinateReferenceSystem(mapCrs)
                    
        transform = QgsCoordinateTransform(source_crs, dest_crs)
        new_box = transform.transformBoundingBox(box)
                    
        #distance pour le buffer: 10% de la distance minimale (hauteur ou largeur)
        dist= min(new_box.width(),new_box.height())*0.1  
        #zoom sur la couche Remarque_Ripart
        self.context.mapCan.setExtent(new_box.buffer(dist))
        
        
    def showImportResult(self,cnt):
        """Résultat de l'import
        
        :param cnt: le nombre de remarques importées
        :type cnt: int
        """
        
        self.context.iface.messageBar().clearWidgets() 
        QApplication.setOverrideCursor(Qt.ArrowCursor)
                
        submit= self.context.countRemarqueByStatut(cst.STATUT.submit.__str__())
        pending= self.context.countRemarqueByStatut(cst.STATUT.pending.__str__()) + \
                self.context.countRemarqueByStatut(cst.STATUT.pending0.__str__()) + \
                self.context.countRemarqueByStatut(cst.STATUT.pending1.__str__()) + \
                self.context.countRemarqueByStatut(cst.STATUT.pending2.__str__())
        reject =self.context.countRemarqueByStatut(cst.STATUT.reject.__str__()) 
        valid = self.context.countRemarqueByStatut(cst.STATUT.valid.__str__()) + self.context.countRemarqueByStatut(cst.STATUT.valid0.__str__())
                
        resultMessage="Extraction réussie avec succès de " + str(cnt)+ " remarque(s) RIPart depuis le serveur \n" +\
                    "avec la répartition suivante : \n\n"+\
                    "- "+ str(submit) +" remarque(s) nouvelle(s).\n" +\
                    "- "+ str(pending) +" remarque(s) en cours de traitement.\n" +\
                    "- "+ str(valid) +" remarque(s)  validée(s).\n" +\
                    "- "+ str(reject) +" remarque(s) rejetée(s).\n" 
                              
        resultMessage= ClientHelper.getEncodeType(resultMessage)
                              
        RipartHelper.showMessageBox(resultMessage)    
    
    