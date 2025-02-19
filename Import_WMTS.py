# -*- coding: utf-8 -*-
"""
Created on 13 nov. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""

# Imports
import urllib
from urllib.parse import urlparse
from .core import ConstanteRipart as cst
from qgis.core import QgsDataSourceUri

try:
    from owslib.wmts import WebMapTileService
    from owslib.util import ServiceException
    import owslib

    print("Dependencies - owslib version: {}".format(owslib.__version__))
except ImportError as e:
    print("Dependencies - owslib is not present")

try:
    from owslib.util import HTTPError

    print("Dependencies - HTTPError within owslib")
except ImportError as e:
    print(
        "Dependencies - HTTPError not within owslib."
        " Trying to get it from urllib directly."
    )

try:
    from urllib import HTTPError

    print("Dependencies - HTTPError within urllib")
except ImportError as e:
    print(
        "Depencencies - HTTPError not within urllib."
    )


class ImportWMTS:

    def __init__(self, context, layer) -> None:
        self.wmts = None
        self.uri = QgsDataSourceUri().uri()
        self.wmts_lyr = None
        self.tile_matrix_set = None
        self.layer_id = None
        self.crs = None
        self.title_layer = None
        self.selected_layer = None
        self.context = context
        self.selected_layer = layer
        self.__checkOpenService()
        self.__checkGetTile()
        self.__checkTileMatrixSet()

    # Construction url GetCapabilities sur le geoportail
    # exemple : https://wxs.ign.fr/[cle]/wmts?service=WMTS&request=GetCapabilities
    def __appendUriCapabilities(self) -> None:
        params = {
            # 'service': cst.WMTS,
            'request': 'GetCapabilities'
        }

        '''
        Avec l'url https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities,
        la projection proposée est web Mercator sphérique EPSG:3857 (page 18 du document DT_APIGeoportail.pdf)
        '''
        self.crs = "EPSG:3857"
        # TODO problème avec la clé 'url'
        self.uri = self.selected_layer.url.format(urllib.parse.unquote(urllib.parse.urlencode(params)))

    # opening WMTS
    def __checkOpenService(self) -> bool:
        self.__appendUriCapabilities()
        try:
            # Quels sont les geoservices disponibles ?
            self.wmts = WebMapTileService(self.uri)
        except TypeError as e:
            print("OWSLib mixing str and unicode args", str(e))
        except ServiceException as e:
            print("WMTS - Bad operation: " + self.uri, str(e))
        except Exception as e:
            print(str(e))

        return True

    # check if GetTile operation is available
    def __checkGetTile(self) -> bool:
        if not hasattr(self.wmts, "gettile") or "GetTile" not in [op.name for op in self.wmts.operations]:
            print("Required GetTile operation not available in: " + self.uri)
            return False
        else:
            print("GetTile available")
        return True

    # check if tilematrixsets is available
    def __checkTileMatrixSet(self) -> bool:
        if not hasattr(self.wmts, "tilematrixsets"):
            print("Required tilematrixsets not available in: " + self.uri)
            return False
        else:
            print("tilematrixsets available")
        return True

    # GetTile URL
    def getTileUrl(self):
        wmts_lyr_url = self.wmts.getOperationByName("GetTile").methods
        wmts_lyr_url = wmts_lyr_url[0].get("url")
        print("Available url : {}".format(wmts_lyr_url[:len(wmts_lyr_url) - 1]))
        return wmts_lyr_url[:len(wmts_lyr_url) - 1]

    # Style definition
    def getStyles(self):
        lyr_style = None
        styles = self.wmts_lyr.styles
        '''
            La variable styles est de type dict cle:valeur, exemple :
            normal:{'isDefault': True, 'title': 'Légende générique', 'abstract': 'Fichier de légende générique – pour la compatibilité avec certains systèmes', 'legend': 'https://wxs.ign.fr/static/legends/LEGEND.jpg', 'width': '200', 'height': '200', 'format': 'image/jpeg', 'keywords': ['Défaut']}
            ou cle = normal
            et valeur = {'isDefault': True, 'title': 'Légende générique', 'abstract': 'Fichier de légende générique...}
        '''
        for cle, valeur in styles.items():
            print("Available styles : {}".format(cle))
            # Le style est donc la cle du dictionnaire
            lyr_style = cle

        return lyr_style

    # Get a layer
    def getLayer(self, idGuichetLayerWmts):
        if self.wmts is None:
            return None
        layers = list(self.wmts.contents)
        print("Available layers : ", layers)
        for layer in layers:
            self.wmts_lyr = self.wmts[layer]
            if self.wmts_lyr.id != idGuichetLayerWmts:
                continue
            self.layer_id = self.wmts_lyr.id
            self.title_layer = self.wmts_lyr.title
            print("Layer picked : {}:{}".format(self.title_layer, self.layer_id))
            return layer
        return None

    # Tile Matrix Set
    def getTileMatrixSet(self):
        self.tile_matrix_set = self.wmts_lyr._tilematrixsets[0]
        print("Available tileMatrixSet : {}".format(self.tile_matrix_set))

    # Format
    def getFormat(self):
        layer_format = self.wmts_lyr.formats[0]
        print("Available layer format : {}".format(layer_format))
        return layer_format

    # La requete doit être de la forme :
    # crs=EPSG:3857&
    # dpiMode=7&
    # format=image/jpeg&
    # layers=GEOGRAPHICALGRIDSYSTEMS.MAPS&
    # styles=normal&
    # tileMatrixSet=PM&
    # url=https://wxs.ign.fr/choisirgeoportail/geoportail/wmts?
    # SERVICE%3DWMTS%26VERSION%3D1.0.0%26REQUEST%3DGetCapabilities
    # TODO utilisation avec le proxy dans le panneau de configuration en désactivant les variables d'environnement
    def getWtmsUrlParams(self, idGuichetLayerWmts) -> ():
        if not idGuichetLayerWmts:
            return "Exception", "Import_WMTS.getWtmsUrlParams : le nom de la couche géoservices est vide"

        if self.getLayer(idGuichetLayerWmts) is None:
            return "Exception", "Import_WMTS.getWtmsUrlParams.getLayer : géoservices non disponible pour la couche {}" \
                .format(idGuichetLayerWmts)

        self.getTileMatrixSet()

        # Patch pour les flux privés GPF
        url_tmp = self.getTileUrl()

        if url_tmp.find("/private/") == -1:
            wmts_url_params = {
                "IgnoreGetMapUrl": 1,
                "crs": self.crs,
                "dpiMode": "7",
                "format": self.getFormat(),
                "layers": self.layer_id,
                "styles": self.getStyles(),
                "tileMatrixSet": self.tile_matrix_set,
                "url": "{}{}".format(self.getTileUrl(), cst.PARTOFURLWMTS)

            }
        else:
            wmts_url_params = {
                "IgnoreGetMapUrl": 1,
                "crs": self.crs,
                "dpiMode": "7",
                "format": self.getFormat(),
                "layers": self.layer_id,
                "styles": self.getStyles(),
                "tileMatrixSet": self.tile_matrix_set,
                "url": "{}{}%26apikey%3D{}".format(self.getTileUrl(),
                                                   cst.PARTOFURLWMTS,
                                                   cst.APIKEY)
            }
        wmts_url_final = urllib.parse.unquote(urllib.parse.urlencode(wmts_url_params))
        return self.title_layer, wmts_url_final
