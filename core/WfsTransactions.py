from PyQt5.QtWidgets import QMessageBox

from .RipartServiceRequest import RipartServiceRequest
from .SQLiteManager import SQLiteManager
from .XMLResponse import XMLResponse


class WfsTransactions(object):
    context = None
    layer = None
    url = None
    identification = None
    proxy = None
    actions = None

    def __init__(self, context):
        self.context = context
        self.layer = self.context.iface.activeLayer()
        self.url = self.context.client.getUrl() + '/gcms/wfstransactions'
        self.identification = self.context.client.getAuth()
        self.proxy = self.context.client.getProxies()
        self.actions = []

    def formatItemActions(self):
        res = '['
        for action in self.actions:
            res += action
            res += ','
        pos = len(res)
        # Remplacement de la virgule de fin par un crochet fermant
        strActions = res[0:pos-1]
        strActions += ']'
        return strActions

    def getHeader(self):
        return '{"feature": {'

    def getGeometry(self, geometry):
        wktGeometry = geometry.asWkt()
        return '"geometrie": "{0}"'.format(wktGeometry)

    def getGeometries(self, changedGeometries):
        geometries = {}
        for featureId, geometry in changedGeometries.items():
            geometries[featureId] = self.getGeometry(geometry)
        return geometries

    def getCleabs(self, cleabs):
        return '"cleabs": "{0}"'.format(cleabs)

    def getFingerPrint(self, fingerprint):
        return '"gcms_fingerprint": "{0}", '.format(fingerprint)

    def getFieldsNameValue(self, feature):
        fieldsNameValue = ""
        for field in feature.fields():
            fieldName = field.name()
            fieldValue = feature.attribute(field.name())
            if fieldValue is None:
                fieldValue = ""
            fieldsNameValue += '"{0}": "{1}", '.format(fieldName, fieldValue)
        return fieldsNameValue

    def getStateAndLayerName(self, state):
        return '"state": "{0}", "typeName": "{1}"'.format(state, self.layer.name())

    def gcms_transactions(self, strActions, databasename):
        params = dict(actions=strActions, database=databasename)
        print(params)
        response = RipartServiceRequest.makeHttpRequest(self.url, authent=self.identification, proxies=self.proxy,
                                                        data=params)
        print(response)
        xmlResponse = XMLResponse(response)
        errMessage = xmlResponse.checkResponseWfsTransactions()
        if errMessage['status'] == 'SUCCESS':
            #self.logger.info(errMessage['message'])
            self.showMessage('Transaction réussie : {}'.format(errMessage['message']))
        else:
            #self.logger.error(errMessage['message'])
            self.showMessage('Transaction interrompue : {}'.format(errMessage['message']))
            raise Exception(errMessage['message'])

    def commitLayer(self):
        self.actions.clear()

        editBuffer = self.layer.editBuffer()
        if editBuffer:
            # ajout
            addedFeatures = editBuffer.addedFeatures().values()
            if len(addedFeatures) != 0:
                self.pushAddedFeatures(addedFeatures)

            # géométrie modifiée
            changedGeometries = editBuffer.changedGeometries()
            # attributs modifiés
            changedAttributeValues = editBuffer.changedAttributeValues()
            if len(changedGeometries) != 0 and len(changedAttributeValues) != 0:
                self.pushChangedAttributesAndGeometries(changedAttributeValues, changedGeometries)
            elif len(changedGeometries) != 0:
                self.pushChangedGeometries(changedGeometries)
            elif len(changedAttributeValues) != 0:
                self.pushChangedAttributeValues(changedAttributeValues)

            deletedFeaturesId = editBuffer.deletedFeatureIds()
            if len(deletedFeaturesId) != 0:
                self.pushDeletedFeatures(deletedFeaturesId)

            # Lancement de la transaction
            strActions = self.formatItemActions()
            print(strActions)
            databaseName = 'bduni_interne_qualif_fxx'
            self.gcms_transactions(strActions, databaseName)

    def pushAddedFeatures(self, addedFeatures):
        for feature in addedFeatures:
            strFeature = self.getHeader()
            strFeature += self.getFieldsNameValue(feature)
            strFeature += self.getGeometry(feature.geometry())
            strFeature += '},'
            strFeature += self.getStateAndLayerName('Insert', self.layer.name())
            strFeature += '}'
            self.actions.append(strFeature)

    def pushChangedAttributesAndGeometries(self, changedAttributeValues, changedGeometries):
        # Récupération des géométries par identifiant d'objet
        geometries = self.getGeometries(changedGeometries)
        # Récupération des attributs et ajout de la géométrie
        for featureId, attributes in changedAttributeValues.items():
            feature = self.layer.getFeature(featureId)
            strFeature = self.getHeader()
            strFeature += self.getFieldsNameValue(feature)
            strFeature += self.getFingerPrint(feature.attribute('gcms_fingerprint'))
            strFeature += self.getCleabs(feature.attribute('cleabs'))
            strFeature += geometries[featureId]
            strFeature += '},'
            strFeature += self.getStateAndLayerName('Update')
            strFeature += '}'
            self.actions.append(strFeature)

    def pushChangedGeometries(self, changedGeometries):
        for featureId, geometry in changedGeometries.items():
            feature = self.layer.getFeature(featureId)
            strFeature = self.getHeader()
            strFeature += self.getFingerPrint(feature.attribute('gcms_fingerprint'))
            strFeature += self.getCleabs(feature.attribute('cleabs'))
            strFeature += self.getGeometry(geometry)
            strFeature += '},'
            strFeature += self.getStateAndLayerName('Update')
            strFeature += '}'
            self.actions.append(strFeature)

    def pushChangedAttributeValues(self, changedAttributeValues):
        for featureId, attributes in changedAttributeValues.items():
            feature = self.layer.getFeature(featureId)
            strFeature = self.getHeader()
            strFeature += self.getFieldsNameValue(feature)
            strFeature += self.getFingerPrint(feature.attribute('gcms_fingerprint'))
            strFeature += self.getCleabs(feature.attribute('cleabs'))
            strFeature += '},'
            strFeature += self.getStateAndLayerName('Update')
            strFeature += '}'
            self.actions.append(strFeature)

    def pushDeletedFeatures(self, deletedFeatures):
        result = SQLiteManager.selectRowsInTable(self.layer.name(), deletedFeatures)
        for r in result:
            strFeature = self.getHeader()
            strFeature += self.getFingerPrint(r[1])
            strFeature += self.getCleabs(r[0])
            strFeature += '},'
            strFeature += self.getStateAndLayerName('Delete')
            strFeature += '}'
            self.actions.append(strFeature)

    def showMessage(self, message):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("IGN Espace Collaboratif")
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(message)
        ret = msgBox.exec_()
