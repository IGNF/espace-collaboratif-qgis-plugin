import json
from datetime import datetime
from .RipartLoggerCl import RipartLogger
from .SQLiteManager import SQLiteManager
from . import Constantes as cst
from ..PluginHelper import PluginHelper


class Report(object):
    """
    Classe implémentant un signalement avec ses attributs
    """
    # Initialisation des variables utiles à un signalement
    __id = -1
    __author = ''
    __commune = ''
    __insee = ''
    __departement = ''
    __departementId = ''
    __dateCreation = ''
    __dateMaj = ''
    __dateValidation = ''
    __theme = ''
    __statut = ''
    __message = ''
    __replies = ''
    __url = ''
    __urlPrive = ''
    __attachments = ''
    __autorisation = ''
    __geometry = ''

    def __init__(self, urlHostEspaceCo, data) -> None:

        self.__logger = RipartLogger("Report").getRipartLogger()
        self.__urlHostEspaceCo = urlHostEspaceCo
        if PluginHelper.keyExist('id', data):
            self.__id = data['id']
            self.__url = self.__setUrl(data['id'])
        if PluginHelper.keyExist('author', data):
            self.__author = data['author']
        if PluginHelper.keysExists('commune', 'title', data):
            self.__commune = data['commune']['title']
        if PluginHelper.keysExists('commune', 'name', data):
            self.__insee = data['commune']['name']
        if PluginHelper.keysExists('departement', 'title', data):
            self.__departement = data['departement']['title']
        if PluginHelper.keysExists('departement', 'name', data):
            self.__departementId = data['departement']['name']
        if PluginHelper.keyExist('opening_date', data):
            self.__dateCreation = data['opening_date']
        if PluginHelper.keyExist('updating_date', data):
            self.__dateMaj = data['updating_date']
        if PluginHelper.keyExist('closing_date', data):
            self.__dateValidation = data['closing_date']
        if PluginHelper.keyExist('attributes', data):
            self.__theme = data['attributes']
        if PluginHelper.keyExist('status', data):
            self.__statut = data['status']
        if PluginHelper.keyExist('comment', data):
            self.__message = data['comment']
        if PluginHelper.keyExist('replies', data):
            self.__replies = data['replies']
        self.__urlPrive = ''
        if PluginHelper.keyExist('attachments', data):
            self.__attachments = data['attachments']
        # TODO les autorisations ne sont plus dans la réponse il faut les déduire...???? dixit Sylvain
        #  résultat : ticket redmine to Madeline
        self.__autorisation = ''
        if PluginHelper.keyExist('input_device', data):
            self.__inputDevice = data['input_device']
        if PluginHelper.keyExist('geometry', data):
            self.__geometry = data['geometry']
        if PluginHelper.keyExist('sketch', data):
            self.__sketch = data['sketch']

    def getId(self) -> int:
        return self.__id

    def getCommune(self) -> str:
        return self.__commune

    def getInsee(self) -> str:
        return self.__insee

    def getStatut(self) -> str:
        return self.__statut

    def getMessage(self) -> str:
        return self.__message

    def getInputDevice(self) -> str:
        return self.__inputDevice

    def getGeometry(self) -> str:
        return self.__geometry

    def getSketch(self) -> str:
        return self.__sketch

    # TODO dans SQLIte, on stoke du json ou une chaine reformatée ?
    #  j'ai pris l'option chaine reformatée
    def getColumnsForSQlite(self) -> dict:
        return {
            'NoSignalement': self.__id,
            'Auteur': self.getStrAuthor(),
            'Commune': self.__commune,
            'Insee': self.__insee,
            'Département': self.__departement,
            'Département_id': self.__departementId,
            'Date_création': self.getStrDateCreation(),
            'Date_MAJ': self.getStrDateMaj(),
            'Date_validation': self.getStrDateValidation(),
            # TODO faut-il le name ou le title de l'attribut dans SQLite (pour l'instant j'ai pris le name)
            'Thèmes': self.getStrThemeInReformattedString(),
            'Statut': self.__statut,
            'Message': self.__message,
            'Réponses': self.getStrReplies().replace('\n', ' '),
            'URL': self.__url,
            'URL_privé': self.__urlPrive,
            'Document': self._getStrAttachments(),
            'Autorisation': self.__autorisation,
            'geom': self.__geometry
        }

    def InsertSketchIntoSQLite(self) -> None:
        if self.getSketch() is None:
            return

        jsonDatas = json.loads(self.getSketch())
        objects = self.__getKey(jsonDatas, 'objects')
        nbSketch = 0
        for obj in objects:
            geom = self.__getKey(obj, 'geometry')
            if geom == '':
                continue
            attributesRows = [{
                'NoSignalement': self.__id,
                'Nom': self.__getKey(obj, 'name'),
                'Attributs_croquis': self.__getAttributes(obj),
                'Lien_objet_BDUNI': '',
                'geom': geom
            }]
            geomAndTable = self.__whatGeometryAndTableIs(geom)
            parameters = {'tableName': geomAndTable[1], 'geometryName': 'geom', 'sridTarget': cst.EPSGCRS4326,
                          'sridSource': cst.EPSGCRS4326, 'isStandard': False, 'is3D': False,
                          'geometryType': geomAndTable[0]}

            sqliteManager = SQLiteManager()
            nbSketch += sqliteManager.insertRowsInTable(parameters, attributesRows)
        print('signalement n° {0}, {1} croquis'.format(self.__id, nbSketch))

    def __getKey(self, datas, key) -> str:
        if key in datas:
            return datas[key]
        return ''

    def __getAttributes(self, datas) -> str:
        strAttributes = ''
        data = None
        if 'attributes' in datas:
            data = datas
        elif 'objects' in datas:
            if 'attributes' in datas['objects']:
                data = datas['objects']
        else:
            return strAttributes

        if data['attributes'] is None:
            return strAttributes

        if len(data['attributes']) == 0:
            return strAttributes

        for k, v in data['attributes'].items():
            strAttributes += "{0}='{1}'|".format(PluginHelper.notNoneValue(k), PluginHelper.notNoneValue(v))

        if len(strAttributes) > 0:
            strAttributes = strAttributes[:-1]

        return strAttributes

    def __whatGeometryAndTableIs(self, geom) -> tuple:
        if 'POINT' in geom:
            return 'POINT', cst.nom_Calque_Croquis_Point
        if 'LINESTRING' in geom:
            return 'LINESTRING', cst.nom_Calque_Croquis_Ligne
        if 'POLYGON' in geom:
            return 'POLYGON', cst.nom_Calque_Croquis_Polygone

    def __formatDateToStrftime(self, dateToFormat) -> str:
        # valeur en entrée 2023-08-01T14:51:55+02:00
        # valeur de retour 2023-08-01 14:51:55
        if dateToFormat == '':
            return dateToFormat
        dt = datetime.fromisoformat(dateToFormat)
        dtc = dt.strftime('%Y-%m-%d %H:%M:%S')
        return dtc

    def getStrDateCreation(self) -> str:
        dc = PluginHelper.notNoneValue(self.__dateCreation)
        return self.__formatDateToStrftime(dc)

    def getStrDateMaj(self) -> str:
        dm = PluginHelper.notNoneValue(self.__dateMaj)
        return self.__formatDateToStrftime(dm)

    def getStrDateValidation(self) -> str:
        dv = PluginHelper.notNoneValue(self.__dateValidation)
        return self.__formatDateToStrftime(dv)

    def getAuthor(self) -> dict:
        # valeur de retour
        # {
        # "id": 676,
        # "username": "epeyrouse",
        # "email": "eric.peyrouse@ign.fr"
        # }
        # ou
        # un entier
        return self.__author

    # SQLite, colonne 'Auteur' : il faut retourner le nom 'username'
    def getStrAuthor(self) -> str:
        if type(self.__author) is int:
            return str(self.__author)
        return self.__author

    # SQLite, colonne 'Document' : il faut retourner l'url 'download_uri'
    def _getStrAttachments(self) -> str:
        # valeur de retour
        # https://qlf-collaboratif.ign.fr/collaboratif-develop/document/download/7058
        # si plusieurs documents, insertion d'un espace entre les url
        documents = ''
        if self.__attachments is None or len(self.__attachments) == 0:
            return documents
        for attachment in self.__attachments:
            documents += "{} ".format(attachment['download_uri'])
        return documents[:-1]

    def getListAttachments(self) -> list:
        attachments = []
        for attachment in self.__attachments:
            attachments.append(attachment['download_uri'])
        return attachments

    def getTheme(self) -> [{}]:
        # valeur de retour
        # attributes": [{
        # "community": 80,
        # "theme": "Dépose-Repose",
        # "attributes": {
        #   "Organisme": "AZERT",
        #   "Téléphone": "4254777",
        #   "Adresse mail": "ffss",
        #   "Disparition RN": "1",
        #   "Adresse Postale": "123 rue poc",
        #   "Nom Correspondant": "azert"
        #   }
        # }]
        return self.__theme

    def getStrThemeInReformattedString(self) -> str:
        """
        Le thème d'un signalement est remanié sous la forme :
        'test levé(Revêtu=1,date=2025-07-17,Nb de voies=12,Largeur=5612)'
        pour le remplissage de la colonne 'Thèmes' de la base SQLite du projet en cours.

        :return: le thème remanié
        """
        strThemes = ""
        for t in self.__theme:
            # le nom du thème
            if 'theme' in t:
                strThemes += "{}".format(t['theme'])
            else:
                strThemes += "Nom de thème inconnu"
            # les attributs du thème
            if 'attributes' not in t:
                continue
            if len(t['attributes']) != 0:
                z = 0
                for key, value in t['attributes'].items():
                    if z == 0:
                        strThemes += "("
                        z += 1
                    strThemes += "{}={},".format(key, PluginHelper.notNoneValue(value))
                if z > 0:
                    strThemes = strThemes[:-1]
                    strThemes += ")"
            strThemes += "|"
        return strThemes[:-1]

    def getStrTheme(self) -> str:
        """
        Mise en page de l'attribut 'Thème' d'un signalement en vue de son affichage lorsque l'utilisateur
        clique sur 'Voir le signalement'

        :return: le thème mis en forme
        """
        strThemes = ""
        for t in self.__theme:
            # le nom du thème
            if 'theme' in t:
                strThemes += "{}\n".format(t['theme'])
            else:
                strThemes += "Nom de thème inconnu\n"
            # les attributs du thème
            if 'attributes' not in t:
                continue
            if len(t['attributes']) != 0:
                for key, value in t['attributes'].items():
                    strThemes += " {} : {}\n".format(key, PluginHelper.notNoneValue(value))
        return strThemes

    def getStrReplies(self) -> str:
        """
        Concatène les réponses existantes (__replies) pour un signalement.

        :return: les réponses assemblées.
        """
        strReplies = ''
        if self.__replies is None or len(self.__replies) == 0:
            return strReplies
        count = len(self.__replies)
        if count == 0:
            strReplies += "Ce signalement n'a pas reçu de réponses."
        else:
            for replie in self.__replies:
                strReplies += "Réponse n°{}".format(count.__str__())
                count -= 1
                # TODO -> Noémie c'est un n° et non le username
                #  que fait-on ?
                #  ticket redmine
                #  ou requete https://qlf-collaboratif.ign.fr/collaboratif-develop/gcms/api/users/user_id
                if replie['author'] is None:
                    strReplies += " par utilisateur inconnu"
                else:
                    strReplies += " par {}".format(replie['author']['username'])
                if replie['date'] is None:
                    strReplies += " le date inconnue."
                else:
                    strReplies += " le {}.".format(self.__formatDateToStrftime(replie['date']))
                if replie['content'] is None:
                    strReplies += "\nCommentaire inconnu\n"
                else:
                    strReplies += "\n{}\n".format(replie['content'])
        return strReplies[:-1]

    def __setUrl(self, idReport) -> str:
        """
        Crée une route HTTP pour accéder aux informations d'un signalement.

        :param idReport: l'identifiant du signalement
        :type idReport: str

        :return: l'url d'accès au signalement
        """
        # TODO -> Noémie faut-il demander l'ajout de cette url dans la réponse de la nouvelle API ?
        return "{0}/gcms/api/reports/{1}".format(self.__urlHostEspaceCo, idReport)
