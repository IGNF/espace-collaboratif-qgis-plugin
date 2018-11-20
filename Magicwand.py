# -*- coding: utf-8 -*-
'''
Created on 10 nov. 2015

@author: AChang-Wailing
'''
#from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
from .RipartHelper import RipartHelper
#from builtins import False


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
            if l.name()==RipartHelper.nom_Calque_Signalement  and len(l.selectedFeatures())>0:
                selectedRemarque=True
                
        if selectedCroquis and selectedRemarque:
            self.context.iface.messageBar().pushMessage("",
                                                u"Veuillez sélectionner des signalements ou des croquis (mais pas les deux)",
                                                 level=1, duration =10)
            return None
        elif selectedCroquis:
            return "croquis"
        elif selectedRemarque:
            return "remarque"
        else :
            self.context.iface.messageBar().pushMessage("",
                                                u"Aucun croquis ou signalement sélectionné",
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
                    idx= l.fieldNameIndex("NoSignalement")
                    noSignalement= feat.attributes()[idx]
                    remNos+=str(noSignalement)+","         
                    l.removeSelection()
                        
        self.context.selectRemarkByNo(remNos[:-1])
        
    
    
    def selectAssociatedCroquis(self):
        """Sélectionne les croquis associés aux remarques sélectionnées et déselectionne les remarques
        """
        #key: layer name, value: noSignalement
        croquisLays={}
        
        remarqueLay=self.context.getLayerByName(RipartHelper.nom_Calque_Signalement) 
        feats=remarqueLay.selectedFeatures()
        
        for f in feats:
            idx= remarqueLay.fieldNameIndex("NoSignalement")
            noSignalement= f.attributes()[idx]
            croquisLays=self.context.getCroquisForRemark(noSignalement,croquisLays)
            

        for cr in croquisLays:
            lay=self.context.getLayerByName(cr) 
            lay.setSelectedFeatures( croquisLays[cr])       
            remarqueLay.removeSelection()
        
        
    
        