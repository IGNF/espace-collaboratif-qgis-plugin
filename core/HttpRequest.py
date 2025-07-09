import json
import requests
from . import requests


# Classe implémentant une requête HTTP
class HttpRequest(object):

    def __init__(self, url, headers, proxies):
        self.__url = url
        self.__headers = headers
        self.__proxies = proxies

    # Retourne une réponse HTTP GET
    def getResponse(self, partOfUrl, params=None) -> requests.Response:
        uri = "{}/{}".format(self.__url, partOfUrl)
        if params is not None:
            response = requests.get(uri, headers=self.__headers, proxies=self.__proxies,
                                    params=params, verify=False)
            print(response.url)
        else:
            # Ne pas vérifier le certificat en localhost
            if uri.find("localhost.ign.fr") != -1:
                response = requests.get(uri, headers=self.__headers, proxies=self.__proxies,
                                        verify=False)
            else:
                response = requests.get(uri, headers=self.__headers, proxies=self.__proxies)
        response.encoding = 'utf-8'
        return response

    # Retourne un dictionnaire comprenant le status de la réponse HTTP GET, les données et s'il faut relancer
    # la requête (status_code 206)
    def getNextResponse(self, partOfUrl, params) -> {}:
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
                    # le parametre page est mis à 0, car la récupération des données est finie
                    return {'status': 'ok', 'page': 0, 'data': data, 'stop': True}
            else:
                return {'status': 'error', 'reason': data['message'], 'url': response.url}
        except Exception as e:
            return {'status': 'error'}

    @staticmethod
    # Même requête que précédemment, mais en utilisant les paramètres offset et maxFeatures
    def nextRequest(url, headers=None, proxies=None, params=None) -> {}:
        try:
            r = requests.get(url, headers=headers, proxies=proxies,
                             params=params, verify=False)
            print("HttpRequest.nextRequest.url : {}".format(r.url))
            if r.status_code == 200:
                r.encoding = 'utf-8'
                response = json.loads(r.text)
                if len(response) == params['maxFeatures']:
                    return {'status': 'ok', 'offset': params['offset'] + params['maxFeatures'], 'features': response,
                            'stop': False}
                elif len(response) < params['maxFeatures']:
                    # le parametre offset est mis à 0, car la récupération des données est finie
                    return {'status': 'ok', 'offset': 0, 'features': response, 'stop': True}
            else:
                return {'status': 'error', 'reason': r.reason, 'url': r.url}
        except Exception as e:
            return {'status': 'error'}

    @staticmethod
    # lance une requête HTTP GET ou POST en fonction des vcariables données en entrée
    def makeHttpRequest(url, proxies=None, params=None, data=None, headers=None, files=None) -> ():
        response = ()
        if data is None and files is None:
            response = requests.get(url, proxies=proxies, params=params, headers=headers, verify=False)
        elif files is None and headers is None:
            response = requests.post(url, proxies=proxies, data=data, headers=headers, verify=False)
        elif files is None:
            response = requests.post(url, proxies=proxies, data=data, headers=headers, verify=False)
        else:
            response = requests.post(url, proxies=proxies, data=data, headers=headers, files=files, verify=False)
        response.encoding = 'utf-8'
        return response
