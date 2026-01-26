import time
from qgis.core import QgsCoordinateReferenceSystem
from .HttpRequest import HttpRequest
from .SQLiteManager import SQLiteManager
from .PluginLogger import PluginLogger
from ..PluginHelper import PluginHelper


class WfsGet(object):
    """
    Classe implémentant une requête en HTTP GET pour une couche WFS.
    """

    def __init__(self, parameters) -> None:
        """
        Constructeur.

        :param parameters: les paramètres nécessaires pour lancer une requête HTTP GET
        :type parameters: dict
        """
        self.__logger = PluginLogger("WfsGet").getPluginLogger()
        self.context = None
        if PluginHelper.keyExist('context', parameters):
            self.context = parameters['context']
        if PluginHelper.keyExist('urlHostEspaceCo', parameters):
            self.urlHostEspaceCo = parameters['urlHostEspaceCo']
            self.url = parameters['urlHostEspaceCo'] + '/gcms/api/wfs'
        if PluginHelper.keyExist('proxies', parameters):
            self.proxies = parameters['proxies']
        if PluginHelper.keyExist('headers', parameters):
            self.headers = parameters['headers']
        if PluginHelper.keyExist('databasename', parameters):
            self.databasename = parameters['databasename']
        if PluginHelper.keyExist('layerName', parameters):
            self.layerName = parameters['layerName']
        if PluginHelper.keyExist('geometryName', parameters):
            self.geometryName = parameters['geometryName']
        if PluginHelper.keyExist('sridProject', parameters):
            self.sridProject = parameters['sridProject']
        if PluginHelper.keyExist('sridLayer', parameters):
            self.sridLayer = parameters['sridLayer']
        if PluginHelper.keyExist('bbox', parameters):
            self.bbox = parameters['bbox']
        self.parametersGcmsGet = {}
        if PluginHelper.keyExist('detruit', parameters):
            self.bDetruit = parameters['detruit']
        if PluginHelper.keyExist('isStandard', parameters):
            self.isStandard = parameters['isStandard']
        if PluginHelper.keyExist('is3D', parameters):
            self.is3D = parameters['is3D']
        if PluginHelper.keyExist('numrec', parameters):
            self.numrec = int(parameters['numrec'])
        # Paramètres pour insérer un objet dans une table SQLite
        self.parametersForInsertsInTable = {'tableName': self.layerName, 'geometryName': self.geometryName,
                                            'sridTarget': self.sridProject, 'sridSource': self.sridLayer,
                                            'isStandard': self.isStandard, 'is3D': self.is3D,
                                            'geometryType': ""}
        if PluginHelper.keyExist('databaseid', parameters):
            self.databaseid = parameters['databaseid']
        if PluginHelper.keyExist('tableid', parameters):
            self.tableid = parameters['tableid']

    def __initParametersGcmsGet(self, filterDelete=False) -> None:
        """
        Initialisation des paramètres pour une requête HTTP GET.

        :param filterDelete: à True, si la requête doit récupérer les objets détruits d'une couche BDUni
        :type filterDelete: bool
        """
        offset = 0
        maxFeatures = 10000  # Maximum API limit - increased from 5000 for better performance
        # Passage des paramètres pour l'url
        self.__setService()
        self.__setRequest()
        self.__setOutputFormat()
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
        """
        Retrouver les objets détruits d'une table BDUni pour supprimer les enregistrements dans la base SQLite
        du projet utilisateur.
        """
        self.__initParametersGcmsGet(True)
        while True:
            response = HttpRequest.nextRequest(self.url, headers=self.headers, proxies=self.proxies,
                                               params=self.parametersGcmsGet)
            if response['status'] == 'error':
                break

            if len(response['features']) == 0 and response['stop']:
                break
            # Synchronisation (maj) de toutes les couches
            # ou un update après un post (enregistrement des couches actives)
            else:
                for feature in response['features']:
                    cleabs = SQLiteManager.selectColumnFromTableWithCondition("cleabs", self.layerName,
                                                                              "cleabs", feature['cleabs'])
                    if cleabs is None:
                        continue
                    else:
                        # si la cleabs est trouvée dans la base SQLite du client alors il faut supprimer
                        # l'enregistrement
                        SQLiteManager.deleteRowsInTableBDUni(self.layerName, [cleabs[0]])
            self.__setOffset(response['offset'])
            if response['stop']:
                break

    def gcmsGet(self, bExtraction=False) -> ():
        """
        Envoie une requête GET et met à jour les tables SQLite du projet en cours.
        NB : le dernier numéro de mise à jour (numRec) d'une table est fixé à 0 pour une table différente de la BDUni.

        :param bExtraction: à True quand il s'agit d'extraire les données sur une zone de travail
        :type bExtraction: bool

        :return: le dernier numéro de mise à jour sur une table et un message de fin
        """
        import gc  # For garbage collection
        
        message = ""
        self.__initParametersGcmsGet()
        start = time.time()
        totalRows = 0
        requestCount = 0
        if self.isStandard:
            maxNumrec = 0
        else:
            # Try to get maxNumrec, but don't block extraction if it fails
            try:
                print("[INFO] Attempting to get maxNumrec for BDUni layer...")
                maxNumrec = self.getMaxNumrec()
                print("[INFO] MaxNumrec: {}".format(maxNumrec))
            except Exception as e:
                print("[WARNING] Failed to get maxNumrec (server error), defaulting to 0")
                print("[WARNING] Error: {}".format(str(e)))
                self.__logger.warning("getMaxNumrec failed: {}, continuing with 0".format(str(e)))
                maxNumrec = 0

        print("\n" + "="*80)
        print("[EXTRACTION START] Layer: {}".format(self.layerName))
        print("[EXTRACTION] Mode: {}".format("Extraction" if bExtraction else "Synchronisation"))
        print("[EXTRACTION] MaxFeatures per request: {}".format(self.parametersGcmsGet.get('maxFeatures', 'N/A')))
        print("="*80)
        self.__logger.info("Starting extraction for layer: {} (mode: {})".format(
            self.layerName, "Extraction" if bExtraction else "Synchronisation"))

        sqliteManager = SQLiteManager()
        MAX_RETRIES = 3
        RETRY_DELAY = 2  # seconds between retries
        
        while True:
            requestCount += 1
            print("\n[REQUEST #{}] Fetching data from API...".format(requestCount))
            print("[REQUEST #{}] Offset: {}, MaxFeatures: {}".format(
                requestCount, 
                self.parametersGcmsGet.get('offset', 0),
                self.parametersGcmsGet.get('maxFeatures', 'N/A')))
            
            # Retry logic for transient errors
            response = None
            for attempt in range(1, MAX_RETRIES + 1):
                if attempt > 1:
                    print("[REQUEST #{}] Retry attempt {}/{} after {} seconds...".format(
                        requestCount, attempt, MAX_RETRIES, RETRY_DELAY))
                    time.sleep(RETRY_DELAY)
                
                response = HttpRequest.nextRequest(self.url, headers=self.headers, proxies=self.proxies,
                                                   params=self.parametersGcmsGet)
                
                if response['status'] == 'ok':
                    if attempt > 1:
                        print("[REQUEST #{}] Success after {} attempts".format(requestCount, attempt))
                    break
                else:
                    # Detailed error information
                    errorReason = response.get('reason', 'Unknown error')
                    errorUrl = response.get('url', 'N/A')
                    errorCode = response.get('code', 'N/A')
                    errorDetails = response.get('details', 'N/A')
                    
                    print("[REQUEST #{}] Attempt {}/{} FAILED".format(requestCount, attempt, MAX_RETRIES))
                    print("  - Error reason: {}".format(errorReason))
                    print("  - Error code: {}".format(errorCode))
                    print("  - URL: {}".format(errorUrl))
                    print("  - Details: {}".format(errorDetails))
                    
                    if attempt == MAX_RETRIES:
                        message += "[WfsGet.py::gcms_get::nextRequest] {0} : {1}".format(response['status'], errorReason)
                        print("\n[ERROR] Request PERMANENTLY FAILED after {} attempts".format(MAX_RETRIES))
                        print("[ERROR] Full error: {}".format(message))
                        print("[ERROR] Server may be overloaded or rate-limiting requests")
                        print("[ERROR] Total features extracted before error: {}".format(totalRows))
                        self.__logger.error("Request failed after {} retries: {}".format(MAX_RETRIES, message))
                        break
            
            # If all retries failed, exit the loop
            if response['status'] == 'error':
                break

            featuresReceived = len(response['features'])
            print("[REQUEST #{}] Received {} features".format(requestCount, featuresReceived))
            
            if featuresReceived == 0 and response['stop']:
                print("[REQUEST #{}] No more data to fetch".format(requestCount))
                break
            
            # si c'est une table standard (non BDUni) ou une extraction,
            # on insére tous les objets dans la base SQLite en appliquant un filtre avec la zone de travail active
            if self.isStandard in (True, 1) or bExtraction is True:
                # Appliquer le filtrage géométrique fin pour les extractions
                features_to_insert = response['features']
                if bExtraction is True:
                    print("[REQUEST #{}] Applying geometric filter...".format(requestCount))
                    features_to_insert = self.__filterFeaturesWithWorkArea(response['features'])
                    featuresAfterFilter = len(features_to_insert)
                    print("[REQUEST #{}] Features after filter: {} (filtered out: {})".format(
                        requestCount, featuresAfterFilter, featuresReceived - featuresAfterFilter))
                
                print("[REQUEST #{}] Inserting {} features into SQLite...".format(requestCount, len(features_to_insert)))
                insertedRows = sqliteManager.insertRowsInTable(self.parametersForInsertsInTable, features_to_insert)
                totalRows += insertedRows
                print("[REQUEST #{}] Inserted {} rows. Total: {}".format(requestCount, insertedRows, totalRows))
                
                # Memory cleanup - release references and force garbage collection
                features_to_insert = None
                response['features'] = None
                gc.collect()
                print("[REQUEST #{}] Memory cleanup completed".format(requestCount))
                
            # sinon c'est une synchronisation (maj) de toutes les couches
            # ou un update après un post (enregistrement des couches actives)
            else:
                print("[REQUEST #{}] Processing BDUni synchronization...".format(requestCount))
                processedInBatch = 0
                for feature in response['features']:
                    cleabs = SQLiteManager.selectColumnFromTableWithCondition("cleabs", self.layerName, "cleabs",
                                                                              feature['cleabs'])
                    if cleabs is None:
                        # création d'un nouvel objet
                        totalRows += sqliteManager.insertRowsInTable(self.parametersForInsertsInTable, [feature])
                    else:
                        # modification d'un objet
                        # si la cleabs est trouvée dans la base SQLite du client alors il faut supprimer
                        # l'ancien enregistrement et en insérer un nouveau
                        SQLiteManager.deleteRowsInTableBDUni(self.layerName, [cleabs[0]])
                        totalRows += sqliteManager.insertRowsInTable(self.parametersForInsertsInTable, [feature])
                    processedInBatch += 1
                print("[REQUEST #{}] Processed {} BDUni features. Total: {}".format(requestCount, processedInBatch, totalRows))
                
                # Memory cleanup for BDUni mode
                response['features'] = None
                gc.collect()
                
            self.__setOffset(response['offset'])
            if response['stop']:
                print("[REQUEST #{}] Extraction complete flag received".format(requestCount))
                break
            else:
                # Small delay between requests to avoid overwhelming the server
                if requestCount % 10 == 0:  # Every 10 requests
                    print("[REQUEST #{}] Pausing 1 second to avoid server overload...".format(requestCount))
                    time.sleep(1)
        # suppression des objets pour une table BDUni et différent d'une extraction
        if self.isStandard in (False, 0) and not bExtraction:
            print("\n[CLEANUP] Processing deleted objects for BDUni...")
            self.__makeRequestDeletedObjects()
            print("[CLEANUP] Deleted objects processed")
        
        # nettoyage de la base SQLite
        print("\n[CLEANUP] Running SQLite VACUUM to optimize database...")
        SQLiteManager.vacuumDatabase()
        print("[CLEANUP] Database optimization completed")
        
        end = time.time()
        timeResult = end - start
        
        # Detailed completion statistics
        print("\n" + "="*80)
        print("[EXTRACTION COMPLETE] Layer: {}".format(self.layerName))
        print("[STATISTICS] Total features extracted: {}".format(totalRows))
        print("[STATISTICS] Total API requests: {}".format(requestCount))
        print("[STATISTICS] Average features per request: {}".format(
            round(totalRows / requestCount, 1) if requestCount > 0 else 0))
        print("[STATISTICS] Total time: {} seconds ({} minutes)".format(
            round(timeResult, 1), round(timeResult / 60, 2)))
        if totalRows > 0:
            print("[STATISTICS] Processing speed: {} features/second".format(
                round(totalRows / timeResult, 1) if timeResult > 0 else 0))
        print("="*80 + "\n")
        
        self.__logger.info("Extraction completed: {} features in {} seconds ({} requests)".format(
            totalRows, round(timeResult, 1), requestCount))
        
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

    def __filterFeaturesWithWorkArea(self, features) -> list:
        """
        Filtrer les objets en cherchant ceux qui intersectent la zone de travail.
        Applique un filtre géométrique fin après le filtre BBox de la requête HTTP.

        :param features: les objets retournés par la requête
        :type features: list
        :return: la liste des objets intersectant la géométrie réelle de la zone de travail
        """
        # Si pas de contexte, on ne peut pas filtrer
        if self.context is None:
            return features

        target_crs = QgsCoordinateReferenceSystem.fromEpsgId(self.sridLayer)
        return PluginHelper.filterWithWorkArea(self.context, features, geometryKey=self.geometryName, targetCrs=target_crs)

    def getMaxNumrec(self) -> int:
        """
        Requête pour récupérer le dernier numéro de réconciliation (NumRec) d'une table BDUni. Chaque mise à jour
        d'une table BDUni se fait par l'intermédiaire d'une surface qui entoure les objets mis à jour appelée
        réconciliation. Chaque réconciliation porte un numéro de séquence, le NumRec.

        :return: le numéro de la mise à jour.
        """
        url = "{0}/gcms/api/databases/{1}/tables/{2}/max-numrec".format(self.urlHostEspaceCo, self.databaseid,
                                                                        self.tableid)
        response = HttpRequest.makeHttpRequest(url, proxies=self.proxies, headers=self.headers,
                                               launchBy='getMaxNumrec : {}'.format(self.layerName))
        
        # Succès : get (code 200) post (code 201)
        if response.status_code == 200 or response.status_code == 201:
            numrec = response.json()
        else:
            message = "code : {} raison : {} response_text: {}".format(response.status_code, response.reason, response.text)
            print("[ERROR] getMaxNumrec failed: {}".format(message))
            self.__logger.error("getMaxNumrec failed: {}".format(message))
            raise Exception("WfsGet.getMaxNumrec -> {}".format(message))
        return numrec

    def __setService(self) -> None:
        """Complète le dictionnaire des paramètres en vue d'une requête GET par l'item 'service'."""
        self.parametersGcmsGet['service'] = 'WFS'

    def __setVersion(self, version) -> None:
        """
        Fixe le numéro de version d'une requête GET en complètant le dictionnaire des paramètres avec l'item 'version'.

        :param version: version du protocole HTTP
        :type version: str
        """
        self.parametersGcmsGet['version'] = version

    def __setRequest(self) -> None:
        """
        Complète le dictionnaire des paramètres en vue d'une requête GET par l'item 'request' en fixant le type
        à 'GetFeature'.
        """
        self.parametersGcmsGet['request'] = 'GetFeature'

    def __setOutputFormat(self, outputFormat='JSON') -> None:
        """
        Complète le dictionnaire des paramètres en vue d'une requête GET par l'item 'outputFormat' en fixant le format
        de retour pour la réponse.

        :param outputFormat: type de réponse attendue, par défaut JSON. Autres formats GeoJSON | CSV | GML
        :type outputFormat: str
        """
        self.parametersGcmsGet['outputFormat'] = outputFormat

    def __setTypeName(self) -> None:
        """
        Complète le dictionnaire des paramètres en vue d'une requête GET par l'item 'typename'.
        """
        typename = "{0}:{1}".format(self.databasename, self.layerName)
        self.parametersGcmsGet['typename'] = typename

    def __setNumrec(self) -> None:
        """
        Complète le dictionnaire des paramètres en vue d'une requête GET par l'item 'numrec'.
        """
        self.parametersGcmsGet['numrec'] = self.numrec

    def __setFilter(self, _filter) -> None:
        """
        Complète le dictionnaire des paramètres en vue d'une requête GET par l'item 'filter'.

        :param _filter: à True, permet de récupérer les objets détruits dans une table
        :type _filter: bool
        """
        if self.bDetruit:
            if _filter:
                self.parametersGcmsGet['filter'] = '{"detruit":true}'
            else:
                self.parametersGcmsGet['filter'] = '{"detruit":false}'

    def __setBBox(self) -> None:
        """Complète le dictionnaire des paramètres en vue d'une requête GET par l'item 'bbox'."""
        self.parametersGcmsGet['bbox'] = self.bbox.boxToStringWithSrid(self.sridProject, self.sridLayer)

    def __setOffset(self, offset) -> None:
        """
        Complète le dictionnaire des paramètres en vue d'une requête GET par l'item 'offset'

        :param offset: nombre de pages que retourne une requête, initialisé à 0 pour la première.
        :type offset: int
        """
        self.parametersGcmsGet['offset'] = offset

    def __setMaxFeatures(self, maxFeatures) -> None:
        """
        Complète le dictionnaire des paramètres en vue d'une requête GET par l'item 'maxFeatures'.

        :param maxFeatures: nombre d'objets maximum que retourne une réponse du serveur
        :type maxFeatures: int
        """
        self.parametersGcmsGet['maxFeatures'] = maxFeatures
