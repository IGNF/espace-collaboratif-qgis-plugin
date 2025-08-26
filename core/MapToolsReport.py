from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
from qgis._core import QgsSettings, QgsPointXY
from qgis._gui import QgsVertexMarker
from qgis.gui import QgsMapTool, QgsMapMouseEvent
from ..Contexte import Contexte
from ..ToolsReport import ToolsReport
from .PluginLogger import PluginLogger


class MapToolsReport(QgsMapTool):
    """
    Classe dérivée de QgsMapTool pour la création d'un outil de saisie directe d'un signalement
    sans besoin de joindre un croquis.
    """

    def __init__(self, context) -> None:
        """
        Définit en particulier, un nouveau curseur (une croix noire), un carré de couleur rouge matérialisant
        le pointé à l'écran.

        :param context: le contexte du projet QGIS
        :type context: Contexte
        """
        self.__logger = PluginLogger("MapToolsReport").getPluginLogger()
        self.__context = context
        self.__canvas = context.iface.mapCanvas()
        QgsMapTool.__init__(self, self.__canvas)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.__vertex = None
        self.__snapcolor = QgsSettings().value("/qgis/digitizing/snap_color", QColor(Qt.GlobalColor.red))
        self.__canvas.setMapTool(self)
        # self.activate()

    def canvasReleaseEvent(self, event) -> None:
        """
        Récupère le pointé de l'utilisateur sur la carte et lance la création d'un signalement.

        :param event: relachement du clic de la souris
        :type event: QgsMapMouseEvent
        """
        try:
            screenPoint = self.snappoint(event.originalPixelPoint())
            if screenPoint is not None:
                # Création et envoi du signalement sur le serveur
                toolsReport = ToolsReport(self.__context)
                # La liste de croquis est vide puisque c'est un pointé sur la carte qui sert à créer le signalement
                sketchList = []
                toolsReport.createReport(sketchList, screenPoint)
                self.endCreateReport()
        except Exception as e:
            self.endCreateReport()
            self.__logger.error(format(e))
            self.__context.iface.messageBar().pushMessage("Erreur", u"Problème dans la création de signalement(s) : {}"
                                                          .format(e), level=2, duration=4)

    def snappoint(self, qpoint) -> QgsPointXY:
        """
        Transforme le pointé écran en coordonnées de la carte et dessine un carré (QgsVertexMarker) de couleur rouge
        matérialisant l'emplacement du futur signalement.

        :param qpoint: le point écran original
        :type qpoint: QPoint

        :return: un point QGIS
        """
        point = None
        if self.__vertex is None:
            point = self.toMapCoordinates(qpoint)
            self.__vertex = QgsVertexMarker(self.__canvas)
            self.__vertex.setIconSize(10)
            self.__vertex.setPenWidth(1)
            self.__vertex.setColor(self.__snapcolor)
            self.__vertex.setIconType(QgsVertexMarker.ICON_BOX)
            self.__vertex.setCenter(point)
        return point

    def endCreateReport(self) -> None:
        """
        Ferme l'outil de saisie directe en fin de création d'un signalement.
        """
        self.setOriginalCursor()
        self.removeVertexMarker()
        self.__canvas.unsetMapTool(self)
        self.__canvas.refresh()
        return

    def removeVertexMarker(self) -> None:
        """
        Efface à l'écran le carré rouge matérialisant le pointé de l'utilisateur.
        """
        if self.__vertex is not None:
            self.__canvas.scene().removeItem(self.__vertex)
            self.__vertex = None

    def setOriginalCursor(self) -> None:
        """
        Remet le curseur à son apparence originale.
        """
        self.setCursor(Qt.CursorShape.ArrowCursor)
