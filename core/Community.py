from . import Constantes as cst
from .Layer import Layer
from .Query import Query
from .Theme import Theme
from ..PluginHelper import PluginHelper


class Community(object):
    """
    Classe permettant de récupérer la description d'un groupe (communauté) et de ses couches cartographiques.
    """

    def __init__(self, params) -> None:
        """
        Constructeur.

        :param params: les paramètres généraux pour lancer une requête HTTP GET sur une communauté (groupe)
        :type params: dict
        """
        self.__name = ''
        self.__id = -1
        self.__userId = -1
        self.__emprises = []
        self.__theme = []
        self.__active = False
        self.__logo = ''
        self.__tokenType = params['tokentype']
        self.__tokenAccess = params['tokenaccess']
        self.__query = Query(params['url'], params['proxies'])

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
        """
        :return: le nom du groupe
        """
        return self.__name

    def getId(self) -> int:
        """
        :return: l'identifiant du groupe
        """
        return self.__id

    def getEmprises(self) -> []:
        """
        L'emprise serveur est la partie du territoire sur laquelle l'utilisateur a les droits d'écriture.
        Cette emprise peut-être FR : la métropole, 38185 : insee de commune ou une autre désignation.

        :return: l'emprise serveur du groupe, variable égale à 0 pour l'immédiat.
        """
        return self.__emprises

    def getTheme(self) -> []:
        """
        :return: le thème d'un signalement
        """
        return self.__theme

    def getLogo(self) -> str:
        """
        :return: le logo du groupe
        """
        return self.__logo

    def extractLayers(self, communityId, page, limit) -> []:
        """
        À partir d'un identifiant de groupe, extrait par une requête HTTP GET, les couches appartenant à ce groupe.

        :param communityId: l'identifiant d'un groupe
        :type communityId: int

        :param page: numéro initial de page
        :type page: int

        :param limit: nombre d'objets par page
        :type limit: int

        :return: la liste des couches appartenant au groupe de l'utilisateur
        """
        self.__query.setPage(page)
        self.__query.setLimit(limit)
        self.__query.setHeaders(self.__tokenType, self.__tokenAccess)
        self.__query.setPartOfUrl("gcms/api/communities/{}/layers".format(communityId))
        data = self.__query.multiple()
        if len(data) == 0:
            return
        layers = self.__getLayers(data)
        return layers

    def __getLayers(self, data) -> []:
        """
        Récupère les infos générales (symbologie par exemple) et spécifiques WFS : __getDataLayerFromTable et WMS :
        __getDataLayerFromGeoservice pour l'ensemble des couches d'un groupe.

        :param data: les données d'une couche
        :type data: dict

        :return: la liste des couches disponibles pour un groupe
        """
        layers = []
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
                if d['type'] == cst.FEATURE_TYPE:
                    self.__getDataLayerFromTable(layer)
                if d['type'] == cst.GEOSERVICE:
                    if PluginHelper.keyExist('geoservice', d):
                        self.__getDataLayerFromGeoservice(layer, d['geoservice'])
            layers.append(layer)
        return layers

    def __getDataLayerFromTable(self, layer) -> None:
        """
        Récupère les informations d'une table de la base de données correspondant à une couche cartographique (WFS)
        par une requête HTTP GET.

        :param layer: couche avec les infos permettant la recherche de ses informations spécifiques
        :type layer: Layer
        """
        self.__query.setHeaders(self.__tokenType, self.__tokenAccess)
        self.__query.setPartOfUrl("gcms/api/databases/{0}/tables/{1}".format(layer.databaseid, layer.tableid))
        response = self.__query.simple()
        if response is None:
            return
        data = response.json()
        self.__getDataFromTable(data, layer)

    def __getDataFromTable(self, data, layer) -> None:
        """
        Initialisation des caractéristiques d'une couche (layer) avec les données en entrée (data).

        :param data: les données retournées par la fonction __getDataLayerFromTable
        :type: dict

        :param layer: la couche cartographique (WFS) dans QGIS
        :type layer: Layer
        """
        if PluginHelper.keyExist('name', data):
            layer.setName(data['name'])
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
        Lance une requête GET pour récupérer les informations liées à une couche geoservice (WMS).

        :param layer: une couche geoservice du projet QGIS
        :type layer: Layer

        :param geoservice: le numéro du geoservice
        :type geoservice:dict
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
        Initialise des caractéristiques d'une couche geoservice (WMS).

        :param data: les informations sur le geoservice
        :type data: dict

        :param layer: la couche geoservice dans QGIS
        :type layer: Layer
        """
        if PluginHelper.keyExist('title', data):
            layer.setName(data['title'])
        if PluginHelper.keyExist('url', data):
            layer.url = data['url']
        if PluginHelper.keyExist('layers', data):
            layer.layers = data['layers']
        layer.geoservice.update(data)
