# -*- coding: utf-8 -*-

"""
Created on 3 jul. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""

from PyQt5.QtWidgets import QMessageBox, QProgressBar, QApplication
from PyQt5.QtCore import Qt
from .RipartHelper import RipartHelper
from .core.RipartLoggerCl import RipartLogger
from .core.Box import Box
from .core.ClientHelper import ClientHelper
from .core.NoProfileException import NoProfileException
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
        self.progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
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
            # Non pris en compte en v4.0.1 car le filtrage par BBOX du WFS ne semble pas fonctionner
            filtre = RipartHelper.load_CalqueFiltrage(self.context.projectDir).text

            if filtre is not None and len(filtre.strip()) > 0:
                self.logger.debug("Spatial filter :" + filtre)

                filtreLay = self.context.getLayerByName(filtre)
                bbox = self.getSpatialFilterBbox(filtre, filtreLay)
                if bbox == -999:
                    return
            else:
                message = "Impossible de déterminer dans le fichier de paramétrage de l'Espace Collaboratif, le nom du calque à utiliser pour le filtrage spatial.\n\n" + \
                           "Souhaitez-vous poursuivre le chargement des couches du guichet sur la France entière ? " + \
                           "(Cela risque de prendre un certain temps)."
                if self.noFilterWarningDialog(message):
                    bbox = None
                else:
                    return

            self.context.iface.messageBar().pushWidget(self.progressMessageBar, level=0)
            QApplication.setOverrideCursor(Qt.BusyCursor)

            # Import des couches du guichet sélectionnées par l'utilisateur
            self.context.addGuichetLayersToMap(guichet_layers, bbox, self.context.profil.geogroup.name)

        finally:
            self.context.iface.messageBar().clearWidgets()
            QApplication.setOverrideCursor(Qt.ArrowCursor)

    def getSpatialFilterBbox(self, filtre, filtreLay):
        """Retourne la boundingbox du filtre spatial

        :param filtre: le nom du calque utilisé comme filtre
        :type: string

        :param filtreLay: le layer correspondant
        :type filtreLay: QgsVectorLayer
        """
        bbox = None
        if filtreLay is None:
            message = "La carte en cours ne contient pas le calque '" + \
                      filtre + \
                      "' défini pour être le filtrage spatial (ou le calque n'est pas activé).\n\n" + \
                      "Souhaitez-vous poursuivre le chargement des couches du guichet sur la France entière ? " + \
                      "(Cela risque de prendre un certain temps)."

            reply = QMessageBox.question(None, 'IGN Espace Collaboratif', message, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                bbox = None
            else:
                return -999

        else:
            # emprise=> getExtent + transform in 4326 crs
            filtreExtent = RipartHelper.getBboxFromLayer(filtreLay)
            bbox = Box(filtreExtent.xMinimum(), filtreExtent.yMinimum(), filtreExtent.xMaximum(),
                       filtreExtent.yMaximum())

        return bbox

    def noFilterWarningDialog(self, message):
        """Avertissement si pas de filtre spatial
        """
        message = ClientHelper.notNoneValue(message)
        reply = QMessageBox.question(None, 'IGN Espace Collaboratif', message, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        else:
            return False
