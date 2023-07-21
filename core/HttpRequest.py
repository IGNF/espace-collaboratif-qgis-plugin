import json
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

    @staticmethod
    def nextRequest(url, authent=None, proxies=None, params=None):
        try:
            r = requests.get(url, auth=HTTPBasicAuth(authent['login'], authent['password']), proxies=proxies,
                             params=params, verify=False)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                response = json.loads(r.text)
                if len(response) == params['maxFeatures']:
                    return {'status': 'ok', 'offset': params['offset'] + params['maxFeatures'], 'features': response,
                            'stop': False}
                elif len(response) < params['maxFeatures']:
                    # le parametre offset est mis à 0 car la récupération des données est finie
                    return {'status': 'ok', 'offset': 0, 'features': response, 'stop': True}
            else:
                return {'status': 'error', 'reason': r.reason, 'url': r.url}
        except Exception as e:
            return {'status': 'error'}

    @staticmethod
    def makeHttpRequest(url, authent=None, proxies=None, params=None, data=None, files=None):
        try:
            if data is None and files is None:
                r = requests.get(url, auth=HTTPBasicAuth(authent['login'], authent['password']), proxies=proxies,
                                 params=params, verify=False)
            else:
                r = requests.post(url, auth=HTTPBasicAuth(authent['login'], authent['password']), proxies=proxies,
                                  data=data, files=files, verify=False)
            if r.status_code != 200:
                raise Exception(r.reason)
            r.encoding = 'utf-8'
            response = r.text

        except Exception as e:
            raise Exception(u"Connexion impossible.\nVeuillez vérifier les paramètres de connexion\n(Aide>Configurer "
                            u"le plugin.\nErreur : {0})".format(e))
        return response
