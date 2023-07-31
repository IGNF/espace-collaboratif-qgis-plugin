from .PluginHelper import PluginHelper
from .core.RipartLoggerCl import RipartLogger
from .core.BBox import BBox
from .core.NoProfileException import NoProfileException
from .core.SQLiteManager import SQLiteManager


# Importation des signalements dans le projet QGIS
class ImporterGuichet(object):

    def __init__(self, context):
        self.__context = context
        self.__logger = RipartLogger("ImporterGuichet").getRipartLogger()

    # Téléchargement et import des couches du guichet sur la carte
    def doImport(self, guichet_layers):
        try:
            self.__logger.debug("doImport")

            if self.__context.profil is None:
                raise NoProfileException(
                    "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

            if self.__context.profil.geogroup.getName() is None:
                raise NoProfileException(
                    "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

            # filtre spatial
            bbox = BBox(self.__context)
            box = bbox.getFromLayer(PluginHelper.load_CalqueFiltrage(self.__context.projectDir).text, False, True)
            # si la box est à None alors, l'utilisateur veut extraire France entière
            # si la box est égale 0.0 pour ces 4 coordonnées alors l'utilisateur
            # ne souhaite pas extraire les données France entière
            if box is not None and box.XMax == 0.0 and box.YMax == 0.0 and box.XMin == 0.0 and box.YMin == 0.0:
                return

            # création de la table des tables
            SQLiteManager.createTableOfTables()

            # Import des couches du guichet sélectionnées par l'utilisateur
            self.__context.addGuichetLayersToMap(guichet_layers, box, self.__context.profil.geogroup.getName())

        except Exception as e:
            PluginHelper.showMessageBox('{}'.format(e))
