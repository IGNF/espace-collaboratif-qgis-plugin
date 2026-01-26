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
                # Detailed error information
                return {
                    'status': 'error',
                    'reason': r.reason,
                    'code': r.status_code,
                    'url': r.url,
                    'details': r.text[:500] if len(r.text) > 0 else 'No response body'
                }
        except Exception as e:
            HttpRequest.logger.error("Request error: {}".format(str(e)))
            return {
                'status': 'error',
                'reason': str(e),
                'code': 'EXCEPTION',
                'url': url,
                'details': str(type(e).__name__)
            }

    @staticmethod
    def makeHttpRequest(url, proxies=None, params=None, data=None, headers=None, files=None, launchBy=None) -> Response:
        """
        Lance une requête HTTP GET, POST ou PATCH en fonction des variables passées en entrée.

        :param url: l'url complète
        :type url: str

        :param proxies: les noms des serveurs proxy
        :type proxies: dict

        :param params: paramètres de la requête
        :type params: dict

        :param data: les données a envoyé sur le serveur
        :type data: str

        :param headers: l'entête d'autorisation
        :type headers: dict

        :param files: fichiers à télécharger
        :type files: dict

        :param launchBy: indique quelle fonction a lancé la requête
        :type launchBy: str

        :return: les données retournées par le serveur
        """
        try:
            print("HttpRequest.makeHttpRequest.files : {}".format(files))
            print("HttpRequest.makeHttpRequest.data : {}".format(data))
            
            # DEBUG: Log request details
            print("\n=== makeHttpRequest DEBUG START ===")
            print("LaunchedBy: {}".format(launchBy))
            print("URL: {}".format(url))
            print("Params: {}".format(params))
            print("Headers: {}".format(headers))
            print("Proxies: {}".format(proxies))
            
            HttpRequest.logger.debug("=== makeHttpRequest DEBUG START ===")
            HttpRequest.logger.debug("LaunchedBy: {}".format(launchBy))
            HttpRequest.logger.debug("URL: {}".format(url))
            HttpRequest.logger.debug("Params: {}".format(params))
            HttpRequest.logger.debug("Headers: {}".format(headers))
            HttpRequest.logger.debug("Proxies: {}".format(proxies))
            
            if launchBy == 'gcmsPatch':
                response = requests.patch(url, data=data, headers=headers, proxies=proxies, verify=False)
            elif data is None and files is None:
                response = requests.get(url, params=params, headers=headers, proxies=proxies, verify=False)
            elif files is None:
                response = requests.post(url, data=data, headers=headers, proxies=proxies, verify=False)
            else:
                response = requests.post(url, data=data, headers=headers, files=files, proxies=proxies, verify=False)

            # DEBUG: Log response details
            print("Response status: {}".format(response.status_code))
            print("Response reason: {}".format(response.reason))
            print("Response URL: {}".format(response.url))
            print("Response headers: {}".format(response.headers))
            print("Response text (first 500 chars): {}".format(response.text[:500]))
            
            HttpRequest.logger.debug("Response status: {}".format(response.status_code))
            HttpRequest.logger.debug("Response reason: {}".format(response.reason))
            HttpRequest.logger.debug("Response URL: {}".format(response.url))
            HttpRequest.logger.debug("Response headers: {}".format(response.headers))
            HttpRequest.logger.debug("Response text (first 500 chars): {}".format(response.text[:500]))
            
            if response.status_code != 200 and response.status_code != 201 and response.status_code != 206:
                message = "{}:makeHttpRequest [{}]".format(launchBy, response.text)
                print("ERROR: {}".format(message))
                print("Request failed with status {}, URL: {}".format(response.status_code, url))
                print("=== makeHttpRequest DEBUG END (ERROR) ===\n")
                HttpRequest.logger.error(message)
                HttpRequest.logger.error("Request failed with status {}, URL: {}".format(response.status_code, url))
                HttpRequest.logger.debug("=== makeHttpRequest DEBUG END (ERROR) ===")
                raise Exception(message)

            response.encoding = 'utf-8'
            print("=== makeHttpRequest DEBUG END (SUCCESS) ===\n")
            HttpRequest.logger.debug("=== makeHttpRequest DEBUG END (SUCCESS) ===")

        except Exception as e:
            print("EXCEPTION in makeHttpRequest: {}".format(format(e)))
            print("Request details - URL: {}, LaunchedBy: {}".format(url, launchBy))
            print("=== makeHttpRequest DEBUG END (EXCEPTION) ===\n")
            HttpRequest.logger.error("Exception in makeHttpRequest: {}".format(format(e)))
            HttpRequest.logger.error("Request details - URL: {}, LaunchedBy: {}".format(url, launchBy))
            HttpRequest.logger.debug("=== makeHttpRequest DEBUG END (EXCEPTION) ===")
            raise Exception(format(e))

        return response
