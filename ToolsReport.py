import json
import os.path

from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsVectorLayer, QgsProject, \
    QgsEditorWidgetSetup

from .PluginHelper import PluginHelper
from .FormCreateReport import FormCreateReport
from .core.ProgressBar import ProgressBar
from .core.BBox import BBox
from .core.Box import Box
from .core.PluginLogger import PluginLogger
from .core.NoProfileException import NoProfileException
from .core.SQLiteManager import SQLiteManager
from .core.Query import Query
from .core.Report import Report
from .core.HttpRequest import HttpRequest
from .core import Constantes as cst

from requests_toolbelt import MultipartEncoder


# Importation des signalements dans le projet QGIS
class ToolsReport(object):

    def __init__(self, context) -> None:
        self.__logger = PluginLogger("ToolsReport").getPluginLogger()
        self.__context = context
        # barre de progression des signalements importés
        self.__progress = None
        self.__progressVal = 0
        self.__datasForRequest = {}
        self.__crsTransform = self.__setCoordinateTransform()

    def __addReportSketchLayersToTheCurrentMap(self) -> None:
        uri = self.__context.getUriDatabaseSqlite()
        self.__logger.debug(uri.uri())
        maplayers = self.__context.getAllMapLayers()
        root = QgsProject.instance().layerTreeRoot()
        for table in PluginHelper.reportSketchLayersName:
            if not PluginHelper.keyExist(table, maplayers):
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

    def getReport(self, idReport):
        query = Query(self.__context.urlHostEspaceCo, self.__context.proxies)
        query.setHeaders(self.__context.getTokenType(), self.__context.getTokenAccess())
        query.setPartOfUrl('gcms/api/reports/{}'.format(idReport))
        response = query.simple()
        return Report(self.__context.urlHostEspaceCo, response.json())

    def __getReports(self, date) -> []:
        # filtre spatial
        bbox = BBox(self.__context)
        box = bbox.getFromLayer(PluginHelper.load_CalqueFiltrage(self.__context.projectDir).text, True, True)
        # si la box est à None alors, l'utilisateur veut extraire France entière
        # si la box est égale 0.0 pour ces 4 coordonnées alors l'utilisateur
        # ne souhaite pas extraire les données France entière
        if box is not None and box.getXMax() == 0.0 and box.getYMax() == 0.0 \
                and box.getXMin() == 0.0 and box.getYMin() == 0.0:
            return
        query = Query(self.__context.urlHostEspaceCo, self.__context.proxies)
        query.setHeaders(self.__context.getTokenType(), self.__context.getTokenAccess())
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

        # Création des tables de signalements et de croquis
        self.__context.createTablesReportsAndSketchs()

        message = "Placement des signalements sur la carte"
        self.__progress = ProgressBar(200, message)

        # Création des couches dans QGIS et des liens vers la base SQLite
        self.__addReportSketchLayersToTheCurrentMap()

        # Téléchargement des signalements
        date = PluginHelper.load_ripartXmlTag(self.__context.projectDir, PluginHelper.xml_DateExtraction, "Map").text
        date = PluginHelper.formatDate(date)
        data = self.__getReports(date)

        # Insertion des signalements dans la base SQLite
        if data is None or len(data) == 0:
            self.__progress.close()
            return

        self.__insertReportsSketchsIntoSQLite(data)

        # Rafraichir la carte
        self.__context.refresh_layers()

        # Fermer la patience
        self.__progress.close()

        # Afficher les résultats
        self.__showImportResult()

    def __showImportResult(self) -> None:
        # Résultat de l'import
        totalSubmit = self.__context.countReportsByStatut(cst.STATUT.submit.__str__())
        pending = self.__context.countReportsByStatut(cst.STATUT.pending.__str__())
        pending0 = self.__context.countReportsByStatut(cst.STATUT.pending0.__str__())
        pending1 = self.__context.countReportsByStatut(cst.STATUT.pending1.__str__())
        pending2 = self.__context.countReportsByStatut(cst.STATUT.pending2.__str__())
        totalPending = pending + pending0 + pending1 + pending2
        reject = self.__context.countReportsByStatut(cst.STATUT.reject.__str__())
        reject0 = self.__context.countReportsByStatut(cst.STATUT.reject0.__str__())
        totalReject = reject + reject0
        valid = self.__context.countReportsByStatut(cst.STATUT.valid.__str__())
        valid0 = self.__context.countReportsByStatut(cst.STATUT.valid0.__str__())
        totalValid = valid + valid0
        autre = self.__context.countReportsByStatut(cst.STATUT.undefined.__str__())
        autre0 = self.__context.countReportsByStatut(cst.STATUT.test.__str__())
        totalAutre = autre + autre0

        resultMessage = "Extraction réussie avec succès de " + str(totalSubmit + totalPending + totalValid +
                                                                   totalReject + totalAutre) + \
                        " signalement(s) depuis le serveur avec la répartition suivante : \n\n" + \
                        "- " + str(totalSubmit) + " signalement(s) nouveau(x).\n" + \
                        "- " + str(totalPending) + " signalement(s) en cours de traitement.\n" + \
                        "- " + str(totalValid) + " signalement(s)  validé(s).\n" + \
                        "- " + str(totalReject) + " signalement(s) rejeté(s).\n" + \
                        "- " + str(totalAutre) + " signalement(s) autre(s)."

        PluginHelper.showMessageBox(resultMessage)

    # NOTE : non utilisée mais peut servir ;-)
    def setFormAttributes(self) -> None:
        listLayers = QgsProject.instance().mapLayersByName(cst.nom_Calque_Signalement)
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

    def __setCoordinateTransform(self) -> QgsCoordinateTransform:
        """
        Construit un QgsCoordinateTransform pour transformer le système de référence de coordonnées source
        en système de référence de coordonnées de destination.

        :return: un QgsCoordinateTransform
        """
        mapCrs = self.__context.mapCan.mapSettings().destinationCrs().authid()
        sridSource = QgsCoordinateReferenceSystem(mapCrs)
        crsSource = QgsCoordinateReferenceSystem(sridSource)

        sridTarget = QgsCoordinateReferenceSystem(cst.EPSGCRS4326)
        crsTarget = QgsCoordinateReferenceSystem(sridTarget)

        return QgsCoordinateTransform(crsSource, crsTarget, QgsProject.instance())

    # NOTE : non utilisée mais peut servir ;-)
    def setMapExtent(self, box) -> None:
        """ Set de l'étendue de la carte

        :param box : bounding box
        """
        source_crs = QgsCoordinateReferenceSystem(cst.EPSGCRS4326)

        mapCrs = self.__context.mapCan.mapSettings().destinationCrs().authid()
        dest_crs = QgsCoordinateReferenceSystem(mapCrs)
        if not dest_crs.isValid():
            return

        transform = QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())
        new_box = transform.transformBoundingBox(box)

        # distance pour le buffer : 10% de la distance minimale (hauteur ou largeur)
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
        parameters = {'name': cst.nom_Calque_Signalement, 'attributes': attributes, 'condition': condition}
        SQLiteManager.updateTable(parameters)

    # Ajoute une réponse à un signalement
    def addResponseToServer(self, parameters) -> None:
        idReport = parameters['reportId']
        uri = "{0}/gcms/api/reports/{1}/replies".format(self.__context.urlHostEspaceCo, idReport)
        response = HttpRequest.makeHttpRequest(uri, parameters['proxies'], data=parameters['requestBody'],
                                               headers=parameters['headers'], launchBy='addResponseToServer')
        # Succès : get (code 200) post (code 201)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        elif response.status_code == 403:
            PluginHelper.showMessageBox("Vous n'avez pas les droits pour modifier "
                                        "le signalement {}.".format(idReport))
            return None
        else:
            message = "code : {} raison : {}".format(response.status_code, response.reason)
            self.__context.iface.messageBar().pushMessage("Attention", message, level=1, duration=3)
            return

    def __sendReport(self, filesAttachments):
        self.__datasForRequest.update(filesAttachments)
        datas = MultipartEncoder(fields=self.__datasForRequest)
        responseFromServer = self.__sendRequest(datas)
        if responseFromServer is None:
            return
        return responseFromServer.json()

    def __sendRequest(self, datas):
        # envoi de la requête
        uri = '{0}/gcms/api/reports'.format(self.__context.urlHostEspaceCo)
        headers = {'Content-Type': datas.content_type, 'Authorization': '{} {}'.format(self.__context.getTokenType(),
                                                                                       self.__context.getTokenAccess())}
        response = HttpRequest.makeHttpRequest(uri, self.__context.proxies, datas, headers,
                                               launchBy='__sendRequest')
        if response.status_code == 200 or response.status_code == 201:
            return response
        else:
            message = "Code : {0}, Raison : {1}".format(response.status_code, response.reason)
            self.__context.iface.messageBar().pushMessage("Attention", message, level=1, duration=3)
        return None

    def createReport(self, sketchList, pointFromClipboard):
        # Ouverture du formulaire de création du signalement
        formCreate = FormCreateReport(self.__context, len(sketchList))
        formCreate.exec_()

        # Envoi ou pas vers l'espace collaboratif ?
        if not formCreate.bSend:
            return

        # TODO voir Noémie pour les thèmes préférés
        # PluginHelper.save_preferredThemes(self.__context.projectDir, selectedThemes)
        PluginHelper.save_preferredGroup(self.__context.projectDir, formCreate.preferredGroup)

        # Pour joindre un fichier à un signalement avec Request HTTP library,
        # une partie des données doit être de type dictionnaire l'autre transformée en json (sketch et attributes)
        # comme l'exemple ci-dessous. Cela fonctionne aussi pour la simple création d'un signalement.
        """
        {
            'community': 375,
            'comment': 'Test QGIS avec la nouvelle API',
            'input_device': 'SIG-QGIS',
            'attributes': '{"community": 1, "theme": "Route", "attributes": {}}',
            'sketch': '{"name": "", "objects": [{"type": "Ligne", "geometry": "LINESTRING(2.4383950982381015
                        48.85775256550695, 2.4378823444106827 48.85735617006071, 2.4375939203827577 
                        48.8572549622097)", '"attributes": {}}]}',
            'geometry': 'POINT(2.437957121010514 48.85745456592579)'
        }
        """
        self.__datasForRequest.clear()
        # Si l'utilisateur a choisi un thème n'appartenant pas à sa community
        communityId = formCreate.getCommunityIdWhenThemeChanged()
        if communityId is None:
            communityId = self.__context.getUserCommunity().getId()
        self.__datasForRequest = {
            'community': str(communityId),  # champ obligatoire
            'comment': formCreate.getComment(),
            'input_device': cst.CLIENT_INPUT_DEVICE
        }

        # Le thème sélectionné et ses attributs
        themeWithAttributes = formCreate.getUserSelectedThemeWithAttributes()
        if len(themeWithAttributes) == 0:
            message = "Impossible de créer un signalement sans thème. Veuillez en sélectionner un."
            QMessageBox.information(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)
            return
        self.__datasForRequest['attributes'] = json.dumps(themeWithAttributes)

        # Récupération du (ou des) fichier(s) joint(s) (max 4) au signalement
        filesAttachments = formCreate.getFilesAttachments()

        # Création du ou des signalements
        if len(sketchList) == 0 and pointFromClipboard != '':
            tmpPoint = self.__crsTransform.transform(pointFromClipboard)
            geometrySingleReport = 'POINT({0} {1})'.format(tmpPoint.x(), tmpPoint.y())
            self.__datasForRequest['geometry'] = geometrySingleReport
            contents = self.createSingleReportFromClipboard()
        elif formCreate.isSingleReport():
            contents = self.__createSingleReport(sketchList, filesAttachments)
        else:
            if len(sketchList) == 1:
                raise Exception("ToolsReport.__createMultiReports : attention, il fallait cocher la case [Créer un signalement unique].")
            contents = self.__createMultiReports(sketchList, filesAttachments)

        if contents is None:
            raise Exception("ToolsReport.createSingleReport : erreur dans la création d'un signalement")

        # Insertion des signalements et des croquis dans la base SQLite
        listNewReportIds = self.__insertReportsSketchsIntoSQLite(contents)

        # Message de fin
        self.__sendMessageEndProcess(listNewReportIds)

    def createSingleReportFromClipboard(self) -> []:
        contents = []
        filesAttachments = {}
        contents.append(self.__sendReport(filesAttachments))
        return contents

    def __createSingleReport(self, sketchList, filesAttachments) -> []:
        contents = []
        sketchsDatasGeometryReport = self.__createReportWithSketchs(sketchList, True)
        self.__datasForRequest['sketch'] = json.dumps(sketchsDatasGeometryReport[0]['sketch'])
        self.__datasForRequest['geometry'] = sketchsDatasGeometryReport[0]['geometryReport']  # obligatoire
        contents.append(self.__sendReport(filesAttachments))
        return contents

    def __createMultiReports(self, sketchList, filesAttachments) -> []:
        contents = []
        sketchsDatasGeometryReport = self.__createReportWithSketchs(sketchList, False)
        for sketchDataGeometryReport in sketchsDatasGeometryReport:
            self.__datasForRequest['sketch'] = json.dumps(sketchDataGeometryReport['sketch'])
            self.__datasForRequest['geometry'] = sketchDataGeometryReport['geometryReport']
            contents.append(self.__sendReport(filesAttachments))
        return contents

    def __getBarycentreInWkt(self, listPoints):
        """
        Retourne les coordonnées du signalement en WKT en calculant le barycentre en fonction
        d'une liste de points représentant la géométrie du croquis

        :param listPoints : la géométrie sous forme d'une liste de points du croquis
        :type listPoints : list

        :return : le barycentre
        :rtype : Point
        """
        barycentreX = 0
        barycentreY = 0
        if len(listPoints) == 0:
            raise Exception("Impossible de créer un signalement sans coordonnées, veuillez recommencer.")
        for pt in listPoints:
            barycentreX += pt.longitude
            barycentreY += pt.latitude
        ptX = barycentreX / len(listPoints)
        ptY = barycentreY / len(listPoints)
        barycentre = 'POINT({0} {1})'.format(ptX, ptY)
        return barycentre

    def __createReportWithSketchs(self, sketchList, bOneReport) -> []:
        datas = []
        if bOneReport:
            points = []
            sketch = {
                'name': '',
                'objects': []
            }
            for sk in sketchList:
                points.extend(sk.getAllPoints())
                obj = {'type': sk.getTypeEnumInStr(sk.type), 'geometry': sk.getCoordinatesFromPointsToPost(),
                       'attributes': sk.getAttributes()}
                sketch['objects'].append(obj)
            datas.append({'sketch': sketch, 'geometryReport': self.__getBarycentreInWkt(points)})
        else:
            for sk in sketchList:
                sketch = {
                    'name': '',
                    'objects': []
                }
                obj = {'type': sk.getTypeEnumInStr(sk.type), 'geometry': sk.getCoordinatesFromPointsToPost(),
                       'attributes': sk.getAttributes()}
                sketch['objects'].append(obj)
                datas.append({'sketch': sketch, 'geometryReport': self.__getBarycentreInWkt(sk.getAllPoints())})
        return datas

    def __calculateRows(self, datas):
        report = Report(self.__context.urlHostEspaceCo, datas)
        report.InsertSketchIntoSQLite()
        columns = report.getDatasForSQlite()
        return columns, report.getId()

    def __insertReportsSketchsIntoSQLite(self, datas) -> []:
        parameters = {'tableName': cst.nom_Calque_Signalement, 'geometryName': 'geom', 'sridTarget': cst.EPSGCRS4326,
                      'sridSource': cst.EPSGCRS4326, 'isStandard': False, 'is3D': False, 'geometryType': 'POINT'}
        attributesRows = []
        idsReports = []
        if type(datas) is list:
            for data in datas:
                rows = self.__calculateRows(data)
                attributesRows.append(rows[0])
                idsReports.append(rows[1])
        if type(datas) is dict:
            rows = self.__calculateRows(datas)
            attributesRows.append(rows[0])
            idsReports.append(rows[1])
        # Insertion des signalements dans la base SQLite
        sqliteManager = SQLiteManager()
        sqliteManager.insertRowsInTable(parameters, attributesRows)
        return idsReports

    def __sendMessageEndProcess(self, listNewReportIds):
        message = "Succès, création "
        if len(listNewReportIds) == 1:
            message += "d'un nouveau signalement : {0}".format(listNewReportIds[0])
        else:
            listIds = ''
            for idReport in listNewReportIds:
                listIds += "{}, ".format(idReport)
            message += "de plusieurs signalements : {0}".format(listIds[:-2])
        QMessageBox.information(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)
