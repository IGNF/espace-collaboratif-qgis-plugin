from typing import Optional
from .ToolsReport import ToolsReport
from .SeeReportView import SeeReportView
from .PluginHelper import PluginHelper
from .core import Report
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
                                                              level=1, duration=5)
                return

            selectedFeatures = activeLayer.selectedFeatures()
            if len(selectedFeatures) != 1:
                self.__context.iface.messageBar().pushMessage("Attention",
                                                              "Il faut sélectionner un et un seul signalement",
                                                              level=1, duration=10)
                return

            reportsId = []
            for feat in selectedFeatures:
                reportsId.append(feat.attribute('NoSignalement'))
            report = self.getReportWithId(reportsId[0])
            self.__logger.debug("SeeReport")
            seeReportView = SeeReportView(self.__context.getActiveCommunityName())
            seeReportView.setReport(report)
            seeReportView.show()
            return seeReportView

        except Exception as e:
            self.__logger.error(format(e) + ";" + str(type(e)) + " " + str(e))
            raise

    def getReportWithId(self, reportId) -> Report:
        toolsReport = ToolsReport(self.__context)
        return toolsReport.getReport(reportId)
