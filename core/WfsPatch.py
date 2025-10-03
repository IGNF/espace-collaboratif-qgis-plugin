import json
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsWkbTypes
from .HttpRequest import HttpRequest
from .SQLiteManager import SQLiteManager
from . import Constantes as cst
from .Wkt import Wkt


class WfsPatch(object):
    """
    Classe implémentant une requête en HTTP PATCH pour une couche WFS.
    """

    def __init__(self, context, layer) -> None:
        """
        Constructeur.

        :param context: le contexte du client QGIS

        :param layer: la couche QGIS en édition
        :type layer: QgsMapLayer
        """
        self.__context = context
        self.__layer = layer
        self.__proxies = context.getProxies()
        self.__headers = {}
        self.__url = None
        self.__datas = {}
        self.__geometryReportModified = None
        self.__reportId = None
        self.__originalFeatureId = None
        self.__editBuffer = None

    def __setReportIdAndGeometry(self) -> None:
        """
        Remplie l'identifiant espace collaboratif du signalement ainsi que sa nouvelle géométrie.
        Vide en mémoire le buffer de QGIS.
        """
        self.__editBuffer = self.__layer.editBuffer()
        changedGeometries = self.__editBuffer.changedGeometries()
        if len(changedGeometries) != 1:
            return
        for fId, newGeom in changedGeometries.items():
            self.__originalFeatureId = fId
            # Récupérer le signalement d'origine
            originalFeature = self.__layer.getFeature(fId)
            statusReport = originalFeature['Statut']
            if statusReport not in cst.openStatut:
                message = "WfsPatch.gcmsPatch : impossible d'envoyer la mise à jour du signalement vers le serveur" \
                          " car son statut n'est pas valide. " \
                          "Il est clôturé depuis le {}.".format(originalFeature['Date_validation'])
                QMessageBox.information(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)
                self.__editBuffer.rollBack()
                return
            self.__reportId = originalFeature['NoSignalement']
            self.__geometryReportModified = newGeom.asWkt()

    def __setUrl(self) -> None:
        """
        Remplie l'url générale permettant de constituer la requête finale HTTP PATCH d'envoi de la mise à jour partielle
        du signalement.
        """
        if self.__reportId is None:
            return
        self.__url = "{0}/gcms/api/reports/{1}".format(self.__context.urlHostEspaceCo, self.__reportId)

    def __setHeaders(self) -> None:
        """
        Fixe l'entête d'autorisation avec les tokens d'authentification pour une connexion sécurisée
        à l'espace collaboratif.
        """
        self.__headers['Authorization'] = '{} {}'.format(self.__context.getTokenType(), self.__context.getTokenAccess())

    def __setCommunity(self) -> None:
        """
        Fixe l'identifiant du groupe pour la variable __params passée à une requête multiple.
        """
        self.__datas['community'] = self.__context.getUserCommunity().getId()

    def __setGeometry(self) -> None:
    #     parameters = {'geometryName': 'geometry', 'sridSource': cst.EPSGCRS4326,
    #                   'sridTarget': QgsProject.instance().crs().postgisSrid(),
    #                   'geometryType': QgsWkbTypes.displayString(self.__layer.wkbType())}
    #     wkt = Wkt(parameters)
    #     if self.__geometryReportModified is None:
    #         message = "WfsPatch.gcmsPatch : impossible d'envoyer la mise à jour du signalement vers le serveur car " \
    #                   "sa nouvelle géométrie n'a pas pu être récupérée."
    #         QMessageBox.information(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)
    #         return
        self.__datas['geometry'] = self.__geometryReportModified.replace('Point', 'POINT')

    def __setInputDevice(self):
        """
        Indique d'où vient la modification, ici QGIS
        """
        self.__datas['input_device'] = cst.CLIENT_INPUT_DEVICE

    def __updateReportIntoSQLite(self, jsonResponse):
        parameters = {'geometryName': 'geom', 'sridSource': cst.EPSGCRS4326,
                      'sridTarget': QgsProject.instance().crs().postgisSrid(),
                      'geometryType': QgsWkbTypes.displayString(self.__layer.wkbType())}
        wkt = Wkt(parameters)
        geomToSqlite = wkt.toGetGeometry(jsonResponse['geometry'])
        attributes = "geom = {} Date_MAJ = '{}'".format(geomToSqlite, jsonResponse['updating_date'])
        condition = "NoSignalement = {}".format(jsonResponse['id'])
        parameters = {'name': cst.nom_Calque_Signalement, 'attributes': attributes, 'condition': condition}
        SQLiteManager.updateTable(parameters)

    def gcmsPatch(self):
        self.__setReportIdAndGeometry()
        self.__setUrl()
        self.__setHeaders()
        self.__setCommunity()
        self.__setGeometry()
        self.__setInputDevice()
        # Si le principal paramètre de la requête n'est pas rempli, il faut sortir
        if self.__url is None:
            message = "WfsPatch.gcmsPatch : impossible d'envoyer la mise à jour du signalement vers le serveur car " \
                      "l'url de la requête n'est pas remplie."
            QMessageBox.critical(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)
            return
        data = json.dumps(self.__datas)
        response = HttpRequest.makeHttpRequest(self.__url, headers=self.__headers, proxies=self.__proxies,
                                               data=data, launchBy='gcmsPatch')
        # Si tout s'est bien passé, il faut mettre à jour la base SQLite
        if response.status_code != 200:
            message = "WfsPatch.gcmsPatch:makeHttpRequest, la requête a renvoyé " \
                      "un code d'erreur : [{}]".format(response.reason)
            raise Exception(message)
        # self.__updateReportIntoSQLite(response.json())
        self.__layer.commitChanges()
        self.__layer.triggerRepaint()
        self.__editBuffer.rollBack()
