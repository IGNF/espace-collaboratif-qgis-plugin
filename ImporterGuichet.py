# -*- coding: utf-8 -*-

"""
Created on 3 jul. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""
from .PluginHelper import PluginHelper
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

    def __init__(self, context):
        """
        Constructor
        Initialisation du contexte

        :param context: le contexte de la carte actuelle
        :type context: Contexte
        """
        self.context = context

    def doImport(self, guichet_layers):
        """Téléchargement et import des couches du guichet sur la carte
        """
        try:
            self.logger.debug("doImport")

            if self.context.profil is None:
                raise NoProfileException(
                    "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

            if self.context.profil.geogroup.getName() is None:
                raise NoProfileException(
                    "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

            # filtre spatial
            bbox = BBox(self.context)
            box = bbox.getFromLayer(PluginHelper.load_CalqueFiltrage(self.context.projectDir).text)
            # si la box est à None alors, l'utilisateur veut extraire France entière
            # si la box est égale 0.0 pour ces 4 coordonnées alors l'utilisateur
            # ne souhaite pas extraire les données France entière
            if box is not None and box.XMax == 0.0 and box.YMax == 0.0 and box.XMin == 0.0 and box.YMin == 0.0:
                return

            # création de la table des tables
            SQLiteManager.createTableOfTables()

            # Import des couches du guichet sélectionnées par l'utilisateur
            self.context.addGuichetLayersToMap(guichet_layers, box, self.context.profil.geogroup.getName())

        except Exception as e:
            PluginHelper.showMessageBox('{}'.format(e))
