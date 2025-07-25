from .Query import Query
from .Community import Community
from ..PluginHelper import PluginHelper


class CommunitiesMember(object):
    """
    Classe implémentant l'appartenance d'un utilisateur à des groupes.
    """

    def __init__(self, url, tokenType, tokenAccess, proxies) -> None:
        """
        Constructeur.

        :param url: la première partie de l'url (https://espacecollaboratif.ign.fr/)
        :type url: str

        :param tokenType: jeton sur le type de compte
        :type tokenType: str

        :param tokenAccess: jeton individuel d'accès
        :type tokenAccess: str

        :param proxies: le nom des serveurs proxy
        :type proxies: {}

        """
        self.__url = url
        self.__proxies = proxies
        self.__id = -1
        self.__username = ''
        # Liste des communautés de l'utilisateur
        self.__communities = []
        self.__tokenType = tokenType
        self.__tokenAccess = tokenAccess
        self.__query = Query(url, proxies)
        # liste des noms des communautés de l'utilisateur
        self.__listNameOfCommunities = []

    def getUserCommunity(self, communityToFind) -> None:
        """
        Indique si un groupe appartient à l'utilisateur

        :param communityToFind: le nom du groupe
        :type communityToFind: str

        :return: le nom du groupe ou None si l'utilisateur n'appartient pas au groupe cherché
        """
        for community in self.__communities:
            if community.getName() == communityToFind:
                return community
        return None

    def extractCommunities(self) -> []:
        """
        Lance une requête HTTP GET et récupère les informations sur un utilisateur.

        :return: la liste des groupes auxquels appartient l'utilisateur
        """
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
        """
        Récupère les caractéristiques de tous les groupes appartenant à l'utilisateur.

        :param datas: les données issues d'une requête HTTP GET
        :type datas: dict
        """
        if len(datas) == 0:
            return
        params = {'url': self.__url, 'tokentype': self.__tokenType, 'tokenaccess': self.__tokenAccess,
                  'proxies': self.__proxies}
        for data in datas:
            community = Community(params)
            community.getDatas(data)
            self.__communities.append(community)
            self.__listNameOfCommunities.append({'name': community.getName(), 'id': community.getId()})

    def getId(self) -> int:
        """
        :return: l'identifiant utilisateur
        """
        return self.__id

    def getUserName(self) -> str:
        """
        :return: le nom de l'utilisateur
        """
        return self.__username

    def getCommunities(self) -> []:
        """
        :return: la liste des groupes de l'utilisateur avec leurs caractéristiques
        """
        return self.__communities

    def getListNameOfCommunities(self) -> []:
        """
        :return: la liste des noms de groupes de l'utilisateur
        """
        return self.__listNameOfCommunities
