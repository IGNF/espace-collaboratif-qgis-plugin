from typing import Optional
from .ToolsReport import ToolsReport
from .SeeReportView import SeeReportView
from .core.PluginLogger import PluginLogger
from .core import Constantes as cst


class SeeReport(object):
    """
    Classe pour l'affichage des caractéristiques d'un signalement.
    """
    def __init__(self, context) -> None:
        """
        Constructeur.
        Initialisation du Contexte et récupération du fichier de log.
        """
        self.__context = context
        self.__logger = PluginLogger("SeeReport").getPluginLogger()

    def do(self) -> Optional[SeeReportView]:
        """
        Lance et affiche le dialogue "Voir un signalement" qui affiche les caractéristiques d'un signalement.
         - si la couche Signalement dans QGIS est active
         - si un et un seul signalement est sélectionné
        L'affichage de la boite de visualisation n'est possible qu'après récupération par une requête sur le site
        de l'espace collaboratif .../gcms/api/reports/id (ou id peut-être 162918) des données du signalement.

        NB : appeler dans PluginModule.py, fonction : __viewReport

        :return: l'instance du dialogue de visualisation
        """
        try:
            activeLayer = self.__context.iface.activeLayer()
            if activeLayer is None or activeLayer.name() != cst.nom_Calque_Signalement:
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
            # TODO Mélanie suggestion
            #  Aller chercher les données dans SQLite ??? plutôt que de lancer la requête (dans getReport)
            #  https://qlf-collaboratif.ign.fr/collaboratif-develop/gcms/api/reports/162918
            #  Les données clientes dans SQLite sont censées être les mêmes que sur le serveur
            #  même si la base SQLite contient moins de colonnes que d'attributs serveur retournés par la nouvelle API
            #  bref faut voir si on aura les mêmes infos dans SQLite
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
