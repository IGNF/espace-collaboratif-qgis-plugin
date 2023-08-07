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

    def getColumnsForSQlite(self) -> {}:
        return {
            'NoSignalement': self.__id,
            'Auteur': self.getStrAuthor(),
            'Commune': self.__commune,
            'Insee': self.__insee,
            'Département': self.__departement,
            'Département_id': self.__departementId,
            'Date_création': self.getDatetimeCreation(),
            'Date_MAJ': self.getDatetimeMaj(),
            'Date_validation': self.getDatetimeValidation(),
            'Thèmes': self.getStrThemes(),
            'Statut': self.__statut,
            'Message': self.__message,
            'Réponses': self.getStrReplies(),
            'URL': self.__url,
            'URL_privé': self.__urlPrive,
            'Document': self._getStrAttachments(),
            'Autorisation': self.__autorisation,
            'geom': self.__geometry
        }

    def getDatetimeCreation(self):
        # valeur en entrée 2023-08-01T14:51:55+02:00
        # valeur de retour 2023-08-01 14:51:55
        dt = datetime.fromisoformat(self.__dateCreation)
        dtc = dt.strftime('%Y-%m-%d %H:%M:%S')
        return dtc

    def getDatetimeMaj(self):
        # valeur en entrée 2023-08-01T14:51:55+02:00
        # valeur de retour 2023-08-01 14:51:55
        dt = datetime.fromisoformat(self.__dateCreation)
        dtmaj = dt.strftime('%Y-%m-%d %H:%M:%S')
        return dtmaj

    def getDatetimeValidation(self):
        # valeur en entrée 2023-08-01T14:51:55+02:00
        # valeur de retour 2023-08-01 14:51:55
        dt = datetime.fromisoformat(self.__dateCreation)
        dtv = dt.strftime('%Y-%m-%d %H:%M:%S')
        return dtv

    def getAuthor(self) -> {}:
        # valeur de retour
        # {"id": 676,
        # "username": "epeyrouse",
        # "email": "eric.peyrouse@ign.fr"}
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
        # {"short_fileName": "Toto.txt",
        # "id": 7056,
        # "title": "Toto",
        # "description": null,
        # "filename": "IMG/txt/4990fcaa50b7e36c7e4b2b3d04463de5_Toto.txt",
        # "size": 52,
        # "width": null,
        # "height": null,
        # "date": "2023-08-01T13:01:13+02:00",
        # "geometry": "POINT(2.53161412208155 48.8635337081288)",
        # "download_uri": "https://qlf-collaboratif.ign.fr/collaboratif-develop/document/download/7056"}
        #
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
        return self.__themes

    def getStrThemes(self) -> str:
        strThemes = ''
        if self.__themes is None or len(self.__themes) == 0:
            return strThemes
        for theme in self.__themes:
            strThemes += "{},".format(theme)
        return strThemes[:-1]

    def getReplies(self) -> [{}]:
        return self.__replies

    def getStrReplies(self) -> str:
        strReplies = ''
        if self.__replies is None or len(self.__replies) == 0:
            return strReplies
        for replie in self.__replies:
            strReplies += "{},".format(replie)
        return strReplies[:-1]

    def _setUrl(self, idReport) -> str:
        return "{0}/gcms/api/reports/{1}".format(self.__urlHostEspaceCo, idReport)

    #  Concatène les réponses existantes d'un signalement
    # def concatenateReplies(self) -> str:
    #     concatenate = ""
    #
    #     if len(self.__replies) == 0:
    #         concatenate += "Ce signalement n'a pas reçu de réponses."
    #     else:
    #         count = len(self.__replies)
    #         for response in self.__replies:
    #             concatenate += "Réponse n°" + count.__str__()
    #             count -= 1
    #
    #             if response.author.name is not None:
    #                 author_name = response.author.name
    #                 if len(author_name) != 0:
    #                     concatenate += " par " + response.author.name
    #             if response.date is not None:
    #                 concatenate += " le " + response.date.strftime("%Y-%m-%d %H:%M:%S")
    #
    #             try:
    #                 if response.response is not None:
    #                     concatenate += ".\n" + response.response.strip() + "\n"
    #                 else:
    #                     self.__logger.error("No message in response " + self.__id)
    #             except Exception as e:
    #                 self.__logger.error(format(e))
    #
    #     return concatenate
