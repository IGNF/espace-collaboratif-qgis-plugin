import json
import urllib.parse
import uuid

from qgis.core import QgsBlockingNetworkRequest, QgsNetworkAccessManager
from qgis.PyQt.QtCore import QUrl, QByteArray, QEventLoop
from qgis.PyQt.QtNetwork import QNetworkRequest
from .PluginLogger import PluginLogger


class QgisNetworkResponse(object):
    """
    Adaptateur exposant une interface compatible avec ``requests.Response`` autour d'une réponse
    obtenue via la pile réseau de QGIS (``QgsBlockingNetworkRequest`` / ``QgsNetworkAccessManager``).

    Cela permet de remplacer la librairie ``requests`` par l'API réseau native de QGIS (proxy, SSL et
    authentification gérés automatiquement par ``QgsNetworkAccessManager``) sans modifier le code appelant
    qui utilise ``status_code``, ``reason``, ``text``, ``content`` et ``json()``.
    """

    def __init__(self, content, status_code, reason, url) -> None:
        """
        Constructeur.

        :param content: le corps de la réponse
        :type content: bytes

        :param status_code: le code HTTP de la réponse
        :type status_code: int

        :param reason: le texte associé au code HTTP
        :type reason: str

        :param url: l'url finale de la requête
        :type url: str
        """
        self._content = content or b''
        self.status_code = status_code
        self.reason = reason or ''
        self.url = url
        self.encoding = 'utf-8'

    @property
    def content(self) -> bytes:
        """
        :return: le corps brut de la réponse
        """
        return self._content

    @property
    def text(self) -> str:
        """
        :return: le corps de la réponse décodé (utf-8 par défaut)
        """
        return self._content.decode(self.encoding or 'utf-8', errors='replace')

    def json(self):
        """
        :return: le corps de la réponse interprété comme du JSON
        """
        return json.loads(self.text)


