from .core.RipartLoggerCl import RipartLogger
from qgis.core import QgsProject
from.FormCompterGuichet import FormCompterGuichet


class CompterGuichet(object):

    def __init__(self):
        self.nodeGroups = QgsProject.instance().layerTreeRoot().findGroups()
        self.message = "Groupe {}\n".format(self.nodeGroups[0].name())


    def doCount(self):
        layersId = self.nodeGroups[0].findLayerIds()
        for layerId in layersId:
            qgsmaplayer = QgsProject.instance().mapLayer(layerId)
            print("Différentiel")
            qgsmaplayer.doDifferentielAfterBeforeWorks()
            print("Comptage : {}".format(qgsmaplayer.name()))
            stat = qgsmaplayer.getStat()
            stat.count()
            self.message += stat.countToDialog(qgsmaplayer.name())

        # Affichage du résultat
        # TODO QLabel à remplacer dans la boite mais par quoi ?
        dlgCompterGuichet = FormCompterGuichet(self.message)
        dlgCompterGuichet.exec_()