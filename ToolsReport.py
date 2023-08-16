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
from .core.Report import Report
from .core.HttpRequest import HttpRequest
from .core import Constantes as cst


# Importation des signalements dans le projet QGIS
class ToolsReport(object):

    def __init__(self, context) -> None:
        self.__logger = RipartLogger("ToolsReport").getRipartLogger()
        self.__context = context
        # barre de progression des signalements importés
        self.__progress = None
        self.__progressVal = 0

    def addReportSketchLayersToTheCurrentMap(self) -> None:
        uri = self.__context.getUriDatabaseSqlite()
        self.__logger.debug(uri.uri())
        maplayers = self.__context.getAllMapLayers()
        root = QgsProject.instance().layerTreeRoot()
        for table in PluginHelper.reportSketchLayersName:
            if table not in maplayers:
                uri.setDataSource('', table, 'geom')
                uri.setSrid(str(cst.EPSGCRS4326))
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                vlayer.setCrs(
                    QgsCoordinateReferenceSystem(cst.EPSGCRS4326, QgsCoordinateReferenceSystem.CrsType.EpsgCrsId))
                QgsProject.instance().addMapLayer(vlayer, False)
                root.insertLayer(0, vlayer)
                self.__logger.debug("Layer " + vlayer.name() + " added to map")
                # ajoute les styles aux couches
                style = os.path.join(self.__context.projectDir, "espacecoStyles", table + ".qml")
                vlayer.loadNamedStyle(style)
        self.__context.mapCan.refresh()

    def insertReportsIntoSQLite(self, datas) -> None:
        parameters = {'tableName': 'Signalement', 'geometryName': 'geom', 'sridTarget': cst.EPSGCRS4326,
                      'sridSource': cst.EPSGCRS4326, 'isStandard': False, 'is3D': False, 'geometryType': 'POINT'}
        attributesRows = []
        for data in datas:
            report = Report(self.__context.urlHostEspaceCo, data)
            columns = report.getColumnsForSQlite()
            attributesRows.append(columns)
        sqliteManager = SQLiteManager()
        sqliteManager.insertRowsInTable(parameters, attributesRows)

    def getReport(self, id):
        query = Query(self.__context.urlHostEspaceCo, self.__context.auth['login'], self.__context.auth['password'],
                      self.__context.proxy)
        query.setPartOfUrl('gcms/api/reports/{}'.format(id))
        response = query.simple()
        return Report(self.__context.urlHostEspaceCo, response.json())

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
    def download(self) -> None:
        self.__logger.debug("ToolsReport.download")

        # l'utilisateur n'a pas de profil actif, impossible pour lui de travailler
        if self.__context.getUserCommunity() is None or self.__context.getActiveCommunityName() == '':
            raise NoProfileException(
                "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

        message = "Placement des signalements sur la carte"
        self.progress = ProgressBar(200, message)

        # Création des couches dans QGIS et des liens vers la base SQLite
        self.addReportSketchLayersToTheCurrentMap()

        # Vider les tables signalement et croquis
        SQLiteManager.setEmptyTablesReportsAndSketchs(PluginHelper.reportSketchLayersName)

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

    def showImportResult(self, cnt) -> None:
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

    # NOTE : non utilisée mais peut servir ;-)
    def setFormAttributes(self) -> None:
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

    # NOTE : non utilisée mais peut servir ;-)
    def setMapExtent(self, box) -> None:
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

    def updateReportIntoSQLite(self, jsonResponse) -> None:
        # TODO "ancien code" remis au gout du jour
        # attributes = "Date_MAJ = '{}', Date_validation = '{}', Réponses = '{}', Statut ='{}'".format(
        #     jsonResponse['updating_date'], jsonResponse['closing_date'], jsonResponse['replies']['content'],
        #     jsonResponse['status'])
        # TODO nouveau code avec la réponse de la nouvelle API ticket redmine #18070
        #   {'report_id': 162920, 'id': 103797, 'author': {'id': 676, 'username': 'epeyrouse',
        #   'email': 'eric.peyrouse@ign.fr'}, 'title': None, 'content': 'Nouvelle réponse pour le signalement',
        #   'status': 'valid', 'date': '2023-08-16T15:54:30+02:00'}
        #  Noémie -> je suppose que la date retournée est la date de maj et non de validation
        content = jsonResponse['content']
        if type(content) == str:
            content = content.replace("'", "''")
        attributes = "Date_MAJ = '{}', Réponses = '{}', Statut ='{}'".format(jsonResponse['date'],
                                                                             content,
                                                                             jsonResponse['status'])
        condition = "NoSignalement = {}".format(jsonResponse['report_id'])
        parameters = {'name': PluginHelper.nom_Calque_Signalement, 'attributes': attributes, 'condition': condition}
        SQLiteManager.updateTable(parameters)

    # Ajoute une réponse à un signalement
    def addResponseToServer(self, parameters) -> None:
        idReport = parameters['reportId']
        uri = "{0}/gcms/api/reports/{1}/replies".format(self.__context.urlHostEspaceCo, idReport)
        response = HttpRequest.makeHttpRequest(uri, parameters['authentification'], parameters['proxy'],
                                               data=parameters['requestBody'])
        # Succès : get (code 200) post (code 201)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        elif response.status_code == 403:
            PluginHelper.showMessageBox("Vous n'avez pas les droits pour modifier "
                                        "le signalement {}.".format(idReport))
            return None
        else:
            message = "code : {} raison : {}".format(response.status_code, response.reason)
            raise Exception("ToolsReport.addResponse -> ".format(message))
