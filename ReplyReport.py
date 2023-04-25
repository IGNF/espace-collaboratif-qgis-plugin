# -*- coding: utf-8 -*-
"""
Created on 20 déc. 2021
@author: EPEyrouse
"""
from .core.RipartLoggerCl import RipartLogger
from .RipartHelper import RipartHelper
from .core import ConstanteRipart as cst
from .ReplyReportView import ReplyReportView
from .core.ClientHelper import ClientHelper


class ReplyReport(object):
    """
    Classe pour répondre à un signalement
    """
    logger = RipartLogger("ReplyReport").getRipartLogger()
    context = None

    def __init__(self, context):
        self.context = context

    def do(self):
        """
        Affichage de la fenêtre de réponse à un signalement
        """
        try:
            if self.context.client is None:
                connResult = self.context.getConnexionEspaceCollaboratif()
                if not connResult:
                    return 0
                # la connexion a échoué, on ne fait rien
                if self.context.client is None:
                    self.context.iface.messageBar().pushMessage("",
                                                                u"Un problème de connexion avec avec l'Espace Collaboratif est survenu. Veuillez rééssayer",
                                                                level=2, duration=5)
                    return

            # Est-ce que la couche Signalement existe dans la carte ?
            bExist = self.context.IsLayerInMap(RipartHelper.nom_Calque_Signalement)
            if not bExist:
                mess = "Pas de couche 'Signalement' dans la carte.\nIl est donc impossible de répondre à un signalement.\nIl faut se connecter à l'Espace collaboratif et télécharger les signalements."
                self.context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=5)
                return
            else:
                activeLayer = self.context.iface.activeLayer()
                if activeLayer is None or activeLayer.name() != RipartHelper.nom_Calque_Signalement:
                    self.context.iface.messageBar().pushMessage("Attention",
                                                                'Le calque "Signalement" doit être le calque actif',
                                                                level=1, duration=5)
                    return
                # get selected features
                selFeats = activeLayer.selectedFeatures()
                messageReportNoValid = ""
                replyReports = []
                for feat in selFeats:
                    idReport = feat.attribute('NoSignalement')
                    report = self.context.client.getGeoRem(idReport)
                    # Le statut du signalement est-il cloturé ?
                    pos = 0
                    if report.statut.__str__() not in cst.openStatut:
                        messageReportNoValid += "Impossible de répondre au signalement n°{0}, car il est clôturé depuis le {1}\n".format(idReport, report.DateValidation)
                        pos = -1
                    # Les autorisations sont-elles suffisantes pour modifier le signalement par une réponse
                    bAuthorisation = True
                    if report.autorisation not in ["RW", "RW+", "RW-"]:
                        messageReportNoValid += "Vous n'êtes pas autorisé à modifier le signalement n°{0}\n".format(idReport)
                        bAuthorisation = False
                    if pos != -1 and bAuthorisation:
                        replyReports.append(report)

                if len(replyReports) == 0:
                    mess = "Pas de signalements sélectionnés. Veuillez sélectionner un ou plusieurs signalements."
                    if messageReportNoValid != "":
                        mess = "Les signalements sélectionnés ne sont pas valides. Opération terminée.\n{0}".format(messageReportNoValid)
                    self.context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=5)
                    return

                self.logger.debug("view reply report")
                dlgReplyReport = ReplyReportView(replyReports)
                dlgReplyReport.exec_()
                if dlgReplyReport.bResponse:
                    for report in replyReports:
                        report.statut = cst.CorrespondenceStatusWording[dlgReplyReport.newStatus]
                        newReport = self.context.client.addResponse(report, ClientHelper.notNoneValue(dlgReplyReport.newResponse), "")
                        if newReport is None:
                            raise Exception("georep_post a renvoyé une erreur")
                        self.context.updateRemarqueInSqlite(newReport)
                    information = "Votre réponse "
                    if len(replyReports) == 1:
                        information += "au signalement {0} a bien été envoyée.".format(replyReports[0].id)
                    else:
                        information += "aux {0} signalements a bien été envoyée.".format(len(replyReports))
                    self.context.iface.messageBar().pushMessage("Succès", information, level=0, duration=15)

        except Exception as e:
            self.logger.error(format(e) + ";" + str(type(e)) + " " + str(e))
            raise
