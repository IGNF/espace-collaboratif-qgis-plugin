from PyQt5.QtWidgets import QMessageBox

from .RipartServiceRequest import RipartServiceRequest
from .XMLResponse import XMLResponse

class WfsTransactions(object):
    context = None
    layer = None
    url = None
    identification = None
    proxy = None
    actions = []
    enteteActions = '{"feature": {'

    def __init__(self, context):
        self.context = context
        self.layer = self.context.iface.activeLayer()
        self.url = self.context.client.getUrl() + '/gcms/wfstransactions'
        self.identification = self.context.client.getAuth()
        self.proxy = self.context.client.getProxies()

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
            QMessageBox().information('Transaction réussie : {}'.format(errMessage['message']))
            QMessageBox.Open()
        else:
            # self.logger.error(errMessage['message'])
            QMessageBox().information('Transaction interrompue : {}'.format(errMessage['message']))
            QMessageBox.Open()
            raise Exception(errMessage['message'])

    def commitLayer(self):
        databaseName = 'bduni_interne_qualif_fxx'
        editBuffer = self.layer.editBuffer()
        if editBuffer:
            # ajout
            addedFeatures = editBuffer.addedFeatures().values()
            if len(addedFeatures) != 0:
                self.pushAddedFeatures(addedFeatures, databaseName)

            # géométrie modifiée
            changedGeometries = editBuffer.changedGeometries()
            if len(changedGeometries) != 0:
                self.pushChangedGeometries(self.layer, changedGeometries, databaseName)

            # attributs modifiés
            changedAttributeValues = editBuffer.changedAttributeValues()
            if len(changedAttributeValues) != 0:
                self.pushChangedAttributeValues(self.layer, changedAttributeValues, databaseName)

        # deletedFeaturesId = editBuffer.deletedFeatureIds()
        # if len(deletedFeaturesId) != 0:
        # self.pushDeletedFeatures(deletedFeaturesId, editBuffer, authentification, proxies)

    def pushAddedFeatures(self, addedFeatures, databasename):
        self.actions.clear()
        for feature in addedFeatures:
            strFeature = self.enteteActions
            for field in feature.fields():
                fieldName = field.name()
                fieldValue = feature.attribute(field.name())
                if fieldValue is None:
                    fieldValue = ""
                strFeature += '"{}": "{}", '.format(fieldName, fieldValue)
            wktGeometry = feature.geometry().asWkt()
            strFeature += '"geometrie": "{}"'.format(wktGeometry)
            strFeature += '},'
            strFeature += '"state": "Insert", "typeName": "{}"'.format(self.layer.name())
            strFeature += '}'
            self.actions.append(strFeature)
        strActions = self.formatItemActions()
        print(strActions)
        self.gcms_transactions(strActions, databasename)

    def pushChangedGeometries(self, layer, changedGeometries, databaseName):
        self.actions.clear()
        for featureId, geometry in changedGeometries.items():
            feature = layer.getFeature(featureId)
            cleabs = feature.attribute('cleabs')
            fingerprint = feature.attribute('gcms_fingerprint')
            strFeature = self.enteteActions
            strFeature += '"gcms_fingerprint": "{}", '.format(fingerprint)
            strFeature += '"cleabs": "{}", '.format(cleabs)
            wktGeometry = geometry().asWkt()
            strFeature += '"geometrie": "{}"'.format(wktGeometry)
            strFeature += '},'
            strFeature += '"state": "Update", "typeName": "{}"'.format(self.layer.name())
            strFeature += '}'
            self.actions.append(strFeature)
        strActions = self.formatItemActions()
        print(strActions)
        self.gcms_transactions(strActions, databaseName)

    def pushChangedAttributeValues(self, layer, changedAttributeValues, databaseName):
        for featureId, attributes in changedAttributeValues.items():
            feature = layer.getFeature(featureId)
            cleabs = feature.attribute('cleabs')
            fingerprint = feature.attribute('gcms_fingerprint')
            strFeature = self.enteteActions
            fields = feature.fields()
            for idx, value in attributes.items():
                field = fields.at(idx)
                strFeature += '"{}": "{}", '.format(field.name(), value)
            strFeature += '"gcms_fingerprint": "{}", '.format(fingerprint)
            strFeature += '"cleabs": "{}"'.format(cleabs)
            strFeature += '},'
            strFeature += '"state": "Update", "typeName": "{}"'.format(self.layer.name())
            strFeature += '}'
            self.actions.append(strFeature)
        strActions = self.formatItemActions()
        print(strActions)
        self.gcms_transactions(strActions, databaseName)

    def pushDeletedFeatures(self, deletedFeatures):
        for d in deletedFeatures:
            qgsFeature = self.getFeature(d)
            cleabs = qgsFeature.attribute('cleabs')
            fingerprint = qgsFeature.attribute('gcms_fingerprint')
            self.actions.append('{"feature": {"gcms_fingerprint": "{}", '.format(fingerprint) +
                           '"cleabs": "{}}", '.format(cleabs) +
                           '"state": "Delete",' +
                           '"typeName": "{}}"'.format(self.layer.nom))
        strActions = self.formatItemActions()
        self.gcms_transactions(strActions)

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
