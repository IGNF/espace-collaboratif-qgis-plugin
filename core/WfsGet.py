import time
from .HttpRequest import HttpRequest
from .SQLiteManager import SQLiteManager


class WfsGet(object):

    def __init__(self, parameters) -> None:
        if 'urlHostEspaceCo' in parameters:
            self.urlHostEspaceCo = parameters['urlHostEspaceCo']
            self.url = parameters['urlHostEspaceCo'] + '/gcms/api/wfs'
        if 'proxy' in parameters:
            self.proxy = parameters['proxy']
        if 'headers' in parameters:
            self.headers = parameters['headers']
        self.databasename = parameters['databasename']
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
        # Paramètres pour insérer un objet dans une table SQLite
        self.parametersForInsertsInTable = {'tableName': self.layerName, 'geometryName': self.geometryName,
                                            'sridTarget': self.sridProject, 'sridSource': self.sridLayer,
                                            'isStandard': self.isStandard, 'is3D': self.is3D,
                                            'geometryType': ""}
        self.databaseid = parameters['databaseid']
        self.tableid = parameters['tableid']

    def __initParametersGcmsGet(self, filterDelete=False) -> None:
        offset = 0
        maxFeatures = 5000
        # Passage des paramètres pour l'url
        self.__setService()
        self.__setRequest()
        # GeoJSON | JSON | CSV | GML (par défaut)
        self.__setOutputFormat('JSON')
        self.__setTypeName()
        if self.numrec != 0:
            self.__setNumrec()
        if self.bbox is not None:
            self.__setBBox()
        self.__setFilter(filterDelete)
        self.__setOffset(offset)
        self.__setMaxFeatures(maxFeatures)
        self.__setVersion('1.0.0')

    def __makeRequestDeletedObjects(self) -> None:
        # il s'agit de retrouver
        self.__initParametersGcmsGet(True)
        while True:
            response = HttpRequest.nextRequest(self.url, headers=self.headers, proxies=self.proxy,
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
            self.__setOffset(response['offset'])
            if response['stop']:
                break

    # La requête doit être de type :
    # https://espacecollaboratif.ign.fr/gcms/api/wfs
    # ?service=WFS
    # &request=GetFeature
    # &typeName=bduni_interne_qualif_fxx:troncon_de_route
    # &bbox=721962.3431462792,6828963.456591784,722530.9622283925,6829331.475409639
    # &filter={%22detruit%22:false}
    # &offset=0
    # &maxFeatures=200
    # &version=1.1.0
    # http://gitlab.dockerforge.ign.fr/rpg/oukile_v2/blob/master/assets/js/oukile/saisie_controle/services/layer-service.js
    def gcms_get(self, bExtraction=False) -> ():
        message = ""
        self.__initParametersGcmsGet()
        start = time.time()
        totalRows = 0
        if self.isStandard:
            maxNumrec = 0
        else:
            maxNumrec = self.getMaxNumrec()

        sqliteManager = SQLiteManager()
        while True:
            response = HttpRequest.nextRequest(self.url, headers=self.headers, proxies=self.proxy,
                                               params=self.parametersGcmsGet)
            if response['status'] == 'error':
                message += "[WfsGet.py::gcms_get::nextRequest] {0} : {1}".format(response['status'], response['reason'])
                break

            if len(response['features']) == 0 and response['stop']:
                break
            # si c'est une table standard (non BDUni) ou une extraction,
            # on insére tous les objets dans la base SQLite en appliquant un filtre avec la zone de travail active
            if self.isStandard is True or self.isStandard == 1 or bExtraction is True:
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
            self.__setOffset(response['offset'])
            if response['stop']:
                break
        # suppression des objets pour une table BDUni et différent d'une extraction
        if self.isStandard is False or self.isStandard == 0 and bExtraction is False:
            self.__makeRequestDeletedObjects()
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

    def getMaxNumrec(self) -> int:
        # https://espacecollaboratif.ign.fr/gcms/database/bdtopo_fxx/feature-type/troncon_hydrographique/max-numrec
        # https://qlf-collaboratif.cegedim-hds.fr/collaboratif-4.0/gcms/api/databases/18/tables/479/max-numrec

        url = "{0}/gcms/api/databases/{1}/tables/{2}/max-numrec".format(self.urlHostEspaceCo, self.databaseid,
                                                                        self.tableid)
        response = HttpRequest.makeHttpRequest(url, proxies=self.proxy, headers=self.headers,
                                               launchBy='getMaxNumrec : {}'.format(self.layerName))
        # Succès : get (code 200) post (code 201)
        if response.status_code == 200 or response.status_code == 201:
            numrec = response.json()
            print("database : {} numrec : {}".format(self.databasename, numrec))
        else:
            message = "code : {} raison : {}".format(response.status_code, response.reason)
            raise Exception("WfsGet.getMaxNumrec -> ".format(message))
        return numrec

    def __setService(self) -> None:
        self.parametersGcmsGet['service'] = 'WFS'

    def __setVersion(self, version) -> None:
        self.parametersGcmsGet['version'] = version

    def __setRequest(self) -> None:
        self.parametersGcmsGet['request'] = 'GetFeature'

    def __setOutputFormat(self, outputFormat) -> None:
        self.parametersGcmsGet['outputFormat'] = outputFormat

    def __setTypeName(self) -> None:
        typename = "{0}:{1}".format(self.databasename, self.layerName)
        self.parametersGcmsGet['typename'] = typename

    def __setNumrec(self) -> None:
        self.parametersGcmsGet['numrec'] = self.numrec

    def __setFilter(self, _filter) -> None:
        if self.bDetruit:
            if _filter:
                self.parametersGcmsGet['filter'] = '{"detruit":true}'
            else:
                self.parametersGcmsGet['filter'] = '{"detruit":false}'

    def __setBBox(self) -> None:
        self.parametersGcmsGet['bbox'] = self.bbox.boxToStringWithSrid(self.sridProject, self.sridLayer)

    def __setOffset(self, offset) -> None:
        self.parametersGcmsGet['offset'] = offset

    def __setMaxFeatures(self, maxFeatures) -> None:
        self.parametersGcmsGet['maxFeatures'] = maxFeatures
