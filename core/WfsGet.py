import json

from .RipartServiceRequest import RipartServiceRequest
from .SQLiteManager import SQLiteManager


class WfsGet(object):
    context = None
    url = None
    identification = None
    proxy = None
    databaseName = None
    layerName = None
    layerRole = None
    geometryName = None
    sridProject = None
    sridLayer = None
    is3d = None
    bbox = None
    parametersGcmsGet = None

    def __init__(self, context, parameters):
        self.context = context
        self.url = self.context.client.getUrl() + '/gcms/wfs'
        self.identification = self.context.client.getAuth()
        self.proxy = self.context.client.getProxies()
        self.databaseName = parameters['databasename']
        self.layerName = parameters['layerName']
        self.layerRole = parameters['role']
        self.geometryName = parameters['geometryName']
        self.sridProject = parameters['sridProject']
        self.sridLayer = parameters['sridLayer']
        self.is3d = parameters['is3d']
        self.bbox = parameters['bbox']
        self.parametersGcmsGet = {}

    # La requête doit être de type :
    # https://espacecollaboratif.ign.fr/gcms/wfs
    # ?service=WFS
    # &request=GetFeature
    # &typeName=bduni_interne_qualif_fxx:troncon_de_route
    # &bbox=721962.3431462792,6828963.456591784,722530.9622283925,6829331.475409639
    # &filter={%22detruit%22:false}
    # &offset=0
    # &maxFeatures=200
    # &version=1.1.0
    def gcms_get(self):
        offset = 0
        maxFeatures = 5000

        # Passage des paramètres pour l'url
        self.setService()
        self.setRequest()
        # GeoJSON | JSON | CSV | GML (par défaut)
        self.setOutputFormat('JSON')
        self.setTypeName()
        self.setBBox(self.bbox)
        self.setFilter()
        self.setOffset(offset.__str__())
        self.setMaxFeatures(maxFeatures.__str__())
        self.setVersion('1.0.0')
        # Lancement de la requête
        data = RipartServiceRequest.makeHttpRequest(self.url, authent=self.identification, proxies=self.proxy,
                                                    params=self.parametersGcmsGet)
        # Remplissage de la table avec les objets de la couche
        parametersForInsertsInTable = {}
        parametersForInsertsInTable['tableName'] = self.layerName
        parametersForInsertsInTable['geometryName'] = self.geometryName
        parametersForInsertsInTable['sridProject'] = self.sridProject
        parametersForInsertsInTable['sridLayer'] = self.sridLayer
        parametersForInsertsInTable['is3d'] = self.is3d
        parametersForInsertsInTable['role'] = self.layerRole
        SQLiteManager.insertRowsInTable(parametersForInsertsInTable, json.loads(data))

    def setService(self):
        self.parametersGcmsGet['service'] = 'WFS'

    def setVersion(self, version):
        self.parametersGcmsGet['version'] = version

    def setRequest(self):
        self.parametersGcmsGet['request'] = 'GetFeature'

    def setOutputFormat(self, format):
        self.parametersGcmsGet['outputFormat'] = format

    def setTypeName(self):
        typename = "{0}:{1}".format(self.databaseName, self.layerName)
        self.parametersGcmsGet['typename'] = typename

    def setFilter(self):
        self.parametersGcmsGet['filter'] = '{"detruit":false}'

    def setBBox(self, bbox):
        self.parametersGcmsGet['bbox'] = bbox.boxToStringLambert93()

    def setOffset(self, offset):
        self.parametersGcmsGet['offset'] = offset

    def setMaxFeatures(self, maxFeatures):
        self.parametersGcmsGet['maxFeatures'] = maxFeatures
