from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject

from . import ConstanteRipart as cst
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
        self.__params = {}

    def setPage(self, offset):
        self.__params['page'] = offset

    def setLimit(self, maxFeatures):
        self.__params['limit'] = maxFeatures

    def multiQuery(self, partOfUrl, params):
        message = ""
        httpRequest = HttpRequest(self.__url, self.__login, self.__password, self.__proxies)
        data = {}
        while True:
            response = httpRequest.getNextResponse(partOfUrl, params)

            if response['status'] == 'error':
                message += "[Community.py::query::getNextResponse] {0} : {1}".format(response['status'],
                                                                                     response['reason'])
                break

            if response['status'] == 'ok' and response['stop'] is True and response['page'] == 0:
                return response['data']

            for dt in response['data']:
                data.update(dt)

            if len(data) != 0 and response['stop'] and response['page'] == 0:
                return JsonResponse(data)
            self.setPage(response['page'])
            if response['stop']:
                break
        if message != '':
            msgBox = QMessageBox()
            msgBox.setWindowTitle(cst.IGNESPACECO)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText(message)
            msgBox.exec_()
            return

    def query(self, partOfUrl) -> JsonResponse:
        httpRequest = HttpRequest(self.__url, self.__login, self.__password, self.__proxies)
        response = httpRequest.getResponse(partOfUrl, None)
        jsonResponse = JsonResponse(response)
        return jsonResponse

    def getUserProfil(self, community_id) -> Profil:
        jsonResponse = self.query("gcms/api/communities/{}".format(community_id))
        profil = jsonResponse.extractProfileFromCommunities()
        return profil

    def extractCommunities(self) -> []:
        jsonResponse = self.query("gcms/api/users/me")
        if jsonResponse is None:
            return
        return jsonResponse.getCommunities()

    def extractLayers(self, communityId) -> []:
        self.setLimit(10)
        self.setPage(1)
        jsonResponse = self.multiQuery("gcms/api/communities/{}/layers".format(communityId), self.__params)
        if jsonResponse is None:
            return
        return jsonResponse.getLayers()

    def getProfile(self):
        self.__profile.listGroup = self.extractProfile()
        return self.__profile

    def extractProfile(self) -> []:
        jsonResponse = self.query("gcms/api/users/me")
        if jsonResponse is None:
            return
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
        response = httpRequest.getResponse("gcms/api/communities/{}".format(communityId), None)
        jsonResponse = JsonResponse(response)
        jsonResponse.checkResponseValidity()
        # jsonResponse.readData()
        jsonResponse.getAttributes()
        return nameThemes
