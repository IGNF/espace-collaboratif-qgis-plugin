import json
import uuid
from .PluginLogger import PluginLogger
from qgis.core import QgsBlockingNetworkRequest, QgsNetworkAccessManager
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtCore import QUrl, QUrlQuery, QEventLoop

class Response(object):
    """
    Enveloppe compatible avec l'API de requests.Response, construite à partir
    d'une réponse QGIS (QgsNetworkReplyContent).
    """

    def __init__(self, status_code, content, reason='', url='', encoding='utf-8'):
        self.status_code = status_code
        self.content = content          # bytes
        self.reason = reason
        self.url = url
        self.encoding = encoding

    @property
    def text(self):
        return self.content.decode(self.encoding, errors='replace')

    def json(self):
        return json.loads(self.text)


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

    def getResponse(self, partOfUrl, params=None) -> 'Response':
        """
        Lance une requête HTTP GET.

        :param partOfUrl: une partie de l'url finale
        :type partOfUrl: str

        :param params: paramètres de la requête
        :type params: dict

        :return: une réponse encodée en utf-8
        """
        uri = QUrl("{}/{}".format(self.__url, partOfUrl))

        if params is not None:
            query = QUrlQuery()
            for k, v in params.items():
                query.addQueryItem(str(k), str(v))
            uri.setQuery(query)

        urlString = uri.toString()
        print(urlString)

        request = QNetworkRequest(uri)
        for key, value in (self.__headers or {}).items():
            request.setRawHeader(key.encode(), str(value).encode())

        blocking = QgsBlockingNetworkRequest()
        err = blocking.get(request)
        reply = blocking.reply()

        # Erreur réseau/proxy 
        if err != QgsBlockingNetworkRequest.ErrorCode.NoError:
            raise Exception("HttpRequest.getResponse : {} ({})".format(
                blocking.errorMessage(), urlString))

        status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        reason = reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute) or ''
        content = bytes(reply.content())

        return Response(status_code=status, content=content, reason=reason, url=urlString)  

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

        :param proxies: les noms des serveurs proxy
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

            qurl = QUrl(url)
            if params:
                query = QUrlQuery()
                for k, v in params.items():
                    query.addQueryItem(str(k), str(v))
                qurl.setQuery(query)

            request = QNetworkRequest(qurl)
            for key, value in (headers or {}).items():
                request.setRawHeader(key.encode(), str(value).encode())

            blocking = QgsBlockingNetworkRequest()
            err = blocking.get(request)
            reply = blocking.reply()
            status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)

             # Erreur réseau/proxy sans réponse HTTP
            if err != QgsBlockingNetworkRequest.ErrorCode.NoError and status is None:
                raise Exception(blocking.errorMessage())

            text = bytes(reply.content()).decode('utf-8')

            if status == 200:
                response = json.loads(text)
                if len(response) == params['maxFeatures']:
                    return {'status': 'ok', 'offset': params['offset'] + params['maxFeatures'],
                            'features': response, 'stop': False}
                elif len(response) < params['maxFeatures']:
                    return {'status': 'ok', 'offset': 0, 'features': response, 'stop': True}
            else:
                reason = reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute) or ''
                return {
                    'status': 'error',
                    'reason': reason,
                    'code': status,
                    'url': url,
                    'details': text[:500] if len(text) > 0 else 'No response body'
                }
        except Exception as e:
            error_str = str(e)
            error_type = str(type(e).__name__)
            HttpRequest.logger.error("Request error: {}".format(error_str))
            is_proxy_error = 'ProxyError' in error_str or 'RemoteDisconnected' in error_str or \
                           'proxy' in error_str.lower() or 'Max retries exceeded' in error_str
            return {
                'status': 'error',
                'reason': error_str,
                'code': status if 'status' in locals() else 'EXCEPTION',
                'url': url,
                'details': error_type,
                'is_proxy_error': is_proxy_error
            }

    @staticmethod
    def _buildMultipart(data, files):
        """
        Construit un corps multipart/form-data.

        :param data: champs simples {nom: valeur}
        :param files: {champ: (filename, fileobj, content_type)}
        :return: (corps_bytes, valeur_du_header_Content-Type)
        """
        boundary = "----QGISFormBoundary{}".format(uuid.uuid4().hex)
        b = boundary.encode()
        crlf = b"\r\n"
        body = b""

        for name, value in (data or {}).items():
            body += b"--" + b + crlf
            body += 'Content-Disposition: form-data; name="{}"'.format(name).encode() + crlf + crlf
            body += str(value).encode('utf-8') + crlf

        for field, fileinfo in (files or {}).items():
            filename, fileobj, content_type = fileinfo
            filecontent = fileobj.read()
            if isinstance(filecontent, str):
                filecontent = filecontent.encode('utf-8')
            body += b"--" + b + crlf
            body += 'Content-Disposition: form-data; name="{}"; filename="{}"'.format(
                field, filename).encode() + crlf
            body += 'Content-Type: {}'.format(content_type).encode() + crlf + crlf
            body += filecontent + crlf

        body += b"--" + b + b"--" + crlf
        return body, "multipart/form-data; boundary={}".format(boundary)
    

    @staticmethod
    def makeHttpRequest(url, proxies=None, params=None, data=None, headers=None, files=None, launchBy=None, timeout=60) -> 'Response':
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

        :param timeout: délai d'attente en secondes, ou tuple (connect_timeout, read_timeout) pour
                        distinguer l'établissement de la connexion de la lecture de la réponse.
        :type timeout: int or tuple

        :return: les données retournées par le serveur
        """
        try:
            HttpRequest.logger.debug("=== makeHttpRequest DEBUG START ===")
            HttpRequest.logger.debug("LaunchedBy: {} | URL: {}".format(launchBy, url))

            qurl = QUrl(url)
            if params and data is None and files is None:
                query = QUrlQuery()
                for k, v in params.items():
                    query.addQueryItem(str(k), str(v))
                qurl.setQuery(query)

            request = QNetworkRequest(qurl)
            for key, value in (headers or {}).items():
                request.setRawHeader(key.encode(), str(value).encode())

            blocking = QgsBlockingNetworkRequest()
            
            # PATCH 
            if launchBy == 'gcmsPatch':
                body = data.encode('utf-8') if isinstance(data, str) else bytes(data or b'')
                nam = QgsNetworkAccessManager.instance()
                reply = nam.sendCustomRequest(request, b"PATCH", body)
                loop = QEventLoop()
                reply.finished.connect(loop.quit)
                loop.exec()
                status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
                reason = reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute) or ''
                content = bytes(reply.readAll())
                reply.deleteLater()

            # GET 
            elif data is None and files is None:
                err = blocking.get(request)
                if err != QgsBlockingNetworkRequest.ErrorCode.NoError and blocking.reply().attribute(
                        QNetworkRequest.Attribute.HttpStatusCodeAttribute) is None:
                    raise Exception(blocking.errorMessage())
                reply = blocking.reply()
                status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
                reason = reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute) or ''
                content = bytes(reply.content())

            # POST 
            elif files is None:
                if isinstance(data, str):
                    body = data.encode('utf-8')
                else:
                    q = QUrlQuery()
                    for k, v in (data or {}).items():
                        q.addQueryItem(str(k), str(v))
                    body = q.toString(QUrl.FullyEncoded).encode('utf-8')
                    request.setHeader(QNetworkRequest.ContentTypeHeader,
                                    "application/x-www-form-urlencoded")
                err = blocking.post(request, body)
                if err != QgsBlockingNetworkRequest.ErrorCode.NoError and blocking.reply().attribute(
                        QNetworkRequest.Attribute.HttpStatusCodeAttribute) is None:
                    raise Exception(blocking.errorMessage())
                reply = blocking.reply()
                status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
                reason = reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute) or ''
                content = bytes(reply.content())

            # POST multipart
            else:
                body, contentType = HttpRequest._buildMultipart(data, files)
                request.setHeader(QNetworkRequest.ContentTypeHeader, contentType)
                err = blocking.post(request, body)
                if err != QgsBlockingNetworkRequest.ErrorCode.NoError and blocking.reply().attribute(
                        QNetworkRequest.Attribute.HttpStatusCodeAttribute) is None:
                    raise Exception(blocking.errorMessage())
                reply = blocking.reply()
                status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
                reason = reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute) or ''
                content = bytes(reply.content())

            response = Response(status_code=status, content=content,
                                reason=reason, url=qurl.toString())

            HttpRequest.logger.debug("Response status: {} | reason: {}".format(status, reason))
            HttpRequest.logger.debug("Response text (first 500): {}".format(response.text[:500]))
            
            if status not in (200, 201, 206):
                message = "{}:makeHttpRequest [{}]".format(launchBy, response.text)
                print("ERROR: {}".format(message))
                HttpRequest.logger.error(message)
                raise Exception(message)

            return response

        except Exception as e:
            HttpRequest.logger.error("Exception in makeHttpRequest: {}".format(format(e)))
            HttpRequest.logger.error("Request details - URL: {}, LaunchBy: {}".format(url, launchBy))
            raise Exception(format(e))
