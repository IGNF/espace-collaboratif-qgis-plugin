from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsDataSourceUri,
    QgsSingleSymbolRenderer,
    QgsFillSymbol,
    QgsEditorWidgetSetup,
    QgsCoordinateReferenceSystem
)
from .ConflictsView import ConflictsView
from .core import Constantes as cst
from .PluginHelper import PluginHelper
from .core.SQLiteManager import SQLiteManager


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

    def __applySymbology(self):
        properties = {
            'outline_color': '255,0,0',
            'outline_width': '0.66',
            'outline_style': 'solid',
            'color': '0,0,0,0'  # transparent
        }
        self.conflictslayer.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(properties)))

    def __applyJsonWidget(self):
        """
        Applique par défaut une vue JSON de type arborescence/indenté au champ en cours.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Vue JSON ]
        """
        # Type:JsonEdit
        QgsEWS_type = 'JsonEdit'
        # Config:{'DefaultView': 1, 'FormatJson': 0} arborescence/indenté
        QgsEWS_config = {'DefaultView': 1, 'FormatJson': 0}
        setup = QgsEditorWidgetSetup(QgsEWS_type, QgsEWS_config)
        idx = self.conflictslayer.fields().indexOf('data_server')
        self.conflictslayer.setEditorWidgetSetup(idx, setup)
        idx = self.conflictslayer.fields().indexOf('data_client')
        self.conflictslayer.setEditorWidgetSetup(idx, setup)

    def __applySrid(self):
        self.conflictslayer.setCrs(QgsCoordinateReferenceSystem(4326))

    def __toQgsVectorLayer(self) -> QgsVectorLayer:
        """
        Retourne une QgsVectorLayer (provider 'spatialite') pointant sur la table créée.
        """
        uri = QgsDataSourceUri()
        uri.setDatabase(SQLiteManager.getBaseSqlitePath())
        uri.setDataSource("", cst.CONFLICT_LAYER, "geom")
        return QgsVectorLayer(uri.uri(), cst.CONFLICT_LAYER, "spatialite")

    def __addLayerConflicts(self) -> None:
        self.conflictslayer = self.__toQgsVectorLayer()
        if self.conflictslayer and self.conflictslayer.isValid():
            QgsProject.instance().addMapLayer(self.conflictslayer)
            self.__applySrid()
            self.__applySymbology()
            self.__applyJsonWidget()
            print("[INFO] Couche Conflits ajoutée au projet")

    def __deleteLayerConflicts(self):
        """
        Cherche la couche conflits dans le projet QGIS et la supprime.
        """
        project = QgsProject.instance()
        listLayers = project.mapLayersByName(cst.CONFLICT_LAYER)
        if not listLayers:
            print("[INFO] La couche {} est déjà supprimée.".format(cst.CONFLICT_LAYER))
            return False
        # Supprimer toutes les couches "conflits" trouvées
        layerIds = []
        for lLayer in listLayers:
            layerIds.append(lLayer.id())
        if len(layerIds) >= 1:
            project.removeMapLayers(layerIds)
            project.write()
        print("[INFO] Couche {} supprimée".format(cst.CONFLICT_LAYER))
        return True

    def createTable(self):
        # Création de la table si elle n'existe pas
        if SQLiteManager.isTableExist(cst.CONFLICT_LAYER):
            SQLiteManager.deleteTable(cst.CONFLICT_LAYER)
            print("[INFO] Table {} détruite".format(cst.CONFLICT_LAYER))
        SQLiteManager.createTableConflicts()
        print("[INFO] Table {} créée".format(cst.CONFLICT_LAYER))

    def createLayer(self):
        self.__deleteLayerConflicts()
        self.__addLayerConflicts()

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
