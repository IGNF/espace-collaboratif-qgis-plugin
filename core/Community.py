from . import Constantes as cst
from .Layer import Layer
from .Query import Query
from .Theme import Theme


# Classe permettant de récupérer la description d'une communauté, d'une couche cartographique
class Community(object):

    def __init__(self, params) -> None:
        self.__name = ''
        self.__id = -1
        self.__userId = -1
        self.__emprises = []
        # self.__role = ''
        self.__theme = []
        self.__active = False
        self.__logo = ''
        # self.__description = ''
        # self.__date = None
        # self.__query = Query(params['url'], params['login'], params['pwd'], params['proxy'])
        self.__tokenType = params['tokentype']
        self.__tokenAccess = params['tokenaccess']
        self.__query = Query(params['url'], params['proxy'])

    def getDatas(self, data) -> None:
        if len(data) == 0:
            return
        if self.__keyExist('community_name', data):
            self.__name = data['community_name']
        if self.__keyExist('community_id', data):
            self.__id = data['community_id']
        if self.__keyExist('user_id', data):
            self.__userId = data['user_id']
        if self.__keyExist('emprises', data):
            self.__emprises = data['emprises']
        if self.__keyExist('profile', data):
            self.__getDataTheme(data['profile'])

    def __getDataTheme(self, datas) -> None:
        if len(datas) == 0:
            return
        for data in datas:
            communityId = -1
            if self.__keyExist('community_id', data):
                communityId = data['community_id']
            if self.__keyExist('themes', data):
                for d in data['themes']:
                    theme = Theme(communityId)
                    theme.setTheme(d)
                    self.__theme.append(theme)

    def getName(self) -> str:
        return self.__name

    def getId(self) -> int:
        return self.__id

    def getUserId(self) -> int:
        return self.__userId

    def getEmprises(self) -> []:
        return self.__emprises

    def getTheme(self) -> []:
        return self.__theme

    def getActive(self) -> bool:
        return self.__active

    def getLogo(self) -> str:
        return self.__logo

    def __keyExist(self, key, data) -> bool:
        if key in data:
            return True
        return False

    def getProfil(self, datas):
        # TODO à compléter suivant réponse ligne 38 dans seeReport.py
        return 'utilisateur inconnu'

    # Récupère les informations d'une communauté
    def getUserProfil(self, community_id) -> None:
        self.__query.setHeaders(self.__tokenType, self.__tokenAccess)
        self.__query.setPartOfUrl("gcms/api/communities/{}".format(community_id))
        response = self.__query.simple()
        if response is None:
            return
        data = response.json()
        self.getProfil(data)

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
        for d in data:
            layer = Layer()
            if self.__keyExist('visibility', d):
                layer.visibility = d['visibility']
            if self.__keyExist('opacity', d):
                layer.opacity = d['opacity']
            if self.__keyExist('type', d):
                layer.type = d['type']
            if self.__keyExist('role', d):
                layer.role = d['role']
            if self.__keyExist('id', d):
                layer.id = d['id']
            if self.__keyExist('database', d):
                layer.databaseid = d['database']
            if self.__keyExist('order', d):
                layer.order = d['order']
            if self.__keyExist('preferred_style', d):
                layer.preferred_style = d['preferred_style']
            if self.__keyExist('snapto', d):
                layer.snapto = d['snapto']
            if self.__keyExist('table', d):
                layer.tableid = d['table']
            if self.__keyExist('type', d):
                if d['type'] == cst.WFS:
                    self.__getDataLayerFromTable(layer)
                if d['type'] == cst.WMTS:
                    if self.__keyExist('geoservice', d):
                        self.__getDataLayerFromGeoservice(layer, d['geoservice'])
            layers.append(layer)
        return layers

    # Récupère les informations d'une table de la base de données correspondant à une couche cartographique
    def __getDataLayerFromTable(self, layer):
        self.__query.setHeaders(self.__tokenType, self.__tokenAccess)
        self.__query.setPartOfUrl("gcms/api/databases/{0}/tables/{1}".format(layer.databaseid, layer.tableid))
        response = self.__query.simple()
        if response is None:
            return
        data = response.json()
        self.__getDataFromTable(data, layer)

    def __getDataFromTable(self, data, layer):
        if self.__keyExist('name', data):
            layer.name = data['name']
            layer.tablename = data['name']
        if self.__keyExist('description', data):
            layer.description = data['description']
        if self.__keyExist('min_zoom_level', data):
            layer.minzoom = data['min_zoom_level']
        if self.__keyExist('max_zoom_level', data):
            layer.maxzoom = data['max_zoom_level']
        if self.__keyExist('database_versioning', data):
            if data['database_versioning'] is True:
                layer.isStandard = False
        if self.__keyExist('tile_zoom_level', data):
            layer.tileZoomLevel = data['tile_zoom_level']
        if self.__keyExist('read_only', data):
            layer.readOnly = data['read_only']
        if self.__keyExist('geometry_name', data):
            layer.geometryName = data['geometry_name']
        if self.__keyExist('database', data):
            layer.databasename = data['database']
        if self.__keyExist('wfs', data):
            layer.wfs = data['wfs']
        if self.__keyExist('wfs_transactions', data):
            layer.wfsTransaction = data['wfs_transactions']
        if self.__keyExist('style', data):
            layer.style = data['style']
        if self.__keyExist('id_name', data):
            layer.idName = data['id_name']
        if self.__keyExist('columns', data):
            layer.attributes = data['columns']
            for column in data['columns']:
                if self.__keyExist('name', column):
                    if column['name'] != layer.geometryName:
                        continue
                if self.__keyExist('is3d', column):
                    layer.is3d = column['is3d']
                if self.__keyExist('type', column):
                    layer.geometryType = column['type']
                if self.__keyExist('srid', column):
                    layer.srid = column['srid']
        # layer.styles = data['styles']

    # Récupère les informations d'un géoservice
    def __getDataLayerFromGeoservice(self, layer, geoservice):
        self.__query.setHeaders(self.__tokenType, self.__tokenAccess)
        self.__query.setPartOfUrl("gcms/api/geoservices/{}".format(geoservice['id']))
        response = self.__query.simple()
        if response is None:
            return
        data = response.json()
        self.__getDataFromGeoservice(data, layer)

    def __getDataFromGeoservice(self, data, layer):
        # il faut copier le nom de la couche pour récupérer les données
        # de la layer dans la boite "Charger le guichet"
        if self.__keyExist('title', data):
            layer.name = data['title']
        layer.geoservice.update(data)

    def switchNameToTitleFromThemeAttributes(self, nameAttribute) -> str:
        title = ''
        for theme in self.__theme:
            title = theme.getSwitchAttributeNameToTitle(nameAttribute)
        return title
