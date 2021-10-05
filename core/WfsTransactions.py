from RipartHelper import RipartHelper
from .RipartServiceRequest import RipartServiceRequest
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

    def getStateAndLayerName(self, state, layerName):
        return '"state": "{0}", "typeName": "{1}"'.format(state, layerName)

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
            RipartHelper.showMessageBox('Transaction réussie : {}'.format(errMessage['message']))
        else:
            #self.logger.error(errMessage['message'])
            RipartHelper.showMessageBox('Transaction interrompue : {}'.format(errMessage['message']))
            raise Exception(errMessage['message'])

    def commitLayer(self):
        self.actions.clear()
        databaseName = 'bduni_interne_qualif_fxx'

        editBuffer = self.layer.editBuffer()
        if editBuffer:
            # ajout
            addedFeatures = editBuffer.addedFeatures().values()
            if len(addedFeatures) != 0:
                self.pushAddedFeatures(addedFeatures, databaseName)

            # géométrie modifiée
            changedGeometries = editBuffer.changedGeometries()
            # attributs modifiés
            changedAttributeValues = editBuffer.changedAttributeValues()
            if len(changedGeometries) != 0 and len(changedAttributeValues) != 0:
                self.pushChangedAttributesAndGeometries(self.layer, changedAttributeValues, changedGeometries, databaseName)
            elif len(changedGeometries) != 0:
                self.pushChangedGeometries(self.layer, changedGeometries, databaseName)
            elif len(changedAttributeValues) != 0:
                self.pushChangedAttributeValues(self.layer, changedAttributeValues, databaseName)

            # deletedFeaturesId = editBuffer.deletedFeatureIds()
            # if len(deletedFeaturesId) != 0:
            # self.pushDeletedFeatures(deletedFeaturesId, editBuffer, authentification, proxies)

            # Lancement de la transaction
            strActions = self.formatItemActions()
            print(strActions)
            self.gcms_transactions(strActions, databaseName)

    def pushAddedFeatures(self, addedFeatures, databaseName):
        for feature in addedFeatures:
            strFeature = self.getHeader()
            strFeature += self.getFieldsNameValue(feature)
            strFeature += self.getGeometry(feature.geometry())
            strFeature += '},'
            strFeature += self.getStateAndLayerName('Insert', self.layer.name())
            strFeature += '}'
            self.actions.append(strFeature)

    def pushChangedAttributesAndGeometries(self, layer, changedAttributeValues, changedGeometries, databaseName):
        # Récupération des géométries par identifiant d'objet
        geometries = self.getGeometries(changedGeometries)
        # Récupération des attributs et ajout de la géométrie
        for featureId, attributes in changedAttributeValues.items():
            feature = layer.getFeature(featureId)
            strFeature = self.getHeader()
            strFeature += self.getFieldsNameValue(feature)
            strFeature += self.getFingerPrint(feature.attribute('gcms_fingerprint'))
            strFeature += self.getCleabs(feature.attribute('cleabs'))
            strFeature += geometries[featureId]
            strFeature += '},'
            strFeature += self.getStateAndLayerName('Update', self.layer.name())
            strFeature += '}'
            self.actions.append(strFeature)

    def pushChangedGeometries(self, layer, changedGeometries, databaseName):
        for featureId, geometry in changedGeometries.items():
            feature = layer.getFeature(featureId)
            strFeature = self.getHeader()
            strFeature += self.getFingerPrint(feature.attribute('gcms_fingerprint'))
            strFeature += self.getCleabs(feature.attribute('cleabs'))
            strFeature += self.getGeometry(geometry)
            strFeature += '},'
            strFeature += self.getStateAndLayerName('Update', self.layer.name())
            strFeature += '}'
            self.actions.append(strFeature)

    def pushChangedAttributeValues(self, layer, changedAttributeValues, databaseName):
        for featureId, attributes in changedAttributeValues.items():
            feature = layer.getFeature(featureId)
            strFeature = self.getHeader()
            strFeature += self.getFieldsNameValue(feature)
            strFeature += self.getFingerPrint(feature.attribute('gcms_fingerprint'))
            strFeature += self.getCleabs(feature.attribute('cleabs'))
            strFeature += '},'
            strFeature += self.getStateAndLayerName('Update', self.layer.name())
            strFeature += '}'
            self.actions.append(strFeature)

    def pushDeletedFeatures(self, deletedFeatures, databaseName):
        self.actions.clear()
        for d in deletedFeatures:
            qgsFeature = self.getFeature(d)
            cleabs = qgsFeature.attribute('cleabs')
            fingerprint = qgsFeature.attribute('gcms_fingerprint')
            self.actions.append('{"feature": {"gcms_fingerprint": "{}", '.format(fingerprint) +
                           '"cleabs": "{}", '.format(cleabs) + '}'
                           '"state": "Delete",' +
                           '"typeName": "{}"'.format(self.layer.nom)) + '}'
