import time
import json
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

    def __initParametersGcmsGet(self, skipDetruitFilter=False) -> None:
        """
        Initialisation des paramètres pour une requête HTTP GET.

        :param skipDetruitFilter: à True, ne pas filtrer sur le champ 'detruit' (récupère détruits et
               non-détruits en une seule passe pour traitement local) 
        :type skipDetruitFilter: bool
        """
        offset = 0
        maxFeatures = 10000  # Limite maximum d'objet de l'API 
        # Passage des paramètres pour l'url
        self.__setService()
        self.__setRequest()
        self.__setOutputFormat()
        self.__setTypeName()
        if self.numrec != 0:
            self.__setNumrec()
        if self.bbox is not None:
            self.__setBBox()
        if self.bDetruit or self.numrec != 0:
            self.__setFilter(filterDelete=False, numrec=self.numrec, skipDetruit=skipDetruitFilter) # phase de test pour voir si plus rapide de récupérer détruits et non-détruits en une seule passe (skipDetruitFilter=True) ou pas (skipDetruitFilter=False)
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

    def gcmsGet(self, bExtraction=False, maxNumrec=None) -> ():
        """
        Envoie une requête GET et met à jour les tables SQLite du projet en cours.
        NB : le dernier numéro de mise à jour (numRec) d'une table est fixé à 0 pour une table différente de la BDUni.

        :param bExtraction: à True quand il s'agit d'extraire les données sur une zone de travail
        :type bExtraction: bool

        :param maxNumrec: le numéro de réconciliation max déjà récupéré par l'appelant (évite un appel réseau
                          redondant). Si None, sera récupéré automatiquement pour les couches BDUni.
        :type maxNumrec: int or None

        :return: le dernier numéro de mise à jour sur une table et un message de fin
        """
        message = ""
        # Pour la synchro BDUni, on récupère détruits et non-détruits en une seule passe
        skipDetruit = (self.isStandard in (False, 0) and not bExtraction)
        self.__initParametersGcmsGet(skipDetruitFilter=skipDetruit)
        start = time.time()
        totalRows = 0
        requestCount = 0
        if maxNumrec is not None:
            pass  # Fourni par l'appelant, pas de requête réseau supplémentaire
        elif self.isStandard:
            maxNumrec = 0
        else:
            # Try to get maxNumrec, but don't block extraction if it fails
            try:
                maxNumrec = self.getMaxNumrec()
                print("[INFO] {} | maxNumrec: {}".format(self.layerName, maxNumrec))
            except Exception as e:
                print("[WARNING] {} | getMaxNumrec failed, defaulting to 0: {}".format(self.layerName, str(e)))
                self.__logger.warning("getMaxNumrec failed: {}, continuing with 0".format(str(e)))
                maxNumrec = 0

        mode = "Extraction" if bExtraction else "Synchronisation"
        print("[{}] Layer: {} | URL: {} | Mode: {}".format(
            mode.upper(), self.layerName, self.url, mode))
        self.__logger.info("Starting {} for layer: {}".format(mode, self.layerName))

        sqliteManager = SQLiteManager()
        MAX_RETRIES = 4  # Balanced for proxy issues
        RETRY_DELAY = 2  # Base seconds between retries
        proxy_failures = 0
        using_proxy = self.proxies is not None and len(self.proxies) > 0
        PROXY_FAILURE_THRESHOLD = 2  # Disable proxy after this many failures
        
        while True:
            requestCount += 1
            
            # Retry logic with exponential backoff for transient errors
            response = None
            current_proxies = self.proxies
            
            # If proxy has failed too many times, bypass it from the start
            if proxy_failures >= PROXY_FAILURE_THRESHOLD and using_proxy:
                current_proxies = None
                self.proxies = None
                using_proxy = False
            
            for attempt in range(1, MAX_RETRIES + 1):
                if attempt > 1:
                    # Progressive delays: 2s, 4s, 6s
                    delay = RETRY_DELAY * attempt
                    print("[RETRY] {} | Request #{} attempt {}/{} (delay: {}s)".format(
                        self.layerName, requestCount, attempt, MAX_RETRIES, delay))
                    time.sleep(delay)
                
                # Try without proxy after 2 failed proxy attempts
                if attempt == 3 and proxy_failures >= 2 and using_proxy:
                    print("[PROXY] {} | Switching to direct connection (proxy failed {} times)".format(
                        self.layerName, proxy_failures))
                    current_proxies = None
                
                response = HttpRequest.nextRequest(self.url, headers=self.headers, proxies=current_proxies,
                                                   params=self.parametersGcmsGet)
                
                if response['status'] == 'ok':
                    if attempt > 1 and current_proxies is None and using_proxy:
                        # Continue without proxy for remaining requests
                        self.proxies = None
                        using_proxy = False
                    # Reset proxy failure counter on success
                    proxy_failures = 0
                    break
                else:
                    # Detailed error information
                    errorReason = response.get('reason', 'Unknown error')
                    errorUrl = response.get('url', 'N/A')
                    errorCode = response.get('code', 'N/A')
                    errorDetails = response.get('details', 'N/A')
                    is_proxy_error = response.get('is_proxy_error', False)
                    
                    if is_proxy_error:
                        proxy_failures += 1
                        # Switch to direct connection immediately if threshold reached
                        if proxy_failures >= PROXY_FAILURE_THRESHOLD and using_proxy and current_proxies is not None:
                            current_proxies = None
                            # Don't count this as a retry attempt - try again immediately with direct connection
                            continue
                    
                    if attempt == MAX_RETRIES:
                        message += "[WfsGet.py::gcms_get::nextRequest] {0} : {1}".format(response['status'], errorReason[:200])
                        print("[ERROR] {} - Request failed after {} attempts: {} (code: {})".format(
                            self.layerName, MAX_RETRIES, errorReason[:200], errorCode))
                        self.__logger.error("Request failed after {} retries: {}".format(MAX_RETRIES, message))
                        break
            
            # If all retries failed, exit the loop
            if response['status'] == 'error':
                return maxNumrec, message

            featuresReceived = len(response['features'])
            print("[PROGRESS] {} | Request #{}: {} features (offset: {})".format(
                self.layerName, requestCount, featuresReceived, self.parametersGcmsGet.get('offset', 0)))
            
            if featuresReceived == 0 and response['stop']:
                break
            
            # si c'est une table standard (non BDUni) ou une extraction,
            # on insére tous les objets dans la base SQLite en appliquant un filtre avec la zone de travail active
            if self.isStandard in (True, 1) or bExtraction is True:
                # Appliquer le filtrage géométrique fin pour les extractions
                features_to_insert = response['features']
                if bExtraction is True:
                    features_to_insert = self.__filterFeaturesWithWorkArea(response['features'])
                    print("[FILTER] {} | Geometric filter: {}/{} features kept".format(
                        self.layerName, len(features_to_insert), featuresReceived))
                
                insertedRows = sqliteManager.insertRowsInTable(self.parametersForInsertsInTable, features_to_insert)
                totalRows += insertedRows
                
                # Memory cleanup - release references
                features_to_insert = None
                response['features'] = None
                
            # sinon c'est une synchronisation (maj) de toutes les couches
            # ou un update après un post (enregistrement des couches actives)
            else:
                # Chargement des cleabs en mémoire 
                if requestCount == 1:
                    existingCleabs = set()
                    try:
                        sql = "SELECT cleabs FROM {} WHERE cleabs IS NOT NULL".format(SQLiteManager.echap(self.layerName))
                        connection = SQLiteManager.sqlite3Connect()
                        cursor = connection.cursor()
                        cursor.execute(sql)
                        existingCleabs = {row[0] for row in cursor.fetchall()}
                        cursor.close()
                        connection.close()
                    except Exception as e:
                        self.__logger.warning("Could not preload cleabs: {}".format(e))
                        existingCleabs = set()
                elif 'existingCleabs' not in locals():
                    existingCleabs = set()
                
                processedInBatch = 0
                deletedInBatch = 0
                featuresToInsert = []
                cleabsToDelete = []
                cleabsDestroyed = []
                # Traiter les features reçues en batch pour minimiser les opérations SQL
                # On reçoit détruits et non-détruits en une seule passe
                for feature in response['features']:
                    featureCleabs = feature.get('cleabs')

                    # Objet détruit côté serveur → supprimer localement si présent
                    if feature.get('detruit', False):
                        if featureCleabs in existingCleabs:
                            cleabsDestroyed.append(featureCleabs)
                            existingCleabs.discard(featureCleabs)
                        deletedInBatch += 1
                        continue
                    
                    if featureCleabs in existingCleabs:
                        # modification d'un objet - marquer pour suppression puis réinsertion
                        cleabsToDelete.append(featureCleabs)
                        featuresToInsert.append(feature)
                    else:
                        # création d'un nouvel objet
                        featuresToInsert.append(feature)
                        existingCleabs.add(featureCleabs)  # Ajouter au cache
                    
                    processedInBatch += 1
                
                # Suppression en batch des objets détruits
                if cleabsDestroyed:
                    SQLiteManager.deleteRowsInTableBDUni(self.layerName, cleabsDestroyed)

                # Suppression en batch des cleabs à mettre à jour
                if cleabsToDelete:
                    SQLiteManager.deleteRowsInTableBDUni(self.layerName, cleabsToDelete)
                
                # Insertion en batch de toutes les features
                if featuresToInsert:
                    insertedRows = sqliteManager.insertRowsInTable(self.parametersForInsertsInTable, featuresToInsert)
                    totalRows += insertedRows
                
                print("[SYNC] {} | BDUni batch: {} updated, {} new, {} destroyed, total: {}".format(
                    self.layerName, len(cleabsToDelete), processedInBatch - len(cleabsToDelete),
                    deletedInBatch, totalRows))
                
               
                response['features'] = None
                
            self.__setOffset(response['offset'])
            if response['stop']:
                break
            else:
                # Small delay between requests to avoid overwhelming the server
                if requestCount % 10 == 0:
                    time.sleep(1)
        # Note: les objets détruits sont maintenant traités dans la boucle principale
        # (pas de requête HTTP supplémentaire pour le cleanup)
        
  
        
        end = time.time()
        timeResult = end - start
        
        print("[DONE] {} | {} features | {} requests | {:.1f}s".format(
            self.layerName, totalRows, requestCount, timeResult))
        self.__logger.info("{}: {} features in {:.1f}s ({} requests)".format(
            self.layerName, totalRows, timeResult, requestCount))
        
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
        return PluginHelper.filterWithWorkArea(self.context, features, geometryKey=self.geometryName,
                                               targetCrs=target_crs)

    def getMaxNumrec(self) -> int:
        """
        Requête pour récupérer le dernier numéro de réconciliation (NumRec) d'une table BDUni.
        Essaie d'abord au niveau de la base (table reconciliations, bien indexée),
        puis se rabat sur l'endpoint par table (peut être lent si mal indexé).

        :return: le numéro de la mise à jour.
        """
        # 1) Essai via l'endpoint database (table reconciliations, rapide), à termes on ne requetera plus que de cette façon
        try:
            numrec = self.__getMaxNumrecFromDatabase()
            return numrec
        except Exception as e:
            self.__logger.warning("getMaxNumrec database-level failed, falling back to table-level: {}".format(str(e)))

        # 2) Fallback : endpoint par table (peut être lent sur vues métier)
        return self.__getMaxNumrecFromTable()

    def __getMaxNumrecFromDatabase(self) -> int:
        """
        Récupère le max-numrec au niveau de la base de données (table reconciliations).
        Plus rapide car cette table est bien indexée.

        :return: le numéro de la mise à jour.
        """
        url = "{0}/gcms/api/databases/{1}/max-numrec".format(self.urlHostEspaceCo, self.databaseid)
        response = HttpRequest.makeHttpRequest(url, proxies=self.proxies, headers=self.headers,
                                               launchBy='getMaxNumrecFromDatabase : {}'.format(self.layerName))
        if response.status_code in (200, 201):
            return response.json()
        else:
            raise Exception("code: {} raison: {}".format(response.status_code, response.reason))

    def __getMaxNumrecFromTable(self) -> int:
        """
        Récupère le max-numrec au niveau d'une table spécifique.
        Peut être lent sur les vues métier si le numrec n'est pas indexé.

        :return: le numéro de la mise à jour.
        """
        url = "{0}/gcms/api/databases/{1}/tables/{2}/max-numrec".format(self.urlHostEspaceCo, self.databaseid,
                                                                        self.tableid)
        response = HttpRequest.makeHttpRequest(url, proxies=self.proxies, headers=self.headers,
                                               launchBy='getMaxNumrecFromTable : {}'.format(self.layerName))
        if response.status_code in (200, 201):
            return response.json()
        else:
            message = "code : {} raison : {} response_text: {}".format(response.status_code, response.reason, response.text)
            print("[ERROR] getMaxNumrec failed: {}".format(message))
            self.__logger.error("getMaxNumrec failed: {}".format(message))
            raise Exception("WfsGet.getMaxNumrec -> {}".format(message))

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
        self.parametersGcmsGet['gcms_numrec'] = self.numrec

    def __setFilter(self, filterDelete, numrec, skipDetruit=False) -> None:
        """
        Complète le dictionnaire des paramètres en vue d'une requête GET par l'item 'filter'.
        Le filtre doit être du genre :
        filter={"$and":[{"class_adm":"Autoroute","longueur":"$gte":10}]}

        :param filterDelete: à True, permet de récupérer les objets détruits dans une table
        :type filterDelete: bool

        :param numrec: le dernier numéro de réconciliation de la table, il sert au filtrage des objets
                        à 0 pour une couche standard
        :type numrec: int

        :param skipDetruit: à True, ne pas inclure le filtre 'detruit' (on récupère tout d'un coup)
        :type skipDetruit: bool
        """
        filters = {}
        # 1) Filtre 'detruit' si applicable (sauf si skipDetruit)
        # bDetruit indique si la couche est standard ou BDUni
        if self.bDetruit and not skipDetruit:
            filters['detruit'] = filterDelete

        # 2) Filtre 'numrec' si applicable
        if numrec != 0:
            filters['gcms_numrec'] = {"$gte": numrec}
            # clauses.append({"numrec": {"$gte": numrec}})

        # 3) Construction du JSON final selon le nombre de filtres
        if len(filters) == 1:
            # Un seul filtre → on envoie l'objet seul
            loadFilters = filters
        else:
            # Deux filtres (ou plus) → on met tout dans un $and
            # On crée une liste de dictionnaires individuels pour chaque condition
            conditions = [{key: value} for key, value in filters.items()]
            loadFilters = {"$and": conditions}

        self.parametersGcmsGet["filter"] = json.dumps(loadFilters)

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

