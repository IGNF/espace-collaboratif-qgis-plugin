# -*- coding: utf-8 -*-
"""
Created on 3 janv. 2022
@author: EPeyrouse
"""
from .SeeReportView import SeeReportView
from .core.RipartLoggerCl import RipartLogger
from .RipartHelper import RipartHelper


class SeeReport(object):
    """
    Classe pour visualiser un signalement
    """
    logger = RipartLogger("SeeReport").getRipartLogger()
    context = None
    error = "Il faut sélectionner un et un seul signalement"

    def __init__(self, context):
        self.context = context

    def do(self):
        """
        Affichage de la fenêtre de visualisation d'un signalement
        """
        try:
            if self.context.client is None:
                connResult = self.context.getConnexionRipart()
                if not connResult:
                    return 0
                # la connexion a échoué, on ne fait rien
                if self.context.ripClient is None:
                    self.context.iface.messageBar().pushMessage("",
                                                                u"Un problème de connexion avec le service RIPart est survenu.Veuillez rééssayer",
                                                                level=2, duration=5)
                    return

            activeLayer = self.context.iface.activeLayer()
            if activeLayer is None or activeLayer.name() != RipartHelper.nom_Calque_Signalement:
                self.context.iface.messageBar().pushMessage("Attention",
                                                            'Le calque "Signalement" doit être le calque actif',
                                                            level=1, duration=5)
                return
            else:
                selFeats = activeLayer.selectedFeatures()
                if len(selFeats) != 1:
                    self.context.iface.messageBar().pushMessage("Attention", self.error, level=1, duration=10)
                    return

                remIds = []
                for feat in selFeats:
                    remIds.append(feat.attribute('NoSignalement'))

            client = self.context.client
            remId = remIds[0]
            report = client.getGeoRem(remId)
            self.logger.debug("SeeReport")
            seeReportView = SeeReportView(self.context, report)
            seeReportView.setReport()
            seeReportView.show()
            return seeReportView

        except Exception as e:
            self.logger.error(format(e) + ";" + str(type(e)) + " " + str(e))
            raise
