import json
from .requests import Response
import requests
from . import requests
from .PluginLogger import PluginLogger


class HttpRequest(object):
    """
    # Classe implémentant une requête HTTP.
    """
    logger = PluginLogger("HttpRequest").getPluginLogger()

    def __init__(self, url, headers, proxies):
        """
        Constructeur.

        :param url: la première partie de l'url (https://espacecollaboratif.ign.fr/)
        :type url:str

        :param headers: l'entête d'autorisation
        :type headers: dict

        :param proxies: les noms des serveurs proxy
        :type proxies: dict
        """
        self.__url = url
        self.__headers = headers
        self.__proxies = proxies

    def getResponse(self, partOfUrl, params=None) -> requests.Response:
        """
        Lance une requête HTTP GET.

        :param partOfUrl: une partie de l'url finale
        :type partOfUrl: str

        :param params: paramètres de la requête
        :type params: dict

        :return: une réponse encodée en utf-8
        """
        uri = "{}/{}".format(self.__url, partOfUrl)
        print(uri)
        if params is not None:
            response = requests.get(uri, headers=self.__headers, proxies=self.__proxies,
                                    params=params, verify=False)
        else:
            # Ne pas vérifier le certificat en localhost
            if uri.find("localhost.ign.fr") != -1:
                response = requests.get(uri, headers=self.__headers, proxies=self.__proxies,
                                        verify=False)
            else:
                response = requests.get(uri, headers=self.__headers, proxies=self.__proxies)
        response.encoding = 'utf-8'
        return response

    #
    def getNextResponse(self, partOfUrl, params) -> {}:
        """
        Traite les réponses fournies dans le cas d'une requête multiple en utilisant le status de la réponse.

        :param partOfUrl: une partie de l'url finale
        :type partOfUrl: str

        :param params: paramètres de la requête
        :type params: dict

        :return: un dictionnaire comprenant le status de la réponse, les données et s'il faut relancer la requête
                 (status_code 206)
        """
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
        """
        Traite les réponses fournies dans le cas d'une requête multiple en utilisant les paramètres offset
        et maxFeatures de la réponse.

        :param url: l'url complète
        :type url:str

        :param headers: l'entête d'autorisation
        :type headers: dict

        :param proxies: les noms des serveurs proxy
        :type proxies: dict

        :param params: paramètres de la requête
        :type params: dict
        """
        try:
            r = requests.get(url, headers=headers, proxies=proxies,
                             params=params, verify=False)
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
    #
    def makeHttpRequest(url, proxies=None, params=None, data=None, headers=None, files=None, launchBy=None) -> Response:
        """
        Lance une requête HTTP GET ou POST en fonction des variables passées en entrée.

        :param url: l'url complète
        :type url: str

        :param proxies: les noms des serveurs proxy
        :type proxies: dict

        :param params: paramètres de la requête
        :type params: dict

        :param data: les données a envoyé sur le serveur
        :type data: dict

        :param headers: l'entête d'autorisation
        :type headers: dict

        :param files: fichiers à télécharger
        :type files: dict

        :param launchBy: indique quelle fonction a lancé
        :type launchBy: str

        :return: les données
        """
        try:
            if data is None and files is None:
                response = requests.get(url, proxies=proxies, params=params, headers=headers, verify=False)
            elif files is None:
                response = requests.post(url, proxies=proxies, data=data, headers=headers, verify=False)
            else:
                response = requests.post(url, proxies=proxies, data=data, headers=headers, files=files, verify=False)

            if response.status_code != 200 and response.status_code != 201 and response.status_code != 206:
                message = "{}:makeHttpRequest [{}]".format(launchBy, response.text)
                HttpRequest.logger.error(message)
                raise Exception(message)

            response.encoding = 'utf-8'

        except Exception as e:
            HttpRequest.logger.error(format(e))
            raise Exception(format(e))

        return response
