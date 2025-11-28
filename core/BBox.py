from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from . import Constantes as cst
from .Box import Box


class BBox(object):
    """Classe représentant une bounding box."""

    def __init__(self, context) -> None:
        self.__context = context
        self.__filterName = None
        self.__layerFilter = None

    def getFromLayer(self, filterName, bAskConfirmation, bTransformCoordinates) -> Box:
        """
        Retourne la boite englobante de la zone de travail utilisateur présente dans une couche QGIS.

        :param filterName: le nom de la zone de travail utilisateur
        :type filterName: str

        :param bAskConfirmation: à True, si l'utilisateur doit répondre à un message de confirmation
        :type bAskConfirmation: bool

        :param bTransformCoordinates: à True, si les coordonnées doivent être transformées
        :type bTransformCoordinates: bool

        :return: la boite englobante issue de la couche 'zone de travail'
        """
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
                                             QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return Box(0.0, 0.0, 0.0, 0.0)
        return box

    def getSpatialFilter(self, bTransformCoordinates) -> Box:
        """
        Retourne la boite englobante d'une zone de travail utilisateur avec transformation ou non des coordonnées.
        Envoie un message si :
         - la zone de travail n'est pas définie ou trouvée
         - le système de coordonnées n'est pas défini

        :param bTransformCoordinates: à True, si les coordonnées doivent être transformées
        :type bTransformCoordinates: bool

        :return: la boite englobante issue de la couche 'zone de travail'
        """
        if self.__layerFilter is None:
            message = "La carte en cours ne contient pas la couche '" + \
                      self.__filterName + \
                      "' définie comme zone de travail ou celle-ci n'est pas activée.\n\n" + \
                      "Souhaitez-vous poursuivre l'import sur la totalité du territoire ? "
            reply = QMessageBox.question(self.__context.iface.mainWindow(), cst.IGNESPACECO, message, QMessageBox.StandardButton.Yes,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
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
                destCrs = QgsCoordinateReferenceSystem.fromEpsgId(cst.EPSGCRS4326)
                coordTransform = QgsCoordinateTransform(layerFilterCrs, destCrs, QgsProject.instance())
                newLayerFilterExtent = coordTransform.transform(layerFilterExtent)
                return Box(newLayerFilterExtent.xMinimum(), newLayerFilterExtent.yMinimum(),
                           newLayerFilterExtent.xMaximum(), newLayerFilterExtent.yMaximum())
            return Box(layerFilterExtent.xMinimum(), layerFilterExtent.yMinimum(),
                       layerFilterExtent.xMaximum(), layerFilterExtent.yMaximum())

    def getBBoxAsWkt(self, filterName) -> str:
        """
        :param filterName: le nom de la zone de travail utilisateur
        :type filterName: str

        :return: la boite englobante d'une zone de travail utilisateur sous forme d'une géométrie WKT
        """
        if filterName is None or len(filterName) == 0 or filterName == '':
            return ''
        self.__layerFilter = self.__context.getLayerByName(filterName)
        qgsRectangle = self.__layerFilter.extent()
        layerFilterCrs = self.__layerFilter.crs()
        destCrs = QgsCoordinateReferenceSystem.fromEpsgId(cst.EPSGCRS4326)
        coordTransform = QgsCoordinateTransform(layerFilterCrs, destCrs, QgsProject.instance())
        newQgsRectangle = coordTransform.transform(qgsRectangle)
        return newQgsRectangle.asWktPolygon()
