from . import requests
from .requests.auth import HTTPBasicAuth


class HttpRequest(object):

    def __init__(self, url, login, pwd, proxies):
        self.__url = url
        self.__login = login
        self.__password = pwd
        self.__proxies = proxies

    def getResponse(self, partOfUrl):
        uri = "{}/{}".format(self.__url, partOfUrl)

        # Ne pas vérifier le certificat en localhost
        if uri.find("localhost.ign.fr") != -1:
            response = requests.get(uri, auth=HTTPBasicAuth(self.__login, self.__password), proxies=self.__proxies,
                                    verify=False)
        else:
            #TODO comment implanter le '_next' dans la réponse si différent de 'None'
            response = requests.get(uri, auth=HTTPBasicAuth(self.__login, self.__password), proxies=self.__proxies)
        return response
