import json

import qgis.core

from .RipartServiceRequest import RipartServiceRequest
from .SQLiteManager import SQLiteManager
from .WfsGet import WfsGet
from .XMLResponse import XMLResponse
from . import ConstanteRipart as cst
from .Wkt import Wkt
from .BBox import BBox
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from qgis.PyQt.QtWidgets import QMessageBox


class WfsPost(object):
    context = None
    layer = None
    url = None
    identification = None
    proxy = None
    actions = None
    isTableStandard = True
    endReport = None
    transactionReport = None
    bbox = None
    filterName = None

    def __init__(self, context, layer, filterName):
        self.context = context
        self.layer = layer
        self.url = self.context.client.getUrl() + '/gcms/wfstransactions'
        self.identification = self.context.client.getAuth()
        self.proxy = self.context.client.getProxies()
        self.actions = []
        self.endReport = ''
        self.transactionReport = ''
        ''' Il faut recharger certains paramètres de la couche quand l'utilisateur a fermé QGIS
        que l'on peut stocker dans une table sqlite'''
        self.initParametersLayer()
        self.bbox = BBox(self.context)
        self.filterName = filterName
        self.libelle_transaction = []

    def initParametersLayer(self):
        result = SQLiteManager.selectRowsInTableOfTables(self.layer.name())
        if result is not None:
            for r in result:
                self.layer.databasename = r[4]
                self.isTableStandard = r[3]
                self.layer.isStandard = r[3]
                self.layer.srid = r[5]
                self.layer.idNameForDatabase = r[2]
                self.layer.geometryNameForDatabase = r[6]
                self.layer.geometryDimensionForDatabase = r[7]
                self.layer.geometryTypeForDatabase = r[8]

    def formatItemActions(self) -> list:
        # Evolution #20450, les transactions n'acceptent que 40 actions à chaque fois
        actionsPackage = []
        nb = 0
        nbTotal = 0
        res = ''
        for action in self.actions:
            if nb == 0:
                res = '['
            res += action
            res += ','
            nb += 1
            nbTotal += 1
            if nbTotal == len(self.actions):
                pos = len(res)
                # Remplacement de la virgule de fin par un crochet fermant
                strActions = res[0:pos - 1]
                strActions += ']'
                actionsPackage.append((nb, strActions))
            elif nb == 39:
                pos = len(res)
                # Remplacement de la virgule de fin par un crochet fermant
                strActions = res[0:pos - 1]
                strActions += ']'
                actionsPackage.append((40, strActions))
                nb = 0
                res = ''
        return actionsPackage

    def setHeader(self):
        return '{"feature": {'

    def getGeometryWorkingArea(self):
        self.layerWorkingArea = self.context.getLayerByName(self.filterName)
        layerWorkingAreaCrs = self.layerWorkingArea.crs()
        destCrs = QgsCoordinateReferenceSystem(cst.EPSGCRS, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId)
        coordTransform = QgsCoordinateTransform(layerWorkingAreaCrs, destCrs, QgsProject.instance())
        featureIds = self.layerWorkingArea.selectedFeatureIds()
        geomWorkingArea = self.layerWorkingArea.getGeometry(featureIds[0])
        if destCrs != layerWorkingAreaCrs:
            geomWorkingArea.transform(coordTransform)
        return geomWorkingArea

    def setGeometry(self, geometry, bBDUni):
        parameters = {'geometryName': self.layer.geometryNameForDatabase, 'sridSource': cst.EPSGCRS,
                      'sridTarget': self.layer.srid, 'geometryType': self.layer.geometryTypeForDatabase}
        wkt = Wkt(parameters)
        # Est-ce que la géométrie de l'objet intersecte la bounding box de la zone de travail
        # bboxWorkingArea = self.bbox.getBBoxAsWkt(self.filterName)
        # if bboxWorkingArea is not None and not wkt.isBoundingBoxIntersectGeometryObject(bboxWorkingArea, geometry):
        #     return None
        # Est-ce que la géométrie de l'objet intersecte la zone de travail ?
        bboxWorkingArea = self.bbox.getBBoxAsWkt(self.filterName)
        if bboxWorkingArea is not None and not wkt.isBoundingBoxIntersectGeometryObject(bboxWorkingArea, geometry):
            raise Exception("Un objet au moins se situe en dehors de votre zone de travail. Veuillez le(s) "
                            "déplacer ou le(s) supprimer.")
        return wkt.toPostGeometry(geometry, self.layer.geometryDimensionForDatabase, bBDUni)

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
        if self.isTableStandard:
            self.setKey(feature.id(), self.layer.idNameForDatabase)
        for key, value in attributesChanged.items():
            # if value == "NULL" or value is None or value == qgis.core.NULL: #Remplacement par QGIS d'une valeur vide, on n'envoie pas
            #     fieldsNameValue += '"{0}": null, '.format(feature.fields()[key].name())
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
        return '"state": "{0}", "typeName": "{1}"'.format(state, self.layer.name())

    def setClientId(self, clientFeatureId):
        return ', "{0}": "{1}"'.format(cst.CLIENTFEATUREID, clientFeatureId)

    def gcms_post(self, strActions, bNormalWfsPost):
        print("Post_action : {}".format(strActions))
        params = dict(actions=strActions, database=self.layer.databasename)
        response = RipartServiceRequest.makeHttpRequest(self.url, authent=self.identification, proxies=self.proxy,
                                                        data=params)
        xmlResponse = XMLResponse(response)
        responseWfs = xmlResponse.checkResponseWfsTransactions()
        if responseWfs['status'] == 'SUCCESS':
            # Mise à jour de la base SQLite pour les objets détruits et modifiés
            # d'une couche BDUni
            if not self.layer.isStandard:
                SQLiteManager.setActionsInTableBDUni(self.layer.name(), self.actions)
            # Mise à jour de la couche
            try:
                self.synchronize()
            except Exception as e:
                QMessageBox.information(self.context.iface.mainWindow(), cst.IGNESPACECO, format(e))
                # Suppression de la couche dans la carte. Virer la table dans SQLite
                layersID = [self.layer.id()]
                QgsProject.instance().removeMapLayers(layersID)
                if SQLiteManager.isTableExist(self.layer.nom):
                    SQLiteManager.emptyTable(self.layer.nom)
                    SQLiteManager.deleteTable(self.layer.nom)
                if SQLiteManager.isTableExist(cst.TABLEOFTABLES):
                    SQLiteManager.emptyTable(cst.TABLEOFTABLES)
                SQLiteManager.vacuumDatabase()
                return
            numrec = self.getNumrecFromTransaction(responseWfs['urlTransaction'])
            # Cas des couches standard, il faut mettre numrec à 0
            if numrec is None:
                numrec = 0
            SQLiteManager.updateNumrecTableOfTables(self.layer.name(), numrec)
            SQLiteManager.vacuumDatabase()
            # Le buffer de la couche est vidée et elle est rechargée
            if bNormalWfsPost:
                self.layer.rollBack()
            self.layer.reload()
        if responseWfs['status'] == 'FAILED':
            responseWfs['message'] = "<br/>Attention, les modifications sur la couche {0} ont été refusées par le " \
                                     "serveur, les données sont corrompues. Veuillez télécharger de nouveau cette " \
                                      "couche pour pouvoir continuer à la modifier. En cas de besoin, vous pouvez " \
                                      "contacter le gestionnaire de votre groupe.<br><br>{1}".format(self.layer.name(),
                                                                                                 responseWfs['message'])
        return responseWfs

    def getJsonTransaction(self, urlTransaction):
        url = "{0}.json".format(urlTransaction)
        response = RipartServiceRequest.makeHttpRequest(url, authent=self.identification, proxies=self.proxy)
        return json.loads(response)

    def getNumrecFromTransaction(self, urlTransaction):
        # https://espacecollaboratif.ign.fr/gcms/database/test/transaction/281922.json
        # https://espacecollaboratif.ign.fr/gcms/database/test/transaction/281927/action/1130961.json
        url = "{0}.json".format(urlTransaction)
        response = RipartServiceRequest.makeHttpRequest(url, authent=self.identification, proxies=self.proxy)
        data = json.loads(response)
        return data['numrec']

    def synchronize(self):
        # la colonne detruit existe pour une table BDUni donc le booleen est mis à True par défaut
        bDetruit = True
        # si c'est une autre table donc standard alors la colonne n'existe pas
        # et il faut vider la table pour éviter de créer un objet à chaque Get
        if self.layer.isStandard:
            bDetruit = False
            SQLiteManager.emptyTable(self.layer.name())
            SQLiteManager.vacuumDatabase()
            self.layer.reload()

        numrec = SQLiteManager.selectNumrecTableOfTables(self.layer.name())
        parameters = {'databasename': self.layer.databasename, 'layerName': self.layer.name(),
                      'geometryName': self.layer.geometryNameForDatabase, 'sridProject': cst.EPSGCRS,
                      'sridLayer': self.layer.srid, 'bbox': self.bbox.getFromLayer(self.filterName, False),
                      'detruit': bDetruit, 'isStandard': self.layer.isStandard,
                      'is3D': self.layer.geometryDimensionForDatabase,
                      'numrec': numrec}
        wfsGet = WfsGet(self.context, parameters)
        numrecmessage = wfsGet.gcms_get()
        if 'error' in numrecmessage[1]:
            message = "Vos modifications ont bien été prises en compte mais la couche n'a pas pu être rechargée " \
                      "dans QGIS. Il faut la ré-importer. En cas de problème, veuillez contacter le gestionnaire " \
                      "de votre groupe."
            raise Exception(message)

    def commitLayer(self, currentLayer, editBuffer, bNormalWfsPost):
        totalOftransactions = []
        self.transactionReport += "<br/>Couche {0}".format(currentLayer)
        self.actions.clear()
        addedFeatures = editBuffer.addedFeatures().values()
        changedGeometries = editBuffer.changedGeometries()
        changedAttributeValues = editBuffer.changedAttributeValues()
        deletedFeaturesId = editBuffer.deletedFeatureIds()
        if len(addedFeatures) == 0 and \
                len(changedGeometries) == 0 and \
                len(changedAttributeValues) == 0 and \
                len(deletedFeaturesId) == 0:
            self.transactionReport += "<br/>Rien à synchroniser"
            self.endReport += self.transactionReport
            return totalOftransactions.append(dict(status="SUCCESS", report=self.endReport))

        # Est-ce une table BDUni
        result = SQLiteManager.isColumnExist(currentLayer, cst.FINGERPRINT)
        bBDUni = False
        if result[0] == 1:
            bBDUni = True

        # ajout
        if len(addedFeatures) != 0:
            self.pushAddedFeatures(addedFeatures, bBDUni)
            self.transactionReport += "<br/>Objets créés : {0}".format(len(addedFeatures))

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
            self.transactionReport += "<br/>Objets détruits : {0}".format(len(deletedFeaturesId))

        # Lancement de la transaction
        nbObjModified = len(self.actions) - (len(deletedFeaturesId) + len(addedFeatures))
        if nbObjModified >= 1:
            self.transactionReport += "<br/>Objets modifiés : {0}".format(nbObjModified)
        actionsPacket = self.formatItemActions()
        endReport = self.transactionReport
        for strActions in actionsPacket:
            endTransaction = self.gcms_post(strActions[1], bNormalWfsPost)
            endReport += self.setEndReport(strActions[0], endTransaction)
            totalOftransactions.append(dict(status=endTransaction['status'], report=endReport))
            endReport = ''
        return totalOftransactions

    def setEndReport(self, nbObjects, endTransactionMessage):
        information = ''
        message = endTransactionMessage['message']
        status = endTransactionMessage['status']
        if status == 'FAILED':
            tmp = message.replace('transaction', '<a href="{0}" target="_blank">transaction</a>'.format(
                endTransactionMessage['urlTransaction']))
            information = '<br/><font color="red">{0} : {1}</font>'.format(status, tmp)
        elif status == 'SUCCESS':
            information += "<br/>Objets impactés : {0}".format(nbObjects)
            tabInfo = message.split(' : ')
            self.libelle_transaction.append(tabInfo)
            information += '<br/>{0} : <a href="{1}" target="_blank">{2}</a><br>'.format(tabInfo[0], endTransactionMessage['urlTransaction'], tabInfo[1])
            print(information)
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
            self.actions.append(strFeature)

    def pushChangedAttributesAndGeometries(self, changedAttributeValues, changedGeometries, bBDUni):
        idsGeom = []
        idsAtt = []
        # Récupération des géométries par identifiant d'objet
        geometries = self.setGeometries(changedGeometries, bBDUni)
        # Traitement des actions doubles (ou simples) sur un objet (geometrie, attributs)
        for featureId, attributes in changedAttributeValues.items():
            feature = self.layer.getFeature(featureId)
            result = SQLiteManager.selectRowsInTable(self.layer, [featureId])
            for r in result:
                strFeature = self.setHeader()
                if not self.isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(r[0], self.layer.idNameForDatabase)
                else:
                    strFeature += self.setKey(r[0], self.layer.idNameForDatabase)
                strFeature += ', '
                strFeature += self.setFieldsNameValueWithAttributes(feature, attributes)
                if featureId in geometries:
                    strFeature += ', {0}'.format(geometries[featureId])
                    idsGeom.append(featureId)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'
                self.actions.append(strFeature)
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
            result = SQLiteManager.selectRowsInTable(self.layer, [featureId])
            for r in result:
                strFeature = self.setHeader()
                if not self.isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(r[0], self.layer.idNameForDatabase)
                else:
                    strFeature += self.setKey(r[0], self.layer.idNameForDatabase)
                postGeometry = self.setGeometry(geometry, bBDUni)
                strFeature += ', {0}'.format(postGeometry)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'
                self.actions.append(strFeature)

    def pushChangedGeometryTransformed(self, geometryTransformed):
        for featureId, geometry in geometryTransformed.items():
            result = SQLiteManager.selectRowsInTable(self.layer, [featureId])
            for r in result:
                strFeature = self.setHeader()
                if not self.isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(r[0], self.layer.idNameForDatabase)
                else:
                    strFeature += self.setKey(r[0], self.layer.idNameForDatabase)
                strFeature += ', {0}'.format(geometry)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'
                self.actions.append(strFeature)

    def pushChangedAttributeValues(self, changedAttributeValues):
        for featureId, attributes in changedAttributeValues.items():
            result = SQLiteManager.selectRowsInTable(self.layer, [featureId])
            for r in result:
                feature = self.layer.getFeature(featureId)
                strFeature = self.setHeader()
                if not self.isTableStandard:
                    # Attention, ne pas changer l'ordre d'insertion
                    strFeature += self.setFingerPrint(r[1])
                    strFeature += self.setKey(r[0], self.layer.idNameForDatabase)
                else:
                    strFeature += self.setKey(r[0], self.layer.idNameForDatabase)
                strFeature += ', '
                strFeature += self.setFieldsNameValueWithAttributes(feature, attributes)
                strFeature += '},'
                strFeature += self.setStateAndLayerName('Update')
                strFeature += '}'
                self.actions.append(strFeature)

    def pushDeletedFeatures(self, deletedFeatures):
        result = SQLiteManager.selectRowsInTable(self.layer, deletedFeatures)
        for r in result:
            strFeature = self.setHeader()
            if not self.isTableStandard:
                # Attention, ne pas changer l'ordre d'insertion
                strFeature += self.setFingerPrint(r[1])
                strFeature += self.setKey(r[0], self.layer.idNameForDatabase)
            else:
                strFeature += self.setKey(r[0], self.layer.idNameForDatabase)
            strFeature += '},'
            strFeature += self.setStateAndLayerName('Delete')
            strFeature += '}'
            self.actions.append(strFeature)
