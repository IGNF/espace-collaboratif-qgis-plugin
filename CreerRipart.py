# -*- coding: utf-8 -*-
'''
Created on 27 oct. 2015

@author: AChang-Wailing
'''
from __future__ import absolute_import
from builtins import str
from builtins import object
from .core.RipartLoggerCl import RipartLogger
from .FormCreerRemarque import FormCreerRemarque
from .RipartHelper import RipartHelper
from .core.Remarque import Remarque



class CreerRipart(object):
    """
    Classe pour la création d'une nouvelle remarque ripart
    
    """
    logger=RipartLogger("CreerRipart").getRipartLogger()
    context=None

    def __init__(self, context):
        """
        Constructor
        """
        self.context=context
        
       
    def do(self): 
        """Création de la nouvelle remarque
        """
        self.context.iface.messageBar().clearWidgets()

        try:
            hasSelectedFeature=self.context.hasMapSelectedFeatures()
       
            if  not hasSelectedFeature:
                RipartHelper.showMessageBox(u"Aucun object sélectionné.\nIl est donc impossible de déterminer le point d'application du nouveau signalement à créer.")
                return    #si pas d'objet sélectionné, on arrête le processus
            
 
            if  self.context.ripClient == None :
                self.context.getConnexionRipart()
                if self.context.ripClient == None : #la connexion a échoué, on ne fait rien
                    self.context.iface.messageBar().pushMessage("",u"Un problème de connexion avec le service RIPart est survenu.Veuillez rééssayer", level=2, duration=5)            
                    return
            
            
            #Création des croquis à partir de la sélection de features
            croquisList=self.context.makeCroquisFromSelection()
                       
            self.logger.debug(str(len(croquisList)) + u" croquis générés")
        
            #ouverture du formulaire de création de la remarque
            formCreate= FormCreerRemarque(context=self.context,croquisCnt=len(croquisList))
            r=formCreate.exec_()
            
            if formCreate.cancel:
                return
            
            else:
                #création de la remarque
                self._createNewRemark(formCreate,croquisList)
              
        except Exception as e:
            self.logger.error(format(e))
            self.context.iface.messageBar().pushMessage("", u"Problème dans la création de signalement(s)",level=2, duration =15)  
            
         
        
    def _createNewRemark(self,formCreate,croquisList):
        """Création d'une nouvelle remarque (requête au service ripart)
        
        :param formCreate: le formulaire de création de la remarque
        :type formCreate: FormCreerRemarque
        
        :param croquisList: la liste des croquis associés à la remarque
        :type croquisList: list d'objet Croquis
        """
  
        try:
            tmpRem= Remarque()
                
            tmpRem.setCommentaire(formCreate.textEditMessage.toPlainText())
            
            selectedThemes= formCreate.getSelectedThemes()
            
            RipartHelper.save_preferredThemes(self.context.projectDir,selectedThemes)
            
            tmpRem.addThemeList(selectedThemes)  
            
            #liste contenant les identifiants des nouvelles remarques créées
            listNewRemIds=[]
            
            #si on doit attacher un document
            if formCreate.optionWithAttDoc():
                tmpRem.addDocument(formCreate.getAttachedDoc())
           
            #création d'une seule remarque
            if formCreate.isSingleRemark():  
                remarqueNouvelle=self._prepareAndSendRemark(tmpRem,croquisList,formCreate.optionWithCroquis())
                if remarqueNouvelle==None:
                    self.context.iface.messageBar().pushMessage("", u"Une erreur est survenue dans la création du signalement ",level=2, duration =15)  
                     
                listNewRemIds.append(remarqueNouvelle.id)        
            
            #création de plusieurs remarques  
            else:             
                listNewRemIds=[]
                
                for cr in croquisList:                
                    tmpRem.clearCroquis()
                    remarqueNouvelle=self._prepareAndSendRemark(tmpRem,[cr],formCreate.optionWithCroquis())
                    if remarqueNouvelle==None:                 
                        self.context.iface.messageBar().pushMessage("", u"Une erreur est survenue dans la création d'un signalement",level=2, duration =15)  
                        continue
                    
                    listNewRemIds.append(remarqueNouvelle.id)
   
            self.context.refresh_layers()
          
            RipartHelper.showMessageBox(u"Succès de la création de " + str(len(listNewRemIds)) + u" nouveau(x) signalement(s)") 
             
        except Exception as e:
            self.logger.error("in _createNewRemark "+ format(e))
        
        finally:
            self.context.conn.close()   
            
            
            
            
    def _prepareAndSendRemark(self,tmpRem,croquisList,optionWithCroquis): 
        """Trouve la position de la remarque, ajoute les croquis et envoie la requête au service Ripart
        
        :param tmpRem: remarque temporaire
        :type tmpRem: Remarque
        
        :param croquisList: la liste de croquis à ajouter à la remarque
        :type croquisList: List
        
        :param optionWithCroquis: option d'ajouter ou non les croquis à la remarque
        :type optionWithCroquis: boolean
        
        :return: La Remarque créée
        :rtype: Remarque
        """
        
        client= self.context.client
        
        positionRemarque=self.context.getPositionRemarque(croquisList)
                    
        if positionRemarque==None:  
            self.logger.error("error in _createRemark: positionRemarque not created")
            return None
        
        tmpRem.setPosition(positionRemarque)
                    
        if optionWithCroquis:
            tmpRem.addCroquisList(croquisList)
                   
        #create new remark (ripart service)
        remarqueNouvelle=client.createRemarque(tmpRem) 
        
        
        self.logger.info(u"Succès de la création du nouveau signalement n°" + str(remarqueNouvelle.id))
        
        RipartHelper.insertRemarques(self.context.conn, remarqueNouvelle)
        self.context.conn.commit()
            
        return remarqueNouvelle
                    