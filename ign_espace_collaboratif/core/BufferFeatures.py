import json
import re
from . import Constantes as cst
from datetime import datetime
from qgis.PyQt.QtCore import NULL
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsField,
    QgsFeatureRequest,
    QgsFeature,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsCoordinateReferenceSystem
)
from PyQt5.QtCore import QVariant
from .Query import Query
from ..PluginHelper import PluginHelper


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def sanitize_name(name: str) -> str:
    """Nom de colonne sûr pour SQLite/SpatiaLite."""
    s = re.sub(r"[^0-9a-zA-Z_]+", "_", name).strip("_")
    if not s:
        s = "fld"
    if s[0].isdigit():
        s = "f_" + s
    return s.lower()


def map_qvariant_to_sqlite_type(qfield: QgsField) -> str:
    """Mappe le type QGIS -> type SQLite."""
    t = qfield.type()
    if t in (QVariant.Int, QVariant.LongLong, QVariant.UInt, QVariant.ULongLong, QVariant.Bool):
        return "INTEGER"
    if t in (QVariant.Double,):
        return "REAL"
    if t in (QVariant.ByteArray,):
        return "BLOB"
    # Dates/Heures, String, autres -> TEXT
    return "TEXT"


class BufferFeatures:
    """
    Prend un feature QGIS + sa couche, crée un buffer (par défaut 5.0 m)
    et insère dans une table SpatiaLite :
      - id INTEGER PRIMARY KEY AUTOINCREMENT
      - ts (TEXT ISO)
      - layer_name (TEXT)
      - fid (INTEGER)
      - cleabs (TEXT)  <-- nom d'attribut configurable
      - tous les attributs originaux du feature
      - geom (MULTIPOLYGON) = ST_Multi(ST_Buffer(...))

    La classe :
      - crée la table si nécessaire,
      - transforme la géométrie au SRID cible avant insertion.
    """
    def __init__(
            self,
            context,
            source_layer: QgsVectorLayer,
            distance: float = 15.0,  # distance de buffer (en unités du SRID)
            cleabs_attr: str = "cleabs"  # attribut unique/clé métier
    ):
        if not source_layer or not source_layer.isValid():
            raise ValueError("BufferFeatures.__init__: la couche de l'objet en conflit est invalide.")
        self.__context = context
        self.table_name = cst.CONFLICT_LAYER
        self.feature = None
        self.sourceLayer = source_layer
        self.conflictslayer = self.__retrieveLayer()
        self.srid = int(QgsProject.instance().crs().postgisSrid())
        print("[INFO] srid project : {}".format(self.srid))
        self.distance = float(distance)
        self.cleabs_attr = cleabs_attr

    def __retrieveLayer(self):
        layers = QgsProject.instance().mapLayersByName(cst.CONFLICT_LAYER)
        # QgsMapLayer to QgsVectorLayer
        return QgsVectorLayer(layers[0].source(), layers[0].name(), layers[0].providerType())

    def setFeatureByAttribute(self, params) -> None:
        isObjectClientDeleted = False
        idx = self.sourceLayer.fields().indexOf(params['attr'])
        if idx < 0:
            raise ValueError(f"BufferFeatures.setFeatureByAttribute: l'attribut '{params['attr']}' "
                             f"n'existe pas dans la couche de l'objet en conflit.")
        expr = f"\"{params['attr']}\" = '{params['attr_val']}'"
        req = QgsFeatureRequest().setFilterExpression(expr)
        self.feature = next(self.sourceLayer.getFeatures(req), None)
        # TODO si l'objet a été détruit que retourne la requete ? None
        if self.feature is None:
            isObjectClientDeleted = True
        # TODO attention self.feature peut-être None
        print("[INFO] Objet en conflit d'identifiant {} et de cleabs {}".format(self.feature.id(), params['attr_val']))
        # Retrouver les caractéristiques de l'objet serveur
        dataObjectServer = self.__retrieveObjectFromServer(params['database_id'], params['table_id'],
                                                           params['attr_val'])
        # Insère la ligne (buffer + attributs)
        print("[INFO] Données de l'objet server : {}".format(dataObjectServer))
        # TODO attention self.feature peut-être None
        self.__insertBufferedFeature(self.feature, isObjectClientDeleted, dataObjectServer)
        self.conflictslayer.triggerRepaint()
        self.conflictslayer.reload()

    def __searchTypeConflict(self, isObjectClientDeleted, datasObjectServer):
        isObjectServerDeleted = False
        datasServer = json.loads(datasObjectServer)
        if PluginHelper.keyExist('detruit', datasServer):
            isObjectServerDeleted = datasServer['detruit']
        if isObjectClientDeleted and not isObjectServerDeleted:
            return cst.CONFLICT_SUPPRESSION_CLIENT
        if not isObjectClientDeleted and isObjectServerDeleted:
            return cst.CONFLICT_SUPPRESSION_SERVEUR
        return cst.CONFLICT_MODIFICATION

    def __retrieveObjectFromServer(self, database_id, table_id, feature_id):
        query = Query(self.__context.urlHostEspaceCo, self.__context.getProxies())
        query.setHeaders(self.__context.getTokenType(), self.__context.getTokenAccess())
        query.setPartOfUrl("gcms/api/databases/{}/tables/{}/features/{}".format(database_id, table_id, feature_id))
        response = query.simple()
        if response is None:
            return ''
        return response.text

    def __bufferedGeometry(self):
        if self.feature is None:
            raise Exception("BufferFeatures.__bufferedGeometry : l'objet en conflit n'a pas été récupéré correctement.")
        geom = self.feature.geometry()
        if geom is None or geom.isEmpty():
            raise Exception("BufferFeatures.__bufferedGeometry : l'objet en conflit n’a pas de géométrie valide.")
        crs = self.sourceLayer.crs()
        # Si CRS en degrés → reprojection vers un CRS métrique
        if crs.isGeographic():
            target_crs = QgsCoordinateReferenceSystem("EPSG:3857")  # métrique
            transform = QgsCoordinateTransform(crs, target_crs, QgsProject.instance())
            geom_proj = QgsGeometry(geom)
            geom_proj.transform(transform)
            # Buffer dans le CRS métrique
            buffered = geom_proj.buffer(self.distance, 8)
            # Retour au CRS original
            back_transform = QgsCoordinateTransform(target_crs, crs, QgsProject.instance())
            buffered.transform(back_transform)
            return buffered
        else:
            # CRS déjà métrique → buffer direct
            return geom.buffer(self.distance, 8)

    def __insertBufferedFeature(
            self,
            source_feat: QgsFeature,
            source_feat_deleted: bool,
            dataObjectServer: str
    ):
        """
        Crée un nouvel objet dans target_layer à partir d’un feature source :
          - buffer de sa géométrie (buffer_dist)
          - pas de conversion de géométrie (la couche cible doit gérer MULTIPOLYGON)
          - stockage des attributs du feature source dans 'data_client'
            avec conversion des NULL QGIS → None
        """
        # -- 1) Calcul du buffer autour de l'objet en conflit --
        buffer = self.__bufferedGeometry()

        # -- 2) Nouveau feature --
        new_feat = QgsFeature(self.conflictslayer.fields())
        new_feat.setGeometry(buffer)

        # -- 3) Préparer attributs du feature source --
        attributesFeatureSource = {}
        for field in source_feat.fields():
            name = field.name()
            val = source_feat[name]
            # conversion QGIS NULL → Python None
            if val == NULL:
                val = None
            attributesFeatureSource[name] = val

        # -- 4) Attributs spécifiques au conflit --
        new_feat["date_conflict"] = now_iso()
        new_feat["layer_name"] = self.sourceLayer.name() if self.sourceLayer else None
        new_feat["id_object_client"] = int(source_feat.id())
        new_feat["cleabs"] = source_feat[self.cleabs_attr] if self.cleabs_attr in source_feat.fields().names() else None
        new_feat["data_server"] = dataObjectServer
        new_feat["data_client"] = json.dumps(attributesFeatureSource, ensure_ascii=False)
        new_feat["type_conflict"] = self.__searchTypeConflict(source_feat_deleted, dataObjectServer)
        new_feat["geometry_conflict"] = source_feat.geometry().asWkt()

        # -- 5) Insertion dans la couche --
        must_commit = False
        if not self.conflictslayer.isEditable():
            self.conflictslayer.startEditing()
            must_commit = True

        if not self.conflictslayer.addFeature(new_feat):
            raise Exception("Impossible d’ajouter le nouvel objet à la couche.")

        if must_commit:
            if not self.conflictslayer.commitChanges():
                raise Exception("Erreur durant le commit des modifications.")

        return new_feat
