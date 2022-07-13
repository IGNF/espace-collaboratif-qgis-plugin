from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject

from . import ConstanteRipart as cst
from .Box import Box


class BBox(object):
    """
        Représente une bounding box
    """
    context = None
    filterName = None
    layerFilter = None

    def __init__(self, context):
        self.context = context

    def getFromLayer(self, filterName):
        box = None
        self.filterName = filterName
        if self.filterName is not None and len(self.filterName.strip()) > 0:
            self.layerFilter = self.context.getLayerByName(self.filterName)
            box = self.getSpatialFilter()
        else:
            message = "Le fichier de paramétrage de l'Espace Collaboratif ne contient pas le nom du calque " \
                      "à utiliser pour le filtrage spatial.\n\n" + \
                      "Souhaitez-vous poursuivre l'importation des objets sur la France entière ? " + \
                      "(Cela risque de prendre un certain temps)."
            reply = QMessageBox.question(None, 'IGN Espace Collaboratif', message, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        return box

    def getSpatialFilter(self):
        if self.layerFilter is None:
            message = "La carte en cours ne contient pas le calque '" + \
                      self.filterName + \
                      "' défini pour être le filtrage spatial (ou le calque n'est pas activé).\n\n" + \
                      "Souhaitez-vous poursuivre le chargement des couches du guichet sur la France entière ? " + \
                      "(Cela risque de prendre un certain temps)."
            reply = QMessageBox.question(None, 'IGN Espace Collaboratif', message, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        else:
            layerFilterExtent = self.layerFilter.extent()
            layerFilterCrs = self.layerFilter.crs()
            destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
            coordTransform = QgsCoordinateTransform(layerFilterCrs, destCrs, QgsProject.instance())
            newLayerFilterExtent = coordTransform.transform(layerFilterExtent)
            return Box(newLayerFilterExtent.xMinimum(), newLayerFilterExtent.yMinimum(), newLayerFilterExtent.xMaximum()
                       , newLayerFilterExtent.yMaximum())
