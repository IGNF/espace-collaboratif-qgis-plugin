from qgis.core import QgsAction


class Action(QgsAction):
    """
    Classe représentant une action QGIS
    """
    qgsActionManager = None
    layer = None

    def __init__(self, layer):
        super(Action, self).__init__()
        self.actions = layer.actions()
        self.layer = layer

    def defineActionPython(self, attributeToModify):
        code = 'from qgis.gui import QgsAttributeDialog\n'
        code += 'from qgis.utils import iface\n'
        code += 'layer = iface.activeLayer()\n'
        code += 'if layer.selectedFeatures() == 0:return\n'
        code += 'feature = layer.selectedFeatures()[0]\n'
        code += 'attrDialog = QgsAttributeDialog(layer, feature, False)\n'
        code += 'attrDialog.exec_()'
        return code

    def do(self, actionType, actionDescription, actionShortName, actionCode):
        actionScopes = ['Feature', 'Field', 'Layer']
        # ActionType type, const QString &description, const QString &action, const QString &icon, bool capture, const QString &shortTitle = QString(), const QSet<QString> &actionScopes = QSet<QString>(), const QString &notificationMessage = QString(), bool enabledOnlyWhenEditable SIP_PYARGREMOVE = false
        qgsAction = QgsAction(actionType, actionDescription, actionCode, '', False, actionShortName, actionScopes, '')
        self.actions.addAction(qgsAction)
