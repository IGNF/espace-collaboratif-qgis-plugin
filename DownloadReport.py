import os.path
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsVectorLayer, QgsProject, \
    QgsEditorWidgetSetup
from .PluginHelper import PluginHelper
from .core.ProgressBar import ProgressBar
from .core.BBox import BBox
from .core.RipartLoggerCl import RipartLogger
from .core.NoProfileException import NoProfileException
from .core.SQLiteManager import SQLiteManager
from .core.Query import Query
from .core import Constantes as cst


# Importation des signalements dans le projet QGIS
class DownloadReport(object):

    def __init__(self, context):
        self.__logger = RipartLogger("DownloadReport").getRipartLogger()
        self.__context = context
        # barre de progression des signalements importés
        self.__progress = None
        self.__progressVal = 0

    def addReportSketchLayersToTheCurrentMap(self):
        uri = self.__context.getUriDatabaseSqlite()
        self.__logger.debug(uri.uri())
        maplayers = self.__context.getAllMapLayers()
        root = QgsProject.instance().layerTreeRoot()
        for table in PluginHelper.reportSketchLayersName:
            if table not in maplayers:
                uri.setDataSource('', table, 'geom')
                uri.setSrid(str(cst.EPSGCRS4326))
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                vlayer.setCrs(QgsCoordinateReferenceSystem(cst.EPSGCRS4326, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId))
                QgsProject.instance().addMapLayer(vlayer, False)
                root.insertLayer(0, vlayer)
                self.__logger.debug("Layer " + vlayer.name() + " added to map")
                # ajoute les styles aux couches
                style = os.path.join(self.__context.projectDir, "espacecoStyles", table + ".qml")
                vlayer.loadNamedStyle(style)
        self.__context.mapCan.refresh()

    def getAttachments(self, attachments) -> str:
        docs = ''
        if attachments is None or len(attachments) == 0:
            return docs
        for attachment in attachments:
            docs += "{} ".format(attachment['download_uri'])
        return docs[:-1]

    def setUrl(self, idReport) -> str:
        # https://qlf-collaboratif.ign.fr/collaboratif-develop/gcms/api/reports/162918
        return "{0}/gcms/api/reports/{1}".format(self.__context.urlHostEspaceCo, idReport)

    def getThemes(self, themes) -> str:
        strThemes = ''
        if themes is None or len(themes) == 0:
            return strThemes
        for theme in themes:
            strThemes += "{},".format(theme)
        return strThemes[:-1]

    def insertReportsIntoSQLite(self, datas):
        parameters = {'tableName': 'Signalement', 'geometryName': 'geom', 'sridTarget': cst.EPSGCRS4326,
                      'sridSource': cst.EPSGCRS4326, 'isStandard': False, 'is3D': False, 'geometryType': 'POINT'}
        attributesRows = []
        for data in datas:
            attributesRow = {
                'NoSignalement': data['id'],
                'Auteur': data['author'],
                'Commune': data['commune']['title'],
                'Insee': data['commune']['name'],
                'Département': data['departement']['title'],
                'Département_id': data['departement']['name'],
                'Date_création': data['opening_date'],
                'Date_MAJ': data['updating_date'],
                'Date_validation': data['closing_date'],
                'Thèmes': self.getThemes(data['attributes']),
                'Statut': data['status'],
                'Message': data['comment'],
                'Réponses': '',
                'URL': self.setUrl(data['id']),
                'URL_privé': '',
                'Document': self.getAttachments(data['attachments']),
                'Autorisation': '',
                'geom': data['geometry']
            }
            attributesRows.append(attributesRow)
        sqliteManager = SQLiteManager()
        sqliteManager.insertRowsInTable(parameters, attributesRows)
        # TODO que fait-on des attributs suivants ?
        # data['replies']
        # data['community']
        # data['validator']
        # data['territory']
        # data['sketch_xml']
        # data['sketch']
        # data['input_device']
        # data['device_version']

    def getReports(self, date) -> []:
        # filtre spatial
        bbox = BBox(self.__context)
        box = bbox.getFromLayer(PluginHelper.load_CalqueFiltrage(self.__context.projectDir).text, False, False)
        # si la box est à None alors, l'utilisateur veut extraire France entière
        # si la box est égale 0.0 pour ces 4 coordonnées alors l'utilisateur
        # ne souhaite pas extraire les données France entière
        if box is not None and box.XMax == 0.0 and box.YMax == 0.0 and box.XMin == 0.0 and box.YMin == 0.0:
            return

        query = Query(self.__context.urlHostEspaceCo, self.__context.auth['login'], self.__context.auth['password'],
                      self.__context.proxy)
        query.setPartOfUrl('gcms/api/reports')
        query.setPage(1)
        query.setLimit(100)
        query.setBox(box)
        query.setOpeningDate(date)
        data = query.multiple()
        return data

    # Téléchargement et import des signalements sur la carte
    def do(self):
        self.__logger.debug("DownloadReport.do")

        # l'utilisateur n'a pas de profil actif, impossible pour lui de travailler
        if self.__context.profil.geogroup.getName() is None:
            raise NoProfileException(
                "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

        message = "Placement des signalements sur la carte"
        self.progress = ProgressBar(200, message)

        # Création des couches dans QGIS et des liens vers la base SQLite
        self.addReportSketchLayersToTheCurrentMap()

        # Vider les tables signalement et croquis
        SQLiteManager.emptyReportsAndSketchsInTables(PluginHelper.reportSketchLayersName)

        # Téléchargement des signalements
        date = PluginHelper.load_ripartXmlTag(self.__context.projectDir, PluginHelper.xml_DateExtraction, "Map").text
        date = PluginHelper.formatDate(date)
        data = self.getReports(date)

        # Insertion des signalements dans la base SQLite
        if len(data) == 0:
            return
        self.insertReportsIntoSQLite(data)

        # Rafraichir la carte
        self.__context.refresh_layers()

        # Fermer la patience
        self.progress.close()

        # Afficher les résultats
        cnt = 0
        self.showImportResult(cnt)

        # pagination = PluginHelper.load_ripartXmlTag(self.context.projectDir, PluginHelper.xml_Pagination, "Map").text
        # if pagination is None:
        #     pagination = PluginHelper.defaultPagination
        #
        # date = PluginHelper.load_ripartXmlTag(self.context.projectDir, PluginHelper.xml_DateExtraction, "Map").text
        # date = PluginHelper.formatDate(date)
        #
        # groupFilter = PluginHelper.load_ripartXmlTag(self.context.projectDir, PluginHelper.xml_Group, "Map").text
        # if groupFilter == 'true':
        #     groupId = self.context.profil.geogroup.getId()
        #
        #     params['group'] = str(groupId)
        #
        # self.context.client.setIface(self.context.iface)
        #
        # if box is not None:
        #     params['box'] = box.boxToString()
        #
        # params['pagination'] = pagination
        # params['updatingDate'] = date
        #
        # rems = self.context.client.getGeoRems(params)
        #
        # # Filtrage spatial affiné des remarques.
        # if box is not None:
        #     remsToKeep = {}
        #
        #     for key in rems:
        #         ptx = rems[key].position.longitude
        #         pty = rems[key].position.latitude
        #         pt = "POINT(" + ptx + " " + pty + ")"
        #         ptgeom = QgsGeometry.fromWkt(pt)
        #
        #         if PluginHelper.isInGeometry(ptgeom, filtreLay):
        #             remsToKeep[key] = rems[key]
        #
        # else:
        #     remsToKeep = rems
        #
        # cnt = len(remsToKeep)
        #
        # try:
        #     i = 100
        #     try:
        #         self.context.conn = spatialite_connect(self.context.dbPath)
        #
        #         for remId in remsToKeep:
        #
        #             if remId == '618195' or remId == '618197':
        #                 debug = True
        #
        #             PluginHelper.insertRemarques(self.context.conn, remsToKeep[remId])
        #             i += 1
        #             if cnt > 0:
        #                 self.progressVal = int(round(i * 100 / cnt))
        #                 self.progress.setValue(self.progressVal)
        #
        #         self.context.conn.commit()
        #
        #     except Exception as e:
        #         self.logger.error(format(e))
        #         raise
        #     finally:
        #         self.context.conn.close()
        #
        #     if cnt > 1:
        #         remLayer = self.context.getLayerByName(PluginHelper.nom_Calque_Signalement)
        #         remLayer.updateExtents(True)
        #         box = remLayer.extent()
        #         self.setMapExtent(box)
        #
        #     elif filtreLay is not None:
        #         box = filtreLay.extent()
        #         self.setMapExtent(box)
        #
        #     # Résultat
        #     self.showImportResult(cnt)
        #
        #     # Modification du formulaire pour afficher l'attribut "Thèmes" sous forme de "Vue JSON"
        #     # Vue par défaut : Arborescence
        #     # Formater le JSON : Indenté
        #     self.setFormAttributes()
        #     self.progress.close()
        #
        # except Exception as e:
        #     raise
        #
        # finally:
        #     self.progress.close()

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
        source_crs = QgsCoordinateReferenceSystem(cst.EPSGCRS4326)

        mapCrs = self.__context.mapCan.mapSettings().destinationCrs().authid()
        dest_crs = QgsCoordinateReferenceSystem(mapCrs)

        transform = QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())
        new_box = transform.transformBoundingBox(box)

        # distance pour le buffer: 10% de la distance minimale (hauteur ou largeur)
        dist = min(new_box.width(), new_box.height()) * 0.1
        # zoom sur la couche Signalement
        self.__context.mapCan.setExtent(new_box.buffered(dist))

    def showImportResult(self, cnt):
        """Résultat de l'import

        :param cnt: le nombre de remarques importées
        :type cnt: int
        """
        submit = self.__context.countRemarqueByStatut(cst.STATUT.submit.__str__())
        pending = self.__context.countRemarqueByStatut(cst.STATUT.pending.__str__()) + \
                  self.__context.countRemarqueByStatut(cst.STATUT.pending0.__str__()) + \
                  self.__context.countRemarqueByStatut(cst.STATUT.pending1.__str__()) + \
                  self.__context.countRemarqueByStatut(cst.STATUT.pending2.__str__())
        reject = self.__context.countRemarqueByStatut(cst.STATUT.reject.__str__())
        valid = self.__context.countRemarqueByStatut(cst.STATUT.valid.__str__()) + self.__context.countRemarqueByStatut(
            cst.STATUT.valid0.__str__())

        resultMessage = "Extraction réussie avec succès de " + str(cnt) + " signalement(s) depuis le serveur \n" + \
                        "avec la répartition suivante : \n\n" + \
                        "- " + str(submit) + " signalement(s) nouveau(x).\n" + \
                        "- " + str(pending) + " signalement(s) en cours de traitement.\n" + \
                        "- " + str(valid) + " signalement(s)  validé(s).\n" + \
                        "- " + str(reject) + " signalement(s) rejeté(s).\n"

        PluginHelper.showMessageBox(resultMessage)
