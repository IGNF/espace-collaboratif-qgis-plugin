# -*- coding: utf-8 -*-
"""
Created on 10 nov. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""
from typing import Optional

from .PluginHelper import PluginHelper
from .core import Constantes as cst
from .core.SQLiteManager import SQLiteManager


class Magicwand(object):
    """
    Baguette magique : sélection du (des) croquis associés au signalement et vice-versa.
    """
    context = None

    def __init__(self, context) -> None:
        """
        Constructeur.

        :param context: le contexte du projet QGIS de l'utilisateur
        """
        self.context = context

    def selectReportOrSketchObjects(self) -> None:
        """
        Sélection des croquis associés à un signalement
        ou le signalement associé à un ou plusieurs croquis.

        NB : appeler dans PluginModule.py, fonction : __magicwand
        """
        res = self.checkObjectSelection()
        if res is None:
            return
        elif res == "croquis":
            self.selectAssociatedReport()
        elif res == "signalement":
            self.selectAssociatedCroquis()

    def checkObjectSelection(self) -> Optional[str]:
        """
        Contrôle si un des cas suivants est vrai :
         - un ou plusieurs croquis sélectionnés
         - un signalement sélectionné

        :return: None si pas de sélection de croquis ou signalement ou sélection des deux types d'objets,
                 "croquis" si des croquis sont sélectionnés,
                 "signalement" si un signalement est sélectionné
        """
        selectedCroquis = False
        selectedReport = False
        mapLayers = self.context.mapCan.layers()
        for ml in mapLayers:
            if ml.name() in PluginHelper.sketchLayers and len(ml.selectedFeatures()) > 0:
                selectedCroquis = True
            if ml.name() == cst.nom_Calque_Signalement and len(ml.selectedFeatures()) > 0:
                selectedReport = True

        if selectedCroquis and selectedReport:
            self.context.iface.messageBar().pushMessage("",
                                                        u"Veuillez sélectionner un signalement ou un croquis"
                                                        u" (mais pas les deux)",
                                                        level=1, duration=3)
            return None
        elif selectedCroquis:
            return "croquis"
        elif selectedReport:
            return "signalement"
        else:
            self.context.iface.messageBar().pushMessage("",
                                                        u"Aucun croquis ou signalement sélectionné",
                                                        level=1, duration=3)
            return None

    def selectAssociatedReport(self) -> None:
        """
        Sélectionne le signalement associé au croquis sélectionné.
        """
        # identifiant du signalement (Numéro de signalement)
        remNos = ""
        mapLayers = self.context.mapCan.layers()

        for ml in mapLayers:
            if ml.name() in PluginHelper.sketchLayers and len(ml.selectedFeatures()) > 0:
                for feat in ml.selectedFeatures():
                    idx = ml.fields().lookupField("NoSignalement")
                    noSignalement = feat.attributes()[idx]
                    remNos += str(noSignalement) + ","
                    ml.removeSelection()

        featIds = SQLiteManager.selectReportByNumero(remNos[:-1])
        lay = self.context.getLayerByName(cst.nom_Calque_Signalement)
        lay.selectByIds(featIds)

    def selectAssociatedCroquis(self) -> None:
        """
        Sélectionne les croquis associés au signalement sélectionné puis le désélectionne.
        """
        # key: layer name, value: noSignalement
        croquisLays = {}

        remarqueLay = self.context.getLayerByName(cst.nom_Calque_Signalement)
        feats = remarqueLay.selectedFeatures()

        for f in feats:
            idx = remarqueLay.fields().lookupField("NoSignalement")
            noSignalement = f.attributes()[idx]
            croquisLays = SQLiteManager.getCroquisForReport(noSignalement, croquisLays)

        for cr in croquisLays:
            lay = self.context.getLayerByName(cr)
            lay.selectByIds(croquisLays[cr])
            remarqueLay.removeSelection()
