import time
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
    geometryName = None
    sridProject = None
    sridLayer = None
    bbox = None
    parametersGcmsGet = None
    bDetruit = None
    isStandard = None
    is3D = None
    numrec = None
    urlTransaction = None

    def __init__(self, context, parameters):
        self.context = context
        self.url = self.context.client.getUrl() + '/gcms/wfs'
        self.identification = self.context.client.getAuth()
        self.proxy = self.context.client.getProxies()
        self.databaseName = parameters['databasename']
        self.layerName = parameters['layerName']
        self.geometryName = parameters['geometryName']
        self.sridProject = parameters['sridProject']
        self.sridLayer = parameters['sridLayer']
        self.bbox = parameters['bbox']
        self.parametersGcmsGet = {}
        self.bDetruit = parameters['detruit']
        self.isStandard = parameters['isStandard']
        self.is3D = parameters['is3D']
        self.numrec = int(parameters['numrec'])
        self.urlTransaction = parameters['urlTransaction']

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
    # http://gitlab.dockerforge.ign.fr/rpg/oukile_v2/blob/master/assets/js/oukile/saisie_controle/services/layer-service.js
    def gcms_get(self):
        # Remplissage de la table avec les objets de la couche
        parametersForInsertsInTable = {'tableName': self.layerName, 'geometryName': self.geometryName,
                                       'sridTarget': self.sridProject, 'sridSource': self.sridLayer,
                                       'isStandard': self.isStandard, 'is3D': self.is3D,
                                       'geometryType': ""}
        offset = 0
        maxFeatures = 5000
        # Passage des paramètres pour l'url
        self.setService()
        self.setRequest()
        # GeoJSON | JSON | CSV | GML (par défaut)
        self.setOutputFormat('JSON')
        self.setTypeName()
        if self.numrec != 0:
            self.setNumrec()
        if self.bbox is not None:
            self.setBBox()
        self.setFilter()
        self.setOffset(offset)
        self.setMaxFeatures(maxFeatures)
        self.setVersion('1.0.0')
        start = time.time()
        totalRows = 0
        if self.isStandard:
            maxNumrec = 0
        else:
            maxNumrec = self.getMaxNumrec()
        sqliteManager = SQLiteManager()
        while True:
            response = RipartServiceRequest.nextRequest(self.url, authent=self.identification, proxies=self.proxy,
                                                        params=self.parametersGcmsGet)
            if response['status'] == 'error':
                break
            totalRows += sqliteManager.insertRowsInTable(parametersForInsertsInTable, response['features'])
            self.setOffset(response['offset'])
            if response['stop']:
                break
        sqliteManager.vacuumDatabase()
        end = time.time()
        timeResult = end - start
        if timeResult > 60:
            print("{0} objets, extraits en : {1} minutes".format(totalRows, timeResult/60))
        else:
            print("{0} objets, extraits en : {1} secondes".format(totalRows, timeResult))
        return maxNumrec

    def getMaxNumrec(self):
        # https://espacecollaboratif.ign.fr/gcms/database/bdtopo_fxx/feature-type/troncon_hydrographique/max-numrec
        url = "{0}/gcms/database/{1}/feature-type/{2}/max-numrec".format(self.context.client.getUrl(), self.databaseName, self.layerName)
        response = RipartServiceRequest.makeHttpRequest(url, authent=self.identification, proxies=self.proxy)
        data = json.loads(response)
        return data['numrec']

    def setService(self):
        self.parametersGcmsGet['service'] = 'WFS'

    def setVersion(self, version):
        self.parametersGcmsGet['version'] = version

    def setRequest(self):
        self.parametersGcmsGet['request'] = 'GetFeature'

    def setOutputFormat(self, outputFormat):
        self.parametersGcmsGet['outputFormat'] = outputFormat

    def setTypeName(self):
        typename = "{0}:{1}".format(self.databaseName, self.layerName)
        self.parametersGcmsGet['typename'] = typename

    def setNumrec(self):
        self.parametersGcmsGet['numrec'] = self.numrec

    def setFilter(self):
        if self.bDetruit:
            self.parametersGcmsGet['filter'] = '{"detruit":false}'

    def setBBox(self):
        self.parametersGcmsGet['bbox'] = self.bbox.boxToStringWithSrid(self.sridProject, self.sridLayer)

    def setOffset(self, offset):
        self.parametersGcmsGet['offset'] = offset

    def setMaxFeatures(self, maxFeatures):
        self.parametersGcmsGet['maxFeatures'] = maxFeatures
