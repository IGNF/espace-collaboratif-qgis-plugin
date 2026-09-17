# -*- coding: utf-8 -*-
"""Accès aux statistiques d'une base via l'API réseau QGIS.

Utilise QgsBlockingNetworkRequest : le proxy et la vérification SSL sont gérés
automatiquement par QgsNetworkAccessManager (configuration QGIS), sans passer
par la bibliothèque ``requests``.
"""
import json

from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QUrl, QUrlQuery
from qgis.PyQt.QtNetwork import QNetworkRequest

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

    def getStatistics(self, databaseid, params=None) -> StatisticsResult:
        """Récupère les statistiques d'une base.

        :param databaseid: identifiant de la base
        :param params: filtres optionnels (startDate, endDate, user_id)
        :return: un :class:`StatisticsResult`
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

        blocking = QgsBlockingNetworkRequest()
        error = blocking.get(request, forceRefresh=True)
        reply = blocking.reply()
        status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        content = bytes(reply.content()).decode('utf-8', errors='replace')

        if error != QgsBlockingNetworkRequest.NoError:
            message = blocking.errorMessage() or content[:300]
            self.__logger.error("StatisticsService.getStatistics : {}".format(message))
            return StatisticsResult(False, status_code=status, error=message)

        try:
            payload = json.loads(content) if content else {}
        except ValueError as e:
            self.__logger.error("StatisticsService.getStatistics JSON : {}".format(e))
            return StatisticsResult(
                False, status_code=status,
                error=u"Réponse non JSON : {}".format(content[:300]))

        return StatisticsResult(True, status_code=status or 200, payload=payload)
