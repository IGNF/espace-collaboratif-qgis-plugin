from . import Constantes as cst
from .Profil import Profil
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
        self.__themes = []
        self.__active = False
        self.__logo = ''
        # self.__description = ''
        # self.__date = None
        self.__query = Query(params['url'], params['login'], params['pwd'], params['proxy'])

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
            self.__getDataThemes(data['profile'])

    def __getDataThemes(self, datas) -> None:
        if len(datas) == 0:
            return
        for data in datas:
            if self.__keyExist('themes', data):
                for d in data['themes']:
                    theme = Theme()
                    theme.getTheme(d)
                    self.__themes.append(theme)

    def getName(self) -> str:
        return self.__name

    def getId(self) -> int:
        return self.__id

    def getUserId(self) -> int:
        return self.__userId

    def getEmprises(self) -> []:
        return self.__emprises

    def getThemes(self) -> []:
        return self.__themes

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
        self.__query.setPartOfUrl("gcms/api/communities/{}/layers".format(communityId))
        data = self.__query.multiple()
        if len(data) == 0:
            return
        layers = self.getLayers(data)
        return layers

    # Récupère les infos d'une couche (table ou geoservice) et retourne une liste de toutes les couches
    def getLayers(self, data) -> []:
        layers = []
        for d in data:
            layer = Layer()
            layer.visibility = d['visibility']
            layer.opacity = d['opacity']
            layer.type = d['type']
            layer.role = d['role']
            layer.id = d['id']
            layer.databaseId = d['database']
            layer.order = d['order']
            layer.preferred_style = d['preferred_style']
            layer.snapto = d['snapto']
            layer.table = d['table']
            if d['type'] == cst.WFS:
                self.getDataLayerFromTable(layer)
            if d['type'] == cst.WMTS:
                self.getDataLayerFromGeoservice(layer, d['geoservice'])
            layers.append(layer)
        return layers

    # Récupère les informations d'une table de la base de données correspondant à une couche cartographique
    def getDataLayerFromTable(self, layer):
        self.__query.setPartOfUrl("gcms/api/databases/{0}/tables/{1}".format(layer.databaseId, layer.table))
        response = self.__query.simple()
        if response is None:
            return
        data = response.json()
        self.getDataFromTable(data, layer)

    def getDataFromTable(self, data, layer):
        layer.name = data['name']
        layer.description = data['description']
        layer.minzoom = data['min_zoom_level']
        layer.maxzoom = data['max_zoom_level']
        if data['database_versioning'] is True:
            layer.isStandard = False
        layer.tileZoomLevel = data['tile_zoom_level']
        layer.readOnly = data['read_only']
        layer.geometryName = data['geometry_name']
        layer.databasename = data['database']
        layer.wfs = data['wfs']
        layer.wfsTransaction = data['wfs_transactions']
        layer.attributes = data['columns']
        layer.idName = data['id_name']
        for column in data['columns']:
            if column['name'] != layer.geometryName:
                continue
            layer.is3d = column['is3d']
            layer.geometryType = column['type']
            layer.srid = column['srid']
        layer.style = data['style']
        # layer.styles = data['styles']

    # Récupère les informations d'un géoservice
    def getDataLayerFromGeoservice(self, layer, geoservice):
        self.__query.setPartOfUrl("gcms/api/geoservices/{}".format(geoservice['id']))
        response = self.__query.simple()
        if response is None:
            return
        data = response.json()
        self.getDataFromGeoservice(data, layer)

    def getDataFromGeoservice(self, data, layer):
        # il faut copier le nom de la couche pour récupérer les données de la layer dans la boite "Charger le guichet"
        layer.name = data['title']
        layer.geoservice.update(data)

    def switchNameToTitleFromThemeAttributes(self, nameAttribute) -> str:
        title = ''
        for theme in self.__themes:
            title = theme.getSwitchAttributeNameToTitle(nameAttribute)
        return title
