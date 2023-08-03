from PyQt5.QtWidgets import QMessageBox
from .HttpRequest import HttpRequest
from .requests import Response
from . import Constantes as cst


# Classe permettant de lancer une ou plusieurs requêtes HTTP GET et de remplir le fichier de paramètres attendu
# pour le get d'une Requests Python
class Query(object):

    def __init__(self, url, login, passwd, proxy):
        self.__url = url
        self.__login = login
        self.__password = passwd
        self.__proxy = proxy
        self.__partOfUrl = ''
        self.__params = {}

    # Le complément de l'url générale permettant de constituer la requête HTTP finale
    def setPartOfUrl(self, partOfUrl):
        self.__partOfUrl = partOfUrl

    # Identifiant de l'utilisateur
    def setAuthor(self, author):
        self.__params['author'] = author

    # Code du pays des signalements recherchés
    # TODO demander la liste pour vérifier
    def setTerritory(self, territory):
        self.__params['territory'] = territory

    # Code du(des) département(s) des signalements recherchés
    # TODO demander la liste pour vérifier
    def setDepartements(self, departements):
        self.__params['departements'] = departements

    # Code insee de la commune des signalements recherchés
    # TODO vérifier par une REGEX le code INSEE
    def setCommune(self, commune):
        self.__params['commune'] = commune

    # Communauté(s) des signalements recherchés
    def setCommunities(self, communities):
        self.__params['communities'] = communities

    # Date(s) minimale de création des signalements
    def setOpeningDate(self, openingDate):
        self.__params['opening_date'] = openingDate

    # Date(s) de mise-à-jour des signalements
    def setUpdatingDate(self, updatingDate):
        self.__params['updating_date'] = updatingDate

    # Date(s) de cloture des signalements
    def setClosingDate(self, closingDate):
        self.__params['closing_date'] = closingDate

    # Émetteur(s) des signalements recherchés
    # Available values : UNKNOWN, www, SIG-GC, SIG-AG, SIG-QGIS, PHONE, SPOTIT
    # TODO demander la liste
    def setInputDevice(self, inputDevice):
        self.__params['input_device'] = inputDevice

    # Recherche la chaîne dans les signalements. Utilisation du % si incomplet
    def setComment(self, comment):
        self.__params['comment'] = comment

    # Liste les status des signalements recherchés
    # Available values : submit, pending0, pending, pending1, pending2, valid, valid0, reject, reject0, test, dump
    # TODO demander la liste pour vérification
    def setStatus(self, status):
        self.__params['status'] = status

    # Emprise géographique de la forme 'lonMin,latMin,lonMax,latMax'
    def setBox(self, box):
        self.__params['box'] = "{},{},{},{}".format(box.XMin, box.YMin, box.XMax, box.YMax)

    # Numéro de la page
    def setPage(self, page):
        self.__params['page'] = page

    # Limite d'objets par page
    def setLimit(self, limit):
        self.__params['limit'] = limit

    # Requêtes HTTP multiples (code retour 206)
    # Retourne une liste de données
    def multiple(self) -> []:
        message = ""
        httpRequest = HttpRequest(self.__url, self.__login, self.__password, self.__proxy)
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
            return

    # Requete HTTP simple
    def simple(self) -> Response:
        httpRequest = HttpRequest(self.__url, self.__login, self.__password, self.__proxy)
        response = httpRequest.getResponse(self.__partOfUrl, None)
        if response.status_code != 200:
            message = "Query.simple : {}".format(response.text)
            raise Exception(message)
        return response
