# -*- coding: utf-8 -*-
"""Accès aux statistiques d'une base via l'API réseau QGIS.

Utilise QgsNetworkAccessManager de façon asynchrone : le proxy et la vérification
SSL suivent la configuration QGIS, sans passer par la bibliothèque ``requests``.
"""
import json

from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import QUrl, QUrlQuery
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from .PluginLogger import PluginLogger


class StatisticsResult(object):
    """Résultat d'un appel à la route statistiques."""

    def __init__(self, ok: bool, status_code=None, payload=None, error=None) -> None:
        self.ok = ok
        self.status_code = status_code
        self.payload = payload
        self.error = error or u""


class StatisticsService(object):
    """Interroge /gcms/api/databases/{id}/statistics via l'API réseau QGIS."""

    def __init__(self, context) -> None:
        self.__context = context
        self.__logger = PluginLogger("StatisticsService").getPluginLogger()

    def requestStatistics(self, databaseid, params=None) -> QNetworkReply:
        """Lance une requête asynchrone pour récupérer les statistiques.

        :param databaseid: identifiant de la base
        :param params: filtres optionnels (startDate, endDate, user_id)
        :return: la réponse réseau, à traiter lorsque son signal ``finished`` est émis
        """
        url = QUrl("{}/gcms/api/databases/{}/statistics".format(
            self.__context.urlHostEspaceCo, databaseid))
        if params:
            query = QUrlQuery()
            for key, value in params.items():
                query.addQueryItem(key, str(value))
            url.setQuery(query)

        request = QNetworkRequest(url)
        auth = '{} {}'.format(
            self.__context.getTokenType(), self.__context.getTokenAccess()).encode('utf-8')
        request.setRawHeader(b'Authorization', auth)

        return QgsNetworkAccessManager.instance().get(request)

    def parseStatisticsReply(self, reply: QNetworkReply) -> StatisticsResult:
        """Convertit une réponse réseau terminée en résultat exploitable."""
        status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        content = bytes(reply.readAll()).decode('utf-8', errors='replace')

        if reply.error() != QNetworkReply.NetworkError.NoError:
            message = reply.errorString() or content[:300]
            self.__logger.error("StatisticsService.parseStatisticsReply : {}".format(message))
            return StatisticsResult(False, status_code=status, error=message)

        try:
            payload = json.loads(content) if content else {}
        except ValueError as e:
            self.__logger.error("StatisticsService.parseStatisticsReply JSON : {}".format(e))
            return StatisticsResult(
                False, status_code=status,
                error=u"Réponse non JSON : {}".format(content[:300]))

        return StatisticsResult(True, status_code=status or 200, payload=payload)
