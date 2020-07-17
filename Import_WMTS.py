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
        " We are in the pâté."
    )

class importWMTS:
    # Variables
    #current_crs = str(QgsProject.instance().mapCanvas().mapRenderer().destinationCrs().authid())

    qgis_wms_formats = (
        "image/png",
        "image/png8",
        "image/jpeg",
        "image/svg",
        "image/gif",
        "image/geotiff",
        "image/tiff",
    )
    wmts = None
    uri = QgsDataSourceUri()
    context = None

    def __init__(self, context):
        self.context = context


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

        print(dir(self.wmts))
        return True


    # Construction url GetCapabilities
    # exemple : https://wxs.ign.fr/[cle]/geoportail/wmts?service=WMTS&request=GetCapabilities
    def appendUriCapabilities(self):

        params = {
            'service': cst.WMTS,
            'request': 'GetCapabilities'
        }
        clegeoportail = self.context.clegeoportail
        if clegeoportail == None or clegeoportail == cst.DEMO:
            clegeoportail = cst.CLEGEOPORTAILSTANDARD

        self.uri = "https://wxs.ign.fr/{}/geoportail/wmts?{}" \
            .format(clegeoportail, urllib.parse.unquote(urllib.parse.urlencode(params)))
        print(self.uri)


    # check if GetTile operation is available
    def checkGetTile(self):
        if not hasattr(self.wmts, "gettile") or "GetTile" not in [op.name for op in self.wmts.operations]:
            print("Required GetTile operation not available in: " + self.uri)
            return False
        else:
            print("GetTile available")
        return True


    # GetTile URL
    def getTileUrl(self):
        wmts_lyr_url = None
        wmts_lyr_url = self.wmts.getOperationByName("GetTile").methods
        print(wmts_lyr_url)
        wmts_lyr_url = wmts_lyr_url[0].get("url")
        print(wmts_lyr_url)
        if wmts_lyr_url[-1] == "&":
            wmts_lyr_url = wmts_lyr_url[:-1]
        return wmts_lyr_url