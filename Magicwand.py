# -*- coding: utf-8 -*-
"""
Created on 10 nov. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""

# standard_library.install_aliases()
from .PluginHelper import PluginHelper


class Magicwand(object):
    """
        Baguette magique: sélection des objets ripart associés
    """
    context = None

    def __init__(self, context):
        """
        Constructor
        """
        self.context = context

    """
        Sélection des croquis associés a une ou des remarque(s) 
        ou les remarques associées à un ou plusieurs croquis
    """

    def selectRipartObjects(self):
        res = self.checkObjectSelection()
        if res is None:
            return
        elif res == "croquis":
            self.selectAssociatedRemarks()
        elif res == "remarque":
            self.selectAssociatedCroquis()

    """
        Contrôle si un des cas suivants est vrai:
            1) un ou plusieurs croquis sélectionnés
            2) une ou plusieurs remarques sélectionnées

            :return: None si  pas de sélection de croquis ou remarque ou sélection des 2 types d'objets, 
                    "croquis" si des croquis sont sélectionnés, 
                    "remarque" si des remarques sont sélectionnées
            :rtype: string

    """

    def checkObjectSelection(self):
        selectedCroquis = False
        selectedRemarque = False
        mapLayers = self.context.mapCan.layers()
        for ml in mapLayers:
            if ml.name() in PluginHelper.sketchLayers and len(ml.selectedFeatures()) > 0:
                selectedCroquis = True
            if ml.name() == PluginHelper.nom_Calque_Signalement and len(ml.selectedFeatures()) > 0:
                selectedRemarque = True

        if selectedCroquis and selectedRemarque:
            self.context.iface.messageBar().pushMessage("",
                                                        u"Veuillez sélectionner des signalements ou des croquis (mais pas les deux)",
                                                        level=1, duration=3)
            return None
        elif selectedCroquis:
            return "croquis"
        elif selectedRemarque:
            return "remarque"
        else:
            self.context.iface.messageBar().pushMessage("",
                                                        u"Aucun croquis ou signalement sélectionné",
                                                        level=1, duration=3)
            return None

    """
        Sélectionne les remarques associées aux croquis sélectionnés 
    """

    def selectAssociatedRemarks(self):
        # identifiant de la remarque (No de remarque)
        remNos = ""
        mapLayers = self.context.mapCan.layers()

        for ml in mapLayers:
            if ml.name() in PluginHelper.sketchLayers and len(ml.selectedFeatures()) > 0:

                for feat in ml.selectedFeatures():
                    idx = ml.fields().lookupField("NoSignalement")
                    noSignalement = feat.attributes()[idx]
                    remNos += str(noSignalement) + ","
                    ml.removeSelection()

        self.context.selectRemarkByNo(remNos[:-1])

    def selectAssociatedCroquis(self):
        """Sélectionne les croquis associés aux remarques sélectionnées et déselectionne les remarques
        """
        # key: layer name, value: noSignalement
        croquisLays = {}

        remarqueLay = self.context.getLayerByName(PluginHelper.nom_Calque_Signalement)
        feats = remarqueLay.selectedFeatures()

        for f in feats:
            idx = remarqueLay.fields().lookupField("NoSignalement")
            noSignalement = f.attributes()[idx]
            croquisLays = self.context.getCroquisForRemark(noSignalement, croquisLays)

        for cr in croquisLays:
            lay = self.context.getLayerByName(cr)
            lay.selectByIds(croquisLays[cr])
            remarqueLay.removeSelection()
