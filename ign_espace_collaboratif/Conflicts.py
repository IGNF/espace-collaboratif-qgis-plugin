from qgis.utils import iface
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
    __dlgConflicts = None

    def __init__(self, context, iface) -> None:
        """
        Constructeur.
        Initialise le contexte, les outils de gestion d'un signalement (ToolsReport).
        Récupère le fichier de log.

        :param context: le contexte du projet
        """
        self.__context = context
        self.__iface = iface
        self.__project = QgsProject.instance()

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
        listLayers = self.__project.mapLayersByName(cst.CONFLICT_LAYER)
        if len(listLayers) == 1:
            return
        self.conflictslayer = self.__toQgsVectorLayer()
        if self.conflictslayer and self.conflictslayer.isValid():
            self.__project.addMapLayer(self.conflictslayer)
            self.__applySrid()
            self.__applySymbology()
            self.__applyJsonWidget()
            print("[INFO] Couche 'conflits' ajoutée au projet")

    def __deleteLayerConflicts(self):
        """
        Cherche la couche conflits dans le projet QGIS et la supprime.
        """
        listLayers = self.__project.mapLayersByName(cst.CONFLICT_LAYER)
        if len(listLayers) == 0:
            print("[INFO] La couche {} est déjà supprimée.".format(cst.CONFLICT_LAYER))
            return False
        # Supprimer toutes les couches "conflits" trouvées
        layerIds = []
        for lLayer in listLayers:
            layerIds.append(lLayer.id())
        if len(layerIds) >= 1:
            self.__project.removeMapLayers(layerIds)
            self.__project.write()
        print("[INFO] Couche {} supprimée".format(cst.CONFLICT_LAYER))
        return True

    def createTable(self):
        # Création de la table si elle n'existe pas
        if SQLiteManager.isTableExist(cst.CONFLICT_LAYER):
            return
            # SQLiteManager.deleteTable(cst.CONFLICT_LAYER)
            # print("[INFO] Table {} détruite".format(cst.CONFLICT_LAYER))
        SQLiteManager.createTableConflicts()
        print("[INFO] Table {} créée".format(cst.CONFLICT_LAYER))

    def createLayer(self):
        # self.__deleteLayerConflicts()
        self.__addLayerConflicts()

    def do(self):
        conflicts = Conflicts.selectAllConflicts()
        if len(conflicts) == 0:
            return
        self.__dlgConflicts = ConflictsView(self.__context, self.__iface, conflicts)
        # Ouverture en non-modale
        self.__dlgConflicts.show()

    @staticmethod
    def selectAllConflicts():
        activeLayer = iface.activeLayer()
        if activeLayer is None:
            return []

        if activeLayer.name() != cst.CONFLICT_LAYER:
            message = "Il faut sélectionner la couche {} avant d'utiliser " \
                      "cette fonctionnalité.".format(cst.CONFLICT_LAYER)
            PluginHelper.showMessageBox(message)
            return []

        features = list(activeLayer.getFeatures())
        nb = len(features)
        if nb == 0:
            message = "La couche {} ne contient pas d'objets.".format(cst.CONFLICT_LAYER)
            PluginHelper.showMessageBox(message)
            return []

        return features
