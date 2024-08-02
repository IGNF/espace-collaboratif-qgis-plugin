# Cette classe sert de client pour le service de l'espace collaboratif
import xml.etree.ElementTree as ET
from collections import OrderedDict
import os.path
import json

from . import Constantes
from .Remarque import Remarque
from .RipartServiceRequest import RipartServiceRequest
from .XMLResponse import XMLResponse
from .ClientHelper import ClientHelper
from .NoProfileException import NoProfileException
from .RipartLoggerCl import RipartLogger
from . import requests
from .requests.auth import HTTPBasicAuth
import os
from .ProgressBar import ProgressBar
from .Community import Community


class Client(object):
    def __init__(self, url, login, pwd, proxies):
        """
        Initialisation du client et connexion au service ripart
        """
        self.__url = url
        self.__login = login
        self.__password = pwd
        self.__auth = {'login': self.__login, 'password': self.__password}
        self.__proxies = proxies
        self.__author = None
        self.__version = None
        self.__profile = None
        # message d'erreur lors de la connexion ou d'un appel au service ("OK" ou message d'erreur)
        self.message = ""
        self.iface = None
        self.progress = None
        self.logger = RipartLogger("Client").getRipartLogger()

    def getUrl(self):
        return self.__url

    def getAuth(self):
        return self.__auth

    def getProxies(self):
        return self.__proxies

    def setIface(self, iface):
        """sets the QgsInterface instance, to be able to access the QGIS application objects (map canvas, menus, ...)
        """
        self.iface = iface

    # def connect(self):
    #     """
    #     Connexion d'un utilisateur par son login et mot de passe
    #     :return : Si la connexion se fait, retourne l'id de l'auteur ; sinon retour du message d'erreur
    #     """
    #     try:
    #         self.logger.debug("tentative de connexion; " + self.__url + ' connect ' + self.__login)
    #         requests.get(self.__url, proxies=self.__proxies, auth=HTTPBasicAuth(self.__login, self.__password))
    #     except Exception as e :
    #         self.logger.error(format(e))
    #         raise Exception(format(e))
    #     return self

    def getProfile(self):
        if self.__profile is None:
            self.__profile = self.getProfilFromService()
        return self.__profile

    def getProfilFromService(self):
        """
        Requête au service pour le profil utilisateur
        :return : le profil de l'utilisateur
        """
        community = Community(self.__url, self.__login, self.__password, self.__proxies)
        profile = community.getProfile()
        return profile

    def getNomProfil(self):
        url = "{}/{}".format(self.__url, "api/georem/geoaut_get.xml")
        self.logger.debug(url)
        data = requests.get(url, auth=HTTPBasicAuth(self.__login, self.__password), proxies=self.__proxies)
        self.logger.debug("data auth ")
        xml = XMLResponse(data.text)

        errMessage = xml.checkResponseValidity()
        if errMessage['code'] == 'OK':
            nomProfil = xml.extractNomProfil()
        else:
            if errMessage['message'] != "":
                result = errMessage['message']
            elif errMessage['code'] != "":
                result = ClientHelper.getErrorMessage(errMessage['code'])
            else:
                result = ClientHelper.getErrorMessage(data.status_code)

            raise Exception(ClientHelper.notNoneValue(result))

        return nomProfil

    '''
        Connexion à une base de données et une couche donnée
        La requête est par exemple :
        https://espacecollaboratif.ign.fr/gcms/api/database/test/feature-type/Surfaces.json
        La réponse transformée en json est sous forme de dictionnaire par exemple :
        ...'attributes': 'zone': {...,'listOfValues': [None, 'Zone1', ' Zone2', 'Zone3'],...}...
    '''

    def connexionFeatureTypeJson(self, layerUrl, layerName):
        if '&' not in layerUrl:
            raise Exception(ClientHelper.notNoneValue(
                "{} : l'url fournie ({}) ne permet pas de déterminer le nom de la base données".format(
                    "connexionFeatureTypeJson", layerUrl)))

        tmp = layerUrl.split('&')
        dbName = tmp[1].split('=')
        url = "{}/gcms/api/database/{}/feature-type/{}.json".format(self.__url, dbName[1], layerName)
        self.logger.debug("{0} {1}".format("connexionFeatureTypeJson : ", url))

        featuretypeResponse = requests.get(url, auth=HTTPBasicAuth(self.__login, self.__password),
                                           proxies=self.__proxies)
        if featuretypeResponse.status_code != 200:
            raise Exception(ClientHelper.notNoneValue(
                "{} : {}".format(featuretypeResponse.status_code, featuretypeResponse.reason)))

        data = json.loads(featuretypeResponse._content)
        return data

    '''
        Pour l'item 'style', récupération de la symbologie d'une couche
    '''

    # TODO à supprimer
    # def getListOfValuesFromItemStyle(self, dataFeaturetype):
    #     listOfValues = {}
    #     tmp = {'children': []}
    #     for dftKey, dftValue in dataFeaturetype.items():
    #         if dftKey != 'style':
    #             continue
    #
    #         # La couche n'a pas de style défini, QGIS applique une symbologie par défaut
    #         if dftValue is None:
    #             return listOfValues
    #
    #         for dftvKey, dftvValues in dftValue.items():
    #             if dftvKey == 'children':
    #                 if type(dftvValues) is list and len(dftvValues) == 0:
    #                     continue
    #                 else:
    #                     for dftvValue in dftvValues:
    #                         listOfValues[dftvValue['name']] = dftvValue
    #             else:
    #                 tmp[dftvKey] = dftvValues
    #
    #         listOfValues['default'] = tmp
    #
    #     return listOfValues

    def getGeoRems(self, parameters):
        """Recherche les remarques.
        Boucle sur la méthode privée __getGeoRemsTotal, pour récupérer d'éventuelles MAJ ou nouvelles remarques
        faites entre le début et la fin de la requête

        :param parameters : les paramètres de la requête
        :type parameters : dictionary
        """
        # progressbar pour le chargement des remarques
        mess = "Téléchargement des signalements depuis le serveur"
        self.progress = ProgressBar(200, mess)
        result = self.__getGeoRemsTotal(parameters)
        total = int(result["total"])  # nb de remarques récupérées
        sdate = result["sdate"]  # date de la réponse du serveur
        while total > 1:
            parameters['updatingDate'] = sdate
            tmp = self.__getGeoRemsTotal(parameters)
            result['dicoRems'].update(tmp['dicoRems'])  # add the tmp result to the result['dicoRems'] dictionnary
            total = tmp['total']
            sdate = tmp["sdate"]
            self.logger.debug("loop on total result " + " total=" + str(result['total']) + ",datetime=" + sdate)
        self.progress.close()
        # tri des remarques par ordre décroissant d'id
        dicoRems = OrderedDict(sorted(list(result['dicoRems'].items()), key=lambda t: t[0], reverse=True))
        return dicoRems

    def __getGeoRemsTotal(self, parameters):
        """Recherche les remarques en fonction des paramètres et retourne le nombre total de remarques trouvées

        :param parameters : les paramètres de la requête
        :type parameters : dictionary

        :return dictionnaire contenant les remarques
        :rtype dictionary
        """
        pagination = parameters['pagination']
        try:
            data = RipartServiceRequest.makeHttpRequest(self.__url + "/api/georem/georems_get.xml",
                                                        authent=self.__auth,
                                                        proxies=self.__proxies,
                                                        params=parameters)
        except Exception as e:
            self.logger.error(str(e))
            raise

        xml = XMLResponse(data)
        errMessage = xml.checkResponseValidity()
        count = int(pagination)

        if errMessage['code'] == 'OK':
            total = int(xml.getTotalResponse())
            sdate = xml.getDate()
            dicoRems = xml.extractRemarques()

            if count > total:
                progressMax = int(pagination)
            else:
                progressMax = total

            self.progress.setMaximum(progressMax)
            self.progress.setValue(count)

            while (total - count) > 0:
                parameters["offset"] = count.__str__()
                data = RipartServiceRequest.makeHttpRequest(self.__url + "/api/georem/georems_get.xml",
                                                            authent=self.__auth, proxies=self.__proxies,
                                                            params=parameters)
                xml = XMLResponse(data)
                count += int(pagination)
                errMessage2 = xml.checkResponseValidity()
                if errMessage2['code'] == 'OK':
                    dicoRems.update(xml.extractRemarques())
                self.progress.setValue(count)

            return {'total': total, 'sdate': sdate, 'dicoRems': dicoRems}

        else:
            err = errMessage.get('message')
            raise NoProfileException(err)

    def getGeoRem(self, idSignalement):
        """Requête pour récupérer une remarque avec un identifiant donné

        :param idSignalement : identifiant de la remarque que l'on souhaite récupérer
        :type idSignalement : int

        :return la remarque
        :rtype Remarque
        """
        rem = Remarque()

        uri = self.__url + "/api/georem/georem_get/" + str(idSignalement) + ".xml"

        data = RipartServiceRequest.makeHttpRequest(uri, authent=self.__auth, proxies=self.__proxies)

        xmlResponse = XMLResponse(data)
        errMessage = xmlResponse.checkResponseValidity()

        total = xmlResponse.getTotalResponse()

        if errMessage['code'] == "OK" and int(total) == 1:
            remarques = xmlResponse.extractRemarques()
            rem = list(remarques.values())[0]

        return rem

    # def setChangeUserProfil(self, idProfil):
    #     message = ""
    #     # uri = self.__url + "/api/georem/geoaut_switch_profile/" + idProfil
    #     # https://espacecollaboratif.ign.fr/gcms/api/communities/375
    #     uri = "{0}/gcms/api/communities/{1}".format(self.__url, idProfil)
    #     print(uri)
    #     response = RipartServiceRequest.makeHttpRequest(uri, authent=self.__auth, proxies=self.__proxies)
    #     jsonResponse = JsonResponse(response)
    #     jsonResponse.checkResponseValidity()
    #     jsonResponse.readData()
    #     profil = jsonResponse.extractProfileFromCommunities()
    #     return profil

    def addResponse(self, report, response, titleResponse):
        """Ajoute une réponse à une remarque

        :param report : la remarque
        :type report: Remarque

        :param response : la réponse
        :type response: string

        :param titleResponse : le titre de la réponse
        :type titleResponse : string

        :return la remarque à laquelle a été ajoutée la réponse
        """
        errMessage = {}
        try:
            parameters = {'id': str(report.id), 'title': titleResponse, 'content': response,
                          'status': report.statut.__str__()}

            uri = self.__url + "/api/georem/georep_post.xml"

            data = RipartServiceRequest.makeHttpRequest(uri, authent=self.__auth, proxies=self.__proxies,
                                                        data=parameters)
            xmlResponse = XMLResponse(data)
            errMessage = xmlResponse.checkResponseValidity()
            if errMessage['code'] == "OK":
                rems = xmlResponse.extractRemarques()
                if len(rems) == 1:
                    remModif = list(rems.values())[0]
                else:
                    raise Exception("Problème survenu lors de l'ajout d'une réponse")
            else:
                raise Exception(errMessage['code'] + " " + errMessage['message'])
        except Exception as e:
            raise Exception(errMessage['message'], e)
        return remModif

    # TODO à supprimer
    # def createRemarque(self, remarque, idSelectedGeogroup):
    #     try:
    #         params = {'version': Constantes.RIPART_CLIENT_VERSION,
    #                   'protocol': Constantes.RIPART_CLIENT_PROTOCOL,
    #                   'comment': ClientHelper.notNoneValue(remarque.commentaire)}
    #         geometry = "POINT(" + str(remarque.getLongitude()) + " " + str(remarque.getLatitude()) + ")"
    #         params['geometry'] = geometry
    #         params['territory'] = self.getProfile().zone.__str__()
    #         params['group'] = idSelectedGeogroup
    #
    #         # Ajout des thèmes selectionnés
    #         themes = remarque.themes
    #         if themes is not None and len(themes) > 0:
    #             attributes = ""
    #             for t in themes:
    #                 groupeIdAndNom = ClientHelper.notNoneValue('"' + t.group.getId() + "::" + t.group.getName())
    #                 attributes += ClientHelper.notNoneValue(groupeIdAndNom + "\"=>\"1\",")
    #                 for at in t.attributes:
    #                     attributes += groupeIdAndNom + "::" + at.nom + '"=>"' + at.valeur + '",'
    #
    #             attributes = attributes[:-1]
    #             params["attributes"] = attributes
    #
    #         # ajout des croquis
    #         if not remarque.isCroquisEmpty():
    #             croquis = remarque.croquis
    #             gmlurl = "http://www.opengis.net/gml"
    #             doc = ET.Element("CROQUIS", {"xmlns:gml": gmlurl})
    #
    #             for cr in croquis:
    #                 doc = cr.encodeToXML(doc)
    #
    #             params["sketch"] = ET.tostring(doc)
    #
    #         # ajout des documents joints
    #         documents = remarque.documents
    #         docCnt = 0
    #         files = {}
    #         for document in documents:
    #             if os.path.isfile(document):
    #                 docCnt += 1
    #                 if os.path.getsize(document) > Constantes.MAX_TAILLE_UPLOAD_FILE:
    #                     raise Exception("Le fichier " + document + " est de taille supérieure à " +
    #                                     str(Constantes.MAX_TAILLE_UPLOAD_FILE))
    #
    #                 files = {"upload" + str(docCnt): open(ClientHelper.notNoneValue(document), 'rb')}
    #
    #         # envoi de la requête
    #         uri = self.__url + "/api/georem/georem_post.xml"
    #         data = RipartServiceRequest.makeHttpRequest(uri, authent=self.__auth, proxies=self.__proxies, data=params,
    #                                                     files=files)
    #         xmlResponse = XMLResponse(data)
    #         errMessage = xmlResponse.checkResponseValidity()
    #
    #         if errMessage['code'] == 'OK':
    #             rems = xmlResponse.extractRemarques()
    #             if len(rems) == 1:
    #                 rem = list(rems.values())[0]
    #             else:
    #                 self.logger.error("Problème lors de l'ajout de la remarque")
    #                 raise Exception("Problème lors de l'ajout de la remarque")
    #         else:
    #             self.logger.error(errMessage['message'])
    #             raise Exception(errMessage['message'])
    #
    #     except Exception as e:
    #         self.logger.error(str(e))
    #         raise Exception(e)
    #
    #     return rem

    @staticmethod
    def get_MAX_TAILLE_UPLOAD_FILE():
        return Constantes.MAX_TAILLE_UPLOAD_FILE
