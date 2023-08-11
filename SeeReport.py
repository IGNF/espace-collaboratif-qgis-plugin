from typing import Optional
from .ToolsReport import ToolsReport
from .SeeReportView import SeeReportView
from .PluginHelper import PluginHelper
from .core.RipartLoggerCl import RipartLogger


# Classe pour visualiser un signalement
class SeeReport(object):

    def __init__(self, context) -> None:
        self.__context = context
        self.__logger = RipartLogger("SeeReport").getRipartLogger()

    def do(self) -> Optional[SeeReportView]:
        """
        Affichage de la fenêtre de visualisation d'un signalement
        """
        try:
            activeLayer = self.__context.iface.activeLayer()
            if activeLayer is None or activeLayer.name() != PluginHelper.nom_Calque_Signalement:
                self.__context.iface.messageBar().pushMessage("Attention",
                                                              'La couche "Signalement" doit être la couche active',
                                                              level=1, duration=3)
                return

            selectedFeatures = activeLayer.selectedFeatures()
            if len(selectedFeatures) != 1:
                self.__context.iface.messageBar().pushMessage("Attention",
                                                              "Il faut sélectionner un et un seul signalement",
                                                              level=1, duration=3)
                return

            reportsId = []
            for feat in selectedFeatures:
                reportsId.append(feat.attribute('NoSignalement'))
            # TODO suggestion
            #  Aller chercher les données dans SQLite ??? plutôt que de lancer la requête (dans getReport)
            #  https://qlf-collaboratif.ign.fr/collaboratif-develop/gcms/api/reports/162918
            #  Les données clientes dans SQLite sont censées être les mêmes que sur le serveur
            #  même si la base SQLite contient moins de colonnes que d'attributs serveur retournés par la nouvelle API
            toolsReport = ToolsReport(self.__context)
            report = toolsReport.getReport(reportsId[0])
            self.__logger.debug("SeeReport.do")
            seeReportView = SeeReportView(self.__context.getUserCommunity())
            seeReportView.setReport(report)
            seeReportView.show()
            return seeReportView

        except Exception as e:
            self.__logger.error(format(e) + ";" + str(type(e)) + " " + str(e))
            raise
