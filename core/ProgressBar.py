from PyQt5.QtWidgets import QProgressBar, QApplication
from PyQt5.QtCore import Qt
from qgis.utils import iface


class ProgressBar(QProgressBar):
    """
    Classe implémentant une patience dérivée de la barre de progression Qt : QProgressBar.
    """

    def __init__(self, nbMax, message) -> None:
        """
        Initialisation de la barre de patience.

        :param nbMax: le nombre maximum d'objets qui sera traité, permet de définir une progression en %
        :type nbMax: int

        :param message: le message indiquant à l'utilisateur le traitement en cours
        :type message: str
        """
        super(ProgressBar, self).__init__()
        self.setMaximum(nbMax)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        progressMessageBar = iface.messageBar().createMessage(message)
        progressMessageBar.layout().addWidget(self)
        iface.messageBar().pushWidget(progressMessageBar, level=0)
        iface.mainWindow().repaint()
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)

    def close(self) -> None:
        """
        Fermeture de la patience, le curseur revient à son état d'origine.
        """
        iface.messageBar().clearWidgets()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
