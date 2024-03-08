import json
from datetime import datetime
from .RipartLoggerCl import RipartLogger
from .SQLiteManager import SQLiteManager
from . import Constantes as cst


class Report(object):

    def __init__(self, urlHostEspaceCo, data) -> None:
        self.__logger = RipartLogger("Report").getRipartLogger()
        self.__urlHostEspaceCo = urlHostEspaceCo
        if self.__keyExist('id', data):
            self.__id = data['id']
            self.__url = self.__setUrl(data['id'])
        if self.__keyExist('author', data):
            self.__author = self.__notNoneValue(data['author'])
        if self.__keysExists('commune', 'title', data):
            self.__commune = data['commune']['title']
        if self.__keysExists('commune', 'name', data):
            self.__insee = data['commune']['name']
        if self.__keysExists('departement', 'title', data):
            self.__departement = data['departement']['title']
        if self.__keysExists('departement', 'name', data):
            self.__departementId = data['departement']['name']
        if self.__keyExist('opening_date', data):
            self.__dateCreation = data['opening_date']
        if self.__keyExist('updating_date', data):
            self.__dateMaj = data['updating_date']
        if self.__keyExist('closing_date', data):
            self.__dateValidation = data['closing_date']
        if self.__keyExist('attributes', data):
            self.__themes = data['attributes']
        if self.__keyExist('status', data):
            self.__statut = data['status']
        if self.__keyExist('comment', data):
            self.__message = data['comment']
        if self.__keyExist('replies', data):
            self.__replies = data['replies']
        self.__urlPrive = ''
        if self.__keyExist('attachments', data):
            self.__attachments = data['attachments']
        # TODO les autorisations ne sont plus dans la réponse il faut les déduire...???? dixit Sylvain
        #  résultat : ticket redmine to Madeline
        self.__autorisation = ''
        if self.__keyExist('input_device', data):
            self.__inputDevice = data['input_device']
        if self.__keyExist('geometry', data):
            self.__geometry = data['geometry']
        # TODO à décoder pour importer les croquis dans la carte
        # self.__sketch_xml = data['sketch_xml']
        if self.__keyExist('sketch', data):
            self.__sketch = data['sketch']
        # TODO -> Noémie les variables suivantes sont retournées par l'API, que fait-on ?
        # self.__community = data['community']
        # self.__validator = data['validator']
        # self.__territory = data['territory']
        # self.__comment = data['comment']

    def __keysExists(self, keyA, keyB, data) -> bool:
        if self.__keyExist(keyA, data):
            datum = data[keyA]
            if self.__keyExist(keyB, datum):
                return True
        return False

    def __keyExist(self, key, data) -> bool:
        if key in data:
            return True
        return False

    def getId(self) -> int:
        return self.__id

    def getCommune(self) -> str:
        return self.__commune

    def getInsee(self) -> str:
        return self.__insee

    def getDateCreation(self) -> str:
        # valeur de retour 2023-08-01T14:51:55+02:00
        return self.__dateCreation

    def setStatut(self, statut):
        self.__statut = statut

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

    def getSketchXml(self) -> str:
        return self.__sketch_xml

    # TODO dans SQLIte, on stoke du json ou une chaine reformatée ?
    #  j'ai pris l'option chaine reformatée
    def getColumnsForSQlite(self) -> {}:
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
            'Thèmes': self.getStrThemes(),
            'Statut': self.__statut,
            'Message': self.__message,
            'Réponses': self.getStrReplies().replace('\n', ' '),
            'URL': self.__url,
            'URL_privé': self.__urlPrive,
            'Document': self._getStrAttachments(),
            'Autorisation': self.__autorisation,
            'geom': self.__geometry
        }

    def InsertSketchIntoSQLite(self):
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

    def __getKey(self, datas, key):
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

        if len(data['attributes']) == 0:
            return strAttributes

        for k, v in data['attributes'].items():
            strAttributes += "{0}='{1}'|".format(self.__notNoneValue(k), self.__notNoneValue(v))

        if len(strAttributes) > 0:
            strAttributes = strAttributes[:-1]

        return strAttributes

    def __whatGeometryAndTableIs(self, geom) -> ():
        if 'POINT' in geom:
            return 'POINT', cst.nom_Calque_Croquis_Point
        if 'LINESTRING' in geom:
            return 'LINESTRING', cst.nom_Calque_Croquis_Ligne
        if 'POLYGON' in geom:
            return 'POLYGON', cst.nom_Calque_Croquis_Polygone

    def __notNoneValue(self, nodeValue) -> str:
        if nodeValue is None:
            return ""
        return nodeValue

    def __formatDateToStrftime(self, dateToFormat):
        # valeur en entrée 2023-08-01T14:51:55+02:00
        # valeur de retour 2023-08-01 14:51:55
        if dateToFormat == '':
            return dateToFormat
        dt = datetime.fromisoformat(dateToFormat)
        dtc = dt.strftime('%Y-%m-%d %H:%M:%S')
        return dtc

    def getStrDateCreation(self):
        dc = self.__notNoneValue(self.__dateCreation)
        return self.__formatDateToStrftime(dc)

    def getStrDateMaj(self):
        dm = self.__notNoneValue(self.__dateMaj)
        return self.__formatDateToStrftime(dm)

    def getStrDateValidation(self):
        dv = self.__notNoneValue(self.__dateValidation)
        return self.__formatDateToStrftime(dv)

    def getAuthor(self) -> {}:
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
        # return self.__author['username']

    def getAttachments(self) -> [{}]:
        # valeur de retour
        # {
        # "short_fileName": "Toto.txt",
        # "id": 7056,
        # "title": "Toto",
        # "description": null,
        # "filename": "IMG/txt/4990fcaa50b7e36c7e4b2b3d04463de5_Toto.txt",
        # "size": 52,
        # "width": null,
        # "height": null,
        # "date": "2023-08-01T13:01:13+02:00",
        # "geometry": "POINT(2.53161412208155 48.8635337081288)",
        # "download_uri": "https://qlf-collaboratif.ign.fr/collaboratif-develop/document/download/7056"
        # }
        return self.__attachments

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

    def getListAttachments(self):
        attachments = []
        for attachment in self.__attachments:
            attachments.append(attachment['download_uri'])
        return attachments

    def getThemes(self) -> [{}]:
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
        return self.__themes

    def getStrThemesForDisplay(self, activeUserCommunity) -> str:
        strThemes = ""
        for t in self.__themes:
            # le nom du thème
            if 'theme' in t:
                strThemes += t['theme']
            else:
                strThemes += 'Nom de thème inconnu'
            # les attributs du thème
            if 'attributes' not in t:
                continue
            if len(t['attributes']) != 0:
                z = 0
                for key, value in t['attributes'].items():
                    if z == 0:
                        strThemes += "("
                        z += 1
                    strThemes += "{}={},".format(activeUserCommunity.switchNameToTitleFromThemeAttributes(key),
                                                 self.__notNoneValue(value))
                if z > 0:
                    strThemes = strThemes[:-1]
                    strThemes += ")"
            strThemes += "|"
        return strThemes[:-1]

    def getStrThemes(self) -> str:
        strThemes = ""
        for t in self.__themes:
            # le nom du thème
            if 'theme' in t:
                strThemes += t['theme']
            else:
                strThemes += 'Nom de thème inconnu'
            # les attributs du thème
            if 'attributes' not in t:
                continue
            if len(t['attributes']) != 0:
                z = 0
                for key, value in t['attributes'].items():
                    if z == 0:
                        strThemes += "("
                        z += 1
                    strThemes += "{}={},".format(key, self.__notNoneValue(value))
                if z > 0:
                    strThemes = strThemes[:-1]
                    strThemes += ")"
            strThemes += "|"
        return strThemes[:-1]

    def getReplies(self) -> [{}]:
        # valeur de retour
        # {"author": 3,
        # "id": 79743,
        # "title": "test",
        # "content": "test",
        # "status": "valid",
        # "date": "2010-01-07T10:46:04+01:00"}
        return self.__replies

    # Concatène les réponses existantes d'un signalement
    def getStrReplies(self) -> str:
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
                strReplies += " par {}".format(replie['author']['username'])
                strReplies += " le {}.".format(self.__formatDateToStrftime(replie['date']))
                strReplies += "\n{}\n".format(replie['content'])
        return strReplies[:-1]

    # Crée de toutes pieces une url d'accès au signalement
    def __setUrl(self, idReport) -> str:
        # TODO -> Noémie faut-il demander l'ajout de cette url dans la réponse de la nouvelle API ?
        return "{0}/gcms/api/reports/{1}".format(self.__urlHostEspaceCo, idReport)
