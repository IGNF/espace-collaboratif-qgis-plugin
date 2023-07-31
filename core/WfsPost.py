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
        self.__url = context.urlHostEspaceCo + '/gcms/api/wfstransactions'
        self.__identification = context.auth
        self.__proxy = context.proxy
        self.__actions = []
        self.__endReport = ''
        self.__transactionReport = ''
        ''' Il faut recharger certains paramètres de la couche quand l'utilisateur a fermé QGIS
        que l'on peut stocker dans une table sqlite'''
        self.initParametersLayer()
        self.__bbox = BBox(context)
        self.__filterName = filterName
        self.__isTableStandard = True

    def initParametersLayer(self):
        result = SQLiteManager.selectRowsInTableOfTables(self.__layer.name())
        if result is not None:
            for r in result:
                self.__layer.databasename = r[4]
                self.__isTableStandard = r[3]
                self.__layer.isStandard = r[3]
                self.__layer.srid = r[5]
                self.__layer.idNameForDatabase = r[2]
                self.__layer.geometryNameForDatabase = r[6]
                self.__layer.geometryDimensionForDatabase = r[7]
                self.__layer.geometryTypeForDatabase = r[8]

    def formatItemActions(self):
        res = '['
        for action in self.__actions:
            res += action
            res += ','
        pos = len(res)
        # Remplacement de la virgule de fin par un crochet fermant
        strActions = res[0:pos - 1]
        strActions += ']'
        return strActions

    def setHeader(self):
        return '{"feature": {'

    def getGeometryWorkingArea(self):
        self.layerWorkingArea = self.__context.getLayerByName(self.__filterName)
        layerWorkingAreaCrs = self.layerWorkingArea.crs()
        destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
        coordTransform = QgsCoordinateTransform(layerWorkingAreaCrs, destCrs, QgsProject.instance())
        featureIds = self.layerWorkingArea.selectedFeatureIds()
        geomWorkingArea = self.layerWorkingArea.getGeometry(featureIds[0])
        if destCrs != layerWorkingAreaCrs:
            geomWorkingArea.transform(coordTransform)
        return geomWorkingArea

    def setGeometry(self, geometry, bBDUni):
        parameters = {'geometryName': self.__layer.geometryNameForDatabase, 'sridSource': cst.EPSGCRS,
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
            postGeometry = self.setGeometry(geometry, bBDUni)
            geometries[featureId] = postGeometry
        return geometries

    def setKey(self, key, idName):
        return '"{0}": "{1}"'.format(idName, key)

    def setFingerPrint(self, fingerprint):
        return '"{0}": "{1}", '.format(cst.FINGERPRINT, fingerprint)

    def setFieldsNameValueWithAttributes(self, feature, attributesChanged):
        fieldsNameValue = ""
        if self.__isTableStandard:
            self.setKey(feature.id(), self.__layer.idNameForDatabase)
        for key, value in attributesChanged.items():
            if value is None or value == qgis.core.NULL: #Remplacement par QGIS d'une valeur vide, on n'envoie pas
                continue
            else:
                if value == "NULL":
                    fieldsNameValue += '"{0}": null, '.format(feature.fields()[key].name())
                else:
                    fieldsNameValue += '"{0}": "{1}", '.format(feature.fields()[key].name(), value)
        # il faut enlever à la fin de la chaine la virgule et l'espace ', ' car c'est un update
        pos = len(fieldsNameValue)
        return fieldsNameValue[0:pos - 2]

    def setFieldsNameValue(self, feature):
        fieldsNameValue = ""
        for field in feature.fields():
            fieldName = field.name()
            if fieldName == cst.ID_SQLITE:
                continue
            fieldValue = feature.attribute(fieldName)
            if fieldValue is None or str(fieldValue) == "NULL":
                continue
            fieldsNameValue += '"{0}": "{1}", '.format(fieldName, fieldValue)
        # il faut garder la virgule et l'espace en fin de chaine car l'action est à "insert"
        # et il y a la géométrie de l'objet à concaténer
        return fieldsNameValue

    def setStateAndLayerName(self, state):
        return '"state": "{0}", "typeName": "{1}"'.format(state, self.__layer.name())

    def setClientId(self, clientFeatureId):
        return ', "{0}": "{1}"'.format(cst.CLIENTFEATUREID, clientFeatureId)

    def gcms_post(self, strActions, bNormalWfsPost):
        print("Post_action : {}".format(strActions))
        params = dict(actions=strActions, database=self.__layer.databasename)
        response = HttpRequest.makeHttpRequest(self.__url, authent=self.__identification, proxies=self.__proxy,
                                                        data=params)
        xmlResponse = XMLResponse(response.text)
        responseWfs = xmlResponse.checkResponseWfsTransactions()
        if responseWfs['status'] == 'SUCCESS':
            # Mise à jour de la base SQLite pour les objets détruits et modifiés
            # d'une couche BDUni
            if not self.__layer.isStandard:
                SQLiteManager.setActionsInTableBDUni(self.__layer.name(), self.__actions)
            # Mise à jour de la couche
            try:
                # Le numrec est égal à 0 pour une couche standard
                # à un numéro pour une couche BDUni
                numrec = self.synchronize()
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

    def synchronize(self):
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
                      'geometryName': self.__layer.geometryNameForDatabase, 'sridProject': cst.EPSGCRS,
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
        self.__transactionReport += "<br/>Couche {0}\n".format(currentLayer)
        self.__actions.clear()
        addedFeatures = editBuffer.addedFeatures().values()
        changedGeometries = editBuffer.changedGeometries()
        changedAttributeValues = editBuffer.changedAttributeValues()
        deletedFeaturesId = editBuffer.deletedFeatureIds()
        if len(addedFeatures) == 0 and \
                len(changedGeometries) == 0 and \
                len(changedAttributeValues) == 0 and \
                len(deletedFeaturesId) == 0:
            self.__transactionReport += "<br/>Rien à synchroniser\n"
            self.__endReport += self.__transactionReport
            return dict(status="SUCCESS", report=self.__endReport)

        # Est-ce une table BDUni
        result = SQLiteManager.isColumnExist(currentLayer, cst.FINGERPRINT)
        bBDUni = False
        if result[0] == 1:
            bBDUni = True

        # ajout
        if len(addedFeatures) != 0:
            self.pushAddedFeatures(addedFeatures, bBDUni)
            self.__transactionReport += "<br/>Objets créés : {0}\n".format(len(addedFeatures))

        # géométrie modifiée et/ou attributs modifiés
        if len(changedGeometries) != 0 and len(changedAttributeValues) != 0:
            self.pushChangedAttributesAndGeometries(changedAttributeValues, changedGeometries, bBDUni)
        elif len(changedGeometries) != 0:
            self.pushChangedGeometries(changedGeometries, bBDUni)
        elif len(changedAttributeValues) != 0:
            self.pushChangedAttributeValues(changedAttributeValues)

        # suppression
        if len(deletedFeaturesId) != 0:
            self.pushDeletedFeatures(deletedFeaturesId)
            self.__transactionReport += "<br/>Objets détruits : {0}\n".format(len(deletedFeaturesId))

        # Lancement de la transaction
        nbObjModified = len(self.__actions) - (len(deletedFeaturesId) + len(addedFeatures))
        if nbObjModified >= 1:
            self.__transactionReport += "<br/>Objets modifiés : {0}\n".format(nbObjModified)
        strActions = self.formatItemActions()
        endTransaction = self.gcms_post(strActions, bNormalWfsPost)
        self.__endReport += self.setEndReport(endTransaction)
        return dict(status=endTransaction['status'], report=self.__endReport)

    def setEndReport(self, endTransactionMessage):
        information = ''
        message = endTransactionMessage['message']
        status = endTransactionMessage['status']
        if status == 'FAILED':
            tmp = message.replace('transaction', '<a href="{0}" target="_blank">transaction</a>'.format(
                endTransactionMessage['urlTransaction']))
            information = '<br/><font color="red">{0} : {1}</font>'.format(status, tmp)
        elif status == 'SUCCESS':
            information = self.__transactionReport
            tabInfo = message.split(' : ')
            information += '<br/>{0} : <a href="{1}" target="_blank">{2}</a>'.format(tabInfo[0], endTransactionMessage['urlTransaction'], tabInfo[1])
        return information

    def pushAddedFeatures(self, addedFeatures, bBDUni):
        for feature in addedFeatures:
            strFeature = self.setHeader()
            strFeature += self.setFieldsNameValue(feature)
            postGeometry = self.setGeometry(feature.geometry(), bBDUni)
            strFeature += postGeometry
            strFeature += self.setClientId(feature.attribute(cst.ID_SQLITE))
            strFeature += '},'
            strFeature += self.setStateAndLayerName('Insert')
            strFeature += '}'
            self.__actions.append(strFeature)

    def pushChangedAttributesAndGeometries(self, changedAttributeValues, changedGeometries, bBDUni):
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
                    strFeature += self.setKey(r[0], self.__layer.idNameForDatabase)
                else:
                    strFeature += self.setKey(r[0], self.__layer.idNameForDatabase)
                strFeature += ', '
                strFeature += self.setFieldsNameValueWithAttributes(feature, attributes)
                if featureId in geometries:
                    strFeature += ', {0}'.format(geometries[featureId])
                    idsGeom.append(featureId)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'
                self.__actions.append(strFeature)
                idsAtt.append(featureId)
        # Suppression des modifications déjà traitées
        for idG in idsGeom:
            del geometries[idG]
        for idA in idsAtt:
            del changedAttributeValues[idA]
        # Il peut rester des modifications simples
        if len(geometries) != 0:
            self.pushChangedGeometryTransformed(geometries)
        elif len(changedAttributeValues) != 0:
            self.pushChangedAttributeValues(changedAttributeValues)

    def pushChangedGeometries(self, changedGeometries, bBDUni):
        for featureId, geometry in changedGeometries.items():
            result = SQLiteManager.selectRowsInTable(self.__layer, [featureId])
            for r in result:
                strFeature = self.setHeader()
                if not self.__isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(r[0], self.__layer.idNameForDatabase)
                else:
                    strFeature += self.setKey(r[0], self.__layer.idNameForDatabase)
                postGeometry = self.setGeometry(geometry, bBDUni)
                strFeature += ', {0}'.format(postGeometry)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'
                self.__actions.append(strFeature)

    def pushChangedGeometryTransformed(self, geometryTransformed):
        for featureId, geometry in geometryTransformed.items():
            result = SQLiteManager.selectRowsInTable(self.__layer, [featureId])
            for r in result:
                strFeature = self.setHeader()
                if not self.__isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(r[0], self.__layer.idNameForDatabase)
                else:
                    strFeature += self.setKey(r[0], self.__layer.idNameForDatabase)
                strFeature += ', {0}'.format(geometry)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'
                self.__actions.append(strFeature)

    def pushChangedAttributeValues(self, changedAttributeValues):
        for featureId, attributes in changedAttributeValues.items():
            result = SQLiteManager.selectRowsInTable(self.__layer, [featureId])
            for r in result:
                feature = self.__layer.getFeature(featureId)
                strFeature = self.setHeader()
                if not self.__isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(r[0], self.__layer.idNameForDatabase)
                else:
                    strFeature += self.setKey(r[0], self.__layer.idNameForDatabase)
                strFeature += ', '
                strFeature += self.setFieldsNameValueWithAttributes(feature, attributes)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'
                self.__actions.append(strFeature)

    def pushDeletedFeatures(self, deletedFeatures):
        result = SQLiteManager.selectRowsInTable(self.__layer, deletedFeatures)
        for r in result:
            strFeature = self.setHeader()
            if not self.__isTableStandard:
                # Attention, ne pas changer l'ordre d'insertion
                strFeature += self.setFingerPrint(r[1])
                strFeature += self.setKey(r[0], self.__layer.idNameForDatabase)
            else:
                strFeature += self.setKey(r[0], self.__layer.idNameForDatabase)
            strFeature += '},'
            strFeature += self.setStateAndLayerName('Delete')
            strFeature += '}'
            self.__actions.append(strFeature)
