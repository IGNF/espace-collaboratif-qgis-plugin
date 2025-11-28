from qgis.PyQt.QtGui import QFontMetrics
from qgis.PyQt.QtWidgets import QProgressBar, QLabel, QApplication
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
from qgis.gui import QgsMessageBar
from qgis.core import Qgis


from ..PluginHelper import PluginHelper


class DynamicProgressBar(QProgressBar):
    """
    Barre de progression personnalisée avec message dynamique pour QGIS.
    """

    def __init__(self, nbMax, message) -> None:
        """
        Initialise la barre de progression avec un message.

        :param nbMax: Nombre maximum d'objets à traiter.
        :type nbMax: int
        :param message: Message initial à afficher.
        :type message: str
        """
        super(DynamicProgressBar, self).__init__()
        self.setMaximum(nbMax)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Création du QLabel pour afficher le message
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Calcul de la largeur du message pour ajuster la taille de la barre
        font_metrics = QFontMetrics(self.label.font())
        message_width = font_metrics.horizontalAdvance(message)
        total_width = 600  # largeur totale disponible dans la MessageBar
        bar_width = max(200, total_width - message_width - 20)  # marge de sécurité

        # Fixer une largeur raisonnable pour éviter qu'elle prenne trop de place
        self.setFixedWidth(bar_width)

        # Création du message dans la barre de message QGIS
        progressMessageBar = iface.messageBar().createMessage("")
        progressMessageBar.layout().addWidget(self.label)
        progressMessageBar.layout().addWidget(self)

        iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
        iface.mainWindow().repaint()
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)

    def updateMessage(self, new_message: str) -> None:
        """
        Met à jour le message affiché à côté de la barre de progression.

        :param new_message: Nouveau message à afficher.
        :type new_message: str
        """
        self.label.setText(new_message)
        iface.mainWindow().repaint()

    def close(self) -> None:
        """
        Ferme la barre de progression et rétablit le curseur.
        """
        iface.messageBar().clearWidgets()
        PluginHelper.setCursor()