from qgis.PyQt.QtWidgets import QProgressBar, QApplication
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface


class ProgressBar(QProgressBar):
    context = None

    def __init__(self, nbMax, message):
        super(ProgressBar, self).__init__()
        self.setMaximum(nbMax)
        self.setValue(0)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        progressMessageBar = iface.messageBar().createMessage(message)
        progressMessageBar.layout().addWidget(self)
        iface.messageBar().pushWidget(progressMessageBar, level=0)
        iface.mainWindow().repaint()
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)

    def setValue(self, value):
        super(ProgressBar, self).setValue(value)

    def setMaximum(self, maximum):
        super(ProgressBar, self).setMaximum(maximum)

    def close(self):
        super(ProgressBar, self).close()
        iface.messageBar().clearWidgets()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
