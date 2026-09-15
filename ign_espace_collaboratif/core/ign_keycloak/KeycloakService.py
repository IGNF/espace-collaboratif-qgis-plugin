import base64
import hashlib
import os
import urllib.parse
import uuid
import webbrowser
import json

from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtNetwork import QNetworkRequest, QSslConfiguration, QSslSocket
from qgis.PyQt.QtCore import QUrl

from .KeycloakAuthListener import KeycloakAuthListener


class KeycloakService:
    def __init__(
        self,
        base_uri: str,
        realm_name: str,
        client_id: str,
        client_secret: str = "",  # nosec B107 - empty string is a default, not a hardcoded secret
        proxies=None,
        ssl_verify: bool = False,
    ) -> None:
        self.base_uri = base_uri
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.ssl_verify = ssl_verify
        self.proxies = proxies

        self.ip = "127.0.0.1"
        self.port = 7070
        self.redirect_uri = f"http://{self.ip}:{self.port}/authorization-code/callback"
        self._code_verifier = None

    @staticmethod
    def _generate_pkce_pair():
        """Generate (code_verifier, code_challenge) according to RFC 7636 using the S256 method."""
        code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode()
        digest = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        return code_verifier, code_challenge

    def get_authorization_code(self, scope):
        if isinstance(scope, list):
            scope = " ".join(scope)

        state = uuid.uuid4().hex
        self._code_verifier, code_challenge = self._generate_pkce_pair()

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        params_encoded = urllib.parse.urlencode(params)

        auth_url = "{}realms/{}/protocol/openid-connect/auth?{}".format(self.base_uri, self.realm_name, params_encoded)

        print(
            "The following link should be opened in your default browser automatically."
            + " If not, please visit the link manually and enter your credentials."
        )
        print(f"--> '{auth_url}'")

        webbrowser.open(auth_url, new=0, autoraise=True)
        keycloak_response = KeycloakAuthListener.listen(self.ip, self.port)
        if state != keycloak_response["state"][0]:
            raise Exception("Authentication failed, invalid state")
        return keycloak_response

    def get_access_token(self, authorization_code: str):
        if self._code_verifier is None:
            raise Exception("code_verifier manquant — appelez get_authorization_code d'abord")

        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "code_verifier": self._code_verifier,
        }
        if self.client_secret:
            data["client_secret"] = self.client_secret
        self._code_verifier = None

        token_url = "{}realms/{}/protocol/openid-connect/token".format(self.base_uri, self.realm_name)
        print("[KeycloakService] POST token exchange → {}".format(token_url))
        print("[KeycloakService] Proxy: {}".format(self.proxies or 'none (system)'))

        status, text = self._send(token_url, data=data)
        print("[KeycloakService] Token response: status={}".format(status))
    
        if status != 200:
            print("[KeycloakService] Token error body: {}".format(text[:500]))
            raise Exception("Failed to get access token: {}".format(text))

        return json.loads(text)
    

    def get_userinfo(self, access_token: str):
        data = {"access_token": access_token}
        userinfo_url = "{}realms/{}/protocol/openid-connect/userinfo".format(self.base_uri, self.realm_name)
        status, text = self._send(userinfo_url, data=data)
        if status != 200:
            raise Exception("Failed to get user info")
        return json.loads(text)

    def logout(self):
        params_encoded = urllib.parse.urlencode({"client_id": self.client_id})
        logout_url = "{}realms/{}/protocol/openid-connect/logout?{}".format(self.base_uri, self.realm_name,
                                                                            params_encoded)
        print(
            "The following link should be opened in your default browser automatically. "
            "If not, please visit the link manually to logout."
        )
        print(f"--> '{logout_url}'")
        webbrowser.open(logout_url, new=0, autoraise=True)

    def get_well_known_config(self) -> dict:
        url = "{}realms/{}/.well-known/openid-configuration".format(self.base_uri, self.realm_name)
        status, text = self._send(url)
        return json.loads(text)

    def _send(self, url, data=None):
        """
        Envoie une requête GET (data=None) ou POST (data=dict, form-urlencoded) via l'API réseau de QGIS.

        :return: (status_code, text)
        """
        request = QNetworkRequest(QUrl(url))

        # Équivalent de session.verify = False
        if not self.ssl_verify:
            sslConfig = QSslConfiguration.defaultConfiguration()
            sslConfig.setPeerVerifyMode(QSslSocket.PeerVerifyMode.VerifyNone)
            request.setSslConfiguration(sslConfig)

        blocking = QgsBlockingNetworkRequest()

        if data is None:
            err = blocking.get(request)
        else:
            request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader,
                            "application/x-www-form-urlencoded")
            body = urllib.parse.urlencode(data).encode("utf-8")
            err = blocking.post(request, body)

        reply = blocking.reply()
        status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)

        # Erreur réseau/proxy sans réponse HTTP exploitable
        if err != QgsBlockingNetworkRequest.ErrorCode.NoError and status is None:
            raise Exception("KeycloakService : erreur réseau {}".format(blocking.errorMessage()))

        text = bytes(reply.content()).decode("utf-8")
        return status, text