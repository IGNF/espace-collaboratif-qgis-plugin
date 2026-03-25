from .ConflictsView import ConflictsView
from .FormInfo import FormInfo
from .core import Constantes as cst
from .PluginHelper import PluginHelper

class Conflicts(object):

    def __init__(self, context, iface) -> None:
        """
        Constructeur.
        Initialise le contexte, les outils de gestion d'un signalement (ToolsReport).
        Récupère le fichier de log.

        :param context: le contexte du projet
        """
        self.__context = context
        self.__iface = iface

    def do(self):
        # datas = self.__selectAll()
        datas = {}
        cf = ConflictsView(self.__context, datas)
        cf.exec_()

    def __selectDatas(self, feature):
        datas = {}
        fields = feature.fields()
        datas.update({fields['cleabs']: [fields['data_server'], fields['data_client']]})
        return datas

    def __selectAll(self):
        activeLayer = self.__iface.activeLayer()
        if activeLayer is None:
            return False

        if activeLayer.name() != cst.CONFLICT_LAYER:
            message = "Il faut sélectionner la couche {} avant d'utiliser " \
                      "cette fonctionnalité.".format(cst.CONFLICT_LAYER)
            PluginHelper.showMessageBox(message)
            return False

        features = activeLayer.getFeatures()
        if len(list(features)) == 0:
            message = "La couche {} ne contient pas d'objets.".format(cst.CONFLICT_LAYER)
            PluginHelper.showMessageBox(message)
            return False

        datas = {}
        for feature in features:
            datas.update(self.__selectDatas(feature))
        return datas
