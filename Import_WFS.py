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
        # Utiliser la version du geoservice ou par défaut 2.0.0
        self.__version = layer.geoservice.get('version', '2.0.0')

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
        Format: url='http://...' typename='layername' version='2.0.0' srsname='EPSG:4326'
        
        :return: tuple (titre de la couche, URI construite pour QGIS)
        :rtype: tuple
        """
        # Nettoyer l'URL (enlever les paramètres existants si présents)
        base_url = self.__url.split('?')[0]
        
        # Séparer le typename des éventuels filtres CQL
        layer_id = self.__layerID
        extra_params = []
        
        # Vérifier si des filtres sont présents dans le layerID (ex: &cql_filter=...)
        if '&' in layer_id:
            parts = layer_id.split('&', 1)
            layer_id = parts[0]
            # Extraire les paramètres supplémentaires
            if len(parts) > 1:
                extra_params_str = parts[1]
                # Parser les paramètres supplémentaires
                for param in extra_params_str.split('&'):
                    if '=' in param:
                        extra_params.append(param)
        
        # Construire l'URI au format QGIS WFS
        # Note: QGIS attend srsname et non crs pour WFS
        uri_parts = [
            f"url={base_url}",
            f"typename={layer_id}",
            f"version={self.__version}",
            f"srsname={self.__crs}"
        ]
        
        # Ajouter les paramètres supplémentaires (filtres, etc.)
        uri_parts.extend(extra_params)
        
        wfs_uri = " ".join(uri_parts)
        
        return self.__titleLayer, wfs_uri
