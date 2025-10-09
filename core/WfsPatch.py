import json
from PyQt5.QtWidgets import QMessageBox
from .HttpRequest import HttpRequest
from .SQLiteManager import SQLiteManager
from .PluginLogger import PluginLogger
from .ProgressBar import ProgressBar
from . import Constantes as cst


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
        self.__logger = PluginLogger("WfsPatch").getPluginLogger()

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
                self.__logger.info(message)
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
        """
        Fixe la géométrie du signalement déplacé
        """
        self.__datas['geometry'] = self.__geometryReportModified.replace('Point', 'POINT')

    def __setInputDevice(self):
        """
        Indique d'où vient la modification, ici QGIS
        """
        self.__datas['input_device'] = cst.CLIENT_INPUT_DEVICE

    def __updateReportIntoSQLite(self, jsonResponse) -> None:
        """
        Mise à jour de la base SQLite du projet de l'utilisateur

        :param jsonResponse: la réponse du serveur après la requête vers le serveur
        :type: dict
        """
        attributes = "geom = '{}', Date_MAJ = '{}'".format(jsonResponse['geometry'], jsonResponse['updating_date'])
        condition = "NoSignalement = {}".format(jsonResponse['id'])
        parameters = {'name': cst.nom_Calque_Signalement, 'attributes': attributes, 'condition': condition}
        SQLiteManager.updateTable(parameters)
        SQLiteManager.vacuumDatabase()

    def gcmsPatch(self):
        """

        """
        progress = ProgressBar(1, "Enregistrement du déplacement du signalement")
        try:
            self.__setReportIdAndGeometry()
            self.__setUrl()
            self.__setHeaders()
            self.__setCommunity()
            self.__setGeometry()
            self.__setInputDevice()

            # Vérification de l'URL
            if self.__url is None:
                message = ("WfsPatch.gcmsPatch : impossible d'envoyer la mise à jour du signalement vers le serveur "
                           "car l'URL de la requête n'est pas remplie.")
                QMessageBox.critical(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)
                self.__logger.critical(message)
                progress.close()
                return

            # Sérialisation des données
            try:
                data = json.dumps(self.__datas)
            except (TypeError, ValueError) as e:
                message = f"WfsPatch.gcmsPatch : erreur lors de la sérialisation des données : {str(e)}"
                QMessageBox.critical(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)
                self.__logger.critical(message)
                progress.close()
                return

            # Envoi de la requête HTTP
            try:
                response = HttpRequest.makeHttpRequest(self.__url, headers=self.__headers,
                                                       proxies=self.__proxies, data=data, launchBy='gcmsPatch')
            except Exception as e:
                message = f"WfsPatch.gcmsPatch : erreur réseau lors de l'envoi de la requête : {str(e)}"
                QMessageBox.critical(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)
                self.__logger.critical(message)
                progress.close()
                return

            # Vérification du code de réponse
            if response.status_code != 200:
                message = f"WfsPatch.gcmsPatch.HttpRequest.makeHttpRequest, " \
                          f"la requête a renvoyé un code d'erreur : [{response.reason}]"
                self.__logger.exception(message)
                progress.close()
                raise Exception(message)

            # Traitement du JSON retourné
            try:
                json_data = response.json()
            except ValueError:
                message = f"WfsPatch.gcmsPatch : réponse du serveur invalide, JSON non parsable"
                QMessageBox.critical(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)
                self.__logger.critical(message)
                progress.close()
                return

            # Mise à jour de la base locale
            progress.setValue(1)
            self.__updateReportIntoSQLite(json_data)
            self.__layer.reload()
            self.__layer.triggerRepaint()
            progress.close()

            # Message de fin
            message = "Le signalement a été déplacé."
            QMessageBox.information(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)

        except Exception as e:
            message = f"WfsPatch.gcmsPatch : une erreur inattendue est survenue : {str(e)}"
            QMessageBox.critical(self.__context.iface.mainWindow(), cst.IGNESPACECO, message)
            self.__logger.critical(message)
            progress.close()
