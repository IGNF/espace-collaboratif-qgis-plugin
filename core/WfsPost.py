from PyQt5.QtWidgets import QMessageBox

from .RipartServiceRequest import RipartServiceRequest
from .SQLiteManager import SQLiteManager
from .XMLResponse import XMLResponse

from . import ConstanteRipart as cst


class WfsPost(object):
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

    def setHeader(self):
        return '{"feature": {'

    def setGeometry(self, geometry):
        wktGeometry = SQLiteManager.formatAndTransformGeometry(geometry.asWkt(), cst.EPSGCRS, self.layer.srid, self.layer.sqliteManager.is3D) #TO-DO
        return '"{0}": "{1}"'.format(self.layer.sqliteManager.geometryName, wktGeometry)

    def setGeometries(self, changedGeometries):
        geometries = {}
        for featureId, geometry in changedGeometries.items():
            geometries[featureId] = self.setGeometry(geometry)
        return geometries

    def setCleabs(self, cleabs):
        return '"cleabs": "{0}"'.format(cleabs)

    def setFingerPrint(self, fingerprint):
        return '"gcms_fingerprint": "{0}", '.format(fingerprint)

    def setFieldsNameValue(self, feature):
        fieldsNameValue = ""
        for field in feature.fields():
            fieldName = field.name()
            if fieldName == cst.ID_SQLITE:
                continue
            fieldValue = feature.attribute(field.name())
            if fieldValue is None or str(fieldValue) == "NULL":
                continue
                #fieldValue = ""
            fieldsNameValue += '"{0}": "{1}", '.format(fieldName, fieldValue)
        return fieldsNameValue

    def setStateAndLayerName(self, state):
        return '"state": "{0}", "typeName": "{1}"'.format(state, self.layer.name())

    def gcms_post(self, strActions):
        params = dict(actions=strActions, database=self.layer.databasename)
        print(params)
        response = RipartServiceRequest.makeHttpRequest(self.url, authent=self.identification, proxies=self.proxy,
                                                        data=params)
        print(response)
        xmlResponse = XMLResponse(response)
        message = xmlResponse.checkResponseWfsTransactions()
        if message['status'] == 'SUCCESS':
            self.showMessage(message['message'])
            self.layer.commitChanges(False)
            #self.layer.reload() - semble inutile pour la couche sqlite, les données enregistrées sont directement affichées
        else:
            self.showMessage('Transaction interrompue : {}'.format(message['message']))
            #raise Exception(message['message'])

    def commitLayer(self):
        self.actions.clear()

        editBuffer = self.layer.editBuffer()
        if not editBuffer:
            return

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
        # suppression
        deletedFeaturesId = editBuffer.deletedFeatureIds()
        if len(deletedFeaturesId) != 0:
            self.pushDeletedFeatures(deletedFeaturesId)

        # Lancement de la transaction
        strActions = self.formatItemActions()
        print(strActions)
        self.gcms_post(strActions)

    def pushAddedFeatures(self, addedFeatures):
        for feature in addedFeatures:
            strFeature = self.setHeader()
            strFeature += self.setFieldsNameValue(feature)
            strFeature += self.setGeometry(feature.geometry())
            strFeature += '},'
            strFeature += self.setStateAndLayerName('Insert')
            strFeature += '}'
            self.actions.append(strFeature)

    def pushChangedAttributesAndGeometries(self, changedAttributeValues, changedGeometries):
        # Récupération des géométries par identifiant d'objet
        geometries = self.setGeometries(changedGeometries)
        # Récupération des attributs et ajout de la géométrie
        for featureId, attributes in changedAttributeValues.items():
            feature = self.layer.getFeature(featureId)
            strFeature = self.setHeader()
            strFeature += self.setFieldsNameValue(feature)
            strFeature += self.setFingerPrint(feature.attribute('gcms_fingerprint'))
            strFeature += self.setCleabs(feature.attribute('cleabs'))
            strFeature += geometries[featureId]
            strFeature += '},'
            strFeature += self.setStateAndLayerName('Update')
            strFeature += '}'
            self.actions.append(strFeature)

    def pushChangedGeometries(self, changedGeometries):
        for featureId, geometry in changedGeometries.items():
            feature = self.layer.getFeature(featureId)
            strFeature = self.setHeader()
            strFeature += self.setFingerPrint(feature.attribute('gcms_fingerprint'))
            strFeature += self.setCleabs(feature.attribute('cleabs'))
            strFeature += ', {0}'.format(self.setGeometry(geometry))
            strFeature += '},'
            strFeature += self.setStateAndLayerName('Update')
            strFeature += '}'
            self.actions.append(strFeature)

    def pushChangedAttributeValues(self, changedAttributeValues):
        for featureId, attributes in changedAttributeValues.items():
            feature = self.layer.getFeature(featureId)
            strFeature = self.setHeader()
            strFeature += self.setFieldsNameValue(feature)
            strFeature += self.setFingerPrint(feature.attribute('gcms_fingerprint'))
            strFeature += self.setCleabs(feature.attribute('cleabs'))
            strFeature += '},'
            strFeature += self.setStateAndLayerName('Update')
            strFeature += '}'
            self.actions.append(strFeature)

    def pushDeletedFeatures(self, deletedFeatures):
        result = SQLiteManager.selectRowsInTable(self.layer.name(), deletedFeatures)
        for r in result:
            strFeature = self.setHeader()
            strFeature += self.setFingerPrint(r[1])
            strFeature += self.setCleabs(r[0])
            strFeature += '},'
            strFeature += self.setStateAndLayerName('Delete')
            strFeature += '}'
            self.actions.append(strFeature)

    def showMessage(self, message):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("IGN Espace Collaboratif")
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(message)
        ret = msgBox.exec_()

