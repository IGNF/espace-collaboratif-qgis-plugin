from .FormInfo import FormInfo
from .ToolsReport import ToolsReport
from .ReplyReportView import ReplyReportView
from .core.PluginLogger import PluginLogger
from .core import Constantes as cst


class ReplyReport(object):
    """
    Classe de gestion d'une réponse à un signalement
    """
    def __init__(self, context) -> None:
        """
        Constructeur.
        Initialise le contexte, les outils de gestion d'un signalement (ToolsReport).
        Récupère le fichier de log.

        :param context: le contexte du projet
        """
        self.__context = context
        self.__logger = PluginLogger("ReplyReport").getPluginLogger()
        self.__toolsReport = ToolsReport(self.__context)

    def do(self) -> None:
        """
        Affichage du dialogue de réponse à un signalement.

        NB : appeler dans PluginModule.py, fonction : __replyToReport
        """
        self.__logger.debug("ReplyReport.do")
        try:
            # Est-ce que la couche Signalement existe ?
            if not self.__isLayerExist():
                return

            # Est-ce que la couche Signalement est active ?
            selFeats = self.__isLayerActive()
            if len(selFeats) == 0:
                return

            # Quels sont les signalements valides ?
            res = self.__isValidReports(selFeats)
            replyReports = res[0]
            messageReportNoValid = res[1]
            if len(replyReports) == 0:
                mess = "Pas de signalements sélectionnés. Veuillez sélectionner un ou plusieurs signalements."
                if messageReportNoValid != "":
                    mess = "Les signalements sélectionnés ne sont pas valides. " \
                           "Opération terminée.\n{0}".format(messageReportNoValid)
                dlgInfo = FormInfo()
                dlgInfo.textInfo.setText(mess)
                dlgInfo.exec_()
                return

            # Donne à l'utilisateur la liste des signalements clôturés
            if messageReportNoValid != "":
                dlgInfo = FormInfo()
                dlgInfo.textInfo.setText(messageReportNoValid)
                dlgInfo.exec_()

            # Ouverture de la fenêtre de Réponse aux signalements
            dlgReplyReport = ReplyReportView(replyReports, len(selFeats))
            self.__logger.debug("ReplyReportView.exec")
            dlgReplyReport.exec_()
            # Si à True, lancement des requêtes de mise à jour des signalements
            if dlgReplyReport.bResponse:
                headers = {
                    'Authorization': '{} {}'.format(self.__context.getTokenType(), self.__context.getTokenAccess())}
                for report in replyReports:
                    newStatut = cst.CorrespondenceStatusWording[dlgReplyReport.newStatus]
                    newResponse = dlgReplyReport.newResponse
                    # TODO Mélanie le post d'une réponse à un signalement demande un title
                    #  j'ai mis vide pour l'instant doit-on mettre une valeur style "envoyée de QGIS",
                    #  y a t'il un standard ?
                    parameters = {'reportId': report.getId(),
                                  'proxies': self.__context.getProxies(), 'headers': headers,
                                  'requestBody': {'title': '', 'content': newResponse, 'status': newStatut}}
                    # Requête de mise à jour
                    jsonResponse = self.__toolsReport.sendResponseToServer(parameters)
                    if jsonResponse == '':
                        raise Exception("toolsReport.addResponse a renvoyé une erreur")
                    # Mise à jour de la base SQLite
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

    def __isLayerExist(self) -> bool:
        """
        Vérifie si la couche "Signalement existe dans le projet

        :return: True si la couche existe, False sinon
        """
        if not self.__context.IsLayerInMap(cst.nom_Calque_Signalement):
            mess = "Pas de couche 'Signalement' dans la carte.\nIl est donc impossible de répondre à un " \
                   "signalement.\nIl faut se connecter à l'Espace collaboratif et télécharger les signalements."
            self.__context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=3)
            self.__logger.error(mess)
            return False
        return True

    def __isLayerActive(self) -> {}:
        """
        Vérifie si la couche "Signalement" est active dans le projet.

        :return: les signalements sélectionnés si la couche Signalement est active, une liste vide sinon
        """
        activeLayer = self.__context.iface.activeLayer()
        if activeLayer is None or activeLayer.name() != cst.nom_Calque_Signalement:
            mess = 'La couche "{}" doit être le calque actif'.format(cst.nom_Calque_Signalement)
            self.__context.iface.messageBar().pushMessage("Attention", mess, level=1, duration=3)
            self.__logger.error(mess)
            return {}
        return activeLayer.selectedFeatures()

    def __isValidReports(self, selFeats) -> ():
        """
        Vérifie si dans le lot de signalements sélectionnés, certains sont clôturés.

        :param selFeats: la liste des signalements sélectionnés
        :type selFeats: list

        :return: la liste des signalements valides, les messages pour chaque signalement clôturé
        """
        messageReportNoValid = ""
        replyReports = []
        for feat in selFeats:
            idReport = feat.attribute('NoSignalement')
            report = self.__toolsReport.getReport(idReport)
            # Le statut du signalement est-il clôturé ?
            pos = 0
            if report.getStatut() not in cst.openStatut:
                messageReportNoValid += "Impossible de répondre au signalement n°{0}, car il est clôturé " \
                                        "depuis le {1}\n".format(idReport, report.getStrDateValidation())
                pos = -1
            # Les autorisations sont-elles suffisantes pour modifier le signalement par une réponse
            # TODO Mélanie
            #  voir ticket redmine http://sd-redmine.ign.fr/issues/18058, Madeline a répondu mais cela ne me donne
            #  pas la solution à implémenter dans le code
            # bAuthorisation = True
            # if report.autorisation not in ["RW", "RW+", "RW-"]:
            #     messageReportNoValid += "Vous n'êtes pas autorisé à modifier le signalement n°{0}\n".
            #     format(idReport)
            #     bAuthorisation = False
            # if pos != -1 and bAuthorisation:
            #     replyReports.append(report)
            if pos != -1:
                replyReports.append(report)
        return replyReports, messageReportNoValid
