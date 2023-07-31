from . import Constantes as cst
from .Profil import Profil
from .Layer import Layer
from .Query import Query


# Classe permettant de récupérer la description d'une communauté, d'une couche cartographique
class Community(object):

    def __init__(self, url, login, pwd, proxy) -> None:
        self.query = Query(url, login, pwd, proxy)
        self.__profile = Profil()

    # Récupère les informations sur un utilisateur
    def extractCommunities(self) -> []:
        self.query.setPartOfUrl("gcms/api/users/me")
        jsonResponse = self.query.simple()
        if jsonResponse is None:
            return
        return jsonResponse.getCommunities()

    # Récupère les informations d'une communauté
    def getUserProfil(self, community_id) -> Profil:
        self.query.setPartOfUrl("gcms/api/communities/{}".format(community_id))
        jsonResponse = self.query.simple()
        profil = jsonResponse.extractProfileFromCommunities()
        return profil

    # Récupère les couches associées à une communauté
    def extractLayers(self, communityId, page, limit) -> []:
        self.query.setPage(page)
        self.query.setLimit(limit)
        self.query.setPartOfUrl("gcms/api/communities/{}/layers".format(communityId))
        data = self.query.multiple()
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
        self.query.setPartOfUrl("gcms/api/databases/{0}/tables/{1}".format(layer.databaseId, layer.table))
        jsonResponse = self.query.simple()
        if jsonResponse is None:
            return
        jsonResponse.getDataFromTable(layer)

    # Récupère les informations d'un géoservice
    def getDataLayerFromGeoservice(self, layer, geoservice):
        self.query.setPartOfUrl("gcms/api/geoservices/{}".format(geoservice['id']))
        jsonResponse = self.query.simple()
        if jsonResponse is None:
            return
        jsonResponse.getDataFromGeoservice(layer)
