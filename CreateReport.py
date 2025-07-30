# -*- coding: utf-8 -*-
"""
Created on 27 oct. 2015
Updated on 30 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""
from .core.MapToolsReport import MapToolsReport
from .core.PluginLogger import PluginLogger
from .ToolsReport import ToolsReport
from PyQt5.QtWidgets import QApplication
from .core import Constantes as cst


# Classe pour la création d'un nouveau signalement
class CreateReport(object):

    def __init__(self, context):
        self.__logger = PluginLogger("CreateReport").getPluginLogger()
        self.__context = context
        self.__activeLayer = self.__context.iface.activeLayer()
        self.__canvas = self.__context.iface.mapCanvas()
        # TODO réactiver les 2 lignes de code si cela fonctionne correctement
        clipboard = QApplication.clipboard()
        clipboard.clear()

    # Création d'un nouveau signalement
    def do(self):
        try:
            # TODO réactiver les 2 lignes de code si cela fonctionne correctement
            clipboard = QApplication.clipboard()
            clipboard.clear()
            hasSelectedFeature = self.__context.hasMapSelectedFeatures()
            # Sans croquis, en cliquant simplement sur la carte
            if not hasSelectedFeature:
                if self.__activeLayer.name() != cst.nom_Calque_Signalement:
                    return
                mapToolsReport = MapToolsReport(self.__context)
                mapToolsReport.activate()
                self.__canvas.setMapTool(mapToolsReport)
                return
            # Avec croquis
            else:
                # Création des croquis à partir de la sélection de features
                sketchList = self.__context.makeSketchsFromSelection()
                # Il y a eu un problème à la génération des croquis, on sort
                if len(sketchList) == 0:
                    return
                self.__logger.debug(str(len(sketchList)) + u" croquis générés")
                # Création du ou des signalements
                toolsReport = ToolsReport(self.__context)
                pointFromClipboard = ''
                toolsReport.createReport(sketchList, pointFromClipboard)
            self.__context.mapCan.refresh()

        except Exception as e:
            self.__logger.error(format(e))
            self.__context.iface.messageBar().pushMessage("Erreur", u"Problème dans la création de signalement(s) : {}"
                                                          .format(e), level=2, duration=4)
