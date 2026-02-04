# -*- coding: utf-8 -*-
"""
Classe pour gérer l'import de couches WFS depuis un geoservice.
URL de test: https://data.geopf.fr/wfs?SERVICE=WFS&VERSION=1.0.0&REQUEST=GetCapabilities
"""

# Imports
import urllib
from urllib.parse import urlparse
from .core import Constantes as cst


class ImportWFS:
    """
    Classe pour importer une couche WFS depuis un geoservice.
    Similaire à ImportWMSR mais pour les services WFS.
    """

    def __init__(self, layer) -> None:
        """
        Constructeur de la classe ImportWFS.
        
        :param layer: la couche contenant les informations du geoservice WFS
        :type layer: Layer
        """
        self.__url = layer.url
        self.__layerID = layer.layers
        self.__crs = cst.EPSG4326
        self.__titleLayer = layer.name()
        self.__version = "1.0.0"

    def getWfsUrlParams(self) -> tuple:
        """
        Construit l'URL pour se connecter à un service WFS.
        
        La requête doit être de la forme compatible avec QgsVectorLayer:
        url='http://...' typename='layername' version='1.0.0' crs='EPSG:4326'
        
        :return: tuple (titre de la couche, URL construite pour QGIS)
        :rtype: tuple
        """
        # Construction de l'URL de base avec GetCapabilities
        base_url = self.__url
        if not base_url.endswith('?'):
            base_url += '?'
        
        # Paramètres pour une couche WFS dans QGIS
        wfs_url_params = {
            "service": "WFS",
            "version": self.__version,
            "request": "GetFeature",
            "typename": self.__layerID,
            "srsname": self.__crs
        }
        
        # Construction de l'URL complète
        wfs_url_final = "{}{}".format(base_url, urllib.parse.urlencode(wfs_url_params))
        
        return self.__titleLayer, wfs_url_final
    
    def getWfsUri(self) -> tuple:
        """
        Construit l'URI au format attendu par QGIS pour une couche WFS.
        Format: url=... typename=... version=... crs=...
        
        :return: tuple (titre de la couche, URI construite pour QGIS)
        :rtype: tuple
        """
        # Construire l'URI au format QGIS WFS
        uri_parts = [
            f"url={self.__url}",
            f"typename={self.__layerID}",
            f"version={self.__version}",
            f"srsname={self.__crs}",
            "restrictToRequestBBOX='1'"
        ]
        
        wfs_uri = " ".join(uri_parts)
        
        return self.__titleLayer, wfs_uri
