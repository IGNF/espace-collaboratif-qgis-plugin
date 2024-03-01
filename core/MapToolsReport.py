from PyQt5.QtGui import QColor
from qgis._core import QgsSettings
from qgis._gui import QgsVertexMarker
from qgis.gui import QgsMapTool
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


# return coordinates from clic in a layer
class MapToolsReport(QgsMapTool):

    def __init__(self, canvas, layer) -> None:
        self.__canvas = canvas
        QgsMapTool.__init__(self, self.__canvas)
        self.__layer = layer
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.__canvas.keyPressed.connect(self.__keyPressed)
        self.__vertex = None
        self.__snapcolor = QgsSettings().value("/qgis/digitizing/snap_color", QColor(Qt.GlobalColor.magenta))

    def canvasReleaseEvent(self, event) -> None:
        pt = self.snappoint(event.originalPixelPoint())
        # pt = self.toLayerCoordinates(self.__layer, event.pos())
        clipboard = QApplication.clipboard()
        clipboard.setText("{0},{1}".format(pt.x(), pt.y()))
        print(clipboard.text())

    def snappoint(self, qpoint):
        point = self.toMapCoordinates(qpoint)
        if self.__vertex is None:
            self.__vertex = QgsVertexMarker(self.__canvas)
            self.__vertex.setIconSize(12)
            self.__vertex.setPenWidth(2)
            self.__vertex.setColor(self.__snapcolor)
            self.__vertex.setIconType(QgsVertexMarker.ICON_BOX)
            self.__vertex.setCenter(point)
        return point  # QPoint input, returns QgsPointXY

    def __keyPressed(self, event):
        if event.key() == Qt.Key.Key_S:
            clipBoard = QApplication.clipboard()
            pt = clipBoard.text()
            print('pt : {}'.format(pt))
            # Création et envoi du signalement sur le serveur

        else:
            self.deactivate()
            self.__canvas.unsetMapTool(self)
            self.removeVertexMarker()

    def removeVertexMarker(self):
        if self.__vertex is not None:
            self.__canvas.scene().removeItem(self.__vertex)
            self.__vertex = None

    def deactivate(self) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        clipboard = QApplication.clipboard()
        clipboard.clear()

# class SendPointToolCoordinates(QgsMapTool):
#     """ Enable to return coordinates from clic in a layer.
#     """
#
#     def __init__(self, canvas, layer):
#         """ Constructor.
#         """
#         QgsMapTool.__init__(self, canvas)
#         self.canvas = canvas
#         self.canvas.keyPressed.connect(self.__keyPressed)
#         self.layer = layer
#         self.setCursor(Qt.CursorShape.CrossCursor)
#
#     def __keyPressed(self, event):
#         if event.key() == Qt.Key.Key_A:
#             # print("A received")
#             clipBoard = QApplication.clipboard()
#             pt = clipBoard.text()
#             print('pt : {}'.format(pt))
#
#     def canvasReleaseEvent(self, event):
#         point = self.toLayerCoordinates(self.layer, event.pos())
#         clipBoard = QApplication.clipboard()
#         clipBoard.setText("{0},{1}".format(point.x(), point.y()))
#         print(clipBoard.text())
