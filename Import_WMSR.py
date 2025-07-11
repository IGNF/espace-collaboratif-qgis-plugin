# -*- coding: utf-8 -*-
"""
Created on 27 feb. 2025

@author: EPeyrouse
"""

# Imports
import urllib
from urllib.parse import urlparse
from .core import Constantes as cst


class ImportWMSR:

    def __init__(self, layer) -> None:
        self.__url = layer.url
        self.__layerID = layer.layers
        self.__crs = cst.EPSG4326
        self.__titleLayer = layer.name
        self.__format = "image/jpeg"

    # La requete doit être de la forme :
    # contextualWMSLegend=0&
    # crs=EPSG:4326&
    # dpiMode=7&
    # featureCount=10&
    # format=image/jpeg&
    # layers=HR.ORTHOIMAGERY.ORTHOPHOTOS-OYAPOCK.2023&
    # styles&
    # url=https://data.geopf.fr/wms-r?version%3D1.3.0
    def getWmsrUrlParams(self) -> ():
        wmsr_url_params = {
            "contextualWMSLegend": 0,
            "crs": self.__crs,
            "dpiMode": "7",
            "format": self.__format,
            "layers": self.__layerID,
            "styles": '',
            "url": "{}?VERSION%3D1.3.0".format(self.__url)
        }
        wmsr_url_final = urllib.parse.unquote(urllib.parse.urlencode(wmsr_url_params))
        return self.__titleLayer, wmsr_url_final
