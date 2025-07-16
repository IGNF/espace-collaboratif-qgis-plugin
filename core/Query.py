from PyQt5.QtWidgets import QMessageBox
from .HttpRequest import HttpRequest
from .requests import Response
from . import Constantes as cst


# Classe permettant de lancer une ou plusieurs requêtes HTTP GET et de remplir le fichier de paramètres attendu
# pour le get d'une Requests Python
class Query(object):

    def __init__(self, url, proxy) -> None:
        self.__headers = {}
        self.__url = url
        self.__proxy = proxy
        self.__partOfUrl = ''
        self.__params = {}

    # Entete pour passer les tokens d'identification
    def setHeaders(self, tokenType, tokenAccess) -> None:
        self.__headers['Authorization'] = '{} {}'.format(tokenType, tokenAccess)

    # Le complément de l'url générale permettant de constituer la requête HTTP finale
    def setPartOfUrl(self, partOfUrl) -> None:
        self.__partOfUrl = partOfUrl

    # Date(s) minimale de création des signalements
    def setOpeningDate(self, openingDate) -> None:
        self.__params['opening_date'] = openingDate

    # Emprise géographique de la forme 'lonMin,latMin,lonMax,latMax'
    def setBox(self, box) -> None:
        self.__params['box'] = "{},{},{},{}".format(box.getXMin(), box.getYMin(), box.getXMax(), box.getYMax())

    # Numéro de la page
    def setPage(self, page) -> None:
        self.__params['page'] = page

    # Limite d'objets par page
    def setLimit(self, limit) -> None:
        self.__params['limit'] = limit

    # Requêtes HTTP multiples (code retour 206 pour les requêtes partielles)
    # Retourne une liste de données
    def multiple(self) -> []:
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

    # Requête HTTP simple
    # Pour toutes les routes, retourne un code 200 pour une lecture OK
    # retourne une response HTTP
    def simple(self) -> Response:
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
