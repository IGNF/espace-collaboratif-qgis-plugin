from .Query import Query
from .Community import Community
from .SharedTheme import SharedTheme
from .ActiveTheme import ActiveTheme


class CommunitiesMember(object):

    def __init__(self, url, login, pwd, proxy) -> None:
        self.__url = url
        self.__login = login
        self.__pwd = pwd
        self.__proxy = proxy
        self.__firstname = ''
        self.__surname = ''
        self.__id = -1
        self.__username = ''
        # self.__email = ''
        # Liste des communautés de l'utilisateur
        self.__communities = []
        # Liste des thèmes partagés
        self.__sharedThemes = []
        # Liste des thèmes actifs
        self.__activeThemes = []
        self.__query = Query(url, login, pwd, proxy)
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
        self.__query.setPartOfUrl("gcms/api/users/me")
        response = self.__query.simple()
        if response is None:
            return []

        data = response.json()

        if self.keyExist('id', data):
            self.__id = data['id']

        if self.keyExist('username', data):
            self.__username = data['username']

        if self.keyExist('firstname', data):
            self.__firstname = data['firstname']

        if self.keyExist('surname', data):
            self.__surname = data['surname']

        if self.keyExist('active_themes', data):
            self.getDatasActiveThemes(data['active_themes'])

        if self.keyExist('communities_member', data):
            self.getDatasCommunities(data['communities_member'])

        if self.keyExist('shared_themes', data):
            self.getDatasSharedThemes(data['shared_themes'])

        return self.__listNameOfCommunities

    def keyExist(self, key, data) -> bool:
        if key in data:
            return True
        return False

    def getDatasActiveThemes(self, datas) -> None:
        if len(datas) == 0:
            return
        for data in datas:
            activeTheme = ActiveTheme()
            activeTheme.getActiveTheme(data)
            self.__activeThemes.append(activeTheme)

    def getDatasCommunities(self, datas) -> None:
        if len(datas) == 0:
            return
        params = {'url': self.__url, 'login': self.__login, 'pwd': self.__pwd, 'proxy': self.__proxy}
        for data in datas:
            community = Community(params)
            community.getDatas(data)
            self.__communities.append(community)
            self.__listNameOfCommunities.append({'name': community.getName(), 'id': community.getId()})

    def getDatasSharedThemes(self, datas) -> None:
        if len(datas) == 0:
            return
        for data in datas:
            sharedTheme = SharedTheme()
            sharedTheme.getSharedTheme(data)
            self.__sharedThemes.append(sharedTheme)

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
