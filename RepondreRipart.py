# -*- coding: utf-8 -*-
"""
Created on 8 oct. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""
from .SeeReportView import SeeReportView
from .core.RipartLoggerCl import RipartLogger
from .RipartHelper import RipartHelper
from .core import Constantes as cst
from .ReplyReportView import ReplyReportView


class RepondreRipart(object):
    """"Classe pour les réponses Ripart
    """

    logger = RipartLogger("RepondreRipart").getRipartLogger()
    context = None

    def __init__(self, context):
        """
        Constructor
        """
        self.context = context

    def do(self, isView = False):
        """
        Affichage de la fenêtre de réponse ou de la fenêtre de visualisation du signalement
        
        :param isView: true si on veut afficher la fenêtre de visualisation, false pour la fenêtre de réponse
        :type isView: boolean
        """
        try:

            activeLayer = self.context.iface.activeLayer()
            if activeLayer is None or activeLayer.name() != RipartHelper.nom_Calque_Signalement:
                self.context.iface.messageBar().pushMessage("Attention",
                                                            'Le calque "Signalement" doit être le calque actif',
                                                            level=1, duration=5)
                return
            else:
                # get selected features
                selFeats = activeLayer.selectedFeatures()

                if len(selFeats) == 0:
                    self.context.iface.messageBar().pushMessage("Attention", 'Pas de signalement sélectionné', level=1,
                                                                duration=10)
                    return

                remIds = []
                for feat in selFeats:
                    remIds.append(feat.attribute('NoSignalement'))

                if len(remIds) > 1:
                    self.context.iface.messageBar().pushMessage("Attention",
                                                                u'Plusieurs signalements sélectionnés. Un seul sera pris en compte (signalement n°='
                                                                + str(remIds[0]) + ')', level=1, duration=10)

            if self.context.client is None:
                connResult = self.context.getConnexionEspaceCollaboratif()
                if not connResult:
                    return 0
                # la connexion a échoué, on ne fait rien
                if self.context.client is None:
                    self.context.iface.messageBar().pushMessage("",
                                                                u"Un problème de connexion avec le service RIPart est survenu.Veuillez rééssayer",
                                                                level=2, duration=5)
                    return

            client = self.context.client
            remId = remIds[0]
            remarque = client.getGeoRem(remId)

            if remarque.statut.__str__() not in cst.openStatut and not isView:
                mess = "Impossible de répondre au signalement n°" + str(remId) + \
                       ", car il est clôturé depuis le " + remarque.dateValidation

                self.context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=5)
                return

            if remarque.autorisation not in ["RW", "RW+", "RW-"] and not isView:
                mess = "Vous n'êtes pas autorisé à modifier le signalement n°" + str(remId)
                self.context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=10)
                return

            if isView:
                self.logger.debug("view report")
                seeReportView = SeeReportView(self.context, remarque)
                seeReportView.setReport()
                seeReportView.show()
                return seeReportView
            else:
                self.logger.debug("view reply report")
                replyReport = ReplyReportView(selFeats)
                replyReport.exec_()

        except Exception as e:
            self.logger.error(format(e) + ";" + str(type(e)) + " " + str(e))
            raise
