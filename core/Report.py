from .RipartLoggerCl import RipartLogger

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
        self.__themes = self.setThemes(data['attributes'])
        self.__statut = data['status']
        self.__message = data['comment']
        self.__replies = self.setReplies(data['replies'])
        self.__url = self.setUrl(data['id'])
        self.__urlPrive = ''
        self.__attachments = self.setAttachments(data['attachments'])
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

    def getAuthor(self) -> str:
        return self.__author

    def getCommune(self) -> str:
        return self.__commune

    def getInsee(self) -> str:
        return self.__insee

    def getDateCreation(self) -> str:
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
            'Auteur': self.__author,
            'Commune': self.__commune,
            'Insee': self.__insee,
            'Département': self.__departement,
            'Département_id': self.__departementId,
            'Date_création': self.__dateCreation,
            'Date_MAJ': self.__dateMaj,
            'Date_validation': self.__dateValidation,
            'Thèmes': self._getStrThemes(),
            'Statut': self.__statut,
            'Message': self.__message,
            'Réponses': self._getStrReplies(),
            'URL': self.__url,
            'URL_privé': self.__urlPrive,
            'Document': self._getStrAttachments(),
            'Autorisation': self.__autorisation,
            'geom': self.__geometry
        }

    def setAttachments(self, attachments) -> []:
        listAttachments = []
        if attachments is None or len(attachments) == 0:
            return listAttachments
        for attachment in attachments:
            listAttachments.append(attachment['download_uri'])
        return listAttachments

    def getAttachments(self) -> []:
        return self.__attachments

    def _getStrAttachments(self) -> str:
        documents = ''
        if self.__attachments is None or len(self.__attachments) == 0:
            return documents
        for attachment in self.__attachments:
            documents += "{} ".format(attachment)
        return documents[:-1]

    def setThemes(self, themes) -> []:
        listThemes = []
        if themes is None or len(themes) == 0:
            return listThemes
        for theme in themes:
            listThemes.append(theme)
        return listThemes

    def getThemes(self) -> []:
        return self.__themes

    def _getStrThemes(self) -> str:
        strThemes = ''
        if self.__themes is None or len(self.__themes) == 0:
            return strThemes
        for theme in self.__themes:
            strThemes += "{},".format(theme)
        return strThemes[:-1]

    def setReplies(self, replies) -> []:
        listReplies = []
        if replies is None or len(replies) == 0:
            return listReplies
        for replie in replies:
            listReplies.append(replie)
        return listReplies

    def getReplies(self) -> []:
        return self.__replies

    def _getStrReplies(self) -> str:
        strReplies = ''
        if self.__replies is None or len(self.__replies) == 0:
            return strReplies
        for replie in self.__replies:
            strReplies += "{},".format(replie)
        return strReplies[:-1]

    def setUrl(self, idReport) -> str:
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
