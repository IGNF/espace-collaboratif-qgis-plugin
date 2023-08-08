from .RipartLoggerCl import RipartLogger
from datetime import datetime


class Report(object):

    def __init__(self, urlHostEspaceCo, data) -> None:
        self.__logger = RipartLogger("Report").getRipartLogger()
        self.__urlHostEspaceCo = urlHostEspaceCo
        self.__id = data['id']
        self.__author = data['author']
        self.__commune = data['commune']['title']
        self.__insee = data['commune']['name']
        self.__departement = data['departement']['title']
        self.__departementId = data['departement']['name']
        self.__dateCreation = data['opening_date']
        self.__dateMaj = data['updating_date']
        self.__dateValidation = data['closing_date']
        self.__themes = data['attributes']
        self.__statut = data['status']
        self.__message = data['comment']
        self.__replies = data['replies']
        self.__url = self._setUrl(data['id'])
        self.__urlPrive = ''
        self.__attachments = data['attachments']
        self.__autorisation = ''
        self.__comment = data['comment']
        self.__inputDevice = data['input_device']
        self.__geometry = data['geometry']
        # TODO autres variables retournées par l'API, que fait-on ?
        # self.__community = data['community']
        # self.__validator = data['validator']
        # self.__territory = data['territory']
        # self.__attributes = data['attributes']
        # self.__sketch_xml = data['sketch_xml']
        # self.__sketch = data['sketch']
        # self.__input_device = data['input_device']

    def getId(self) -> int:
        return self.__id

    def getComment(self) -> str:
        return self.__comment

    def getCommune(self) -> str:
        return self.__commune

    def getInsee(self) -> str:
        return self.__insee

    def getDateCreation(self) -> str:
        # valeur de retour 2023-08-01T14:51:55+02:00
        return self.__dateCreation

    def getStatut(self) -> str:
        return self.__statut

    def getInputDevice(self) -> str:
        return self.__inputDevice

    def getGeometry(self) -> str:
        return self.__geometry

    # TODO dans SQLIte, on stoke du json ou une chaine reformatée ?
    #  j'ai pris l'option chaine reformatée
    def getColumnsForSQlite(self) -> {}:
        return {
            'NoSignalement': self.__id,
            'Auteur': self.__setStrForDatabase(self.getStrAuthor()),
            'Commune': self.__setStrForDatabase(self.__commune),
            'Insee': self.__insee,
            'Département': self.__setStrForDatabase(self.__departement),
            'Département_id': self.__departementId,
            'Date_création': self.getDatetimeCreation(),
            'Date_MAJ': self.getDatetimeMaj(),
            'Date_validation': self.getDatetimeValidation(),
            'Thèmes': self.__setStrForDatabase(self.getStrThemes()),
            'Statut': self.__statut,
            'Message': self.__setStrForDatabase(self.__message),
            'Réponses': self.__setStrForDatabase(self.getStrReplies()),
            'URL': self.__url,
            'URL_privé': self.__urlPrive,
            'Document': self._getStrAttachments(),
            'Autorisation': self.__autorisation,
            'geom': self.__geometry
        }

    def __notNoneValue(self, nodeValue) -> str:
        if nodeValue is None:
            return ""
        return nodeValue

    def __setStrForDatabase(self, strToEvaluate) -> str:
        strForDB = self.__notNoneValue(strToEvaluate)
        strForDB = strForDB.replace("'", "''")
        strForDB = strForDB.replace('"', '""')
        return strForDB

    def __formatDateToStrftime(self, dateToFormat):
        # valeur en entrée 2023-08-01T14:51:55+02:00
        # valeur de retour 2023-08-01 14:51:55
        dt = datetime.fromisoformat(dateToFormat)
        dtc = dt.strftime('%Y-%m-%d %H:%M:%S')
        return dtc

    def getDatetimeCreation(self):
        return self.__formatDateToStrftime(self.__dateCreation)

    def getDatetimeMaj(self):
        return self.__formatDateToStrftime(self.__dateMaj)

    def getDatetimeValidation(self):
        return self.__formatDateToStrftime(self.__dateValidation)

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
        return self.__author['username']

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

    def getStrThemes(self) -> str:
        strThemes = ""
        for t in self.__themes:
            # le nom du thème
            strThemes += self.__setStrForDatabase(t['theme'])
            # les attributs du thème
            if len(t['attributes']) == 0:
                continue
            z = 0
            for attName, attValue in t['attributes'].items():
                if z == 0:
                    strThemes += "("
                    z += 1
                strThemes += self.__setStrForDatabase("{}={},".format(attName, self.__notNoneValue(attValue)))
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
                # TODO c'est un n° et non le username
                #  que fait-on ?
                #  ticket redmine
                #  ou requete https://qlf-collaboratif.ign.fr/collaboratif-develop/gcms/api/users/user_id
                strReplies += " par {}".format(replie['author'])
                strReplies += " le {}.".format(self.__formatDateToStrftime(replie['date']))
                strReplies += "\n{}\n".format(replie['content'])
        return strReplies

    # Crée de toutes pieces une url d'accès au signalement
    def _setUrl(self, idReport) -> str:
        # TODO faut-il demander l'ajout de cette url dans la réponse de la nouvelle API ?
        return "{0}/gcms/api/reports/{1}".format(self.__urlHostEspaceCo, idReport)
