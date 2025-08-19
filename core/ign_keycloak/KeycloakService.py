import urllib.parse
import uuid
import webbrowser

import requests

from .KeycloakAuthListener import KeycloakAuthListener


class KeycloakService:
    def __init__(
        self,
        base_uri: str,
        realm_name: str,
        client_id: str,
        client_secret: str = "",
        proxies=None,
        ssl_verify: bool = False,
    ) -> None:
        self.base_uri = base_uri
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret = client_secret

        self.session = requests.Session()
        self.session.verify = ssl_verify

        if proxies is not None:
            self.session.proxies.update(proxies)

        self.ip = "127.0.0.1"
        self.port = 7070
        self.redirect_uri = f"http://{self.ip}:{self.port}/authorization-code/callback"

    def get_authorization_code(self, scope):
        if isinstance(scope, list):
            scope = " ".join(scope)

        state = uuid.uuid4().hex

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "state": state,
        }
        if self.client_secret != "":
            params["client_secret"] = self.client_secret

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
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
        }

        if self.client_secret != "":
            data["client_secret"] = self.client_secret

        token_url = "{}realms/{}/protocol/openid-connect/token".format(self.base_uri, self.realm_name)

        response = self.session.post(token_url, data=data)
        if response.status_code != 200:
            raise Exception("Failed to get access token")

        return response.json()

    def get_userinfo(self, access_token: str):
        data = {"access_token": access_token}

        userinfo_url = "{}realms/{}/protocol/openid-connect/userinfo".format(self.base_uri, self.realm_name)

        response = self.session.post(userinfo_url, data=data)
        if response.status_code != 200:
            raise Exception("Failed to get user info")

        return response.json()

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
        response = self.session.get("{}realms/{}/.well-known/openid-configuration".format(self.base_uri,
                                                                                          self.realm_name))
        return response.json()