class HttpRequest(object):
    """
    # Classe implémentant une requête HTTP au moyen de la pile réseau de QGIS.
    """
    logger = PluginLogger("HttpRequest").getPluginLogger()

    def __init__(self, url, headers, proxies):
        """
        Constructeur.

        :param url: la première partie de l'url (https://espacecollaboratif.ign.fr/)
        :type url:str

        :param headers: l'entête d'autorisation
        :type headers: dict

        :param proxies: les noms des serveurs proxy (conservé pour compatibilité, le proxy est géré
                        automatiquement par QgsNetworkAccessManager selon la configuration de QGIS)
        :type proxies: dict
        """
        self.__url = url
        self.__headers = headers
        self.__proxies = proxies

    # ------------------------------------------------------------------
    # Fonctions utilitaires internes (pile réseau QGIS)
    # ------------------------------------------------------------------
    @staticmethod
    def __toBytes(value) -> bytes:
        """
        Convertit une valeur en bytes (utf-8).

        :param value: la valeur à convertir (str, bytes ou autre)
        :return: la valeur encodée en bytes
        """
        if value is None:
            return b''
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return value.encode('utf-8')
        return str(value).encode('utf-8')

    @staticmethod
    def __decodeReason(reason) -> str:
        """
        Décode le texte du code HTTP (``HttpReasonPhraseAttribute``) qui peut être renvoyé
        sous forme de ``str`` ou de ``QByteArray`` selon la version de Qt.

        :param reason: le texte associé au code HTTP
        :return: le texte décodé
        """
        if reason is None:
            return ''
        if isinstance(reason, str):
            return reason
        try:
            return bytes(reason).decode('utf-8', errors='replace')
        except Exception:
            return str(reason)

    @staticmethod
    def __buildRequest(url, headers=None, params=None, timeout=None):
        """
        Construit un ``QNetworkRequest`` à partir de l'url, des entêtes, des paramètres et du délai d'attente.

        :param url: l'url de base
        :type url: str

        :param headers: les entêtes HTTP (dont l'autorisation)
        :type headers: dict

        :param params: les paramètres de la requête (ajoutés à la query string)
        :type params: dict

        :param timeout: délai d'attente en secondes (int) ou tuple (connect, read)
        :type timeout: int or tuple

        :return: le couple (QNetworkRequest, url finale)
        """
        if params:
            query = urllib.parse.urlencode(params)
            separator = '&' if '?' in url else '?'
            url = "{}{}{}".format(url, separator, query)
        request = QNetworkRequest(QUrl(url))
        if headers:
            for key, value in headers.items():
                request.setRawHeader(HttpRequest.__toBytes(key), HttpRequest.__toBytes(value))
        timeout_ms = HttpRequest.__timeoutToMs(timeout)
        if timeout_ms is not None and hasattr(request, 'setTransferTimeout'):
            request.setTransferTimeout(timeout_ms)
        return request, url

    @staticmethod
    def __timeoutToMs(timeout):
        """
        Convertit un délai d'attente (secondes) en millisecondes.

        :param timeout: délai en secondes (int) ou tuple (connect, read)
        :return: le délai en millisecondes ou None
        """
        if timeout is None:
            return None
        if isinstance(timeout, (tuple, list)):
            if len(timeout) == 0:
                return None
            seconds = max(timeout)
        else:
            seconds = timeout
        return int(seconds * 1000)

    @staticmethod
    def __sendBlocking(verb, request, body=None) -> 'QgisNetworkResponse':
        """
        Lance une requête GET ou POST bloquante via ``QgsBlockingNetworkRequest``.

        :param verb: 'GET' ou 'POST'
        :type verb: str

        :param request: la requête réseau préparée
        :type request: QNetworkRequest

        :param body: le corps de la requête pour un POST
        :type body: QByteArray

        :return: la réponse adaptée
        """
        blocking = QgsBlockingNetworkRequest()
        if verb == 'GET':
            blocking.get(request, forceRefresh=True)
        elif verb == 'POST':
            blocking.post(request, body if body is not None else QByteArray())
        else:
            raise ValueError("HttpRequest.__sendBlocking : verbe HTTP non supporté : {}".format(verb))

        reply = blocking.reply()
        status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        reason = HttpRequest.__decodeReason(reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute))
        content = bytes(reply.content())
        # Absence de code HTTP => échec au niveau transport (proxy, DNS, SSL...) : on lève une exception
        # pour reproduire le comportement de requests qui lève sur ce type d'erreur.
        if status is None:
            raise Exception(blocking.errorMessage() or reply.errorString() or "Erreur réseau QGIS")
        return QgisNetworkResponse(content, status, reason, request.url().toString())

    @staticmethod
    def __sendCustom(verb, request, body=None) -> 'QgisNetworkResponse':
        """
        Lance une requête avec un verbe HTTP personnalisé (ex : PATCH) non pris en charge par
        ``QgsBlockingNetworkRequest``, via ``QgsNetworkAccessManager`` et une boucle d'évènements bloquante.

        :param verb: le verbe HTTP (ex : 'PATCH')
        :type verb: str

        :param request: la requête réseau préparée
        :type request: QNetworkRequest

        :param body: le corps de la requête
        :type body: QByteArray

        :return: la réponse adaptée
        """
        nam = QgsNetworkAccessManager.instance()
        reply = nam.sendCustomRequest(request, QByteArray(HttpRequest.__toBytes(verb)),
                                      body if body is not None else QByteArray())
        loop = QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec()

        status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        reason = HttpRequest.__decodeReason(reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute))
        content = bytes(reply.readAll())
        error_string = reply.errorString()
        final_url = reply.url().toString()
        reply.deleteLater()
        if status is None:
            raise Exception(error_string or "Erreur réseau QGIS")
        return QgisNetworkResponse(content, status, reason, final_url)

    @staticmethod
    def __buildMultipart(data, files):
        """
        Construit un corps de requête ``multipart/form-data`` à partir des champs simples et des fichiers.

        :param data: les champs simples (nom/valeur)
        :type data: dict

        :param files: les fichiers sous la forme {nom: (nom_fichier, objet_fichier, content_type)}
        :type files: dict

        :return: le couple (boundary, corps en bytes)
        """
        boundary = "----QGISFormBoundary{}".format(uuid.uuid4().hex)
        crlf = b'\r\n'
        parts = []
        for key, value in (data or {}).items():
            parts.append(('--' + boundary).encode('utf-8'))
            parts.append('Content-Disposition: form-data; name="{}"'.format(key).encode('utf-8'))
            parts.append(b'')
            parts.append(HttpRequest.__toBytes(value))
        for field_name, file_info in (files or {}).items():
            filename, file_obj, content_type = HttpRequest.__parseFileTuple(field_name, file_info)
            file_bytes = HttpRequest.__readFileBytes(file_obj)
            parts.append(('--' + boundary).encode('utf-8'))
            parts.append('Content-Disposition: form-data; name="{}"; filename="{}"'.format(
                field_name, filename).encode('utf-8'))
            parts.append('Content-Type: {}'.format(content_type or 'application/octet-stream').encode('utf-8'))
            parts.append(b'')
            parts.append(file_bytes)
        parts.append(('--' + boundary + '--').encode('utf-8'))
        parts.append(b'')
        return boundary, crlf.join(parts)

    @staticmethod
    def __parseFileTuple(field_name, file_info):
        """
        Extrait (nom_fichier, objet_fichier, content_type) d'une valeur du dictionnaire ``files``.

        :param field_name: le nom du champ (utilisé par défaut comme nom de fichier)
        :param file_info: soit un objet fichier, soit un tuple (nom, objet, content_type)
        :return: (nom_fichier, objet_fichier, content_type)
        """
        if isinstance(file_info, (tuple, list)):
            filename = file_info[0] if len(file_info) > 0 and file_info[0] else field_name
            file_obj = file_info[1] if len(file_info) > 1 else None
            content_type = file_info[2] if len(file_info) > 2 else None
            return filename, file_obj, content_type
        return field_name, file_info, None

    @staticmethod
    def __readFileBytes(file_obj) -> bytes:
        """
        Lit le contenu d'un objet fichier (ouvert en mode binaire) ou renvoie directement les bytes.

        :param file_obj: l'objet fichier ou des bytes
        :return: le contenu en bytes
        """
        if file_obj is None:
            return b''
        if isinstance(file_obj, bytes):
            return file_obj
        if hasattr(file_obj, 'read'):
            if hasattr(file_obj, 'seek'):
                try:
                    file_obj.seek(0)
                except Exception:
                    pass
            data = file_obj.read()
            return HttpRequest.__toBytes(data)
        return HttpRequest.__toBytes(file_obj)

    # ------------------------------------------------------------------
    # API publique (inchangée)
    # ------------------------------------------------------------------
    def getResponse(self, partOfUrl, params=None) -> 'QgisNetworkResponse':
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
        request, _ = HttpRequest.__buildRequest(uri, headers=self.__headers, params=params, timeout=(15, 60))
        return HttpRequest.__sendBlocking('GET', request)

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
            
            # Vérifier d'abord le status code avant de parser le JSON
            if response.status_code == 200:
                data = response.json()
                return {'status': 'ok', 'page': 0, 'data': data, 'stop': True}
            elif response.status_code == 206:
                data = response.json()
                if len(data) == params['limit']:
                    return {'status': 'ok', 'page': params['page'] + params['limit'], 'data': data,
                            'stop': False}
                elif len(data) < params['limit']:
                    # le parametre page est mis à 0, car la récupération des données est finie
                    return {'status': 'ok', 'page': 0, 'data': data, 'stop': True}
            else:
                # En cas d'erreur, tenter de récupérer le message s'il y a du JSON
                try:
                    data = response.json()
                    error_message = data.get('message', response.reason)
                except:
                    error_message = response.reason
                return {'status': 'error', 'reason': error_message, 'url': response.url, 
                        'code': response.status_code}
        except Exception as e:
            return {'status': 'error', 'reason': str(e), 'details': 'Exception in getNextResponse'}

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

        :param proxies: les noms des serveurs proxy (géré par QGIS, conservé pour compatibilité)
        :type proxies: dict

        :param params: paramètres de la requête
        :type params: dict
        """
        try:
            # Print the actual request being sent to the server
            print("\n" + "="*80)
            print("[HTTP REQUEST] Sending GET request to server")
            print("[HTTP REQUEST] URL: {}".format(url))
            print("[HTTP REQUEST] Parameters:")
            if params:
                for key, value in params.items():
                    print("  - {}: {}".format(key, value))
            else:
                print("  - No parameters")
            print("="*80 + "\n")

            # timeout=(connect, read): 20s to connect, 120s to read a large WFS response.
            request, _ = HttpRequest.__buildRequest(url, headers=headers, params=params, timeout=(20, 120))
            r = HttpRequest.__sendBlocking('GET', request)
            if r.status_code == 200:
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
            error_str = str(e)
            error_type = str(type(e).__name__)
            HttpRequest.logger.error("Request error: {}".format(error_str))
            
            # Detect proxy-specific errors
            is_proxy_error = 'ProxyError' in error_str or 'RemoteDisconnected' in error_str or \
                           'proxy' in error_str.lower() or 'Max retries exceeded' in error_str
            
            return {
                'status': 'error',
                'reason': error_str,
                'code': 'EXCEPTION',
                'url': url,
                'details': error_type,
                'is_proxy_error': is_proxy_error
            }

    @staticmethod
    def makeHttpRequest(url, proxies=None, params=None, data=None, headers=None, files=None, launchBy=None, timeout=60) -> 'QgisNetworkResponse':
        """
        Lance une requête HTTP GET, POST ou PATCH en fonction des variables passées en entrée.

        :param url: l'url complète
        :type url: str

        :param proxies: les noms des serveurs proxy (géré par QGIS, conservé pour compatibilité)
        :type proxies: dict

        :param params: paramètres de la requête
        :type params: dict

        :param data: les données a envoyé sur le serveur
        :type data: str or dict

        :param headers: l'entête d'autorisation
        :type headers: dict

        :param files: fichiers à télécharger
        :type files: dict

        :param launchBy: indique quelle fonction a lancé la requête
        :type launchBy: str

        :param timeout: délai d'attente en secondes, ou tuple (connect_timeout, read_timeout) pour
                        distinguer l'établissement de la connexion de la lecture de la réponse.
        :type timeout: int or tuple

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
            print("Proxies: {}".format(proxies))
            
            HttpRequest.logger.debug("=== makeHttpRequest DEBUG START ===")
            HttpRequest.logger.debug("LaunchedBy: {}".format(launchBy))
            HttpRequest.logger.debug("URL: {}".format(url))
            HttpRequest.logger.debug("Params: {}".format(params))
            HttpRequest.logger.debug("Proxies: {}".format(proxies))

            if launchBy == 'gcmsPatch':
                # PATCH : corps JSON brut, verbe non géré par QgsBlockingNetworkRequest
                request, _ = HttpRequest.__buildRequest(url, headers=headers, timeout=timeout)
                body = QByteArray(HttpRequest.__toBytes(data))
                response = HttpRequest.__sendCustom('PATCH', request, body)
            elif data is None and files is None:
                # GET
                request, _ = HttpRequest.__buildRequest(url, headers=headers, params=params, timeout=timeout)
                response = HttpRequest.__sendBlocking('GET', request)
            elif files is None:
                # POST simple : dict => form-urlencoded, chaîne => corps brut (ex : JSON)
                request, _ = HttpRequest.__buildRequest(url, headers=headers, timeout=timeout)
                if isinstance(data, dict):
                    request.setRawHeader(b'Content-Type', b'application/x-www-form-urlencoded')
                    body = QByteArray(urllib.parse.urlencode(data).encode('utf-8'))
                else:
                    body = QByteArray(HttpRequest.__toBytes(data))
                response = HttpRequest.__sendBlocking('POST', request, body)
            else:
                # POST multipart/form-data (données + fichiers joints)
                boundary, multipart_body = HttpRequest.__buildMultipart(data if isinstance(data, dict) else {}, files)
                request, _ = HttpRequest.__buildRequest(url, headers=headers, timeout=timeout)
                request.setRawHeader(b'Content-Type',
                                     'multipart/form-data; boundary={}'.format(boundary).encode('utf-8'))
                response = HttpRequest.__sendBlocking('POST', request, QByteArray(multipart_body))

            # DEBUG: Log response details
            print("Response status: {}".format(response.status_code))
            print("Response reason: {}".format(response.reason))
            print("Response URL: {}".format(response.url))
            print("Response text (first 500 chars): {}".format(response.text[:500]))

            HttpRequest.logger.debug("Response status: {}".format(response.status_code))
            HttpRequest.logger.debug("Response reason: {}".format(response.reason))
            HttpRequest.logger.debug("Response URL: {}".format(response.url))
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
