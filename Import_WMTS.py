#Imports
import urllib
from .core import ConstanteRipart as cst
from qgis.core import QgsDataSourceUri, QgsProject

try:
    from owslib.wmts import WebMapTileService
    from owslib.util import ServiceException
    import owslib
    print("Depencencies - owslib version: {}".format(owslib.__version__))
except ImportError as e:
    print("Depencencies - owslib is not present")

try:
    from owslib.util import HTTPError
    print("Depencencies - HTTPError within owslib")
except ImportError as e:
    print(
        "Depencencies - HTTPError not within owslib."
        " Trying to get it from urllib directly."
    )
try:
    from urllib import HTTPError
    print("Depencencies - HTTPError within urllib")
except ImportError as e:
    print(
        "Depencencies - HTTPError not within urllib."
    )


class importWMTS:

    # Variables
    wmts = None
    uri = QgsDataSourceUri()
    context = None
    wmts_lyr = None
    tile_matrix_set = None
    layer_id = None
    crs = None


    def __init__(self, context):
        self.context = context
        self.checkOpenService()
        self.checkGetTile()
        self.checkTileMatrixSet()


    # Construction url GetCapabilities sur le geoportail
    # exemple : https://wxs.ign.fr/[cle]/wmts?service=WMTS&request=GetCapabilities
    def appendUriCapabilities(self):
        params = {
            'service': cst.WMTS,
            'request': 'GetCapabilities'
        }
        clegeoportail = self.context.clegeoportail
        if clegeoportail == None or clegeoportail == cst.DEMO:
            clegeoportail = cst.CLEGEOPORTAILSTANDARD

        '''
        Avec l'url http://wxs.ign.fr/VOTRE_CLE/geoportail/wmts, la projection proposée est
        web Mercator sphérique EPSG:3857 (page 18 du document DT_APIGeoportail.pdf)
        '''
        self.crs = "EPSG:3857"
        self.uri = "https://wxs.ign.fr/{}/geoportail/wmts?{}" \
            .format(clegeoportail, urllib.parse.unquote(urllib.parse.urlencode(params)))


    # opening WMTS
    def checkOpenService(self):
        self.appendUriCapabilities()
        try:
            self.wmts = WebMapTileService(self.uri)
        except TypeError as e:
            print("OWSLib mixing str and unicode args", str(e))
        except ServiceException as e:
            print("WMTS - Bad operation: " + self.uri, str(e))
        except Exception as e:
            print(str(e))

        return True


    # check if GetTile operation is available
    def checkGetTile(self):
        if not hasattr(self.wmts, "gettile") or "GetTile" not in [op.name for op in self.wmts.operations]:
            print("Required GetTile operation not available in: " + self.uri)
            return False
        else:
            print("GetTile available")
        return True


    # check if tilematrixsets is available
    def checkTileMatrixSet(self):
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
        print("Available url : {}".format(wmts_lyr_url))
        return wmts_lyr_url


    # Style definition
    def getStyles(self):
        styles = self.wmts_lyr.styles
        '''
            La variable styles est de type dict cle:valeur, exemple :
            normal:{'isDefault': True, 'title': 'Légende générique', 'abstract': 'Fichier de légende générique – pour la compatibilité avec certains systèmes', 'legend': 'https://wxs.ign.fr/static/legends/LEGEND.jpg', 'width': '200', 'height': '200', 'format': 'image/jpeg', 'keywords': ['Défaut']}
            ou cle = normal
            et valeur = {'isDefault': True, 'title': 'Légende générique', 'abstract': 'Fichier de légende générique...}
        '''
        for cle, valeur in styles.items():
            print ("Available styles : {}".format(cle))
        # Le style est donc la cle du dictionnaire
        lyr_style = cle
        return lyr_style


    # Get a layer
    def getLayer(self, idGuichetLayerWmts):
        layers = list(self.wmts.contents)
        print("Available layers : ", layers)
        for layer in layers:
            self.wmts_lyr = self.wmts[layer]
            if self.wmts_lyr.id != idGuichetLayerWmts:
                continue
            self.layer_id = self.wmts_lyr.id
            print("Layer picked : {}:{}".format(self.wmts_lyr.title, self.layer_id))
            return self.layer_id


    # Tile Matrix Set
    def getTileMatrixSet(self):
        self.tile_matrix_set = self.wmts_lyr._tilematrixsets[0]
        print("Available tileMatrixSet : {}".format(self.tile_matrix_set))


    # Format
    def getFormat(self):
        layer_format = self.wmts_lyr.formats[0]
        print ("Available layer format : {}".format(layer_format))
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
    def getWtmsUrlParams(self, idGuichetLayerWmts):
        self.getLayer(idGuichetLayerWmts)
        self.getTileMatrixSet()
        wmts_url_params = {
            "crs": self.crs,
            "dpiMode": "7",
            "format": self.getFormat(),
            "layers": self.layer_id,
            "styles": self.getStyles(),
            "tileMatrixSet": self.tile_matrix_set,
            "url": "{}{}".format(self.getTileUrl(),"SERVICE%3DWMTS%26VERSION%3D1.0.0%26REQUEST%3DGetCapabilities")
        }
        wmts_url_final = urllib.parse.unquote(urllib.parse.urlencode(wmts_url_params))
        return wmts_url_final