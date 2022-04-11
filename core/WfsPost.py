from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsMapLayerType

from .RipartServiceRequest import RipartServiceRequest
from .SQLiteManager import SQLiteManager
from .XMLResponse import XMLResponse

from . import ConstanteRipart as cst
from .Wkt import Wkt


class WfsPost(object):
    context = None
    layer = None
    url = None
    identification = None
    proxy = None
    actions = None
    isTableStandard = True

    def __init__(self, context, layer):
        self.context = context
        self.layer = layer
        self.url = self.context.client.getUrl() + '/gcms/wfstransactions'
        self.identification = self.context.client.getAuth()
        self.proxy = self.context.client.getProxies()
        self.actions = []
        '''
        il faut recharger certains paramètres de la couche quand l'utilisateur a fermé QGIS
        que l'on peut stocker dans une table sqlite
        '''
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

    def formatItemActions(self):
        res = '['
        for action in self.actions:
            res += action
            res += ','
        pos = len(res)
        # Remplacement de la virgule de fin par un crochet fermant
        strActions = res[0:pos - 1]
        strActions += ']'
        return strActions

    def setHeader(self):
        return '{"feature": {'

    def setGeometry(self, geometry):
        parameters = {'geometryName': self.layer.geometryNameForDatabase, 'sridSource': cst.EPSGCRS,
                      'sridTarget': self.layer.srid}
        wkt = Wkt(parameters)
        return wkt.toPostGeometry(geometry)

    def setGeometries(self, changedGeometries):
        geometries = {}
        for featureId, geometry in changedGeometries.items():
            geometries[featureId] = self.setGeometry(geometry)
        return geometries

    def setKey(self, key, idName):
        return '"{0}": "{1}"'.format(idName, key)

    def setFingerPrint(self, fingerprint):
        return '"{0}": "{1}", '.format(cst.FINGERPRINT, fingerprint)

    def setIsFingerPrint(self, addedFeatures):
        for feature in addedFeatures:
            if self.isTableStandard:
                feature.setAttribute(cst.IS_FINGERPRINT, 0)
            else:
                feature.setAttribute(cst.IS_FINGERPRINT, 1)

    def setFieldsNameValueWithAttributes(self, feature, attributesChanged):
        fieldsNameValue = ""
        if not self.isTableStandard:
            for field in feature.fields():
                fieldName = field.name()
                if fieldName == 'cleabs' or fieldName == cst.FINGERPRINT:
                    fieldsNameValue += '"{0}": "{1}", '.format(fieldName, feature.attribute(fieldName))
        else:
            self.setKey(feature.id(), self.layer.idNameForDatabase)
        for key, value in attributesChanged.items():
            fieldsNameValue += '"{0}": "{1}", '.format(feature.fields()[key].name(), value)
        # il faut enlever à la fin de la chaine la virgule et l'espace ', ' car c'est un update
        pos = len(fieldsNameValue)
        return fieldsNameValue[0:pos - 2]

    def setFieldsNameValue(self, feature):
        fieldsNameValue = ""
        for field in feature.fields():
            fieldName = field.name()
            if fieldName == cst.ID_SQLITE or fieldName == cst.IS_FINGERPRINT:
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

    def gcms_post(self, strActions):
        params = dict(actions=strActions, database=self.layer.databasename)
        response = RipartServiceRequest.makeHttpRequest(self.url, authent=self.identification, proxies=self.proxy,
                                                        data=params)
        xmlResponse = XMLResponse(response)
        message = xmlResponse.checkResponseWfsTransactions()
        if message['status'] == 'SUCCESS':
            res = self.layer.commitChanges()
            if res:
                self.layer.startEditing()
            self.layer.reload()
        return message['message']

    def commitLayer(self, editBuffer):
        self.actions.clear()

        addedFeatures = editBuffer.addedFeatures().values()
        changedGeometries = editBuffer.changedGeometries()
        changedAttributeValues = editBuffer.changedAttributeValues()
        deletedFeaturesId = editBuffer.deletedFeatureIds()
        if len(addedFeatures) == 0 and \
                len(changedGeometries) == 0 and \
                len(changedAttributeValues) == 0 and \
                len(deletedFeaturesId):
            return "Rien à synchroniser"

        # ajout
        if len(addedFeatures) != 0:
            self.pushAddedFeatures(addedFeatures)
            self.setIsFingerPrint(addedFeatures)

        # géométrie modifiée et/ou attributs modifiés
        if len(changedGeometries) != 0 and len(changedAttributeValues) != 0:
            self.pushChangedAttributesAndGeometries(changedAttributeValues, changedGeometries)
        elif len(changedGeometries) != 0:
            self.pushChangedGeometries(changedGeometries)
        elif len(changedAttributeValues) != 0:
            self.pushChangedAttributeValues(changedAttributeValues)

        # suppression
        if len(deletedFeaturesId) != 0:
            self.pushDeletedFeatures(deletedFeaturesId)

        # Lancement de la transaction
        strActions = self.formatItemActions()
        print(strActions)
        information = "{0} []".format(self.gcms_post(strActions))
        return information

    def pushAddedFeatures(self, addedFeatures):
        for feature in addedFeatures:
            strFeature = self.setHeader()
            strFeature += self.setFieldsNameValue(feature)
            strFeature += self.setGeometry(feature.geometry())
            strFeature += self.setClientId(feature.attribute(cst.ID_SQLITE))
            strFeature += '},'
            strFeature += self.setStateAndLayerName('Insert')
            strFeature += '}'
            self.actions.append(strFeature)

    def pushChangedAttributesAndGeometries(self, changedAttributeValues, changedGeometries):
        idsGeom = []
        idsAtt = []
        # Récupération des géométries par identifiant d'objet
        geometries = self.setGeometries(changedGeometries)
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

    def pushChangedGeometries(self, changedGeometries):
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
                strFeature += ', {0}'.format(self.setGeometry(geometry))
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

    def getDataFromTransaction(self, idTransaction):
        # https://espacecollaboratif.ign.fr/gcms/database/test/transaction/281922.json
        url = "{0}/gcms/database/{1}/transaction/{2}.json".format(self.context.client.getUrl(),
                                                                  self.layer.idNameForDatabase,
                                                                  idTransaction)
        data = RipartServiceRequest.makeHttpRequest(url, authent=self.identification, proxies=self.proxy)
        return XMLResponse(data)

    def showMessage(self, message):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("IGN Espace Collaboratif")
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(message)
        msgBox.exec_()
