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

    def getFromLayer(self, filterName, bAskConfirmation=True):
        box = None
        self.filterName = filterName
        if self.filterName is not None and len(self.filterName.strip()) > 0:
            self.layerFilter = self.context.getLayerByName(self.filterName)
            box = self.getSpatialFilter()
        else:
            if bAskConfirmation:
                message = "Vous n'avez pas spécifié de zone de travail. \n\n" \
                          "Souhaitez-vous poursuivre l'import des objets sur la totalité du territoire ? "
                reply = QMessageBox.question(None, 'IGN Espace Collaboratif', message, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.No:
                    return Box(0.0, 0.0, 0.0, 0.0)
        return box

    def getSpatialFilter(self):
        if self.layerFilter is None:
            message = "La carte en cours ne contient pas la couche '" + \
                      self.filterName + \
                      "' définie comme zone de travail ou celle-ci n'est pas activée.\n\n" + \
                      "Souhaitez-vous poursuivre l'import sur la totalité du territoire ? "
            reply = QMessageBox.question(None, 'IGN Espace Collaboratif', message, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        else:
            layerFilterExtent = self.layerFilter.extent()
            layerFilterCrs = self.layerFilter.crs()
            destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
            coordTransform = QgsCoordinateTransform(layerFilterCrs, destCrs, QgsProject.instance())
            newLayerFilterExtent = coordTransform.transform(layerFilterExtent)
            return Box(newLayerFilterExtent.xMinimum(), newLayerFilterExtent.yMinimum(), newLayerFilterExtent.xMaximum(),
                       newLayerFilterExtent.yMaximum())

    def getBBoxAsWkt(self, filterName):
        if filterName is None or len(filterName) == 0 or filterName == '':
            return None
            #raise Exception ("La zone de travail est absente, veuillez en importer une.")
        self.layerFilter = self.context.getLayerByName(filterName)
        qgsRectangle = self.layerFilter.extent()
        layerFilterCrs = self.layerFilter.crs()
        destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
        coordTransform = QgsCoordinateTransform(layerFilterCrs, destCrs, QgsProject.instance())
        newQgsRectangle = coordTransform.transform(qgsRectangle)
        return newQgsRectangle.asWktPolygon()
