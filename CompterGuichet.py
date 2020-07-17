from .core.Statistics import Statistics
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


    def isLayerEdited(self):
        maplayers = self.context.getAllMapLayers()
        for layer in maplayers:
            if not layer.beforeEditingStarted():
                continue

            # Retrouver le groupe activé



    def doCount(self):
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            stat = Statistics(layer)
            stat.run()
            #print("Pour la couche {}".format(layer..nom))
            print("Objets au total : {}".format(stat.nft))
            print("Objets ajoutés : {}".format(stat.nfa))
            print("Objets détruits : {}".format(stat.nfd))
            print("Objets modifiés : {}".format(stat.nfc))

        # Boucler sur les couches de ce groupe

        # Faire le comptage des couches de ce groupe