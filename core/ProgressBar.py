from qgis.PyQt.QtWidgets import QProgressBar, QApplication
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface


class ProgressBar(QProgressBar):

    def __init__(self, nbMax, message):
        super(ProgressBar, self).__init__()
        self.setMaximum(nbMax)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        progressMessageBar = iface.messageBar().createMessage(message)
        progressMessageBar.layout().addWidget(self)
        iface.messageBar().pushWidget(progressMessageBar, level=0)
        iface.mainWindow().repaint()
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)

    def close(self):
        iface.messageBar().clearWidgets()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
