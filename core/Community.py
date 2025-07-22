from . import Constantes as cst
from .Layer import Layer
from .Query import Query
from .Theme import Theme
from ..PluginHelper import PluginHelper


class Community(object):
    """Classe permettant de récupérer la description d'une communauté et de ses couches cartographiques."""

    def __init__(self, params) -> None:
        self.__name = ''
        self.__id = -1
        self.__userId = -1
        self.__emprises = []
        self.__theme = []
        self.__active = False
        self.__logo = ''
        self.__tokenType = params['tokentype']
        self.__tokenAccess = params['tokenaccess']
        self.__query = Query(params['url'], params['proxy'])

    def getDatas(self, data) -> None:
        """
        Remplit les attributs généraux pour une communauté (un groupe).

        :param data: les données liées à une communauté
        :type data: dict
        """
        if len(data) == 0:
            return
        if PluginHelper.keyExist('community_name', data):
            self.__name = data['community_name']
        if PluginHelper.keyExist('community_id', data):
            self.__id = data['community_id']
        if PluginHelper.keyExist('user_id', data):
            self.__userId = data['user_id']
        if PluginHelper.keyExist('emprises', data):
            self.__emprises = data['emprises']
        if PluginHelper.keyExist('profile', data):
            self.__getDataTheme(data['profile'])

    def __getDataTheme(self, datas) -> None:
        """
        Initialiser le thème d'une communauté en chargeant ses caractéristiques.

        :param datas: la liste des attributs d'une communauté, notamment le thème
        :type: list
        """
        if len(datas) == 0:
            return
        for data in datas:
            communityId = -1
            if PluginHelper.keyExist('community_id', data):
                communityId = data['community_id']
            if PluginHelper.keyExist('themes', data):
                for d in data['themes']:
                    theme = Theme(communityId)
                    theme.setTheme(d)
                    self.__theme.append(theme)

    def getName(self) -> str:
        return self.__name

    def getId(self) -> int:
        return self.__id

    def getEmprises(self) -> []:
        return self.__emprises

    def getTheme(self) -> []:
        return self.__theme

    def getLogo(self) -> str:
        return self.__logo

    def getProfil(self, datas) -> str:
        # TODO à compléter suivant réponse ligne 38 dans seeReport.py
        return 'utilisateur inconnu'

    # Récupère les couches associées à une communauté
    def extractLayers(self, communityId, page, limit) -> []:
        self.__query.setPage(page)
        self.__query.setLimit(limit)
        self.__query.setHeaders(self.__tokenType, self.__tokenAccess)
        self.__query.setPartOfUrl("gcms/api/communities/{}/layers".format(communityId))
        data = self.__query.multiple()
        if len(data) == 0:
            return
        layers = self.__getLayers(data)
        return layers

    # Récupère les infos d'une couche (table ou geoservice) et retourne une liste de toutes les couches
    def __getLayers(self, data) -> []:
        layers = []
        print(data)
        for d in data:
            layer = Layer()
            if PluginHelper.keyExist('visibility', d):
                layer.visibility = d['visibility']
            if PluginHelper.keyExist('opacity', d):
                layer.opacity = d['opacity']
            if PluginHelper.keyExist('type', d):
                layer.type = d['type']
            if PluginHelper.keyExist('role', d):
                layer.role = d['role']
            if PluginHelper.keyExist('id', d):
                layer.id = d['id']
            if PluginHelper.keyExist('database', d):
                layer.databaseid = d['database']
            if PluginHelper.keyExist('order', d):
                layer.order = d['order']
            if PluginHelper.keyExist('preferred_style', d):
                layer.preferred_style = d['preferred_style']
            if PluginHelper.keyExist('snapto', d):
                layer.snapto = d['snapto']
            if PluginHelper.keyExist('table', d):
                layer.tableid = d['table']
            if PluginHelper.keyExist('type', d):
                print("__getLayers type : {}".format(d['type']))
                if d['type'] == cst.FEATURE_TYPE:
                    self.__getDataLayerFromTable(layer)
                if d['type'] == cst.GEOSERVICE:
                    if PluginHelper.keyExist('geoservice', d):
                        self.__getDataLayerFromGeoservice(layer, d['geoservice'])
            layers.append(layer)
        return layers

    # Récupère les informations d'une table de la base de données correspondant à une couche cartographique
    def __getDataLayerFromTable(self, layer) -> None:
        self.__query.setHeaders(self.__tokenType, self.__tokenAccess)
        self.__query.setPartOfUrl("gcms/api/databases/{0}/tables/{1}".format(layer.databaseid, layer.tableid))
        response = self.__query.simple()
        if response is None:
            return
        data = response.json()
        self.__getDataFromTable(data, layer)

    def __getDataFromTable(self, data, layer) -> None:
        if PluginHelper.keyExist('name', data):
            layer.name = data['name']
            layer.tablename = data['name']
        if PluginHelper.keyExist('description', data):
            layer.description = data['description']
        if PluginHelper.keyExist('min_zoom_level', data):
            layer.minzoom = data['min_zoom_level']
        if PluginHelper.keyExist('max_zoom_level', data):
            layer.maxzoom = data['max_zoom_level']
        if PluginHelper.keyExist('database_versioning', data):
            if data['database_versioning'] is True:
                layer.isStandard = False
        if PluginHelper.keyExist('tile_zoom_level', data):
            layer.tileZoomLevel = data['tile_zoom_level']
        if PluginHelper.keyExist('read_only', data):
            layer.readOnly = data['read_only']
        if PluginHelper.keyExist('geometry_name', data):
            layer.geometryName = data['geometry_name']
        if PluginHelper.keyExist('database', data):
            layer.databasename = data['database']
        if PluginHelper.keyExist('wfs', data):
            layer.wfs = data['wfs']
        if PluginHelper.keyExist('wfs_transactions', data):
            layer.wfsTransaction = data['wfs_transactions']
        if PluginHelper.keyExist('style', data):
            layer.style = data['style']
        if PluginHelper.keyExist('id_name', data):
            layer.idName = data['id_name']
        if PluginHelper.keyExist('columns', data):
            layer.attributes = data['columns']
            for column in data['columns']:
                if PluginHelper.keyExist('name', column):
                    if column['name'] != layer.geometryName:
                        continue
                if PluginHelper.keyExist('is3d', column):
                    layer.is3d = column['is3d']
                if PluginHelper.keyExist('type', column):
                    layer.geometryType = column['type']
                if PluginHelper.keyExist('srid', column):
                    layer.srid = column['srid']

    def __getDataLayerFromGeoservice(self, layer, geoservice) -> None:
        """
        Lance une requête GET pour récupérer les informations liées à une couche geoservice.

        :param layer: une couche geoservice du projet QGIS
        :type layer: Layer
        """
        self.__query.setHeaders(self.__tokenType, self.__tokenAccess)
        self.__query.setPartOfUrl("gcms/api/geoservices/{}".format(geoservice['id']))
        response = self.__query.simple()
        if response is None:
            return
        data = response.json()
        self.__getDataFromGeoservice(data, layer)

    def __getDataFromGeoservice(self, data, layer) -> None:
        """
        Initialise la couche geoservice.

        :param data: les informations sur le geoservice
        :type data: dict

        :param layer: la couche geoservice dans QGIS
        :type layer: Layer
        """
        if PluginHelper.keyExist('title', data):
            layer.name = data['title']
        if PluginHelper.keyExist('url', data):
            layer.url = data['url']
        if PluginHelper.keyExist('layers', data):
            layer.layers = data['layers']
        layer.geoservice.update(data)
