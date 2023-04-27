from .Profil import Profil
from .HttpRequest import HttpRequest
from .JsonResponse import JsonResponse
from .Theme import Theme


class Community(object):

    def __init__(self, url, login, pwd, proxies):
        self.__url = url
        self.__login = login
        self.__password = pwd
        self.__proxies = proxies
        self.__profile = Profil()

    def getProfil(self):
        self.__extractProfile()
        return self.__profile

    def __extractProfile(self):
        httpRequest = HttpRequest(self.__url, self.__login, self.__password, self.__proxies)
        response = httpRequest.getResponse("gcms/api/users/me")
        jsonResponse = JsonResponse(response)
        jsonResponse.checkResponseValidity()
        jsonResponse.readData()
        ap = jsonResponse.activeProfile()
        self.__profile.title = ap[0]
        self.__profile.geogroup.name = ap[0]
        self.__profile.geogroup.id = ap[1]
        # self.__profile.id_Geoprofil = ''  # TODO trouver l'info
        # self.__profile.logo = ''   # TODO trouver l'info
        # self.__profile.filtre = ''  # TODO trouver l'info
        # self.__profile.prive = ''  # TODO trouver l'info
        th = self.__extractThemes(ap[2])
        self.__profile.themes = th[0]
        self.__profile.filteredThemes = th[1]

    def __extractThemes(self, community_member_profile):
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

    def __extractAttributes(self, groupId):
        nameThemes = []
        httpRequest = HttpRequest(self.__url, self.__login, self.__password, self.__proxies)
        response = httpRequest.getResponse("gcms/api/communities/{}".format(groupId))
        jsonResponse = JsonResponse(response)
        jsonResponse.checkResponseValidity()
        jsonResponse.readData()
        jsonResponse.getAttributes()
        return nameThemes

    def __extractLayers(self):
        a = 1
