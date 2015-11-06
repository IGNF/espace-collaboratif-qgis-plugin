# -*- coding: utf-8 -*-
'''
Created on 27 oct. 2015

@author: AChang-Wailing
'''
from core.RipartLoggerCl import RipartLogger
from core.RipartLoggerCl import RipartLogger
from FormCreerRemarque import FormCreerRemarque
from RipartHelper import RipartHelper
from core.Remarque import Remarque

class CreerRipart(object):
    '''
    classdocs
    '''
    logger=RipartLogger("CreerRipart").getRipartLogger()
    context=None

    def __init__(self, context):
        '''
        Constructor
        '''
        self.context=context
        
        
        
        
    def do(self): 
        self.context.iface.messageBar().clearWidgets()

        try:
            hasSelectedFeature=self.context.hasMapSelectedFeatures()
       
            if  not hasSelectedFeature:
                RipartHelper.showMessageBox(u"Aucun object sélectionné.\nIl est donc impossible de déterminer le point d'application de la nouvelle remarque à créer.")
                return
            
            
            res=self.context.getConnexionRipart()    
            if res!=1:
                return
            
            #Création des croquis à partir de la sélection de features
            croquisList=self.context.makeCroquisFromSelection()
            
            
            self.logger.debug(str(len(croquisList)) + u" croquis générés")
        
            
            formCreate= FormCreerRemarque(context=self.context,croquisCnt=len(croquisList))
            r=formCreate.exec_()
            
            if formCreate.cancel:
                return
            
            else:
                self._createNewRemark(formCreate,croquisList)
            
        
        except Exception as e:
            self.logger.error(e.message)
            self.context.iface.messageBar().pushMessage("", u"Problème dans la création de remarque(s)",level=2, duration =15)  
            
         
        
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
             
            client= self.context.client
            
            listNewRemIds=[]
            
            if formCreate.optionWithAttDoc():
                tmpRem.addDocument(formCreate.getAttachedDoc())
           
            if formCreate.isSingleRemark():
                
                remarqueNouvelle=self._prepareAndSendRemark(tmpRem,croquisList,formCreate.optionWithCroquis())
                if remarqueNouvelle==None:
                    self.context.iface.messageBar().pushMessage("", u"Une erreur est survenue dans la création de la remarque",level=2, duration =15)  
                     
                listNewRemIds.append(remarqueNouvelle.id)
                
            
            #création de plusieurs remarques  
            else:             
                listNewRemIds=[]
                
                for cr in croquisList:                
                    tmpRem.clearCroquis()
                    remarqueNouvelle=self._prepareAndSendRemark(tmpRem,[cr],formCreate.optionWithCroquis())
                    if remarqueNouvelle==None:                 
                        self.context.iface.messageBar().pushMessage("", u"Une erreur est survenue dans la création d'une remarque",level=2, duration =15)  
                        continue
                    
                    listNewRemIds.append(remarqueNouvelle.id)
   
            self.context.refresh_layers()
            #self.context.iface.messageBar().pushMessage("",
            #                                     u"Succès de la création de " + str(len(listNewRemIds)) + u" nouvelle(s) remarque(s) Ripart",
            #                                    level=1, duration =10)
            RipartHelper.showMessageBox(u"Succès de la création de " + str(len(listNewRemIds)) + u" nouvelles remarques Riparts") 
             
        except Exception as e:
            self.logger.error("in _createNewRemark "+ e.message)
        
        finally:
            self.context.conn.close()   
            #self.context.iface.messageBar().clearWidgets()
            
            
            
            
    def _prepareAndSendRemark(self,tmpRem,croquisList,optionWithCroquis): 
        
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

       
        #TODO uncomment !!!!
        #rem= client.getRemarque(remarqueNouvelle.id)
        
        #rem= client.getRemarque(2893)
      
        #TODO comment !!!!
        #remarqueNouvelle=tmpRem
        #remarqueNouvelle.id=10000
        #rem=remarqueNouvelle
        ######
        
        #self.logger.info(u"Succès de la création de la nouvelle remarque n°" + str(rem.id))
        self.logger.info(u"Succès de la création de la nouvelle remarque n°" + str(remarqueNouvelle.id))
        
        RipartHelper.insertRemarques(self.context.conn, remarqueNouvelle)
        self.context.conn.commit()
            
        return remarqueNouvelle
                    