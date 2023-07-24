import time
import json
from .HttpRequest import HttpRequest
from .SQLiteManager import SQLiteManager


class WfsGet(object):

    def __init__(self, parameters):
        if 'urlHostEspaceCo' in parameters:
            self.urlHostEspaceCo = parameters['urlHostEspaceCo']
            self.url = parameters['urlHostEspaceCo'] + '/gcms/api/wfs'
        if 'authentification' in parameters:
            self.identification = parameters['authentification']
        if 'proxy' in parameters:
            self.proxy = parameters['proxy']
        self.databasename = parameters['databasename']
        self.layerName = parameters['layerName']
        self.geometryName = parameters['geometryName']
        self.sridProject = parameters['sridProject']
        self.sridLayer = parameters['sridLayer']
        self.bbox = parameters['bbox']
        self.parametersGcmsGet = {}
        self.bDetruit = parameters['detruit']
        self.isBduni = parameters['isBduni']
        self.is3D = parameters['is3D']
        self.numrec = int(parameters['numrec'])
        # Paramètres pour insérer un objet dans une table SQLite
        self.parametersForInsertsInTable = {'tableName': self.layerName, 'geometryName': self.geometryName,
                                            'sridTarget': self.sridProject, 'sridSource': self.sridLayer,
                                            'isBduni': self.isBduni, 'is3D': self.is3D,
                                            'geometryType': ""}

    def makeRequestDeletedObjects(self):
        # il s'agit de retrouver
        self.initParametersGcmsGet(True)
        while True:
            response = HttpRequest.nextRequest(self.url, authent=self.identification, proxies=self.proxy,
                                                        params=self.parametersGcmsGet)
            if response['status'] == 'error':
                break

            if len(response['features']) == 0 and response['stop']:
                break
            # Synchronisation (maj) de toutes les couches
            # ou un update après un post (enregistrement des couches actives)
            else:
                for feature in response['features']:
                    conditionTable = "{0} WHERE cleabs = '{1}'".format(self.layerName, feature['cleabs'])
                    cleabs = SQLiteManager.selectColumnFromTable(conditionTable, "cleabs")
                    if len(cleabs) == 0:
                        continue
                    else:
                        # si la cleabs est trouvée dans la base SQLite du client alors il faut supprimer
                        # l'enregistrement
                        SQLiteManager.deleteRowsInTableBDUni(self.layerName, [cleabs[0]])
            self.setOffset(response['offset'])
            if response['stop']:
                break

    def initParametersGcmsGet(self, filterDelete=False):
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
        self.setFilter(filterDelete)
        self.setOffset(offset)
        self.setMaxFeatures(maxFeatures)
        self.setVersion('1.0.0')

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
    def gcms_get(self, bExtraction=False):
        message = ""
        self.initParametersGcmsGet()
        start = time.time()
        totalRows = 0
        if self.isBduni:
            maxNumrec = self.getMaxNumrec()
        else:
            maxNumrec = 0

        sqliteManager = SQLiteManager()
        while True:
            response = HttpRequest.nextRequest(self.url, authent=self.identification, proxies=self.proxy,
                                                        params=self.parametersGcmsGet)
            if response['status'] == 'error':
                message += "[WfsGet.py::gcms_get::nextRequest] {0} : {1}".format(response['status'], response['reason'])
                break

            if len(response['features']) == 0 and response['stop']:
                break
            # si c'est une table non BDUni ou une extraction,
            # on insére tous les objets dans la base SQLite en appliquant un filtre avec la zone de travail active
            if not self.isBduni or bExtraction:
                totalRows += sqliteManager.insertRowsInTable(self.parametersForInsertsInTable, response['features'])
            # sinon c'est une synchronisation (maj) de toutes les couches
            # ou un update après un post (enregistrement des couches actives)
            else:
                for feature in response['features']:
                    conditionTable = "{0} WHERE cleabs = '{1}'".format(self.layerName, feature['cleabs'])
                    cleabs = SQLiteManager.selectColumnFromTable(conditionTable, "cleabs")
                    if len(cleabs) == 0:
                        # création d'un nouvel objet
                        totalRows += sqliteManager.insertRowsInTable(self.parametersForInsertsInTable, [feature])
                    else:
                        # modification d'un objet
                        # si la cleabs est trouvée dans la base SQLite du client alors il faut supprimer
                        # l'ancien enregistrement et en insérer un nouveau
                        SQLiteManager.deleteRowsInTableBDUni(self.layerName, [cleabs[0]])
                        totalRows += sqliteManager.insertRowsInTable(self.parametersForInsertsInTable, [feature])
            self.setOffset(response['offset'])
            if response['stop']:
                break
        # suppression des objets pour une table BDUni et différent d'une extraction
        if self.isBduni and bExtraction is False:
            self.makeRequestDeletedObjects()
        # nettoyage de la base SQLite
        SQLiteManager.vacuumDatabase()
        end = time.time()
        timeResult = end - start
        if timeResult > 60:
            if message == '':
                message = "{0} objet(s), extrait(s) en : {1} minute(s)".format(totalRows, round(timeResult / 60, 1))
        else:
            if totalRows == 0:
                message += "Pas d'objets extraits"
            else:
                if message == '':
                    message = "{0} objet(s), extrait(s) en : {1} seconde(s)".format(totalRows, round(timeResult, 1))
        return maxNumrec, message

    def getMaxNumrec(self):
        # https://espacecollaboratif.ign.fr/gcms/database/bdtopo_fxx/feature-type/troncon_hydrographique/max-numrec
        url = "{0}/gcms/database/{1}/feature-type/{2}/max-numrec".format(self.urlHostEspaceCo, self.databasename,
                                                                         self.layerName)
        response = HttpRequest.makeHttpRequest(url, authent=self.identification, proxies=self.proxy)
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
        typename = "{0}:{1}".format(self.databasename, self.layerName)
        self.parametersGcmsGet['typename'] = typename

    def setNumrec(self):
        self.parametersGcmsGet['numrec'] = self.numrec

    def setFilter(self, filter):
        if self.bDetruit:
            if filter:
                self.parametersGcmsGet['filter'] = '{"detruit":true}'
            else:
                self.parametersGcmsGet['filter'] = '{"detruit":false}'

    def setBBox(self):
        self.parametersGcmsGet['bbox'] = self.bbox.boxToStringWithSrid(self.sridProject, self.sridLayer)

    def setOffset(self, offset):
        self.parametersGcmsGet['offset'] = offset

    def setMaxFeatures(self, maxFeatures):
        self.parametersGcmsGet['maxFeatures'] = maxFeatures
