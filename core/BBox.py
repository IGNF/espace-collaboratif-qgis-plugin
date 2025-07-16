from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from . import Constantes as cst
from .Box import Box


# Classe représentant une bounding box
class BBox(object):

    def __init__(self, context) -> None:
        self.__context = context
        self.__filterName = None
        self.__layerFilter = None

    # Retourne la boite englobante de la zone de travail utilisateur
    def getFromLayer(self, filterName, bAskConfirmation, bTransformCoordinates) -> Box:
        box = None
        self.__filterName = filterName
        if self.__filterName is not None and len(self.__filterName.strip()) > 0:
            self.__layerFilter = self.__context.getLayerByName(self.__filterName)
            box = self.getSpatialFilter(bTransformCoordinates)
        else:
            if bAskConfirmation:
                message = "Vous n'avez pas spécifié de zone de travail. \n\n" \
                          "Souhaitez-vous poursuivre l'import des objets sur la totalité du territoire ? "
                reply = QMessageBox.question(self.__context.iface.mainWindow(), cst.IGNESPACECO, message,
                                             QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.No:
                    return Box(0.0, 0.0, 0.0, 0.0)
        return box

    # Retourne la boite englobante d'une zone de travail utilisateur avec transformation ou non des coordonnées
    def getSpatialFilter(self, bTransformCoordinates) -> Box:
        if self.__layerFilter is None:
            message = "La carte en cours ne contient pas la couche '" + \
                      self.__filterName + \
                      "' définie comme zone de travail ou celle-ci n'est pas activée.\n\n" + \
                      "Souhaitez-vous poursuivre l'import sur la totalité du territoire ? "
            reply = QMessageBox.question(self.__context.iface.mainWindow(), cst.IGNESPACECO, message, QMessageBox.Yes,
                                         QMessageBox.No)
            if reply == QMessageBox.No:
                raise Exception("Arrêt demandé")
        else:
            layerFilterCrs = self.__layerFilter.crs()
            if layerFilterCrs.isValid() is False:
                message = "Le système de coordonnées de référence (SCR) n'est pas assigné pour la couche [{0}]. " \
                          "Veuillez le renseigner dans [Propriétés...][Couche][Système de Coordonnées de Référence " \
                          "assigné]".format(self.__filterName)
                raise Exception(message)
            layerFilterExtent = self.__layerFilter.extent()
            if bTransformCoordinates:
                destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS4326, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
                coordTransform = QgsCoordinateTransform(layerFilterCrs, destCrs, QgsProject.instance())
                newLayerFilterExtent = coordTransform.transform(layerFilterExtent)
                return Box(newLayerFilterExtent.xMinimum(), newLayerFilterExtent.yMinimum(),
                           newLayerFilterExtent.xMaximum(), newLayerFilterExtent.yMaximum())
            return Box(layerFilterExtent.xMinimum(), layerFilterExtent.yMinimum(),
                       layerFilterExtent.xMaximum(), layerFilterExtent.yMaximum())

    # Retourne la boite englobante d'une zone de travail utilisateur sous forme d'une géométrie WKT
    def getBBoxAsWkt(self, filterName) -> str:
        if filterName is None or len(filterName) == 0 or filterName == '':
            return ''
        self.__layerFilter = self.__context.getLayerByName(filterName)
        qgsRectangle = self.__layerFilter.extent()
        layerFilterCrs = self.__layerFilter.crs()
        destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS4326, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
        coordTransform = QgsCoordinateTransform(layerFilterCrs, destCrs, QgsProject.instance())
        newQgsRectangle = coordTransform.transform(qgsRectangle)
        return newQgsRectangle.asWktPolygon()
