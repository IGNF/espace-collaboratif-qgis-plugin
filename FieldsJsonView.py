import os
from qgis.PyQt import uic, QtWidgets
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QDialogButtonBox

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FieldsJsonView_base.ui'))


class FieldsJsonView(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, context, layer, parent=None):
        super(FieldsJsonView, self).__init__(parent)
        print("init")
        self.setupUi(self)
        self.setFocus()
        self.setFixedSize(self.width(), self.height())
        self.pushButtonModify.clicked.connect(self.modify)
        self.pushButtonCancel.clicked.connect(self.cancel)
        self.pushbuttonAddJsonField.clicked.connect(self.addJsonField)
        self.pushButtonRemoveJsonField.clicked.connect(self.removeJsonField)
        self.context = context
        jsonFieldName = self.setLabelCombobox(layer.name())
        self.labelJsonField.setText(jsonFieldName)

    def setLabelCombobox(self, layerName):
        datas = self.setConnexion(layerName)
        jsonFieldName = ''
        for a, b in datas['attributes'].items():
            if b['type'] != 'JsonValue':
                continue
            jsonFieldName = b['name']
            i = 0
            for c, d in b['json_schema'].items():
                if c != 'items':
                    continue
                for nameAttributeJson, f in d['properties'].items():
                    enum = []
                    for g, h in f.items():
                        if g == 'enum':
                            enum = h
                    i += 1
                    if nameAttributeJson in d['required']:
                        nameAttributeJson += '*'
                    if i == 1:
                        self.labelField_1.setText(nameAttributeJson)
                        if len(enum) != 0:
                            self.comboBox_1.addItems(enum)
                    if i == 2:
                        self.labelField_2.setText(nameAttributeJson)
                        if len(enum) != 0:
                            self.comboBox_2.addItems(enum)
                    if i == 3:
                        self.labelField_3.setText(nameAttributeJson)
                        if len(enum) != 0:
                            self.comboBox_3.addItems(enum)
                    if i == 4:
                        self.labelField_4.setText(nameAttributeJson)
                        if len(enum) != 0:
                            self.comboBox_4.addItems(enum)
                    if i == 5:
                        self.labelField_5.setText(nameAttributeJson)
                        if len(enum) != 0:
                            self.comboBox_5.addItems(enum)
                    if i == 6:
                        self.labelField_6.setText(nameAttributeJson)
                        if len(enum) != 0:
                            self.comboBox_6.addItems(enum)
                    if i == 7:
                        self.labelField_7.setText(nameAttributeJson)
                        if len(enum) != 0:
                            self.comboBox_7.addItems(enum)
                    if i == 8:
                        self.labelField_8.setText(nameAttributeJson)
                        if len(enum) != 0:
                            self.comboBox_8.addItems(enum)
                    if i == 9:
                        self.labelField_9.setText(nameAttributeJson)
                        if len(enum) != 0:
                            self.comboBox_9.addItems(enum)
                    if i == 10:
                        self.labelField_10.setText(nameAttributeJson)
                        if len(enum) != 0:
                            self.comboBox_10.addItems(enum)
            break

        return jsonFieldName

    def setConnexion(self, layerName):
        connexionLayers = self.context.getInfosLayers()
        if connexionLayers[0] == "Rejected":
            return
        listLayers = []
        if connexionLayers[0] == "Accepted":
            listLayers = connexionLayers[1]
        url = ''
        for layer in listLayers:
            if layer.nom == layerName:
                url = layer.url
        return self.context.client.connexionFeatureTypeJson(url, layerName)

    def modify(self):
        self.accept()

    def cancel(self):
        self.reject()

    def addJsonField(self):
        pass

    def removeJsonField(self):
        pass

    def setFieldJsonToSQLite(self):
        # Il faut récupérer les dictionnaires "json_schema" puis items et properties
        attributeName = ''
        jsonAttribute = {}
        valeurs = self.data['attributes']
        for k, v in valeurs.items():
            attributeName = k
            for a, b in v['json_schema'].items():
                for c, d in b['items'].items():
                    for e, f in d['properties'].items():
                        jsonAttribute[e] = f
        return attributeName, jsonAttribute
