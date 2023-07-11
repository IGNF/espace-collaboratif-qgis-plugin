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
        return response

    def getNextResponse(self, partOfUrl, params=None):
        try:
            response = self.getResponse(partOfUrl, params)
            data = response.json()
            # Statut de la réponse
            if response.status_code == 200:
                return {'status': 'ok', 'page': 0, 'data': data, 'stop': True}
            elif response.status_code == 206:
                if len(data) == params['limit']:
                    return {'status': 'ok', 'page': params['page'] + params['limit'], 'data': data,
                            'stop': False}
                elif len(data) < params['limit']:
                    # le parametre page est mis à 0 car la récupération des données est finie
                    return {'status': 'ok', 'page': 0, 'data': data, 'stop': True}
            else:
                return {'status': 'error', 'reason': response.reason, 'url': response.url}
        except Exception as e:
            return {'status': 'error'}
