from .core.RipartLoggerCl import RipartLogger
from qgis.core import QgsProject

class CompterGuichet(object):

    logger = RipartLogger("ImporterGuichet").getRipartLogger()

    # le contexte de la carte
    context = None
    nomGroupe = None

    def __init__(self, context):
        self.context = context
        self.nomGroupe = ""
        #Quel groupe actif est sélectionné


    def doCount(self):
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer in self.context.guichetLayers:
                stat = layer.getStat()
                print("Différentiel")
                layer.doDifferentielAfterBeforeWorks()
                print("Comptage")
                stat.count()

        # Boucler sur les couches de ce groupe

        # Faire le comptage des couches de ce groupe