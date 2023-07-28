from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject,\
    QgsEditorWidgetSetup

from qgis.utils import spatialite_connect
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry, QgsVectorLayer, QgsProject, \
    QgsDataSourceUri

from .PluginHelper import PluginHelper

from .core.ProgressBar import ProgressBar
from .core.BBox import BBox
from .core.RipartLoggerCl import RipartLogger
from .core.NoProfileException import NoProfileException
from .core.SQLiteManager import SQLiteManager
from .core import Constantes as cst

import os.path


# Importation des signalements dans le projet QGIS
class DownloadReport(object):

    def __init__(self, context):
        self.logger = RipartLogger("DownloadReport").getRipartLogger()
        self.context = context
        # barre de progression des signalements importés
        self.progress = None
        self.progressVal = 0

    def getUriDatabaseSqlite(self):
        uri = QgsDataSourceUri(cst.EPSG4326)
        uri.setDatabase(SQLiteManager.getBaseSqlitePath())
        return uri

    def addReportSketchLayersToTheCurrentMap(self):
        uri = self.getUriDatabaseSqlite()
        self.logger.debug(uri.uri())
        maplayers = self.context.getAllMapLayers()
        root = QgsProject.instance().layerTreeRoot()
        for table in PluginHelper.reportSketchLayersName:
            if table not in maplayers:
                uri.setDataSource('', table, 'geom')
                uri.setSrid(str(cst.EPSGCRS))
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                vlayer.setCrs(QgsCoordinateReferenceSystem(cst.EPSGCRS, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId))
                QgsProject.instance().addMapLayer(vlayer, False)
                root.insertLayer(0, vlayer)
                self.logger.debug("Layer " + vlayer.name() + " added to map")
                # ajoute les styles aux couches
                style = os.path.join(self.context.projectDir, "espacecoStyles", table + ".qml")
                vlayer.loadNamedStyle(style)
        self.context.mapCan.refresh()

    # Téléchargement et import des signalements sur la carte
    def do(self):
        self.logger.debug("DownloadReport.do")

        # paramètres pour la requête au service de l'espace collaboratif
        params = {}

        # l'utilisateur n'a pas de profil actif, impossible pour lui de travailler
        if self.context.profil.geogroup.getName() is None:
            raise NoProfileException(
                "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

        # filtre spatial
        bbox = BBox(self.context)
        box = bbox.getFromLayer(PluginHelper.load_CalqueFiltrage(self.context.projectDir).text)

        # si la box est à None alors, l'utilisateur veut extraire France entière
        # si la box est égale 0.0 pour ces 4 coordonnées alors l'utilisateur
        # ne souhaite pas extraire les données France entière et on sort
        if box is not None and box.XMax == 0.0 and box.YMax == 0.0 and box.XMin == 0.0 and box.YMin == 0.0:
            return

        filtreLay = None
        filtre = PluginHelper.load_CalqueFiltrage(self.context.projectDir).text
        if filtre is not None and len(filtre.strip()) > 0:
            self.logger.debug("Spatial filter :" + filtre)
            filtreLay = self.context.getLayerByName(filtre)

        message = "Placement des signalements sur la carte"
        self.progress = ProgressBar(200, message)

        # Création des couches et des liens vers la base SQLite
        self.addReportSketchLayersToTheCurrentMap()

        # Vider les tables signalement et croquis
        SQLiteManager.emptyAllReportAndSketchInTables(PluginHelper.reportSketchLayersName)
        self.context.refresh_layers()

        pagination = PluginHelper.load_ripartXmlTag(self.context.projectDir, PluginHelper.xml_Pagination, "Map").text
        if pagination is None:
            pagination = PluginHelper.defaultPagination

        date = PluginHelper.load_ripartXmlTag(self.context.projectDir, PluginHelper.xml_DateExtraction, "Map").text
        date = PluginHelper.formatDate(date)

        groupFilter = PluginHelper.load_ripartXmlTag(self.context.projectDir, PluginHelper.xml_Group, "Map").text
        if groupFilter == 'true':
            groupId = self.context.profil.geogroup.getId()

            params['group'] = str(groupId)

        self.context.client.setIface(self.context.iface)

        if box is not None:
            params['box'] = box.boxToString()

        params['pagination'] = pagination
        params['updatingDate'] = date

        rems = self.context.client.getGeoRems(params)

        # Filtrage spatial affiné des remarques.
        if box is not None:
            remsToKeep = {}

            for key in rems:
                ptx = rems[key].position.longitude
                pty = rems[key].position.latitude
                pt = "POINT(" + ptx + " " + pty + ")"
                ptgeom = QgsGeometry.fromWkt(pt)

                if PluginHelper.isInGeometry(ptgeom, filtreLay):
                    remsToKeep[key] = rems[key]

        else:
            remsToKeep = rems

        cnt = len(remsToKeep)

        try:
            i = 100
            try:
                self.context.conn = spatialite_connect(self.context.dbPath)

                for remId in remsToKeep:

                    if remId == '618195' or remId == '618197':
                        debug = True

                    PluginHelper.insertRemarques(self.context.conn, remsToKeep[remId])
                    i += 1
                    if cnt > 0:
                        self.progressVal = int(round(i * 100 / cnt))
                        self.progress.setValue(self.progressVal)

                self.context.conn.commit()

            except Exception as e:
                self.logger.error(format(e))
                raise
            finally:
                self.context.conn.close()

            if cnt > 1:
                remLayer = self.context.getLayerByName(PluginHelper.nom_Calque_Signalement)
                remLayer.updateExtents(True)
                box = remLayer.extent()
                self.setMapExtent(box)

            elif filtreLay is not None:
                box = filtreLay.extent()
                self.setMapExtent(box)

            # Résultat
            self.showImportResult(cnt)

            # Modification du formulaire pour afficher l'attribut "Thèmes" sous forme de "Vue JSON"
            # Vue par défaut : Arborescence
            # Formater le JSON : Indenté
            self.setFormAttributes()
            self.progress.close()

        except Exception as e:
            raise

        finally:
            self.progress.close()

    def setFormAttributes(self):
        listLayers = QgsProject.instance().mapLayersByName(PluginHelper.nom_Calque_Signalement)
        if len(listLayers) == 0:
            return
        features = None
        for layer in listLayers:
            features = layer.getFeatures()
            break
        fields = None
        for feature in features:
            fields = feature.fields()
            break
        if fields is None or len(fields) == 0:
            return
        index = -1
        for field in fields:
            name = field.name()
            if name == 'Thèmes':
                index = fields.indexOf(name)
                break
        # Si l'attribut "Thèmes" n'existe pas, on ne fait rien, on laisse faire QGIS
        if index == -1:
            return
        # modification du formulaire QGIS pour l'attribut "Thèmes"
        # Type:JsonEdit
        QgsEWS_type = 'JsonEdit'
        # Config:{'DefaultView': 1, 'FormatJson': 0}
        QgsEWS_config = {'DefaultView': 1, 'FormatJson': 0}
        setup = QgsEditorWidgetSetup(QgsEWS_type, QgsEWS_config)
        listLayers[0].setEditorWidgetSetup(index, setup)

    def setMapExtent(self, box):
        """set de l'étendue de la carte

        :param box: bounding box
        """
        source_crs = QgsCoordinateReferenceSystem(cst.EPSGCRS)

        mapCrs = self.context.mapCan.mapSettings().destinationCrs().authid()
        dest_crs = QgsCoordinateReferenceSystem(mapCrs)

        transform = QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())
        new_box = transform.transformBoundingBox(box)

        # distance pour le buffer: 10% de la distance minimale (hauteur ou largeur)
        dist = min(new_box.width(), new_box.height()) * 0.1
        # zoom sur la couche Signalement
        self.context.mapCan.setExtent(new_box.buffered(dist))

    def showImportResult(self, cnt):
        """Résultat de l'import

        :param cnt: le nombre de remarques importées
        :type cnt: int
        """
        submit = self.context.countRemarqueByStatut(cst.STATUT.submit.__str__())
        pending = self.context.countRemarqueByStatut(cst.STATUT.pending.__str__()) + \
                  self.context.countRemarqueByStatut(cst.STATUT.pending0.__str__()) + \
                  self.context.countRemarqueByStatut(cst.STATUT.pending1.__str__()) + \
                  self.context.countRemarqueByStatut(cst.STATUT.pending2.__str__())
        reject = self.context.countRemarqueByStatut(cst.STATUT.reject.__str__())
        valid = self.context.countRemarqueByStatut(cst.STATUT.valid.__str__()) + self.context.countRemarqueByStatut(
            cst.STATUT.valid0.__str__())

        resultMessage = "Extraction réussie avec succès de " + str(cnt) + " signalement(s) depuis le serveur \n" + \
                        "avec la répartition suivante : \n\n" + \
                        "- " + str(submit) + " signalement(s) nouveau(x).\n" + \
                        "- " + str(pending) + " signalement(s) en cours de traitement.\n" + \
                        "- " + str(valid) + " signalement(s)  validé(s).\n" + \
                        "- " + str(reject) + " signalement(s) rejeté(s).\n"

        PluginHelper.showMessageBox(resultMessage)
