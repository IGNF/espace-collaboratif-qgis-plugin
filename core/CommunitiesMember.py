from .Query import Query
from .Community import Community
from ..PluginHelper import PluginHelper


class CommunitiesMember(object):

    def __init__(self, url, tokenType, tokenAccess, proxy) -> None:
        self.__url = url
        self.__proxy = proxy
        self.__id = -1
        self.__username = ''
        # Liste des communautés de l'utilisateur
        self.__communities = []
        # Liste des thèmes partagés
        self.__sharedThemes = []
        # Liste des thèmes actifs
        self.__activeThemes = []
        self.__tokenType = tokenType
        self.__tokenAccess = tokenAccess
        self.__query = Query(url, proxy)
        # liste des noms des communautés de l'utilisateur
        self.__listNameOfCommunities = []
        # Le nom de la communauté choisie par l'utilisateur lors de sa connexion
        self.__nameActiveCommunity = ''

    def getUserCommunity(self, communityToFind) -> None:
        for community in self.__communities:
            if community.getName() == communityToFind:
                return community
        return None

    def setActiveCommunity(self, communityChoice) -> None:
        self.__nameActiveCommunity = communityChoice

    def getNameActiveCommunity(self) -> str:
        return self.__nameActiveCommunity

    # Récupère les informations sur un utilisateur
    def extractCommunities(self) -> []:
        self.__query.setHeaders(self.__tokenType, self.__tokenAccess)
        self.__query.setPartOfUrl("gcms/api/users/me")
        response = self.__query.simple()
        if response is None:
            return []

        data = response.json()
        if PluginHelper.keyExist('id', data):
            self.__id = data['id']

        if PluginHelper.keyExist('username', data):
            self.__username = data['username']

        if PluginHelper.keyExist('communities_member', data):
            self.getDatasCommunities(data['communities_member'])

        return self.__listNameOfCommunities

    def getDatasCommunities(self, datas) -> None:
        if len(datas) == 0:
            return
        params = {'url': self.__url, 'tokentype': self.__tokenType, 'tokenaccess': self.__tokenAccess,
                  'proxy': self.__proxy}
        for data in datas:
            community = Community(params)
            community.getDatas(data)
            self.__communities.append(community)
            self.__listNameOfCommunities.append({'name': community.getName(), 'id': community.getId()})

    def getId(self):
        return self.__id

    def getUserName(self):
        return self.__username

    def getCommunities(self):
        return self.__communities

    def getSharedThemes(self):
        return self.__sharedThemes

    def getActiveThemes(self):
        return self.__activeThemes

    def getListNameOfCommunities(self):
        return self.__listNameOfCommunities
