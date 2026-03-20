import json
import os
import re
import sqlite3
from datetime import datetime

from qgis.PyQt.QtCore import NULL
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsField,
    QgsFeatureRequest,
    QgsFillSymbol,
    QgsSingleSymbolRenderer,
    QgsEditorWidgetSetup,
    QgsCoordinateReferenceSystem,
    QgsFeature
)
from PyQt5.QtCore import QVariant

from .SQLiteManager import SQLiteManager
from.Query import Query
from . import Constantes as cst


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _sanitize_name(name: str) -> str:
    """Nom de colonne sûr pour SQLite/SpatiaLite."""
    s = re.sub(r"[^0-9a-zA-Z_]+", "_", name).strip("_")
    if not s:
        s = "fld"
    if s[0].isdigit():
        s = "f_" + s
    return s.lower()


def _map_qvariant_to_sqlite_type(qfield: QgsField) -> str:
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
    Prend un feature QGIS + sa couche, crée un buffer (par défaut 1.0 m)
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
      - ajoute les colonnes manquantes si la structure a évolué,
      - transforme la géométrie au SRID cible avant insertion.
    """

    def __init__(
            self,
            context,
            source_layer: QgsVectorLayer,
            distance: float = 5.0,  # distance de buffer (en unités du SRID)
            cleabs_attr: str = "cleabs"  # attribut unique/clé métier
    ):
        if not source_layer or not source_layer.isValid():
            raise ValueError("Feature et/ou couche source invalide(s).")
        self.__context = context
        self.sqlite_path = SQLiteManager.getBaseSqlitePath()
        self.table_name = cst.CONFLICT_LAYER
        self.feature = None
        self.Sourcelayer = source_layer
        self.conflictslayer = None
        self.srid = int(QgsProject.instance().crs().postgisSrid())
        self.distance = float(distance)
        self.cleabs_attr = cleabs_attr

        # Construire le mapping des attributs (name -> (safe_name, type_sql))
        self.attr_map = self._build_attribute_map()

        # Création de la table si elle n'existe pas
        if not SQLiteManager.isTableExist(cst.CONFLICT_LAYER):
            SQLiteManager.createTableConflicts()

    # ------------------------------------------------------------------ #
    # Préparation schéma
    # ------------------------------------------------------------------ #
    def _build_attribute_map(self):
        """
        Construit un mapping { original_name: (col_name_sql_safe, sqlite_type) }
        en excluant les colonnes techniques et 'geom'.
        """
        reserved = {"id", "ts", "layer_name", "fid", "cleabs", "data", "geom"}
        amap = {}
        for f in self.Sourcelayer.fields():
            oname = f.name()
            if oname in reserved:
                continue
            sname = _sanitize_name(oname)
            if sname in reserved:
                sname = f"a_{sname}"
            sqlite_type = _map_qvariant_to_sqlite_type(f)
            amap[oname] = (sname, sqlite_type)
        return amap

    def _connect_spatialite(self):
        """
        Ouvre une connexion SQLite et charge l'extension SpatiaLite.
        Gère mod_spatialite/libspatialite selon la plateforme.
        """
        if not os.path.isfile(self.sqlite_path):
            # assure un fichier existant
            open(self.sqlite_path, "ab").close()

        con = sqlite3.connect(self.sqlite_path)
        con.enable_load_extension(True)
        loaded = False
        for lib in ("mod_spatialite", "libspatialite"):
            try:
                con.load_extension(lib)
                loaded = True
                break
            except Exception:
                continue
        if not loaded:
            con.close()
            raise RuntimeError("Impossible de charger l'extension SpatiaLite (mod_spatialite/libspatialite).")
        return con

    def _insert_row(self, dataObjectServer, dataObjectClient) -> None:
        """Construit et exécute l'INSERT (attributs + géométrie buffer)."""
        # 1) Prépare les valeurs techniques
        ts = now_iso()
        layer_name = self.Sourcelayer.name() if self.Sourcelayer else None
        fid = int(self.feature.id())
        cleabs = self.feature[self.cleabs_attr] if self.cleabs_attr in self.feature.fields().names() else None

        # 2) Géométrie (WKT) transformée en buffer
        geomFeat = self.feature.geometry()
        wkt = geomFeat.asWkt()
        print("WKT : {}".format(wkt))

        # 3) SQL INSERT
        print("SRID : {}".format(self.srid))
        base_cols = ['"ts"', '"layer_name"', '"fid"', '"cleabs", "data"'] + ['"geom"']
        placeholders = ["?", "?", "?", "?", "?"] + [
            f"ST_Transform(ST_Buffer(ST_Transform(GeomFromText(?, 4326), {self.srid}), ?), 4326)"
        ]
        sql = f'INSERT INTO "{self.table_name}" ({", ".join(base_cols)}) VALUES ({", ".join(placeholders)})'
        params = [ts, layer_name, fid, cleabs, dataObjectServer] + [wkt, self.distance]
        # 5) Exécution
        con = self._connect_spatialite()
        cur = con.cursor()
        cur.execute(sql, params)
        con.commit()
        con.close()

    def __toQgsVectorLayer(self) -> QgsVectorLayer:
        """
        Retourne une QgsVectorLayer (provider 'spatialite') pointant sur la table créée.
        """
        from qgis.core import QgsDataSourceUri
        uri = QgsDataSourceUri()
        uri.setDatabase(self.sqlite_path)
        uri.setDataSource("", cst.LAYER_CONFLICTS, "geom")
        return QgsVectorLayer(uri.uri(), cst.LAYER_CONFLICTS, "spatialite")

    def addLayerConflictsToProject(self) -> None:
        self.conflictslayer = self.__toQgsVectorLayer()
        if self.conflictslayer and self.conflictslayer.isValid():
            QgsProject.instance().addMapLayer(self.conflictslayer)
            # self.applySrid()
            self.applySymbology()
            self.applyJsonWidget()
            print("[INFO] Couche Conflits ajoutée au projet")

    def setFeatureByAttribute(self, params) -> None:
        idx = self.Sourcelayer.fields().indexOf(params['attr'])
        if idx < 0:
            raise ValueError(f"Attribut '{params['attr']}' introuvable")
        expr = f"\"{params['attr']}\" = '{params['attr_val']}'"
        req = QgsFeatureRequest().setFilterExpression(expr)
        self.feature = next(self.Sourcelayer.getFeatures(req), None)
        # dataObjectClient = self.retrieveObjectFromClient()
        print("[INFO] Objet d'identifiant {} et de cleabs {}".format(self.feature.id(), params['attr_val']))
        # Retrouver les caractéristiques de l'objet serveur
        dataObjectServer = self.retrieveObjectFromServer(params['database_id'], params['table_id'], params['attr_val'])
        # Insère la ligne (buffer + attributs)
        print("dataObjectServer : {}".format(dataObjectServer))
        # self._insert_row(dataObjectServer, dataObjectClient)
        self.insert_buffered_feature(self.feature, dataObjectServer)

    def _safe_value(self, val):
        """Convertit tout en type Python SQLite-compatible."""

        # 1) None Python
        if val is None:
            return None

        # 2) QVariant invalid -> None
        if isinstance(val, QVariant):
            if val.isNull() or not val.isValid():
                return None
            # extract Python value
            val = val.toPyObject() if hasattr(val, "toPyObject") else val

        # 3) Bytes
        if isinstance(val, (bytes, bytearray, memoryview)):
            return bytes(val)

        # 4) QDate / QDateTime
        if hasattr(val, "toString"):
            try:
                s = val.toString("yyyy-MM-dd HH:mm:ss")
                if s:
                    return s
            except Exception:
                pass

        # 5) bool → int
        if isinstance(val, bool):
            return int(val)

        # 6) Int / Float / Str OK
        if isinstance(val, (int, float, str)):
            return val

        # 7) Tout le reste → string
        try:
            return str(val)
        except Exception:
            return None

    def retrieveObjectFromClient(self, feat: QgsFeature) -> str:
        """
        Convertit un QgsFeature en dictionnaire Python.
        Gère les valeurs NULL de QGIS (renvoie None).
        """
        out = {}
        fields = feat.fields()
        for field in fields:
            name = field.name()
            value = feat[name]
            # Conversion des QVariant NULL en None
            if value is None or value == NULL:
                value = None
            out[name] = value
        return json.dumps(out)

    def retrieveObjectFromServer(self, database_id, table_id, feature_id):
        query = Query(self.__context.urlHostEspaceCo, self.__context.getProxies())
        query.setHeaders(self.__context.getTokenType(), self.__context.getTokenAccess())
        query.setPartOfUrl("gcms/api/databases/{}/tables/{}/features/{}".format(database_id, table_id, feature_id))
        response = query.simple()
        if response is None:
            return ''
        return response.text

    def applySymbology(self):
        properties = {
            'outline_color': '255,0,0',
            'outline_width': '0.66',
            'outline_style': 'solid',
            'color': '0,0,0,0'  # transparent
        }
        self.conflictslayer.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(properties)))

    def applyJsonWidget(self):
        """
        Applique par défaut une vue JSON de type arborescence/indenté au champ en cours.
        Voir [ Couche/Propriétés.../Formulaire d'attributs/Type d'outil > Vue JSON ]
        """
        # Type:JsonEdit
        QgsEWS_type = 'JsonEdit'
        # Config:{'DefaultView': 1, 'FormatJson': 0} arborescence/indenté
        QgsEWS_config = {'DefaultView': 1, 'FormatJson': 0}
        setup = QgsEditorWidgetSetup(QgsEWS_type, QgsEWS_config)
        idx = self.conflictslayer.fields().indexOf('data')
        self.conflictslayer.setEditorWidgetSetup(idx, setup)

    def applySrid(self):
        self.conflictslayer.setCrs(QgsCoordinateReferenceSystem(4326))

    import json
    from qgis.core import QgsFeature, QgsGeometry, NULL

    def insert_buffered_feature(
            self,
            source_feat: QgsFeature,
            dataObjectServer: str,
            buffer_dist: float = 5.0):
        """
        Crée un nouvel objet dans target_layer à partir d’un feature source :
          - buffer de sa géométrie (buffer_dist)
          - pas de conversion de géométrie (la couche cible doit gérer MULTIPOLYGON)
          - stockage des attributs du feature source dans 'data_client'
            avec conversion des NULL QGIS → None
        """

        # -- 1) Géométrie source --
        geom = source_feat.geometry()
        if geom is None or geom.isEmpty():
            raise Exception("Le feature source n’a pas de géométrie valide.")

        # -- 2) Buffer --
        buffered = geom.buffer(buffer_dist, 8)

        # -- 3) Nouveau feature --
        new_feat = QgsFeature(self.conflictslayer.fields())
        new_feat.setGeometry(buffered)

        # -- 4) Préparer attributs du feature source --
        attr_dict = {}
        for field in source_feat.fields():
            name = field.name()
            val = source_feat[name]

            # conversion QGIS NULL → Python None
            if val == NULL:
                val = None

            attr_dict[name] = val

        # Attribut JSON
        new_feat["data_client"] = json.dumps(attr_dict, ensure_ascii=False)
        new_feat["data_server"] = dataObjectServer

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
