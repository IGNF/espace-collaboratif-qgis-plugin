from PyQt5.QtWidgets import QMessageBox
from .HttpRequest import HttpRequest
from .requests import Response
from . import Constantes as cst
from .Box import Box


class Query(object):
    """
    Classe permettant de lancer une ou plusieurs requêtes HTTP GET et de remplir le fichier de paramètres attendu
    pour le get d'une requête de la librairie Requests de Python
    """

    def __init__(self, url, proxy) -> None:
        self.__headers = {}
        self.__url = url
        self.__proxy = proxy
        self.__partOfUrl = ''
        self.__params = {}

    def setHeaders(self, tokenType, tokenAccess) -> None:
        """
        Fixe l'entête d'autorisation avec les tokens d'authentication pour une connexion sécurisée
        à l'espace collaboratif.

        :param tokenType: jeton sur le type de compte
        :type tokenType: str

        :param tokenAccess: jeton individuel d'accès
        :type tokenAccess: str
        """
        self.__headers['Authorization'] = '{} {}'.format(tokenType, tokenAccess)

    def setPartOfUrl(self, partOfUrl) -> None:
        """
        Fixe le complément de l'url générale permettant de constituer la requête HTTP finale pour la variable
        __params passée à une requête multiple.

        :param partOfUrl: une partie d'url
        :type partOfUrl: str
        """
        self.__partOfUrl = partOfUrl

    def setOpeningDate(self, openingDate) -> None:
        """
        Fixe la date minimale d'extraction pour la variable __params passée à une requête multiple.

        :param openingDate: date minimale
        :type openingDate: str
        """
        self.__params['opening_date'] = openingDate

    def setBox(self, box) -> None:
        """
        Fixe l'emprise géographique pour la variable __params passée à une requête multiple.
        L'emprise est de la forme 'lonMin, latMin, lonMax, latMax'.

        :param box: boite englobante de la zone de travail
        :type box: BBox
        """
        self.__params['box'] = "{},{},{},{}".format(box.getXMin(), box.getYMin(), box.getXMax(), box.getYMax())

    def setPage(self, page) -> None:
        """
        Fixe le numéro de la page pour la variable __params passée à une requête multiple.

        :param page: le numéro de la page
        :type page: int
        """
        self.__params['page'] = page

    def setLimit(self, limit) -> None:
        """
        Fixe le nombre limite d'objets par page pour la variable __params passée à une requête multiple.

        :param limit: le nombre d'objets par page
        :type limit: int
        """
        self.__params['limit'] = limit

    def multiple(self) -> []:
        """
        Enchaine les requêtes HTTP dans le cas d'une réponse à multiples pages.

        :return: les données sous forme de dictionnaire, si les requêtes ont abouti
        """
        message = ""
        httpRequest = HttpRequest(self.__url, self.__headers, self.__proxy)
        data = []
        while True:
            response = httpRequest.getNextResponse(self.__partOfUrl, self.__params)
            if response['status'] == 'error':
                message += "[Query.multiple.getNextResponse] {0} : {1}".format(response['status'], response['reason'])
                break

            for dt in response['data']:
                data.append(dt)

            if response['status'] == 'ok' and response['stop'] is True and response['page'] == 0:
                return data

            if len(data) != 0 and response['stop'] and response['page'] == 0:
                return data

            self.setPage(self.__params['page'] + 1)
            if response['stop']:
                break

        if message != '':
            msgBox = QMessageBox()
            msgBox.setWindowTitle(cst.IGNESPACECO)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText(message)
            msgBox.exec_()

        return data

    def simple(self) -> Response:
        """
        Requête HTTP simple.

        :return: la réponse HTTP ou une exception si le status de la requête est différent de 200.
        """
        httpRequest = HttpRequest(self.__url, self.__headers, self.__proxy)
        response = httpRequest.getResponse(self.__partOfUrl, None)
        if response.status_code != 200:
            if response.reason.find('Unauthorized') != -1:
                message = "Attention, problème de connexion, veuillez recommencer l'action en cours " \
                          "ou vous reconnecter."
            else:
                message = "Query.simple : erreur {} {}".format(response.status_code, response.reason)
            raise Exception(message)
        return response
