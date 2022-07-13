# -*- coding: utf-8 -*-

"""
Created on 3 jul. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""

from PyQt5.QtWidgets import QProgressBar, QApplication
from PyQt5.QtCore import Qt
from .RipartHelper import RipartHelper
from .core.RipartLoggerCl import RipartLogger
from .core.BBox import BBox
from .core.NoProfileException import NoProfileException
from .core.SQLiteManager import SQLiteManager
from .Contexte import Contexte


class ImporterGuichet(object):
    """Importation des remarques dans le projet QGIS
    """
    logger = RipartLogger("ImporterGuichet").getRipartLogger()

    # le contexte de la carte
    context = None

    # barre de progression (des remarques importées)
    progressMessageBar = None
    progress = None

    def __init__(self, context):
        """
        Constructor
        Initialisation du contexte et de la progressbar

        :param context: le contexte de la carte actuelle
        :type context: Contexte
        """
        self.context = context
        self.progressMessageBar = self.context.iface.messageBar().createMessage(
            "Chargement des couches du guichet...")
        self.progress = QProgressBar()
        self.progress.setMaximum(200)
        self.progress.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.progressMessageBar.layout().addWidget(self.progress)

    def doImport(self, guichet_layers):
        """Téléchargement et import des couches du guichet sur la carte
        """
        try:
            self.logger.debug("doImport")
            params = {}  # paramètres pour la requête au service Ripart
            filtreLay = None

            if self.context.ripClient is None:
                connResult = self.context.getConnexionRipart()
                if not connResult:
                    return 0
                if self.context.ripClient is None:  # la connexion a échoué, on ne fait rien
                    self.context.iface.messageBar().pushMessage("",
                                                                "Un problème de connexion avec le service Espace collaboratif est survenu. Veuillez rééssayer",
                                                                level=2, duration=5)
                    return

            if self.context.profil.geogroup.name is None:
                raise NoProfileException(
                    "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

            # filtre spatial
            bbox = BBox(self.context)
            box = bbox.getFromLayer(RipartHelper.load_CalqueFiltrage(self.context.projectDir).text)

            self.context.iface.messageBar().pushWidget(self.progressMessageBar, level=0)
            QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)

            # création de la table des tables
            SQLiteManager.createTableOfTables()

            # Import des couches du guichet sélectionnées par l'utilisateur
            self.context.addGuichetLayersToMap(guichet_layers, box, self.context.profil.geogroup.name)

        finally:
            self.context.iface.messageBar().clearWidgets()
            QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
