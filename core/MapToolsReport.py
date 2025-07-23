from ..ToolsReport import ToolsReport
from PyQt5.QtGui import QColor
from qgis._core import QgsSettings, QgsPointXY
from qgis._gui import QgsVertexMarker
from qgis.gui import QgsMapTool
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


class MapToolsReport(QgsMapTool):

    def __init__(self, context) -> None:
        self.__context = context
        self.__canvas = context.iface.mapCanvas()
        QgsMapTool.__init__(self, self.__canvas)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.__canvas.keyPressed.connect(self.__keyPressed)
        self.__vertex = None
        self.__snapcolor = QgsSettings().value("/qgis/digitizing/snap_color", QColor(Qt.GlobalColor.red))
        self.__geometrySingleReport = ''

    def canvasReleaseEvent(self, event) -> None:
        pt = self.snappoint(event.originalPixelPoint())
        if pt is not None:
            clipboard = QApplication.clipboard()
            self.__geometrySingleReport = 'POINT({0} {1})'.format(pt.x(), pt.y())
            clipboard.setText(self.__geometrySingleReport)
        self.__canvas.unsetMapTool(self)

    def snappoint(self, qpoint) -> QgsPointXY:
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

    def __keyPressed(self, event):
        if event.key() == Qt.Key.Key_A:
            # Création et envoi du signalement sur le serveur
            toolsReport = ToolsReport(self.__context)
            # La liste de croquis est vide puisque c'est un pointé sur la carte qui sert à créer le signalement
            sketchList = []
            toolsReport.createSingleReport(sketchList, self.__geometrySingleReport)
            self.endCreateReport()
        else:
            self.endCreateReport()

    def endCreateReport(self):
        self.deactivate()
        self.removeVertexMarker()
        self.__canvas.refresh()
        return

    def removeVertexMarker(self):
        if self.__vertex is not None:
            self.__canvas.scene().removeItem(self.__vertex)
            self.__vertex = None

    def deactivate(self) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        clipboard = QApplication.clipboard()
        clipboard.clear()
