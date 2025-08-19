from .ToolsReport import ToolsReport
from .ReplyReportView import ReplyReportView
from .core.PluginLogger import PluginLogger
from .core import Constantes as cst


# Classe servant à la gestion d'une réponse à un signalement
class ReplyReport(object):
    def __init__(self, context):
        self.__context = context
        self.__logger = PluginLogger("ReplyReport").getPluginLogger()
        # Initialisation des outils de gestion d'un signalement
        self.__toolsReport = ToolsReport(self.__context)

    # Affichage de la fenêtre de réponse à un signalement
    def do(self):
        self.__logger.debug("ReplyReport.do")
        try:
            # Est-ce que la couche Signalement existe dans la carte ?
            bExist = self.__context.IsLayerInMap(cst.nom_Calque_Signalement)
            if not bExist:
                mess = "Pas de couche 'Signalement' dans la carte.\nIl est donc impossible de répondre à un " \
                       "signalement.\nIl faut se connecter à l'Espace collaboratif et télécharger les signalements."
                self.__context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=3)
                self.__logger.error(mess)
                return
            else:
                activeLayer = self.__context.iface.activeLayer()
                if activeLayer is None or activeLayer.name() != cst.nom_Calque_Signalement:
                    mess = 'Le calque "{}" doit être le calque actif'.format(cst.nom_Calque_Signalement)
                    self.__context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=3)
                    self.__logger.error(mess)
                    return
                # get selected features
                selFeats = activeLayer.selectedFeatures()
                messageReportNoValid = ""
                replyReports = []
                for feat in selFeats:
                    idReport = feat.attribute('NoSignalement')
                    report = self.__toolsReport.getReport(idReport)
                    # Le statut du signalement est-il cloturé ?
                    pos = 0
                    if report.getStatut() not in cst.openStatut:
                        messageReportNoValid += "Impossible de répondre au signalement n°{0}, car il est clôturé " \
                                                "depuis le {1}\n".format(idReport, report.getStrDateValidation())
                        pos = -1
                    # Les autorisations sont-elles suffisantes pour modifier le signalement par une réponse
                    # TODO -> Noémie voir ticket redmine http://sd-redmine.ign.fr/issues/18058
                    # bAuthorisation = True
                    # if report.autorisation not in ["RW", "RW+", "RW-"]:
                    #     messageReportNoValid += "Vous n'êtes pas autorisé à modifier le signalement n°{0}\n".
                    #     format(idReport)
                    #     bAuthorisation = False
                    # if pos != -1 and bAuthorisation:
                    #     replyReports.append(report)
                    if pos != -1:
                        replyReports.append(report)

                if len(replyReports) == 0:
                    mess = "Pas de signalements sélectionnés. Veuillez sélectionner un ou plusieurs signalements."
                    if messageReportNoValid != "":
                        mess = "Les signalements sélectionnés ne sont pas valides. " \
                               "Opération terminée.\n{0}".format(messageReportNoValid)
                    self.__context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=3)
                    return

                self.__logger.debug("ReplyReportView.exec")
                dlgReplyReport = ReplyReportView(replyReports)
                dlgReplyReport.exec_()
                if dlgReplyReport.bResponse:
                    headers = {
                        'Authorization': '{} {}'.format(self.__context.getTokenType(), self.__context.getTokenAccess())}
                    for report in replyReports:
                        newStatut = cst.CorrespondenceStatusWording[dlgReplyReport.newStatus]
                        newResponse = dlgReplyReport.newResponse
                        # TODO -> Noémie le post d'une réponse à un signalement demande un title
                        #  j'ai mis vide pour l'instant doit-on mettre une valeur style "envoyée de QGIS"
                        parameters = {'reportId': report.getId(),
                                      'proxies': self.__context.proxies, 'headers': headers,
                                      'requestBody': {'title': '', 'content': newResponse, 'status': newStatut}}
                        jsonResponse = self.__toolsReport.addResponseToServer(parameters)
                        if jsonResponse == '':
                            raise Exception("toolsReport.addResponse a renvoyé une erreur")
                        self.__toolsReport.updateReportIntoSQLite(jsonResponse)
                    information = "Votre réponse "
                    if len(replyReports) == 1:
                        information += "au signalement {0} a bien été envoyée.".format(replyReports[0].getId())
                    else:
                        information += "aux {0} signalements a bien été envoyée.".format(len(replyReports))
                    self.__context.iface.messageBar().pushMessage("Succès", information, level=0, duration=5)

        except Exception as e:
            self.__logger.error(format(e))
            raise Exception(e)
