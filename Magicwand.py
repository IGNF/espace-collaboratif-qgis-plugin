# -*- coding: utf-8 -*-
'''
Created on 10 nov. 2015

@author: AChang-Wailing
'''

from RipartHelper import RipartHelper
from __builtin__ import False


class Magicwand(object):
    '''
    Baguette magique: sélection des objets ripart associés
    '''
    
    context=None

    def __init__(self, context):
        '''
        Constructor
        '''
        self.context=context
        
     
    def selectRipartObjects(self):
        """Sélection des croquis associés a une ou des remarque(s) 
        ou le remarques associées à un ou plusieurs croquis
        """
        res=self.checkObjectSelection()
        if res==None:
            return
        elif res =="croquis":
            self.selectAssociatedRemarks()
        elif res=="remarque":
            self.selectAssociatedCroquis()
            
       
     
    
    def checkObjectSelection(self):
        """Contrôle si un des cas suivants est vrai:
        1) un ou plusieurs croquis sélectionnés
        2) une ou plusieurs remarques sélectionnées
        
        :return: None si  pas de sélection de croquis ou remarque ou sélection des 2 types d'objets, 
                "croquis" si des croquis sont sélectionnés, 
                "remarque" si des remarques sont sélectionnées
        :rtype: string
        
        """
        selectedCroquis=False
        selectedRemarque=False
        mapLayers = self.context.mapCan.layers() 
        for l in mapLayers:
            if l.name() in RipartHelper.croquis_layers and len(l.selectedFeatures())>0:
                selectedCroquis=True
            if l.name()==RipartHelper.nom_Calque_Remarque  and len(l.selectedFeatures())>0:
                selectedRemarque=True
                
        if selectedCroquis and selectedRemarque:
            self.context.iface.messageBar().pushMessage("",
                                                u"Veuillez sélectionner des remarques ou des croquis (mais pas les deux)",
                                                 level=1, duration =10)
            return None
        elif selectedCroquis:
            return "croquis"
        elif selectedRemarque:
            return "remarque"
        else :
            self.context.iface.messageBar().pushMessage("",
                                                u"Aucun croquis ou remarque sélectionné",
                                                 level=1, duration =10)
            return None
    
    
    
    def selectAssociatedRemarks(self):
        """Sélectionne les remarques associées aux croquis sélectionnés 
        """
        
        #identifiant de la remarque (No de remarque)
        remNos=""
             
        mapLayers = self.context.mapCan.layers() 
        
        for l in mapLayers:
            if l.name() in RipartHelper.croquis_layers and len(l.selectedFeatures())>0:

                for feat in l.selectedFeatures():
                    idx= l.fieldNameIndex("NoRemarque")
                    noRemarque= feat.attributes()[idx]
                    remNos+=str(noRemarque)+","         
                    l.removeSelection()
                        
        self.context.selectRemarkByNo(remNos[:-1])
        
    
    
    def selectAssociatedCroquis(self):
        """Sélectionne les croquis associés aux remarques sélectionnées et déselectionne les remarques
        """
        #key: layer name, value: noRemarque
        croquisLays={}
        
        remarqueLay=self.context.getLayerByName(RipartHelper.nom_Calque_Remarque) 
        feats=remarqueLay.selectedFeatures()
        
        for f in feats:
            idx= remarqueLay.fieldNameIndex("NoRemarque")
            noRemarque= f.attributes()[idx]
            croquisLays=self.context.getCroquisForRemark(noRemarque,croquisLays)
            

        for cr in croquisLays:
            lay=self.context.getLayerByName(cr) 
            lay.setSelectedFeatures( croquisLays[cr])       
            remarqueLay.removeSelection()
        
        
    
        