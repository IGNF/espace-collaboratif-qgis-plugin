import json

import qgis.core
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from qgis.PyQt.QtWidgets import QMessageBox
from .SQLiteManager import SQLiteManager
from .WfsGet import WfsGet
from .XMLResponse import XMLResponse
from .Wkt import Wkt
from .BBox import BBox
from .HttpRequest import HttpRequest
from . import Constantes as cst


# Classe implémentant une requête HTTP POST
class WfsPost(object):

    def __init__(self, context, layer, filterName):
        self.__context = context
        self.__layer = layer
        # self.__url = context.urlHostEspaceCo + '/gcms/api/wfstransactions'
        self.__identification = context.auth
        self.__proxy = context.proxy
        self.__endReporting = ''
        self.__transactionReporting = ''
        ''' Il faut recharger certains paramètres de la couche quand l'utilisateur a fermé QGIS
        que l'on peut stocker dans une table sqlite'''
        database_id = self.__initParametersLayer()
        if database_id is None:
            raise Exception("WfsPost:__init__, pour la couche {}, l'identifiant de la table n'est pas trouvé.".format(
                layer.name()))
        self.__url = "{0}/gcms/api/databases/{1}/transactions".format(context.urlHostEspaceCo, database_id)
        self.__bbox = BBox(context)
        self.__filterName = filterName
        self.__isTableStandard = True
        self.__datasForPost = {}

    def __initParametersLayer(self):
        # r[0] : id
        # r[1] : layer
        # r[2] : idName
        # r[3] : standard
        # r[4] : database
        # r[5] : databaseid
        # r[6] : srid
        # r[7] : geometryName
        # r[8] : geometryDimension
        # r[9] : geometryType
        # r[10] : numrec
        # r[11] : tableid
        databaseid = None
        result = SQLiteManager.selectRowsInTableOfTables(self.__layer.name())
        if result is not None:
            for r in result:
                self.__layer.databasename = r[4]
                self.__isTableStandard = r[3]
                self.__layer.isStandard = r[3]
                self.__layer.srid = r[6]
                self.__layer.idNameForDatabase = r[2]
                self.__layer.geometryNameForDatabase = r[7]
                self.__layer.geometryDimensionForDatabase = r[8]
                self.__layer.geometryTypeForDatabase = r[9]
                self.__layer.tableid = r[11]
                databaseid = r[5]
        return databaseid

    def setHeader(self):
        return '{"data": {'

    def getGeometryWorkingArea(self):
        self.layerWorkingArea = self.__context.getLayerByName(self.__filterName)
        layerWorkingAreaCrs = self.layerWorkingArea.crs()
        destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS4326, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
        coordTransform = QgsCoordinateTransform(layerWorkingAreaCrs, destCrs, QgsProject.instance())
        featureIds = self.layerWorkingArea.selectedFeatureIds()
        geomWorkingArea = self.layerWorkingArea.getGeometry(featureIds[0])
        if destCrs != layerWorkingAreaCrs:
            geomWorkingArea.transform(coordTransform)
        return geomWorkingArea

    def setPostGeometry(self, geometry, bBDUni) -> {}:
        parameters = {'geometryName': self.__layer.geometryNameForDatabase, 'sridSource': cst.EPSGCRS4326,
                      'sridTarget': self.__layer.srid, 'geometryType': self.__layer.geometryTypeForDatabase}
        wkt = Wkt(parameters)
        # Est-ce que la géométrie de l'objet intersecte la bounding box de la zone de travail
        # bboxWorkingArea = self.bbox.getBBoxAsWkt(self.filterName)
        # if bboxWorkingArea is not None and not wkt.isBoundingBoxIntersectGeometryObject(bboxWorkingArea, geometry):
        #     return None
        # Est-ce que la géométrie de l'objet intersecte la zone de travail ?
        bboxWorkingArea = self.__bbox.getBBoxAsWkt(self.__filterName)
        if bboxWorkingArea != '' and not wkt.isBoundingBoxIntersectGeometryObject(bboxWorkingArea, geometry):
            raise Exception("Un objet au moins se situe en dehors de votre zone de travail. Veuillez le(s) "
                            "déplacer ou le(s) supprimer.")
        return wkt.toPostGeometry(geometry, self.__layer.geometryDimensionForDatabase, bBDUni)

    def setGeometries(self, changedGeometries, bBDUni):
        geometries = {}
        for featureId, geometry in changedGeometries.items():
            postGeometry = self.setPostGeometry(geometry, bBDUni)
            geometries[featureId] = postGeometry
        return geometries

    def setFieldsNameValueWithAttributes(self, feature, attributesChanged):
        fieldsNameValue = ""
        if self.__isTableStandard:
            self.setKey(self.__layer.idNameForDatabase, feature.id())
        for key, value in attributesChanged.items():
            if value is None or value == qgis.core.NULL:  # Remplacement par QGIS d'une valeur vide, on n'envoie pas
                continue
            else:
                if value == "NULL":
                    fieldsNameValue += '"{0}": null, '.format(feature.fields()[key].name())
                else:
                    fieldsNameValue += '"{0}": "{1}", '.format(feature.fields()[key].name(), value)
        #  Il faut enlever à la fin de la chaine la virgule et l'espace ', ' car c'est un update
        pos = len(fieldsNameValue)
        return fieldsNameValue[0:pos - 2]

    def setStateAndLayerName(self, state):
        return '"state": "{0}", "table": "{1}"'.format(state, self.__layer.name())

    def setKey(self, key, value) -> {}:
        return {key: value}

    def setFingerPrint(self, fingerprint) -> {}:
        return {cst.FINGERPRINT: fingerprint}

    def setFieldsNameValue(self, feature) -> {}:
        fieldsNameValue = {}
        for field in feature.fields():
            fieldName = field.name()
            if fieldName == cst.ID_SQLITE:
                continue
            fieldValue = feature.attribute(fieldName)
            if fieldValue is None or str(fieldValue) == "NULL":
                continue
            fieldsNameValue[fieldName] = fieldValue
        return fieldsNameValue

    def setClientId(self, clientFeatureId) -> {}:
        return {cst.CLIENTFEATUREID: clientFeatureId}

    def __checkResponseTransactions(self, response):
        # {"user_id":676,"user_name":"epeyrouse","groups":[375,199],"conflicts":[],"numrec":null,"id":397417,
        # "started_at":"2024-08-08 11:09:13.000000","finished_at":"2024-08-08 11:09:13.000000","status":"committed",
        # "comment":"SIG-QGIS","message":"Transaction appliqu\u00e9e avec succ\u00e8s.",
        # "actions":[{"data":{"id_ligne":75},"table":"test.ligne_bidon","id":3142916,"state":"Delete",
        # "server_feature_id":"75","client_feature_id":null}]}
        responseToDict = json.loads(response.text)
        message = {'message': responseToDict["message"], 'status': responseToDict["status"], 'fid': []}
        message['fid'].append(responseToDict["id"])
        return message

    def __gcmsPost(self, bNormalWfsPost):
        print("Post_action : {}".format(json.dumps(self.__datasForPost)))
        response = HttpRequest.makeHttpRequest(self.__url, authent=self.__identification, proxies=self.__proxy,
                                               data=json.dumps(self.__datasForPost))
        responseTransactions = self.__checkResponseTransactions(response)
        if responseTransactions['status'] == 'committed':
            # Mise à jour de la base SQLite pour les objets détruits
            # et modifiés d'une couche BDUni
            if not self.__layer.isStandard:
                SQLiteManager.setActionsInTableBDUni(self.__layer.name(), self.__datasForPost["actions"])
            # Mise à jour de la couche
            try:
                # Le numrec est égal à 0 pour une couche standard
                # à un numéro pour une couche BDUni
                numrec = self.__synchronize()
            except Exception as e:
                QMessageBox.information(self.__context.iface.mainWindow(), cst.IGNESPACECO, format(e))
                # Suppression de la couche dans la carte. Virer la table dans SQLite
                layersID = [self.__layer.id()]
                QgsProject.instance().removeMapLayers(layersID)
                if SQLiteManager.isTableExist(self.__layer.name):
                    SQLiteManager.emptyTable(self.__layer.name)
                    SQLiteManager.deleteTable(self.__layer.name)
                if SQLiteManager.isTableExist(cst.TABLEOFTABLES):
                    SQLiteManager.emptyTable(cst.TABLEOFTABLES)
                SQLiteManager.vacuumDatabase()
                return
            # Mise à jour du numrec pour la couche dans la table des tables
            SQLiteManager.updateNumrecTableOfTables(self.__layer.name(), numrec)
            SQLiteManager.vacuumDatabase()
            # Le buffer de la couche est vidée et elle est rechargée
            if bNormalWfsPost:
                self.__layer.rollBack()
            self.__layer.reload()
        return responseTransactions

    def __gcmsPostSave(self, bNormalWfsPost):
        print("Post_action : {}".format(self.__datasForPost['actions']))
        # params = dict(actions=json.dumps(self.__datasForPost), database=self.__layer.databasename)
        params = dict(actions=json.dumps(self.__datasForPost))
        response = HttpRequest.makeHttpRequest(self.__url, authent=self.__identification, proxies=self.__proxy,
                                               data=params)
        xmlResponse = XMLResponse(response.text)
        responseWfs = xmlResponse.checkResponseWfsTransactions()
        if responseWfs['status'] == 'SUCCESS':
            # Mise à jour de la base SQLite pour les objets détruits
            # et modifiés d'une couche BDUni
            if not self.__layer.isStandard:
                SQLiteManager.setActionsInTableBDUni(self.__layer.name(), self.__datasForPost["actions"])
            # Mise à jour de la couche
            try:
                # Le numrec est égal à 0 pour une couche standard
                # à un numéro pour une couche BDUni
                numrec = self.__synchronize()
            except Exception as e:
                QMessageBox.information(self.__context.iface.mainWindow(), cst.IGNESPACECO, format(e))
                # Suppression de la couche dans la carte. Virer la table dans SQLite
                layersID = [self.__layer.id()]
                QgsProject.instance().removeMapLayers(layersID)
                if SQLiteManager.isTableExist(self.__layer.name):
                    SQLiteManager.emptyTable(self.__layer.name)
                    SQLiteManager.deleteTable(self.__layer.name)
                if SQLiteManager.isTableExist(cst.TABLEOFTABLES):
                    SQLiteManager.emptyTable(cst.TABLEOFTABLES)
                SQLiteManager.vacuumDatabase()
                return
            # Mise à jour du numrec pour la couche dans la table des tables
            SQLiteManager.updateNumrecTableOfTables(self.__layer.name(), numrec)
            SQLiteManager.vacuumDatabase()
            # Le buffer de la couche est vidée et elle est rechargée
            if bNormalWfsPost:
                self.__layer.rollBack()
            self.__layer.reload()
        return responseWfs

    def __synchronize(self):
        # la colonne detruit existe pour une table BDUni donc le booleen est mis à True par défaut
        bDetruit = True
        # si c'est une autre table donc standard alors la colonne n'existe pas
        # et il faut vider la table pour éviter de créer un objet à chaque Get
        if self.__layer.isStandard:
            bDetruit = False
            SQLiteManager.emptyTable(self.__layer.name())
            SQLiteManager.vacuumDatabase()
            self.__layer.reload()

        numrec = SQLiteManager.selectNumrecTableOfTables(self.__layer.name())
        parameters = {'databasename': self.__layer.databasename, 'layerName': self.__layer.name(),
                      'geometryName': self.__layer.geometryNameForDatabase, 'sridProject': cst.EPSGCRS4326,
                      'sridLayer': self.__layer.srid, 'bbox': self.__bbox.getFromLayer(self.__filterName, False, True),
                      'detruit': bDetruit, 'isStandard': self.__layer.isStandard,
                      'is3D': self.__layer.geometryDimensionForDatabase,
                      'numrec': numrec, 'role': None,
                      'urlHostEspaceCo': self.__context.urlHostEspaceCo,
                      'authentification': self.__context.auth, 'proxy': self.__context.proxy}
        wfsGet = WfsGet(parameters)
        numrecmessage = wfsGet.gcms_get()
        if 'error' in numrecmessage[1]:
            message = "Vos modifications ont bien été prises en compte mais la couche n'a pas pu être rechargée " \
                      "dans QGIS. Il faut la ré-importer. En cas de problème, veuillez contacter le gestionnaire " \
                      "de votre groupe."
            raise Exception(message)
        return numrecmessage[0]

    def commitLayer(self, currentLayer, editBuffer, bNormalWfsPost):
        # Ecriture du rapport de fin de synchronisation
        self.__transactionReporting += "<br/>Couche {0}\n".format(currentLayer)

        # Initialisation du corps de la requête
        self.__datasForPost = {
            'comment': cst.CLIENT_INPUT_DEVICE,
            'actions': []
        }

        # Récupération des modifications opérées sur les couches
        addedFeatures = editBuffer.addedFeatures().values()
        changedGeometries = editBuffer.changedGeometries()
        changedAttributeValues = editBuffer.changedAttributeValues()
        deletedFeaturesId = editBuffer.deletedFeatureIds()

        # Si pas de mises à jour, on sort avec un message de fin
        if len(addedFeatures) == 0 and \
                len(changedGeometries) == 0 and \
                len(changedAttributeValues) == 0 and \
                len(deletedFeaturesId) == 0:
            self.__transactionReporting += "<br/>Rien à synchroniser\n"
            self.__endReporting += self.__transactionReporting
            return dict(status="SUCCESS", reporting=self.__endReporting)

        # Est-ce une table BDUni
        result = SQLiteManager.isColumnExist(currentLayer, cst.FINGERPRINT)
        bBDUni = False
        if result[0] == 1:
            bBDUni = True

        # Traitement des ajouts
        if len(addedFeatures) != 0:
            self.__pushAddedFeatures(addedFeatures, bBDUni)
            self.__transactionReporting += "<br/>Objets créés : {0}\n".format(len(addedFeatures))

        # Traitement des géométries modifiées et/ou attributs modifiés
        if len(changedGeometries) != 0 and len(changedAttributeValues) != 0:
            self.__pushChangedAttributesAndGeometries(changedAttributeValues, changedGeometries, bBDUni)
        elif len(changedGeometries) != 0:
            self.__pushChangedGeometries(changedGeometries, bBDUni)
        elif len(changedAttributeValues) != 0:
            self.__pushChangedAttributeValues(changedAttributeValues)

        # Traitement des suppressions
        if len(deletedFeaturesId) != 0:
            self.__pushDeletedFeatures(deletedFeaturesId)
            self.__transactionReporting += "<br/>Objets détruits : {0}\n".format(len(deletedFeaturesId))

        # Lancement de la transaction
        nbObjModified = len(self.__datasForPost['actions']) - (len(deletedFeaturesId) + len(addedFeatures))
        if nbObjModified >= 1:
            self.__transactionReporting += "<br/>Objets modifiés : {0}\n".format(nbObjModified)
        endTransaction = self.__gcmsPost(bNormalWfsPost)
        self.__endReporting += self.__setEndReporting(endTransaction)
        return dict(status=endTransaction['status'], reporting=self.__endReporting)

    def __setEndReporting(self, endTransactionMessage):
        information = ''
        message = endTransactionMessage['message']
        status = endTransactionMessage['status']
        if status == 'FAILED':
            tmp = message.replace('transaction', '<a href="{0}" target="_blank">transaction</a>'.format(
                endTransactionMessage['urlTransaction']))
            information = '<br/><font color="red">{0} : {1}</font>'.format(status, tmp)
        elif status == 'SUCCESS':
            information = self.__transactionReporting
            tabInfo = message.split(' : ')
            information += '<br/>{0} : <a href="{1}" target="_blank">{2}</a>'.format(tabInfo[0], endTransactionMessage[
                'urlTransaction'], tabInfo[1])
        return information

    def __pushChangedAttributesAndGeometries(self, changedAttributeValues, changedGeometries, bBDUni):
        idsGeom = []
        idsAtt = []
        # Récupération des géométries par identifiant d'objet
        geometries = self.setGeometries(changedGeometries, bBDUni)
        # Traitement des actions doubles (ou simples) sur un objet (geometrie, attributs)
        for featureId, attributes in changedAttributeValues.items():
            feature = self.__layer.getFeature(featureId)
            result = SQLiteManager.selectRowsInTable(self.__layer, [featureId])
            for r in result:
                strFeature = self.setHeader()
                if not self.__isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(self.__layer.idNameForDatabase, r[0])
                else:
                    strFeature += self.setKey(self.__layer.idNameForDatabase, r[0])
                strFeature += ', '
                strFeature += self.setFieldsNameValueWithAttributes(feature, attributes)
                if featureId in geometries:
                    strFeature += ', {0}'.format(geometries[featureId])
                    idsGeom.append(featureId)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'
                idsAtt.append(featureId)
        # Suppression des modifications déjà traitées
        for idG in idsGeom:
            del geometries[idG]
        for idA in idsAtt:
            del changedAttributeValues[idA]
        # Il peut rester des modifications simples
        if len(geometries) != 0:
            self.__pushChangedGeometryTransformed(geometries)
        elif len(changedAttributeValues) != 0:
            self.__pushChangedAttributeValues(changedAttributeValues)

    def __pushChangedGeometries(self, changedGeometries, bBDUni):
        for featureId, geometry in changedGeometries.items():
            result = SQLiteManager.selectRowsInTable(self.__layer, [featureId])
            for r in result:
                strFeature = self.setHeader()
                if not self.__isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(self.__layer.idNameForDatabase, r[0])
                else:
                    strFeature += self.setKey(self.__layer.idNameForDatabase, r[0])
                postGeometry = self.setPostGeometry(geometry, bBDUni)
                strFeature += ', {0}'.format(postGeometry)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'

    def __pushChangedGeometryTransformed(self, geometryTransformed):
        for featureId, geometry in geometryTransformed.items():
            result = SQLiteManager.selectRowsInTable(self.__layer, [featureId])
            for r in result:
                strFeature = self.setHeader()
                if not self.__isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(self.__layer.idNameForDatabase, r[0])
                else:
                    strFeature += self.setKey(self.__layer.idNameForDatabase, r[0])
                strFeature += ', {0}'.format(geometry)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'

    def __pushChangedAttributeValues(self, changedAttributeValues):
        for featureId, attributes in changedAttributeValues.items():
            result = SQLiteManager.selectRowsInTable(self.__layer, [featureId])
            for r in result:
                feature = self.__layer.getFeature(featureId)
                strFeature = self.setHeader()
                if not self.__isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(self.__layer.idNameForDatabase, r[0])
                else:
                    strFeature += self.setKey(self.__layer.idNameForDatabase, r[0])
                strFeature += ', '
                strFeature += self.setFieldsNameValueWithAttributes(feature, attributes)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'

    def __pushDeletedFeatures(self, deletedFeatures):
        result = SQLiteManager.selectRowsInTable(self.__layer, deletedFeatures)
        for r in result:
            action = {
                'table': self.__layer.tableid,
                'state': 'Delete',
                'data': {}
            }
            if not self.__isTableStandard:
                # Attention, ne pas changer l'ordre d'insertion
                action['data'].update(self.setFingerPrint(r[1]))
                action['data'].update(self.setKey(self.__layer.idNameForDatabase, r[0]))
            else:
                action['data'].update(self.setKey(self.__layer.idNameForDatabase, r[0]))
            self.__datasForPost['actions'].append(action)

    def __pushAddedFeatures(self, addedFeatures, bBDUni):
        action = {
            'table': self.__layer.tableid,
            'state': 'Insert',
            'data': {}
        }
        data = {}
        for feature in addedFeatures:
            data.update(self.setFieldsNameValue(feature))
            data.update(self.setPostGeometry(feature.geometry(), bBDUni))
            action['data'].update(data)
            self.__datasForPost['actions'].append(action)
            data.clear()
