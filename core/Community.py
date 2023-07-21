from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject

from . import Constantes as cst
from .Profil import Profil
from .HttpRequest import HttpRequest
from .JsonResponse import JsonResponse
from .Theme import Theme
from .Layer import Layer


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
        data = []
        while True:
            response = httpRequest.getNextResponse(partOfUrl, params)

            if response['status'] == 'error':
                message += "[Community.py::query::getNextResponse] {0} : {1}".format(response['status'],
                                                                                     response['reason'])
                break

            for dt in response['data']:
                data.append(dt)

            if response['status'] == 'ok' and response['stop'] is True and response['page'] == 0:
                return data

            if len(data) != 0 and response['stop'] and response['page'] == 0:
                return data
            # Il s'agit du nombre de pages et non d'un offset
            self.setPage(params['page'] + 1)
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
        if response.status_code != 200:
            message = "Community.query : {}".format(response.text)
            raise Exception(message)
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

    def getDataLayersFromTable(self, layer):
        tmp = "gcms/api/databases/{0}/tables/{1}".format(layer.databaseId, layer.table)
        jsonResponse = self.query(tmp)
        if jsonResponse is None:
            return
        jsonResponse.getDataFromTable(layer)

    def getLayers(self, data):
        layers = []
        for d in data:
            layer = Layer()
            if d['type'] == 'geoservice':
                continue
            layer.visibility = d['visibility']
            layer.opacity = d['opacity']
            layer.type = d['type']
            layer.role = d['role']
            layer.id = d['id']
            layer.databaseId = d['database']
            layer.geoservice = d['geoservice']
            layer.order = d['order']
            layer.preferred_style = d['preferred_style']
            layer.snapto = d['snapto']
            layer.table = d['table']
            self.getDataLayersFromTable(layer)
            layers.append(layer)
        return layers

    def extractLayers(self, communityId) -> []:
        self.setLimit(10)
        self.setPage(1)
        data = self.multiQuery("gcms/api/communities/{}/layers".format(communityId), self.__params)
        if len(data) == 0:
            return
        layers = self.getLayers(data)
        return layers

    def getProfile(self):
        self.__profile.listGroup = self.extractProfile()
        return self.__profile

    def extractProfile(self) -> []:
        jsonResponse = self.query("gcms/api/users/me")
        if jsonResponse is None:
            return
        return jsonResponse.getCommunities()
