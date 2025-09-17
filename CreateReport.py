# -*- coding: utf-8 -*-
"""
Created on 27 oct. 2015
Updated on 26 aout 2025

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""
from qgis.core import QgsPointXY
from .core.MapToolsReport import MapToolsReport
from .core.PluginLogger import PluginLogger
from .core import Constantes as cst
from .ToolsReport import ToolsReport


class CreateReport(object):
    """
    Classe pour la création d'un nouveau signalement sans (ou avec) croquis.
    Dans le cas de la création sans croquis, les coordonnées du signalement sont issues de la récupération du clic
    sur la carte (voir core.MapToolsReport qui dérive de QgsMapTool).
    """
    def __init__(self, context) -> None:
        """
        Constructeur.

        :param context: le contexte du projet QGIS
        """
        self.__logger = PluginLogger("CreateReport").getPluginLogger()
        self.__context = context
        self.__activeLayer = self.__context.iface.activeLayer()

    def do(self) -> None:
        """
        Création d'un nouveau signalement avec ou sans croquis.
        Si un objet est sélectionné création avec croquis, si pas d'objet(s) sélectionné(s) création d'un signalement.

        NB : appeler dans PluginModule.py, fonction : __createReport
        """
        try:
            bSelectedFeature = self.__context.asSelectedFeaturesInMap()
            # Sans croquis, en cliquant simplement sur la carte
            if not bSelectedFeature:
                if self.__activeLayer.name() != cst.nom_Calque_Signalement:
                    return
                mapToolsReport = MapToolsReport(self.__context)
                mapToolsReport.activate()
                return
            # Avec croquis
            else:
                # Création du ou des croquis à partir de la sélection de features
                sketchList = self.__context.makeSketchFromSelection()
                # Il y a eu un problème à la génération des croquis, on sort
                if len(sketchList) == 0:
                    return
                self.__logger.debug(str(len(sketchList)) + u" croquis générés")
                # Création du ou des signalements
                toolsReport = ToolsReport(self.__context)
                # Pas de point écran puisque création avec croquis
                pointFromClipboard = QgsPointXY()
                toolsReport.createReport(sketchList, pointFromClipboard)

        except Exception as e:
            self.__logger.error(format(e))
            self.__context.iface.messageBar().pushMessage("Erreur", u"Problème dans la création de signalement(s) : {}"
                                                          .format(e), level=2, duration=4)
