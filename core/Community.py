from .Profil import Profil
from .HttpRequest import HttpRequest
from .JsonResponse import JsonResponse
from .Theme import Theme


class Community(object):

    def __init__(self, url, login, pwd, proxies) -> None:
        self.__url = url
        self.__login = login
        self.__password = pwd
        self.__proxies = proxies
        self.__profile = Profil()

    def query(self, strQuery) -> JsonResponse:
        httpRequest = HttpRequest(self.__url, self.__login, self.__password, self.__proxies)
        response = httpRequest.getResponse(strQuery)
        jsonResponse = JsonResponse(response)
        jsonResponse.checkResponseValidity()
        jsonResponse.readData()
        return jsonResponse

    def getUserProfil(self, community_id):
        jsonResponse = self.query("gcms/api/communities/{}".format(community_id))
        profil = jsonResponse.extractProfileFromCommunities()
        return profil

    def extractCommunities(self) -> []:
        jsonResponse = self.query("gcms/api/users/me")
        return jsonResponse.getCommunities()

    def getProfile(self):
        self.__profile.listGroup = self.extractProfile()
        return self.__profile

    def extractProfile(self) -> []:
        jsonResponse = self.query("gcms/api/users/me")
        return jsonResponse.getCommunities()

    def __extractThemes(self, community_member_profile) -> ([], []):
        themes = []
        theme = Theme()
        filteredThemes = []
        for cmp in community_member_profile:
            groupId = cmp['group_id']
            theme.group.id = groupId
            if 'group_name' in cmp:
                theme.group.name = cmp['group_name']
            theme.isFiltered = True
            nameThemes = self.__extractAttributes(groupId)
            for nameTheme in nameThemes:
                filteredThemes.append(nameTheme)
        return themes.append(theme), filteredThemes

    def __extractAttributes(self, communityId) -> []:
        nameThemes = []
        httpRequest = HttpRequest(self.__url, self.__login, self.__password, self.__proxies)
        response = httpRequest.getResponse("gcms/api/communities/{}".format(communityId))
        jsonResponse = JsonResponse(response)
        jsonResponse.checkResponseValidity()
        jsonResponse.readData()
        jsonResponse.getAttributes()
        return nameThemes

    def __extractLayers(self, communityId) -> None:
        httpRequest = HttpRequest(self.__url, self.__login, self.__password, self.__proxies)
        response = httpRequest.getResponse("gcms/api/communities/{}/layers".format(communityId))
        jsonResponse = JsonResponse(response)
        jsonResponse.checkResponseValidity()
        jsonResponse.readData()
        dataLayers = jsonResponse.getLayers()
        for dl in dataLayers:
            response = httpRequest.getResponse("gcms/api/databases/{}/tables/{}".format(dl['database'], dl['table']))
            jsonResponse = JsonResponse(response)
            jsonResponse.checkResponseValidity()
            jsonResponse.readData()
