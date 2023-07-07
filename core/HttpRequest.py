from . import requests
from .requests.auth import HTTPBasicAuth


class HttpRequest(object):

    def __init__(self, url, login, pwd, proxies):
        self.__url = url
        self.__login = login
        self.__password = pwd
        self.__proxies = proxies

    def getResponse(self, partOfUrl, params):
        uri = "{}/{}".format(self.__url, partOfUrl)
        if params is not None:
            response = requests.get(uri, auth=HTTPBasicAuth(self.__login, self.__password), proxies=self.__proxies,
                                    params=params, verify=False)
        else:
            # Ne pas vérifier le certificat en localhost
            if uri.find("localhost.ign.fr") != -1:
                response = requests.get(uri, auth=HTTPBasicAuth(self.__login, self.__password), proxies=self.__proxies,
                                        verify=False)
            else:
                response = requests.get(uri, auth=HTTPBasicAuth(self.__login, self.__password), proxies=self.__proxies)
        response.encoding = 'utf-8'
        data = response.json()
        return data

    def getNextResponse(self, partOfUrl, params=None):
        try:
            response = self.getResponse(partOfUrl, params)
            if response.status_code == 206:
                if len(response) == params['limit']:
                    return {'status': 'ok', 'page': params['page'] + params['limit'], 'data': response,
                            'stop': False}
                elif len(response) < params['maxFeatures']:
                    # le parametre page est mis à 0 car la récupération des données est finie
                    return {'status': 'ok', 'page': 0, 'data': response, 'stop': True}
            else:
                return {'status': 'error', 'reason': response.reason, 'url': response.url}
        except Exception as e:
            return {'status': 'error'}
